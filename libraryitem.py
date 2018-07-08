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
import logging
from functools import partial

import studiolibrary

import studioqt

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


logger = logging.getLogger(__name__)


class ItemError(Exception):
    """"""


class ItemSaveError(ItemError):
    """"""


class ItemLoadError(ItemError):
    """"""


class LibraryItemSignals(QtCore.QObject):
    """"""
    saved = QtCore.Signal(object)
    saving = QtCore.Signal(object)
    loaded = QtCore.Signal(object)
    copied = QtCore.Signal(object, object, object)
    deleted = QtCore.Signal(object)
    renamed = QtCore.Signal(object, object, object)


class LibraryItem(studioqt.Item):

    EnableDelete = False
    EnableNestedItems = False

    Extensions = []

    MenuName = ""
    MenuOrder = 10
    MenuIconPath = ""
    ThumbnailPath = studioqt.resource.get("icons", "thumbnail.png")

    RegisterOrder = 10
    TypeIconPath = ""
    DisplayInSidebar = False
    CreateWidgetClass = None
    PreviewWidgetClass = None

    _libraryItemSignals = LibraryItemSignals()

    saved = _libraryItemSignals.saved
    saving = _libraryItemSignals.saving
    loaded = _libraryItemSignals.loaded
    copied = _libraryItemSignals.renamed
    renamed = _libraryItemSignals.renamed
    deleted = _libraryItemSignals.deleted

    @classmethod
    def createAction(cls, menu, libraryWidget):
        """
        Return the action to be displayed when the user 
        ks the "plus" icon.

        :type menu: QtWidgets.QMenu
        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: QtCore.QAction
        """
        if cls.MenuName:

            icon = QtGui.QIcon(cls.MenuIconPath)
            callback = partial(cls.showCreateWidget, libraryWidget)

            action = QtWidgets.QAction(icon, cls.MenuName, menu)
            action.triggered.connect(callback)

            return action

    @classmethod
    def showCreateWidget(cls, libraryWidget):
        """
        Show the create widget for creating a new item.

        :type libraryWidget: studiolibrary.LibraryWidget
        """
        widget = cls.CreateWidgetClass()
        libraryWidget.setCreateWidget(widget)

    @classmethod
    def isValidPath(cls, path):
        """
        This method has been deprecated. 
        
        Please use LibraryItem.match(cls, path)
        
        :type path: str
        :rtype: bool 
        """
        return cls.match(path)

    @classmethod
    def match(cls, path):
        """
        Return True if the given path location is supported by the item.

        :type path: str
        :rtype: bool 
        """
        for ext in cls.Extensions:
            if path.endswith(ext):
                return True
        return False

    def __init__(
            self,
            path="",
            library=None,
            libraryWidget=None,
    ):
        """
        The LibraryItem class provides an item for use with the LibraryWidget.

        :type path: str
        :type library: studiolibrary.Library or None 
        :type libraryWidget: studiolibrary.LibraryWidget or None
        """
        studioqt.Item.__init__(self)

        self._path = ""
        self._iconPath = None
        self._typePixmap = None
        self._library = None
        self._libraryWidget = None

        if libraryWidget:
            self.setLibraryWidget(libraryWidget)

        if library:
            self.setLibrary(library)

        if path:
            self.setPath(path)

    def id(self):
        """
        Return the unique id for the item.
    
        :rtype: str 
        """
        return self.path()

    def showToastMessage(self, text):
        """
        A convenience method for showing the toast widget with the given text.

        :type text: str
        :rtype: None
        """
        if self.libraryWidget():
            self.libraryWidget().showToastMessage(text)

    def showErrorDialog(self, title, text):
        """
        Convenience method for showing an error dialog to the user.
        
        :type title: str
        :type text: str
        :rtype: QMessageBox.StandardButton
        """
        if self.libraryWidget():
            self.libraryWidget().showErrorMessage(text)

        return studioqt.MessageBox.critical(self.libraryWidget(), title, text)

    def showExceptionDialog(self, title, error):
        """
        Convenience method for showing a question dialog to the user.

        :type title: str
        :type error: Exception
        :rtype: QMessageBox.StandardButton
        """
        logger.exception(error)
        return self.showErrorDialog(title, error)

    def showQuestionDialog(self, title, text):
        """
        Convenience method for showing a question dialog to the user.

        :type title: str
        :type text: str
        :rtype: QMessageBox.StandardButton
        """
        return studioqt.MessageBox.question(self.libraryWidget(), title, text)

    def typeIconPath(self):
        """
        Return the type icon path on disc.

        :rtype: path or None
        """
        return self.TypeIconPath

    def thumbnailPath(self):
        """
        Return the thumbnail location on disc for this item.

        :rtype: str
        """
        return self.ThumbnailPath

    def showPreviewWidget(self, libraryWidget):
        """
        Show the preview Widget for the item instance.

        :type libraryWidget: studiolibrary.LibraryWidget
        """
        widget = self.previewWidget(libraryWidget)
        libraryWidget.setPreviewWidget(widget)

    def previewWidget(self, libraryWidget):
        """
        Return the widget to be shown when the user clicks on the item.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: QtWidgets.QWidget or None
        """
        widget = None

        if self.PreviewWidgetClass:
            widget = self.PreviewWidgetClass(item=self)

        return widget

    def contextEditMenu(self, menu, items=None):
        """
        Called when the user would like to edit the item from the menu.

        The given menu is shown as a submenu of the main context menu.

        :type menu: QtWidgets.QMenu
        :type items: list[LibraryItem]
        :rtype: None
        """
        if self.EnableDelete:
            action = QtWidgets.QAction("Delete", menu)
            action.triggered.connect(self.showDeleteDialog)
            menu.addAction(action)
            menu.addSeparator()

        action = QtWidgets.QAction("Rename", menu)
        action.triggered.connect(self.showRenameDialog)
        menu.addAction(action)

        action = QtWidgets.QAction("Move to", menu)
        action.triggered.connect(self.showMoveDialog)
        menu.addAction(action)

        action = QtWidgets.QAction("Show in Folder", menu)
        action.triggered.connect(self.showInFolder)
        menu.addAction(action)

    def contextMenu(self, menu, items=None):
        """
        Called when the user right clicks on the item.

        :type menu: QtWidgets.QMenu
        :type items: list[LibraryItem]
        :rtype: None
        """
        pass

    def showInFolder(self):
        """Open the file explorer at the given path location."""
        path = self.path()
        studiolibrary.showInFolder(path)

    def url(self):
        """Used by the mime data when dragging/dropping the item."""
        return QtCore.QUrl("file:///" + self.path())

    def dirname(self):
        """
        :rtype: str
        """
        return os.path.dirname(self.path())

    def extension(self):
        """
        :rtype: str
        """
        _, extension = os.path.splitext(self.path())
        return extension

    def exists(self):
        """
        :rtype: bool
        """
        return os.path.exists(self.path())

    def mtime(self):
        """
        :rtype: float
        """
        return os.path.getmtime(self.path())

    def ctime(self):
        """
        Return when the item was created.

        :rtype: str
        """
        path = self.path()

        if os.path.exists(path):
            return int(os.path.getctime(path))

        return None

    def setLibraryWidget(self, libraryWidget):
        """
        Set the library widget containing the item.
        
        :rtype: studiolibrary.LibraryWidget or None
        """
        self._libraryWidget = libraryWidget

    def libraryWidget(self):
        """
        Return the library widget containing the item.
        
        :rtype: studiolibrary.LibraryWidget or None
        """
        return self._libraryWidget

    def setLibrary(self, library):
        """
        Set the library model for the item.

        :type library: studiolibrary.Library
        """
        self._library = library

    def library(self):
        """
        Return the library model for the item.

        :rtype: studiolibrary.Library or None
        """
        if not self._library and self.libraryWidget():
            return self.libraryWidget().library()

        return self._library

    def setIconPath(self, path):
        """
        Set the icon path for the current item.

        :type path: str
        :rtype: None
        """
        self._iconPath = path

    def iconPath(self):
        """
        Return the icon path for the current item.

        :rtype: None
        """
        return self._iconPath

    def mimeText(self):
        """
        :rtype: str
        """
        return self.path()

    def path(self):
        """
        Return the path for the item.

        :rtype: str
        """
        return self._path

    def setPath(self, path):
        """
        Set the path location on disc for the item.

        :type path: str
        :rtype: None
        """
        if not path:
            raise ItemError('Cannot set an empty item path.')

        self.resetImageSequence()

        path = studiolibrary.normPath(path)

        self._path = path

        self.updatePathData()

    def updatePathData(self):
        """
        Update the data when the item is created or when a new path is set.
        
        :rtype: None 
        """
        path = self.path()

        dirname, basename, extension = studiolibrary.splitPath(path)

        name = os.path.basename(path)
        category = os.path.basename(dirname)
        # modified = ""
        # timeAgo = ""

        # if os.path.exists(path):
        #     modified = os.path.getmtime(path)
        #     timeAgo = studiolibrary.timeAgo(modified)

        itemData = {
            "name": name,
            "path": path,
            "type": extension,
            "folder": dirname,
            "category": category,
            # "modified": modified
        }

        self.setItemData(itemData)
        # self.setDisplayText("modified", timeAgo)

    def load(self):
        """Reimplement this method for loading any item data."""
        logger.debug(u'Loading "{0}"'.format(self.name()))
        LibraryItem.loaded.emit(self)

    def save(self, path=None, contents=None):
        """
        Save the item to the given path.

        :type path: str or None
        :type contents: list[str] or None
        :rtype: None
        """
        path = path or self.path()
        contents = contents or []

        self.setPath(path)
        path = self.path()

        logger.debug(u'Item Saving: {0}'.format(path))
        self.saving.emit(self)

        if os.path.exists(path):
            self.showAlreadyExistsDialog()

        studiolibrary.movePaths(contents, path)

        self.library().addItems([self])

        if self.libraryWidget():
            self.libraryWidget().selectItems([self])

        self.saved.emit(self)
        logger.debug(u'Item Saved: {0}'.format(self.path()))

    # -----------------------------------------------------------------
    # Support for copy and rename
    # -----------------------------------------------------------------

    def delete(self):
        """
        Delete the item from disc and the library model.

        :rtype: None
        """
        studiolibrary.removePath(self.path())

        if self.library():
            self.library().removePath(self.path())

        self.deleted.emit(self)

    def copy(self, dst):
        """
        Make a copy/duplicate the current item to the given destination.

        :type dst: str
        :rtype: None
        """
        src = self.path()
        dst = studiolibrary.copyPath(src, dst)

        if self.library():
            self.library().copyPath(src, dst)

        self.copied.emit(self, src, dst)

    def move(self, dst):
        """
        Move the current item to the given destination.

        :type dst: str
        :rtype: None
        """
        self.rename(dst)

    def rename(self, dst, extension=None):
        """
        Rename the current path to the given destination path.

        :type dst: str
        :type extension: bool or None
        :rtype: None
        """
        extension = extension or self.extension()
        if dst and extension not in dst:
            dst += extension

        src = self.path()
        dst = studiolibrary.renamePath(src, dst)

        self.setPath(dst)

        if self.library():
            self.library().renamePath(src, dst)

        self.renamed.emit(self, src, dst)

    def showRenameDialog(self, parent=None):
        """
        Show the rename dialog.

        :type parent: QtWidgets.QWidget
        """
        parent = parent or self.libraryWidget()

        name, button = studioqt.MessageBox.input(
            parent,
            "Rename item",
            "Rename the current item to:",
            inputText=self.name()
        )

        if button == QtWidgets.QDialogButtonBox.Ok:
            try:
                self.rename(name)
            except Exception as error:
                self.showExceptionDialog("Rename Error", error)
                raise

        return button

    def showMoveDialog(self, parent=None):
        """
        Show the move to browser dialog.

        :type parent: QtWidgets.QWidget
        """
        title = "Move To..."
        path = os.path.dirname(self.dirname())

        dst = QtWidgets.QFileDialog.getExistingDirectory(parent, title, path)

        if dst:
            try:
                self.move(dst)
            except Exception as error:
                self.showExceptionDialog("Move Error", error)
                raise

    def showDeleteDialog(self):
        """
        Show the delete item dialog.

        :rtype: None
        """

        text = 'Are you sure you want to delete this item?'

        button = self.showQuestionDialog("Delete Item", text)

        if button == QtWidgets.QDialogButtonBox.Yes:
            try:
                self.delete()
            except Exception as error:
                self.showExceptionDialog("Delete Error", error)
                raise

    def showAlreadyExistsDialog(self):
        """
        Show a warning dialog if the item already exists on save.
        
        :rtype: None
        """
        if not self.libraryWidget():
            raise ItemSaveError("Item already exists!")

        path = self.path()

        title = "Item already exists"
        text = 'Would you like to move the existing item "{}" to the trash?'
        text = text.format(self.name())

        buttons = QtWidgets.QMessageBox.Yes | \
                  QtWidgets.QMessageBox.Cancel

        button = self.libraryWidget().showQuestionDialog(title, text, buttons)

        if button == QtWidgets.QMessageBox.Yes:
            library = self.library()
            item = studiolibrary.LibraryItem(path, library=library)
            self.libraryWidget().moveItemsToTrash([item])
            self.setPath(path)
        else:
            raise ItemSaveError("You cannot save over an existing item.")

        return button

    # -----------------------------------------------------------------
    # Support for painting the type icon
    # -----------------------------------------------------------------

    def typePixmap(self):
        """
        Return the type pixmap for the plugin.

        :rtype: QtWidgets.QPixmap
        """
        if not self._typePixmap:
            iconPath = self.typeIconPath()
            if iconPath and os.path.exists(iconPath):
                self._typePixmap = QtGui.QPixmap(iconPath)
        return self._typePixmap

    def typeIconRect(self, option):
        """
        Return the type icon rect.

        :rtype: QtGui.QRect
        """
        padding = 2 * self.dpi()
        r = self.iconRect(option)

        x = r.x() + padding
        y = r.y() + padding
        rect = QtCore.QRect(x, y, 13 * self.dpi(), 13 * self.dpi())

        return rect

    def paintTypeIcon(self, painter, option):
        """
        Draw the item type icon at the top left.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        rect = self.typeIconRect(option)
        typePixmap = self.typePixmap()
        if typePixmap:
            painter.setOpacity(0.5)
            painter.drawPixmap(rect, typePixmap)
            painter.setOpacity(1)

    def paint(self, painter, option, index):
        """
        Overriding the paint method to draw the tag icon and type icon.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        studioqt.Item.paint(self, painter, option, index)

        painter.save()
        try:
            if index.column() == 0:
                self.paintTypeIcon(painter, option)
        finally:
            painter.restore()
