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
import shutil
import logging
from functools import partial

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studiolibrary
import studiolibrary.widgets
import studiolibrary.librarywindow

import studioqt


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
    dataChanged = QtCore.Signal(object)

# Note: We will be changing the base class in the near future
class LibraryItem(studiolibrary.widgets.Item):

    NAME = ""
    TYPE = ""
    THUMBNAIL_PATH = studiolibrary.resource.get("icons", "thumbnail.png")

    EXTENSION = ""
    EXTENSIONS = []

    ENABLE_DELETE = False
    ENABLE_NESTED_ITEMS = False

    SYNC_ORDER = 10
    MENU_ORDER = 10

    SAVE_WIDGET_CLASS = None
    LOAD_WIDGET_CLASS = None

    _libraryItemSignals = LibraryItemSignals()

    saved = _libraryItemSignals.saved
    saving = _libraryItemSignals.saving
    loaded = _libraryItemSignals.loaded
    copied = _libraryItemSignals.renamed
    renamed = _libraryItemSignals.renamed
    deleted = _libraryItemSignals.deleted
    dataChanged = _libraryItemSignals.dataChanged

    def createItemData(self):
        """
        Called when syncing the given path with the library cache.

        :rtype: dict
        """
        path = self.path()
        itemData = dict(self.readMetadata())

        dirname, basename, extension = studiolibrary.splitPath(path)

        name = os.path.basename(path)
        category = os.path.basename(dirname) or dirname
        modified = ""

        if os.path.exists(path):
            modified = os.path.getmtime(path)

        itemData.update({
            "name": name,
            "path": path,
            "type": self.TYPE or extension,
            "folder": dirname,
            "category": category,
            "modified": modified,
            "__class__": self.__class__.__module__ + "." + self.__class__.__name__
        })

        return itemData

    @classmethod
    def createAction(cls, menu, libraryWindow):
        """
        Return the action to be displayed when the user 
        ks the "plus" icon.

        :type menu: QtWidgets.QMenu
        :type libraryWindow: studiolibrary.LibraryWindow
        :rtype: QtCore.QAction
        """
        if cls.NAME:

            icon = QtGui.QIcon(cls.ICON_PATH)
            callback = partial(cls.showSaveWidget, libraryWindow)

            action = QtWidgets.QAction(icon, cls.NAME, menu)
            action.triggered.connect(callback)

            return action

    @classmethod
    def showSaveWidget(cls, libraryWindow, item=None):
        """
        Show the create widget for creating a new item.

        :type libraryWindow: studiolibrary.LibraryWindow
        :type item: studiolibrary.LibraryItem or None
        """
        item = item or cls()
        widget = cls.SAVE_WIDGET_CLASS(item=item)
        libraryWindow.setCreateWidget(widget)

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
        extensions = cls.EXTENSIONS
        if not extensions and cls.EXTENSION:
            extensions = [cls.EXTENSION]

        for ext in extensions:
            if path.endswith(ext):
                return True

        return False

    def __init__(
            self,
            path="",
            library=None,
            libraryWindow=None,
    ):
        """
        The LibraryItem class provides an item for use with the LibraryWindow.

        :type path: str
        :type library: studiolibrary.Library or None 
        :type libraryWindow: studiolibrary.LibraryWindow or None
        """
        super(LibraryItem, self).__init__()

        self._path = path
        self._modal = None
        self._library = None
        self._metadata = None
        self._libraryWindow = None

        self._readOnly = False
        self._ignoreExistsDialog = False

        if libraryWindow:
            self.setLibraryWindow(libraryWindow)

        if library:
            self.setLibrary(library)

        # if path:
        #     self.setPath(path)

    def setReadOnly(self, readOnly):
        """
        Set the item to read only.

        :type readOnly: bool
        """
        self._readOnly = readOnly

    def isReadOnly(self):
        """
        Check if the item is read only.

        :rtype: bool
        """
        if self.isLocked():
            return True

        return self._readOnly

    def isLocked(self):
        """
        Check if the item has been locked by the window.

        :rtype: bool
        """
        locked = False
        if self.libraryWindow():
            locked = self.libraryWindow().isLocked()
        return locked

    def isDeletable(self):
        """
        Check if the item is deletable.

        :rtype: bool
        """
        if self.isLocked():
            return False

        return self.ENABLE_DELETE

    def overwrite(self):
        """
        Show the save widget with the input fields populated.
        """
        self._ignoreExistsDialog = True
        widget = self.showSaveWidget(self.libraryWindow(), item=self)

    def loadSchema(self):
        """
        Get the options used to load the item.
        
        :rtype: list[dict]
        """
        return []

    def loadValidator(self, **kwargs):
        """
        Validate the current load options.
        
        :type kwargs: dict
        :rtype: list[dict]
        """
        return []

    def load(self, *args, **kwargs):
        """
        Reimplement this method for loading item data.

        :type args: list
        :type kwargs: dict
        """
        raise NotImplementedError("The load method has not been implemented!")

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
        """
        if self.libraryWindow():
            self.libraryWindow().showToastMessage(text)

    def showErrorDialog(self, title, text):
        """
        Convenience method for showing an error dialog to the user.
        
        :type title: str
        :type text: str
        :rtype: QMessageBox.StandardButton or None
        """
        if self.libraryWindow():
            self.libraryWindow().showErrorMessage(text)

        button = None

        if not self._modal:
            self._modal = True
            
            try:
                button = studiolibrary.widgets.MessageBox.critical(self.libraryWindow(), title, text)
            finally:
                self._modal = False

        return button

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
        return studiolibrary.widgets.MessageBox.question(self.libraryWindow(), title, text)

    def thumbnailPath(self):
        """
        Return the thumbnail location on disc for this item.

        :rtype: str
        """
        thumbnailPath = self.path() + "/thumbnail.jpg"
        if os.path.exists(thumbnailPath):
            return thumbnailPath

        thumbnailPath = thumbnailPath.replace(".jpg", ".png")
        if os.path.exists(thumbnailPath):
            return thumbnailPath

        return self.THUMBNAIL_PATH

    def isTHUMBNAIL_PATH(self):
        """
        Check if the thumbnail path is the default path.

        :rtype: bool
        """
        return self.thumbnailPath() == self.THUMBNAIL_PATH

    def showPreviewWidget(self, libraryWindow):
        """
        Show the preview Widget for the item instance.

        :type libraryWindow: studiolibrary.LibraryWindow
        """
        widget = self.previewWidget(libraryWindow)
        libraryWindow.setPreviewWidget(widget)

    def previewWidget(self, libraryWindow):
        """
        Return the widget to be shown when the user clicks on the item.

        :type libraryWindow: studiolibrary.LibraryWindow
        :rtype: QtWidgets.QWidget or None
        """
        widget = None

        if self.LOAD_WIDGET_CLASS:
            widget = self.LOAD_WIDGET_CLASS(item=self)

        return widget

    def contextEditMenu(self, menu, items=None):
        """
        Called when the user would like to edit the item from the menu.

        The given menu is shown as a submenu of the main context menu.

        :type menu: QtWidgets.QMenu
        :type items: list[LibraryItem] or None
        """
        # Adding a blank icon fixes the text alignment issue when using Qt 5.12.+
        icon = studiolibrary.resource.icon("blank")

        action = QtWidgets.QAction("Rename", menu)
        action.triggered.connect(self.showRenameDialog)
        action.setIcon(icon)
        menu.addAction(action)

        action = QtWidgets.QAction("Move to", menu)
        action.triggered.connect(self.showMoveDialog)
        menu.addAction(action)

        action = QtWidgets.QAction("Copy Path", menu)
        action.triggered.connect(self.copyPathToClipboard)
        menu.addAction(action)

        if self.libraryWindow():
            action = QtWidgets.QAction("Select Folder", menu)
            action.triggered.connect(self.selectFolder)
            menu.addAction(action)

        action = QtWidgets.QAction("Show in Folder", menu)
        action.triggered.connect(self.showInFolder)
        menu.addAction(action)

        if self.isDeletable():
            menu.addSeparator()
            action = QtWidgets.QAction("Delete", menu)
            action.triggered.connect(self.showDeleteDialog)
            menu.addAction(action)

        self.createOverwriteMenu(menu)

    def createOverwriteMenu(self, menu):
        """
        Create a menu or action to trigger the overwrite method.

        :type menu: QtWidgets.QMenu
        """
        if not self.isReadOnly():
            menu.addSeparator()
            action = QtWidgets.QAction("Overwrite", menu)
            action.triggered.connect(self.overwrite)
            menu.addAction(action)

    def copyPathToClipboard(self):
        """Copy the item path to the system clipboard."""
        cb = QtWidgets.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.path(), mode=cb.Clipboard)

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

    def selectFolder(self):
        """select the folder in the library widget"""
        if self.libraryWindow():
            path = '/'.join(studiolibrary.normPath(self.path()).split('/')[:-1])
            self.libraryWindow().selectFolderPath(path)

    def url(self):
        """Used by the mime data when dragging/dropping the item."""
        return QtCore.QUrl("file:///" + self.path())

    def setLibraryWindow(self, libraryWindow):
        """
        Set the library widget containing the item.
        
        :rtype: studiolibrary.LibraryWindow or None
        """
        self._libraryWindow = libraryWindow

    def libraryWindow(self):
        """
        Return the library widget containing the item.
        
        :rtype: studiolibrary.LibraryWindow or None
        """
        return self._libraryWindow

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
        if not self._library and self.libraryWindow():
            return self.libraryWindow().library()

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
        Get the path for the item.

        :rtype: str
        """
        return self._path

    def setPath(self, path):
        """
        Set the path for the item.

        :rtype: str
        """
        self._path = studiolibrary.normPath(path)

    def setMetadata(self, metadata):
        """
        Set the given metadata for the item.
        
        :type metadata: dict
        """
        self._metadata = metadata

    def metadata(self):
        """
        Get the metadata for the item from disc.
        
        :rtype: dict
        """
        return self._metadata

    def updateMetadata(self, metadata):
        """
        Update the current metadata from disc with the given metadata.
        
        :type metadata: dict
        """
        metadata_ = self.readMetadata()
        metadata_.update(metadata)
        self.saveMetadata(metadata_)

    def saveMetadata(self, metadata):
        """
        Save the given metadata to disc.
        
        :type metadata: dict
        """
        formatString = studiolibrary.config.get('metadataPath')
        path = studiolibrary.formatPath(formatString, self.path())
        studiolibrary.saveJson(path, metadata)
        self.setMetadata(metadata)
        self.syncItemData(emitDataChanged=False)
        self.dataChanged.emit(self)

    def readMetadata(self):
        """
        Read the metadata for the item from disc.
        
        :rtype: dict
        """
        if self._metadata is None:
            formatString = studiolibrary.config.get('metadataPath')
            path = studiolibrary.formatPath(formatString, self.path())

            if os.path.exists(path):
                self._metadata = studiolibrary.readJson(path)
            else:
                self._metadata = {}

        return self._metadata

    def syncItemData(self, emitDataChanged=True):
        """Sync the item data to the database."""
        data = self.createItemData()
        self.setItemData(data)

        if self.library():
            self.library().saveItemData([self], emitDataChanged=emitDataChanged)

    def saveSchema(self):
        """
        Get the schema used for saving the item.
        
        :rtype: list[dict]
        """
        return []

    def saveValidator(self, **fields):
        """
        Validate the given save fields.
        
        :type fields: dict
        :rtype: list[dict]
        """
        return []

    @studioqt.showWaitCursor
    def safeSave(self, *args, **kwargs):
        """
        Safe save the item.
        """
        dst = self.path()

        if dst and not dst.endswith(self.EXTENSION):
            dst += self.EXTENSION

        self.setPath(dst)

        logger.debug(u'Item Saving: {0}'.format(dst))
        self.saving.emit(self)

        if os.path.exists(dst):
            if self._ignoreExistsDialog:
                self._moveToTrash()
            else:
                self.showAlreadyExistsDialog()

        tmp = studiolibrary.createTempPath(self.__class__.__name__)

        self.setPath(tmp)

        self.save(*args, **kwargs)

        shutil.move(tmp, dst)

        self.setPath(dst)
        self.syncItemData()

        if self.libraryWindow():
            self.libraryWindow().selectItems([self])

        self.saved.emit(self)
        logger.debug(u'Item Saved: {0}'.format(dst))

    def save(self, *args, **kwargs):
        """
        Save the item io data to the given path.

        :type args: list
        :type kwargs: dict
        """
        raise NotImplementedError("The save method has not been implemented!")

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

        if self.libraryWindow():
            self.libraryWindow().refresh()

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
        extension = extension or self.EXTENSION
        if dst and extension not in dst:
            dst += extension

        src = self.path()

        # Rename the path on the filesystem
        dst = studiolibrary.renamePath(src, dst)

        # Rename the path inside the library database
        if self.library():
            self.library().renamePath(src, dst)

        self._path = dst

        self.syncItemData()

        self.renamed.emit(self, src, dst)

    def showRenameDialog(self, parent=None):
        """
        Show the rename dialog.

        :type parent: QtWidgets.QWidget
        """
        select = False

        if self.libraryWindow():
            parent = parent or self.libraryWindow()
            select = self.libraryWindow().selectedFolderPath() == self.path()

        name, button = studiolibrary.widgets.MessageBox.input(
            parent,
            "Rename item",
            "Rename the current item to:",
            inputText=self.name(),
            buttons=[
                ("Rename", QtWidgets.QDialogButtonBox.AcceptRole),
                ("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
            ]
        )

        if button == "Rename":
            try:
                self.rename(name)

                if select:
                    self.libraryWindow().selectFolderPath(self.path())

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
        path = os.path.dirname(os.path.dirname(self.path()))

        dst = QtWidgets.QFileDialog.getExistingDirectory(None, title, path)

        if dst:
            dst = "{}/{}".format(dst, os.path.basename(self.path()))
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
        if not self.libraryWindow():
            raise ItemSaveError("Item already exists!")

        title = "Item already exists"
        text = 'Would you like to move the existing item "{}" to the trash?'
        text = text.format(os.path.basename(self.path()))

        buttons = [
            QtWidgets.QDialogButtonBox.Yes,
            QtWidgets.QDialogButtonBox.Cancel
        ]

        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
            button = self.libraryWindow().showQuestionDialog(title, text, buttons)
        finally:
             QtWidgets.QApplication.restoreOverrideCursor()

        if button == QtWidgets.QDialogButtonBox.Yes:
            self._moveToTrash()
        else:
            raise ItemSaveError("You cannot save over an existing item.")

        return button

    # -----------------------------------------------------------------
    # Support for painting the type icon
    # -----------------------------------------------------------------

    def _moveToTrash(self):
        """
        Move the current item to the trash.

        This method should only be used when saving.
        """
        path = self.path()
        library = self.library()
        item = studiolibrary.LibraryItem(path, library=library)
        self.libraryWindow().moveItemsToTrash([item])
        # self.setPath(path)
