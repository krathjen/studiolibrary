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

"""
#---------------------------------------------------------------------------
# Saving a mirror table item
#---------------------------------------------------------------------------

from studiolibrarymaya import mirroritem

path = "/AnimLibrary/Characters/Malcolm/malcolm.mirror"
objects = maya.cmds.ls(selection=True) or []
leftSide = "Lf"
rightSide = "Rf"

item = mirroritem.MirrorItem(path)
item.save(objects=objects, leftSide=leftSide, rightSide=rightSide)

#---------------------------------------------------------------------------
# Loading a mirror table item
#---------------------------------------------------------------------------

from studiolibrarymaya import mirroritem

path = "/AnimLibrary/Characters/Malcolm/malcolm.mirror"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

item = mirroritem.MirrorItem(path)
item.load(objects=objects, namespaces=namespaces, animation=True, time=None)
"""

import logging

from studioqt import QtCore

import mutils
import studiolibrary
import studiolibrarymaya

from studiolibrarymaya import baseitem
from studiolibrarymaya import basecreatewidget
from studiolibrarymaya import basepreviewwidget


try:
    import maya.cmds
except ImportError as error:
    print(error)


__all__ = [
    "MirrorItem",
    "MirrorCreateWidget",
    "MirrorPreviewWidget",
]

logger = logging.getLogger(__name__)


class MirrorItem(baseitem.BaseItem):

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        super(MirrorItem, self).__init__(*args, **kwargs)

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

    def options(self):
        """
        Get the options for the item.
        
        :rtype: list[dict]
        """
        return [
            {
                "name": "animation",
                "type": "bool",
                "default": False
            },
            {
                "name": "option",
                "type": "enum",
                "default": "swap",
                "items": ["swap", "left to right", "right to left"],
            },
        ]

    def doubleClicked(self):
        """Overriding this method to load the item on double click."""
        self.loadFromSettings()

    def loadFromSettings(self):
        """Load the mirror table using the settings for this item."""
        kwargs = self.optionsFromSettings()
        namespaces = self.namespaces()
        objects = maya.cmds.ls(selection=True) or []

        try:
            self.load(
                objects=objects,
                namespaces=namespaces,
                **kwargs
            )
        except Exception as error:
            self.showErrorDialog("Item Error", str(error))
            raise

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

    def save(
            self,
            objects,
            leftSide,
            rightSide,
            path="",
            iconPath="",
            metadata=None,
            **kwargs):
        """
        Save the given objects to the location of the current mirror table.

        :type objects: list[str]
        :type leftSide: str
        :type rightSide: str
        :type path: str
        :type iconPath: str
        :type metadata: None or dict
        """
        if path and not path.endswith(".mirror"):
            path += ".mirror"

        logger.info("Saving: %s" % self.transferPath())

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
        contents = [tempPath, iconPath]
        super(MirrorItem, self).save(path, contents=contents, **kwargs)


class MirrorCreateWidget(basecreatewidget.BaseCreateWidget):

    def __init__(self, item=None, parent=None):
        """
        :type parent: QtWidgets.QWidget
        :type item: MirrorItem
        """
        item = item or MirrorItem()
        super(MirrorCreateWidget, self).__init__(item, parent=parent)

    def leftText(self):
        """
        Return the naming convention for the left side.

        :rtype: str
        """
        return str(self.ui.left.text()).strip()

    def rightText(self):
        """
        Return the naming convention for the right side.

        :rtype: str
        """
        return str(self.ui.right.text()).strip()

    def selectionChanged(self):
        """
        Triggered when the user changes the Maya object selection.

        :rtype: None
        """
        objects = maya.cmds.ls(selection=True) or []

        if not self.ui.left.text():
            self.ui.left.setText(mutils.MirrorTable.findLeftSide(objects))

        if not self.ui.right.text():
            self.ui.right.setText(mutils.MirrorTable.findRightSide(objects))

        leftSide = str(self.ui.left.text())
        rightSide = str(self.ui.right.text())

        mt = mutils.MirrorTable.fromObjects(
                [],
                leftSide=leftSide,
                rightSide=rightSide
        )

        self.ui.leftCount.setText(str(mt.leftCount(objects)))
        self.ui.rightCount.setText(str(mt.rightCount(objects)))

        super(MirrorCreateWidget, self).selectionChanged()

    def save(self, objects, path, iconPath, metadata):
        """
        Called by the base class when the user clicks the save button.

        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type metadata: None or dict
        :rtype: None
        """
        iconPath = self.iconPath()
        leftSide = self.leftText()
        rightSide = self.rightText()

        self.item().save(
            path=path,
            objects=objects,
            iconPath=iconPath,
            metadata=metadata,
            leftSide=leftSide,
            rightSide=rightSide,
        )


# Register the mirror table item to the Studio Library
iconPath = studiolibrarymaya.resource().get("icons", "mirrorTable.png")

MirrorItem.Extensions = [".mirror"]
MirrorItem.MenuName = "Mirror Table"
MirrorItem.MenuIconPath = iconPath
MirrorItem.TypeIconPath = iconPath
MirrorItem.CreateWidgetClass = MirrorCreateWidget
MirrorItem.PreviewWidgetClass = basepreviewwidget.BasePreviewWidget

studiolibrary.registerItem(MirrorItem)
