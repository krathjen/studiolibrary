# Copyright 2016 by Kurt Rathjen. All Rights Reserved.
#
# Permission to use, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Kurt Rathjen
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# KURT RATHJEN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# KURT RATHJEN BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import mutils

# studioqt supports both pyside (Qt4) and pyside2 (Qt5)
from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studiolibrary
import studiolibraryitems

from studiolibraryitems import transferitem


class SetsItem(transferitem.TransferItem):

    @staticmethod
    def typeIconPath():
        """Return the location on disc to the type (extension) icon."""
        return studiolibraryitems.resource().get("icons", "selectionSet.png")

    @staticmethod
    def createAction(parent):
        """
        Return the action to be displayed when the user clicks the "plus" icon.

        :type parent: QtWidgets.QWidget or None
        :rtype: QtCore.QAction
        """
        icon = QtGui.QIcon(SetsItem.typeIconPath())
        action = QtWidgets.QAction(icon, "Selection Set", parent)
        return action

    @staticmethod
    def createWidget(libraryWidget):
        """
        Return the widget for creating a new sets item.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: SetsCreateWidget
        """
        item = SetsItem()
        widget = SetsCreateWidget(parent=None, item=item)

        widget.setFolderPath(libraryWidget.selectedFolderPath())
        libraryWidget.folderSelectionChanged.connect(widget.setFolderPath)

        return widget

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


class SetsPreviewWidget(transferitem.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        :type item: SelectionSetItem
        """
        transferitem.PreviewWidget.__init__(self, *args, **kwargs)

    def accept(self):
        """Triggered when the user clicks the apply button."""
        self.item().loadFromSettings()


class SetsCreateWidget(transferitem.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        :type item: SelectionSetItem
        """
        transferitem.CreateWidget.__init__(self, *args, **kwargs)


studiolibrary.register(SetsItem, ".set")
