# Copyright 2020 by Kurt Rathjen. All Rights Reserved.
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
    import maya.cmds
except ImportError as error:
    print(error)


logger = logging.getLogger(__name__)


def save(path, *args, **kwargs):
    """Convenience function for saving a MirrorItem."""
    MirrorItem(path).safeSave(*args, **kwargs)


def load(path, *args, **kwargs):
    """Convenience function for loading a MirrorItem."""
    MirrorItem(path).load(*args, **kwargs)


class MirrorItem(baseitem.BaseItem):

    NAME = "Mirror Table"
    EXTENSION = ".mirror"
    ICON_PATH = os.path.join(os.path.dirname(__file__), "icons", "mirrortable.png")
    TRANSFER_CLASS = mutils.MirrorTable
    TRANSFER_BASENAME = "mirrortable.json"

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        super(MirrorItem, self).__init__(*args, **kwargs)

        self._validatedObjects = []

    def loadSchema(self):
        """
        Get schema used to load the mirror table item.
        
        :rtype: list[dict]
        """
        schema = super(MirrorItem, self).loadSchema()

        mt = self.transferObject()

        schema.insert(2, {"name": "Left", "value": mt.leftSide()})
        schema.insert(3, {"name": "Right", "value": mt.rightSide()})

        schema.extend([
            {
                "name": "optionsGroup",
                "title": "Options",
                "type": "group",
                "order": 2,
            },
            {
                "name": "keysOption",
                "title": "Keys",
                "type": "radio",
                "value": "Selected Range",
                "items": ["All Keys", "Selected Range"],
                "persistent": True,
            },
            {
                "name": "option",
                "type": "enum",
                "default": "swap",
                "items": ["swap", "left to right", "right to left"],
                "persistent": True
            },
        ])

        return schema

    def load(self, **kwargs):
        """
        Load the current mirror table to the given objects.

        :type kwargs: dict
        """
        mt = mutils.MirrorTable.fromPath(self.path() + "/mirrortable.json")
        mt.load(
            objects=kwargs.get("objects"),
            namespaces=kwargs.get("namespaces"),
            option=kwargs.get("option"),
            keysOption=kwargs.get("keysOption"),
            time=kwargs.get("time")
        )

    def saveSchema(self):
        """
        Get the fields used to save the item.
        
        :rtype: list[dict]
        """
        return [
            {
                "name": "folder",
                "type": "path",
                "layout": "vertical",
                "visible": False,
            },
            {
                "name": "name",
                "type": "string",
                "layout": "vertical"
            },
            {
                "name": "mirrorPlane",
                "type": "buttonGroup",
                "default": "YZ",
                "layout": "vertical",
                "items": ["YZ", "XY", "XZ"],
            },
            {
                "name": "leftSide",
                "type": "string",
                "layout": "vertical",
                "menu": {
                    "name": "0"
                }
            },
            {
                "name": "rightSide",
                "type": "string",
                "layout": "vertical",
                "menu": {
                    "name": "0"
                }
            },
            {
                "name": "comment",
                "type": "text",
                "layout": "vertical"
            },
            {
                "name": "objects",
                "type": "objects",
                "label": {
                    "visible": False
                }
            },
        ]

    def saveValidator(self, **kwargs):
        """
        The save validator is called when an input field has changed.
        
        :type kwargs: dict
        :rtype: list[dict] 
        """
        results = super(MirrorItem, self).saveValidator(**kwargs)

        objects = maya.cmds.ls(selection=True) or []

        dirty = kwargs.get("fieldChanged") in ["leftSide", "rightSide"]
        dirty = dirty or self._validatedObjects != objects

        if dirty:
            self._validatedObjects = objects

            leftSide = kwargs.get("leftSide", "")
            if not leftSide:
                leftSide = mutils.MirrorTable.findLeftSide(objects)

            rightSide = kwargs.get("rightSide", "")
            if not rightSide:
                rightSide = mutils.MirrorTable.findRightSide(objects)

            mt = mutils.MirrorTable.fromObjects(
                    [],
                    leftSide=leftSide,
                    rightSide=rightSide
            )

            results.extend([
                {
                    "name": "leftSide",
                    "value": leftSide,
                    "menu": {
                        "name": str(mt.leftCount(objects))
                    }
                },
                {
                    "name": "rightSide",
                    "value": rightSide,
                    "menu": {
                        "name": str(mt.rightCount(objects))
                    }
                },
            ])

        return results

    def save(self, objects, **kwargs):
        """
        Save the given objects to the item path on disc.

        :type objects: list[str]
        :type kwargs: dict
        """
        super(MirrorItem, self).save(**kwargs)

        # Save the mirror table to the given location
        mutils.saveMirrorTable(
            self.path() + "/mirrortable.json",
            objects,
            metadata={"description": kwargs.get("comment", "")},
            leftSide=kwargs.get("leftSide"),
            rightSide=kwargs.get("rightSide"),
            mirrorPlane=kwargs.get("mirrorPlane"),
        )
