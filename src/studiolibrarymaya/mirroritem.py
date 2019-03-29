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

import mutils
import studiolibrary
import studiolibrarymaya

from studiolibrarymaya import baseitem

try:
    import maya.cmds
except ImportError as error:
    print(error)


logger = logging.getLogger(__name__)

# Register the mirror table item to the Studio Library
iconPath = studiolibrarymaya.resource().get("icons", "mirrortable.png")


class MirrorItem(baseitem.BaseItem):

    Extensions = [".mirror"]
    MenuName = "Mirror Table"
    MenuIconPath = iconPath
    TypeIconPath = iconPath

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        super(MirrorItem, self).__init__(*args, **kwargs)

        self._validateObjects = []

        self.setTransferBasename("mirrortable.json")
        self.setTransferClass(mutils.MirrorTable)

    def info(self):
        """
        Get the info to display to user.
        
        :rtype: list[dict]
        """
        info = baseitem.BaseItem.info(self)

        mt = self.transferObject()

        info.insert(2, {"name": "Left", "value": mt.leftSide()})
        info.insert(3, {"name": "Right", "value": mt.rightSide()})

        return info

    def loadSchema(self):
        """
        Get the options for the item.
        
        :rtype: list[dict]
        """
        return [
            {
                "name": "animation",
                "type": "bool",
                "default": False,
                "persistent": True
            },
            {
                "name": "option",
                "type": "enum",
                "default": "swap",
                "items": ["swap", "left to right", "right to left"],
                "persistent": True
            },
        ]

    @mutils.showWaitCursor
    def load(self, objects=None, namespaces=None, option=None, animation=True, time=None):
        """
        Load the current mirror table to the given objects and options.

        :type objects: list[str]
        :type namespaces: list[str]
        :type option: MirrorOption
        :type animation: bool
        :type time: list[int]
        """
        objects = objects or []

        if option.lower() == "swap":
            option = 0
        elif option.lower() == "left to right":
            option = 1
        elif option.lower() == "right to left":
            option = 2
        else:
            raise Exception('Wrong value passed to load: option=' + str(option))

        self.transferObject().load(
            objects=objects,
            namespaces=namespaces,
            option=option,
            animation=animation,
            time=time,
        )

    def saveSchema(self):
        """
        Get the fields used to save the item.
        
        :rtype: list[dict]
        """
        return [
            {
                "name": "name",
                "type": "string"
            },
            {
                "name": "left",
                "type": "string",
                "menu": {
                    "name": "0"
                }
            },
            {
                "name": "right",
                "type": "string",
                "menu": {
                    "name": "0"
                }
            },
            {
                "name": "contains",
                "type": "label"
            },
            {
                "name": "comment",
                "type": "text",
                "layout": "vertical"
            }
        ]

    def saveValidator(self, **options):
        """
        The save validator is called when an input field has changed.
        
        :type options: dict 
        :rtype: list[dict] 
        """
        results = super(MirrorItem, self).saveValidator(**options)

        objects = maya.cmds.ls(selection=True) or []
        if self._validateObjects != objects:
            self._validateObjects = objects

            left = options.get("left")
            if not left:
                left = mutils.MirrorTable.findLeftSide(objects)

            right = options.get("right")
            if not right:
                right = mutils.MirrorTable.findRightSide(objects)

            leftSide = str(left)
            rightSide = str(right)

            mt = mutils.MirrorTable.fromObjects(
                    [],
                    leftSide=leftSide,
                    rightSide=rightSide
            )

            results.extend([
                {
                    "name": "left",
                    "value": leftSide,
                    "menu": {
                        "name": str(mt.leftCount(objects))
                    }
                },
                {
                    "name": "right",
                    "value": rightSide,
                    "menu": {
                        "name": str(mt.rightCount(objects))
                    }
                },
            ])

        return results

    @mutils.showWaitCursor
    def save(self, objects, path="", iconPath="", **options):
        """
        Save the given objects to the location of the current mirror table.

        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type options: dict
        """
        if path and not path.endswith(".mirror"):
            path += ".mirror"

        logger.info("Saving: %s" % self.transferPath())

        # Mapping new option names to legacy names for now
        leftSide = options.get("left")
        rightSide = options.get("right")
        metadata = {"description": options.get("comment", "")}

        # Remove and create a new temp directory
        tempPath = mutils.createTempPath() + "/" + self.transferBasename()

        # Save the mirror table to the temp location
        mutils.saveMirrorTable(
            tempPath,
            objects,
            metadata=metadata,
            leftSide=leftSide,
            rightSide=rightSide,
        )

        # Move the mirror table to the given path using the base class
        super(MirrorItem, self).save(path, contents=[tempPath, iconPath])


studiolibrary.registerItem(MirrorItem)
