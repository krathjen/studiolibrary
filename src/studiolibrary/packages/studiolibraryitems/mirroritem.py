# Copyright 2017 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

"""
#---------------------------------------------------------------------------
# Saving a mirror table item
#---------------------------------------------------------------------------

from studiolibraryitems import mirroritem

path = "/AnimLibrary/Characters/Malcolm/malcolm.mirror"
objects = maya.cmds.ls(selection=True) or []
leftSide = "Lf"
rightSide = "Rf"

item = mirroritem.MirrorItem(path)
item.save(objects=objects, leftSide=leftSide, rightSide=rightSide)

#---------------------------------------------------------------------------
# Loading a mirror table item
#---------------------------------------------------------------------------

from studiolibraryitems import mirroritem

path = "/AnimLibrary/Characters/Malcolm/malcolm.mirror"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

item = mirroritem.MirrorItem(path)
item.load(objects=objects, namespaces=namespaces, animation=True, time=None)
"""

import os
import logging
from functools import partial

# studioqt supports both pyside (Qt4) and pyside2 (Qt5)
import studioqt
from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import mutils
import studiolibrary
import studiolibraryitems

from studiolibraryitems import transferitem

try:
    import maya.cmds
except ImportError, e:
    print e


__all__ = [
    "MirrorItem",
    "MirrorCreateWidget",
    "MirrorPreviewWidget",
]

logger = logging.getLogger(__name__)

MirrorOption = mutils.MirrorOption


class MirrorItem(transferitem.TransferItem):

    @classmethod
    def typeIconPath(cls):
        """
        Return the mirror icon path to be displayed on the thumbnail.

        :rtype: path
        """
        return studiolibraryitems.resource().get("icons", "mirrorTable.png")

    @classmethod
    def createAction(cls, menu, libraryWidget):
        """
        Return the action to be displayed when the user clicks the "plus" icon.

        :type menu: QtWidgets.QMenu
        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: QtCore.QAction
        """
        icon = QtGui.QIcon(cls.typeIconPath())
        callback = partial(cls.showCreateWidget, libraryWidget)

        action = QtWidgets.QAction(icon, "Mirror Table", menu)
        action.triggered.connect(callback)

        return action

    @staticmethod
    def showCreateWidget(libraryWidget):
        """
        Show the widget for creating a new mirror table item.

        :type libraryWidget: studiolibrary.LibraryWidget
        """
        widget = MirrorCreateWidget()
        widget.folderFrame().hide()
        widget.setFolderPath(libraryWidget.selectedFolderPath())

        libraryWidget.setCreateWidget(widget)
        libraryWidget.folderSelectionChanged.connect(widget.setFolderPath)

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        transferitem.TransferItem.__init__(self, *args, **kwargs)
        self.setTransferBasename("mirrortable.json")
        self.setTransferClass(mutils.MirrorTable)

    def previewWidget(self, libraryWidget=None):
        """
        Return the widget to be shown when the user clicks on the item.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: MirrorPreviewWidget
        """
        return MirrorPreviewWidget(item=self, parent=None)

    def doubleClicked(self):
        """Overriding this method to load the item on double click."""
        self.loadFromSettings()

    def loadFromSettings(self):
        """Load the mirror table using the settings for this item."""
        mirrorOption = self.settings().get("mirrorOption", MirrorOption.Swap)
        mirrorAnimation = self.settings().get("mirrorAnimation", True)
        namespaces = self.namespaces()
        objects = maya.cmds.ls(selection=True) or []

        try:
            self.load(
                objects=objects,
                option=mirrorOption,
                animation=mirrorAnimation,
                namespaces=namespaces,
            )
        except Exception, e:
            studioqt.MessageBox.critical(None, "Item Error", str(e))
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
        self.transferObject().load(
            objects=objects,
            namespaces=namespaces,
            option=option,
            animation=animation,
            time=time,
        )

    def save(self, objects, leftSide, rightSide, path=None, iconPath=None):
        """
        Save the given objects to the location of the current mirror table.

        :type path: str
        :type objects: list[str]
        :type iconPath: str
        :rtype: None
        """
        if path and not path.endswith(".mirror"):
            path += ".mirror"

        logger.info("Saving: %s" % self.transferPath())

        tempDir = mutils.TempDir("Transfer", makedirs=True)
        tempPath = os.path.join(tempDir.path(), self.transferBasename())

        t = self.transferClass().fromObjects(
            objects,
            leftSide=leftSide,
            rightSide=rightSide
        )
        t.save(tempPath)

        studiolibrary.LibraryItem.save(self, path=path, contents=[tempPath, iconPath])


class MirrorCreateWidget(transferitem.CreateWidget):

    def __init__(self, item=None, parent=None):
        """
        :type parent: QtWidgets.QWidget
        :type item: MirrorItem
        """
        item = item or MirrorItem()
        transferitem.CreateWidget.__init__(self, item, parent=parent)

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

        transferitem.CreateWidget.selectionChanged(self)

    def save(self, objects, path, iconPath, description):
        """
        Called by the base class when the user clicks the save button.

        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type description: str
        :rtype: None
        """
        iconPath = self.iconPath()
        leftSide = self.leftText()
        rightSide = self.rightText()

        r = self.item()
        r.setDescription(description)

        self.item().save(
            path=path,
            objects=objects,
            iconPath=iconPath,
            leftSide=leftSide,
            rightSide=rightSide,
        )


class MirrorPreviewWidget(transferitem.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        :type item: MirrorItem
        """
        transferitem.PreviewWidget.__init__(self, *args, **kwargs)

        self.ui.mirrorAnimationCheckBox.stateChanged.connect(self.updateState)
        self.ui.mirrorOptionComboBox.currentIndexChanged.connect(self.updateState)

    def setItem(self, item):
        """
        Set the item for the preview widget.

        :type item: MirrorItem
        :rtype: None
        """
        transferitem.PreviewWidget.setItem(self, item)

        mt = item.transferObject()
        self.ui.left.setText(mt.leftSide())
        self.ui.right.setText(mt.rightSide())

    def mirrorOption(self):
        """
        Return the current mirror option.

        :rtype: str
        """
        text = self.ui.mirrorOptionComboBox.currentText()
        return self.ui.mirrorOptionComboBox.findText(text, QtCore.Qt.MatchExactly)

    def mirrorAnimation(self):
        """
        Return True if the animation should also be mirrored.

        :rtype: bool
        """
        return self.ui.mirrorAnimationCheckBox.isChecked()

    def state(self):
        """
        Return the state of the preview widget.

        :rtype: dict
        """
        state = super(MirrorPreviewWidget, self).state()

        state["mirrorOption"] = int(self.mirrorOption())
        state["mirrorAnimation"] = bool(self.mirrorAnimation())

        return state

    def setState(self, state):
        """
        Set the state of the preview widget.

        :type state: dict
        """
        super(MirrorPreviewWidget, self).setState(state)

        mirrorOption = int(state.get("mirrorOption", MirrorOption.Swap))
        mirrorAnimation = bool(state.get("mirrorAnimation", True))

        self.ui.mirrorOptionComboBox.setCurrentIndex(mirrorOption)
        self.ui.mirrorAnimationCheckBox.setChecked(mirrorAnimation)

    def accept(self):
        """
        Called by the base class when the user clicks the apply button.

        :rtype: None
        """
        self.item().loadFromSettings()


studiolibrary.register(MirrorItem, ".mirror")