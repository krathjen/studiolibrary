# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or modify it 
# under the terms of the GNU Lesser General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. This library is distributed in the 
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import os
import logging

from studiolibrarymaya import baseitem

try:
    import mutils
    import mutils.gui
    import maya.cmds
    # Wrapping the following constant for convenience.
    # This also used in the readme.md
    PasteOption = mutils.PasteOption
except ImportError as error:
    print(error)


__all__ = [
    "AnimItem",
]

logger = logging.getLogger(__name__)

DIRNAME = os.path.dirname(__file__)


class AnimItem(baseitem.BaseItem):

    Name = "Animation"
    Extension = ".anim"
    IconPath = os.path.join(DIRNAME, "icons", "animation.png")

    def __init__(self, *args, **kwargs):
        """
        Create a new instance of the anim item from the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        baseitem.BaseItem.__init__(self, *args, **kwargs)

        self.setTransferClass(mutils.Animation)
        self.setTransferBasename("")

    def startFrame(self):
        """Return the start frame for the animation."""
        return self.transferObject().startFrame()

    def endFrame(self):
        """Return the end frame for the animation."""
        return self.transferObject().endFrame()

    def imageSequencePath(self):
        """
        Return the image sequence location for playing the animation preview.

        :rtype: str
        """
        return self.path() + "/sequence"

    def loadSchema(self):
        """
        Get schema used to load the anim item.

        :rtype: list[dict]
        """
        schema = super(AnimItem, self).loadSchema()

        startFrame = self.startFrame() or 0
        endFrame = self.endFrame() or 0

        value = "{0} - {1}".format(startFrame, endFrame)
        schema.insert(3, {"name": "Range", "value": value})

        schema.extend([
            {
                "name": "optionsGroup",
                "title": "Options",
                "type": "group",
                "order": 2,
            },
            {
                "name": "connect",
                "type": "bool",
                "inline": True,
                "default": False,
                "persistent": True,
                "label": {"name": ""}
            },
            {
                "name": "currentTime",
                "type": "bool",
                "inline": True,
                "default": True,
                "persistent": True,
                "label": {"name": ""}
            },
            {
                "name": "source",
                "type": "range",
                "default": [startFrame, endFrame],
            },
            {
                "name": "option",
                "type": "enum",
                "default": "replace all",
                "items": ["replace", "replace all", "insert", "merge"],
                "persistent": True,
            },
        ])

        return schema

    def loadValidator(self, **values):
        """
        Triggered when the user changes options.
        
        This method is not yet used. It will be used to change the state of 
        the options widget. For example the help image.
        
        :type values: list[dict]
        """
        super(AnimItem, self).loadValidator(**values)

        option = values.get("option")
        connect = values.get("connect")

        if option == "replace all":
            basename = "replaceCompletely"
            connect = False
        else:
            basename = option

        if connect and basename != "replaceCompletely":
            basename += "Connect"

        logger.debug(basename)

        return super(AnimItem, self).loadValidator(**values)

    @mutils.showWaitCursor
    def load(
            self,
            objects=None,
            namespaces=None,
            **options
    ):
        """
        Load the animation for the given objects and options.
                
        :type objects: list[str]
        :type namespaces: list[str]
        :type options: dict
        """
        logger.info(u'Loading: {0}'.format(self.path()))

        objects = objects or []

        source = options.get("source")
        option = options.get("option")
        connect = options.get("connect")
        currentTime = options.get("currentTime")

        if option.lower() == "replace all":
            option = "replaceCompletely"

        if source and source != [0, 0]:
            sourceStart, sourceEnd = source
        else:
            sourceStart, sourceEnd = (None, None)

        if sourceStart is None:
            sourceStart = self.startFrame()

        if sourceEnd is None:
            sourceEnd = self.endFrame()

        self.transferObject().load(
            objects=objects,
            namespaces=namespaces,
            currentTime=currentTime,
            connect=connect,
            option=option,
            startFrame=None,
            sourceTime=(sourceStart, sourceEnd)
        )

        logger.info(u'Loaded: {0}'.format(self.path()))

    def saveValidator(self, **kwargs):
        """
        The save validator is called when an input field has changed.

        :type kwargs: dict
        :rtype: list[dict]
        """
        fields = super(AnimItem, self).saveValidator(**kwargs)

        # Validate the by frame field
        if kwargs.get("byFrame") == '' or kwargs.get("byFrame", 1) < 1:
            msg = "The by frame value cannot be less than 1!"
            fields.extend([
                {
                    "name": "byFrame",
                    "error": msg
                }
            ])

        # Validate the frame range field
        start, end = kwargs.get("frameRange", (0, 1))
        if start >= end:
            msg = "The start frame cannot be greater " \
                  "than or equal to the end frame!"
            fields.extend([
                {
                    "name": "frameRange",
                    "error": msg
                }
            ])

        # Validate the current selection field
        selection = maya.cmds.ls(selection=True) or []
        if selection and mutils.getDurationFromNodes(selection) <= 0:
            msg = "No animation was found on the selected object/s! " \
                  "Please create a pose instead!"
            fields.extend([
                {
                    "name": "contains",
                    "error": msg,
                }
            ])

        return fields

    def saveSchema(self):
        """
        Get the anim save schema.
        
        :rtype: list[dict]
        """
        start, end = (1, 100)

        try:
            start, end = mutils.currentFrameRange()
        except NameError as error:
            logger.exception(error)

        return [
            {
                "name": "folder",
                "type": "path",
                "layout": "vertical"
            },
            {
                "name": "name",
                "type": "string",
                "layout": "vertical"
            },
            {
                "name": "fileType",
                "type": "enum",
                "layout": "vertical",
                "default": "mayaAscii",
                "items": ["mayaAscii", "mayaBinary"],
                "persistent": True
            },
            {
                "name": "frameRange",
                "type": "range",
                "layout": "vertical",
                "default": [start, end],
                "actions": [
                    {
                        "name": "From Timeline",
                        "callback": mutils.playbackFrameRange
                    },
                    {
                        "name": "From Selected Timeline",
                        "callback": mutils.selectedFrameRange
                    },
                    {
                        "name": "From Selected Objects",
                        "callback": mutils.selectedObjectsFrameRange
                    },
                ]
            },
            {
                "name": "byFrame",
                "type": "int",
                "default": 1,
                "layout": "vertical",
                "persistent": True
            },
            {
                "name": "comment",
                "type": "text",
                "layout": "vertical"
            },
            {
                "name": "bakeConnected",
                "type": "bool",
                "default": False,
                "persistent": True,
                "inline": True,
                "label": {"visible": False}
            },
            {
                "name": "contains",
                "type": "label",
                "label": {
                    "visible": False
                }
            },
        ]

    def write(self, path, objects, iconPath="", sequencePath="", **options):
        """
        Write the animation on the given objects to the given path.
        
        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type sequencePath: str
        """
        super(AnimItem, self).write(path, objects, iconPath, **options)

        # Save the animation to the given path location on disc
        mutils.saveAnim(
            objects,
            path,
            time=options.get("frameRange"),
            fileType=options.get("fileType"),
            iconPath=iconPath,
            metadata={"description": options.get("comment", "")},
            sequencePath=sequencePath,
            bakeConnected=options.get("bake")
        )
