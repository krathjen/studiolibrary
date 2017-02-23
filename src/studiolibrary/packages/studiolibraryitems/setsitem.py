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

import os
import mutils
from functools import partial

# studioqt supports both pyside (Qt4) and pyside2 (Qt5)
from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studiolibrary
import studiolibraryitems

from studiolibraryitems import transferitem


__all__ = [
    "SetsItem",
    "SetsCreateWidget",
    "SetsPreviewWidget",
]

class SetsItem(transferitem.TransferItem):

    @classmethod
    def typeIconPath(cls):
        """
        Return the type icon path on disc.

        :rtype: path
        """
        return studiolibraryitems.resource().get("icons", "selectionSet.png")

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

        action = QtWidgets.QAction(icon, "Selection Set", menu)
        action.triggered.connect(callback)

        return action

    @staticmethod
    def showCreateWidget(libraryWidget):
        """
        Show the widget for creating a new anim item.

        :type libraryWidget: studiolibrary.LibraryWidget
        """
        widget = SetsCreateWidget()
        widget.folderFrame().hide()
        widget.setFolderPath(libraryWidget.selectedFolderPath())

        libraryWidget.setCreateWidget(widget)
        libraryWidget.folderSelectionChanged.connect(widget.setFolderPath)

    def __init__(self, *args, **kwargs):
        """
        :rtype: None
        """
        transferitem.TransferItem.__init__(self, *args, **kwargs)
        self.setTransferBasename("set.json")
        self.setTransferClass(mutils.SelectionSet)

        self.setTransferBasename("set.list")
        if not os.path.exists(self.transferPath()):
            self.setTransferBasename("set.json")

    def previewWidget(self, parent=None):
        """
        Return the widget to be shown when the user clicks on the item.

        :type parent: QtWidgets.QWidget
        :rtype: SetsPreviewWidget
        """
        return SetsPreviewWidget(parent=parent, item=self)

    def doubleClicked(self):
        """Overriding this method to load the item on double click."""
        self.loadFromSettings()

    def loadFromSettings(self):
        """Load the selection set using the settings for this item."""
        namespaces = self.namespaces()
        self.load(namespaces=namespaces)

    def load(self, namespaces=None):
        """
        :type namespaces: list[str] | None
        """
        self.selectContent(namespaces=namespaces)

    def save(self, objects, path=None, iconPath=None):
        """
        Save all the given object data to the given path on disc.
    
        :type path: path
        :type objects: list
        :type iconPath: str
        """
        if path and not path.endswith(".set"):
            path += ".set"

        transferitem.TransferItem.save(self, objects, path=path, iconPath=iconPath)


class SetsCreateWidget(transferitem.CreateWidget):

    def __init__(self, item=None, parent=None):
        """
        :type parent: QtWidgets.QWidget
        :type item: SelectionSetItem
        """
        item = item or SetsItem()
        transferitem.CreateWidget.__init__(self, item, parent=parent)


class SetsPreviewWidget(transferitem.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        :type item: SelectionSetItem
        """
        transferitem.PreviewWidget.__init__(self, *args, **kwargs)

        self.ui.optionsToggleBox.setVisible(False)

    def accept(self):
        """Triggered when the user clicks the apply button."""
        self.item().loadFromSettings()


studiolibrary.register(SetsItem, ".set")
