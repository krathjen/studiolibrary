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

import logging

import studiolibrarymaya
import studiolibrary.widgets

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

# Register the anim item to the Studio Library
iconPath = studiolibrarymaya.resource().get("icons", "animation.png")


class AnimItem(baseitem.BaseItem):

    Extensions = [".anim"]
    Extension = ".anim"
    MenuName = "Animation"
    MenuIconPath = iconPath
    TypeIconPath = iconPath

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
        self.setReadOnly(True)

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

    def info(self):
        """
        Get the info to display to user.
        
        :rtype: list[dict]
        """
        info = baseitem.BaseItem.info(self)

        startFrame = str(self.startFrame())
        endFrame = str(self.endFrame())

        info.insert(3, {"name": "Start frame", "value": startFrame})
        info.insert(4, {"name": "End frame", "value": endFrame})

        return info

    def loadSchema(self):
        """
        Get the options for the item.
        
        :rtype: list[dict]
        """
        startFrame = self.startFrame() or 0
        endFrame = self.endFrame() or 0

        return [
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
        ]

    def loadValidator(self, **options):
        """
        Triggered when the user changes options.
        
        This method is not yet used. It will be used to change the state of 
        the options widget. For example the help image.
        
        :type options: list[dict]
        """
        super(AnimItem, self).loadValidator(**options)

        option = options.get("option")
        connect = options.get("connect")

        if option == "replace all":
            basename = "replaceCompletely"
            connect = False
        else:
            basename = option

        if connect and basename != "replaceCompletely":
            basename += "Connect"

        logger.debug(basename)

        return []

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
                "layout": "vertical",
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


studiolibrary.registerItem(AnimItem)
