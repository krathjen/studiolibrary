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


class LibraryItem(studioqt.CombinedWidgetItem):

    ENABLE_DELETE = False

    Extensions = []

    MenuName = "Library Item"
    MenuIconPath = ""

    TypeIconPath = ""
    CreateWidgetClass = None
    PreviewWidgetClass = None

    _libraryItemSignals = LibraryItemSignals()

    saved = _libraryItemSignals.saved
    saving = _libraryItemSignals.saving
    loaded = _libraryItemSignals.loaded

    @classmethod
    def createAction(cls, menu, libraryWidget):
        """
        Return the action to be displayed when the user clicks the "plus" icon.

        :type menu: QtWidgets.QMenu
        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: QtCore.QAction
        """
        if cls.CreateWidgetClass:

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
        database=None,
        libraryWidget=None,
    ):
        """
        The LibraryItem class provides an item for use with the LibraryWidget.

        :type path: str
        :type database: studiolibrary.Database or None 
        :type libraryWidget: studiolibrary.LibraryWidget or None
        """
        studioqt.CombinedWidgetItem.__init__(self)

        self._path = ""
        self._library = None
        self._iconPath = None
        self._database = None
        self._typePixmap = None
        self._libraryWidget = None

        if libraryWidget:
            self.setLibraryWidget(libraryWidget)

        if database:
            self.setDatabase(database)

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
        return studioqt.resource.get("icons", "thumbnail.png")

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
        if self.ENABLE_DELETE:
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

    def name(self):
        """
        Return the name of the item.

        :rtype: str
        """
        return self.text("Name")

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

    def libraryWidget(self):
        """
        :rtype: studiolibrary.LibraryWidget or None
        """
        return self._libraryWidget

    def setLibraryWidget(self, libraryWidget):
        """
        :rtype: studiolibrary.LibraryWidget or None
        """
        self._libraryWidget = libraryWidget

    def setDatabase(self, database):
        """
        Set the database for the item.

        :type database: studiolibrary.Database
        """
        self._database = database

    def database(self):
        """
        Return the database for the item.

        :rtype: studiolibrary.Database or None
        """
        if not self._database and self.libraryWidget():
            return self.libraryWidget().database()

        return self._database

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
        return self.text("Path")

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

        dirname, basename, extension = studiolibrary.splitPath(path)

        name = os.path.basename(path)
        category = os.path.basename(dirname)

        self.setName(name)
        self.setText("Path", path)
        self.setText("Category", category)

        if os.path.exists(path):
            modified = os.path.getmtime(path)
            timeAgo = studiolibrary.timeAgo(modified)

            self.setText("Modified", timeAgo)
            self.setSortText("Modified", str(modified))

        self.setText("Type", extension)

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

        if self.database():
            self.database().addPath(path)

        if self.libraryWidget():
            self.libraryWidget().addItem(self, select=True)

        self.saved.emit(self)
        logger.debug(u'Item Saved: {0}'.format(self.path()))

    # -----------------------------------------------------------------
    # Support for copy and rename
    # -----------------------------------------------------------------

    def delete(self):
        """
        Delete the item from disc and the database.

        :rtype: None
        """
        path = self.path()

        studiolibrary.removePath(path)

        if self.database():
            self.database().removePath(path)

        if self.libraryWidget():
            self.libraryWidget().refresh()

    def copy(self, dst):
        """
        Make a copy/duplicate the current item to the given destination.

        :type dst: str
        :rtype: None
        """
        src = self.path()

        path = studiolibrary.copyPath(src, dst)
        self.setPath(path)

        if self.database():
            self.database().addPath(path)

    def move(self, dst):
        """
        Move the current item to the given destination.

        :type dst: str
        :rtype: None
        """
        src = self.path()

        dst = studiolibrary.movePath(src, dst)
        self.setPath(dst)

        if self.database():
            self.database().renamePath(src, dst)

    def rename(self, dst, extension=None, force=True):
        """
        Rename the current path to given destination path.

        :type dst: str
        :type force: bool
        :type extension: bool or None
        :rtype: None
        """
        src = self.path()

        extension = extension or self.extension()
        if dst and extension not in dst:
            dst += extension

        dst = studiolibrary.renamePath(src, dst)
        self.setPath(dst)

        if self.database():
            self.database().renamePath(src, dst)

        if self.libraryWidget():
            self.libraryWidget().refreshSelection()

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
            except Exception, e:
                self.showExceptionDialog("Rename Error", e)
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
            except Exception, e:
                self.showExceptionDialog("Move Error", e)
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
            except Exception, e:
                self.showExceptionDialog("Delete Error", e)
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

        button = self.libraryWidget().showQuestionDialog(title, text)

        if button == QtWidgets.QMessageBox.Yes:
            self.libraryWidget().moveItemsToTrash([studiolibrary.LibraryItem(path)])
        elif button == QtWidgets.QMessageBox.Cancel:
            raise ItemSaveError("Saving was canceled.")
        elif button != QtWidgets.QMessageBox.Yes:
            raise ItemSaveError("You cannot save over an existing item.")

        self.setPath(path)

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
        studioqt.CombinedWidgetItem.paint(self, painter, option, index)

        painter.save()
        try:
            if index.column() == 0:
                self.paintTypeIcon(painter, option)
        finally:
            painter.restore()
