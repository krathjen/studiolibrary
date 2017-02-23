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
import shutil
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

    # The meta path is still named record.json and camel case for legacy.
    META_PATH = "{path}/.studioLibrary/record.json"

    _libraryItemSignals = LibraryItemSignals()

    saved = _libraryItemSignals.saved
    saving = _libraryItemSignals.saving
    loaded = _libraryItemSignals.loaded

    def typeIconPath(self):
        """
        Return the type icon path on disc.

        :rtype: path or None
        """
        pass

    @classmethod
    def createAction(cls, menu, libraryWidget):
        """
        Return the action to be displayed when the user clicks the "plus" icon.

        :type menu: QtWidgets.QMenu
        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: QtCore.QAction or None
        """
        pass

    def __init__(
        self,
        path=None,
        library=None,
    ):
        """
        The LibraryItem class provides an item for use with the LibraryWidget.

        :type path: str or None
        :type library: studiolibrary.Library or None
        """
        studioqt.CombinedWidgetItem.__init__(self)

        self._path = ""
        self._error = ""
        self._library = None
        self._metaFile = None
        self._iconPath = None
        self._typePixmap = None

        if library:
            self.setLibrary(library)

        if path:
            self.setPath(path)

    def localSettings(self):
        """
        Return a settings object for saving data to the users local disc.

        :rtype: studiolibrary.Settings
        """
        return studiolibrary.Settings.instance("StudioLibrary", "Items", self.__class__.__name__)

    def thumbnailPath(self):
        """
        Return the thumbnail location on disc for this item.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: QtWidgets.QWidget
        """
        return studioqt.resource().get("icons", "thumbnail.png")

    def previewWidget(self, libraryWidget):
        """
        Return the widget to be shown when the user clicks on the item.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: QtWidgets.QWidget
        """
        pass

    def openLocation(self):
        """Open the file explorer at the given path location."""
        path = self.path()
        dirname = os.path.dirname(path)
        studiolibrary.openLocation(dirname)

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
        :rtype: float
        """
        return os.path.getctime(self.path())

    def library(self):
        """
        :rtype: studiolibrary.Library
        """
        return self._library

    def setLibrary(self, library):
        """
        :type library: studiolibrary.Library
        :rtype: None
        """
        self._library = library

    def libraryWidget(self):
        """
        :rtype: studiolibrary.LibraryWidget
        """
        if self.library():
            return self.library().libraryWidget()

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

        :type path: str
        :rtype: None
        """
        return self._iconPath

    def mimeText(self):
        """
        :rtype: str
        """
        return self.path()

    def url(self):
        """
        :rtype: str
        """
        return QtCore.QUrl.fromLocalFile(self.path())

    def errorString(self):
        """
        Return the text string that explains why the item didn't save.

        :rtype: str
        """
        return self._error

    def setErrorString(self, error):
        """
        Set the error string to be raised on saving.

        :type error: str
        :rtype: None
        """
        self._error = error

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

        path = path.replace("\\", "/")

        dirname, basename, extension = studiolibrary.splitPath(path)

        name = os.path.basename(path)
        category = os.path.basename(dirname)

        self.setText("Icon", name)
        self.setText("Name", name)
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

        :type path: str
        :type contents: list[str]
        :rtype: None
        """
        path = path or self.path()
        contents = contents or []

        self.setPath(path)
        self.setErrorString("")  # Clear the existing error string.

        logger.debug(u'Item Saving: {0}'.format(path))
        self.saving.emit(self)

        if self.errorString():
            raise ItemSaveError(self.errorString())

        elif os.path.exists(self.path()):
            raise ItemSaveError("Item already exists!")

        path = self.path()
        self.metaFile().save()
        studiolibrary.moveContents(contents, path)

        self.saved.emit(self)
        logger.debug(u'Item Saved: {0}'.format(self.path()))

        # -----------------------------------------------------------------
        # Support for copy and rename
        # -----------------------------------------------------------------

    def move(self, dst):
        """
        Move the current item to the given destination.

        :type dst: str
        :rtype: None
        """
        src = self.path()
        path = studiolibrary.movePath(src, dst)
        self.setPath(path)

    def copy(self, dst):
        """
        Make a copy/duplicate the current item to the given destination.

        :type dst: str
        :rtype: None
        """
        src = self.path()
        path = studiolibrary.copyPath(src, dst)
        self.setPath(path)

    def rename(self, dst, extension=None, force=True):
        """
        Rename the current path to given destination path.

        :type name: str
        :type force: bool
        :type extension: bool or None
        :rtype: None
        """
        self.resetImageSequence()

        src = self.path()

        extension = extension or self.extension()
        if dst and extension not in dst:
            dst += extension

        path = studiolibrary.renamePath(src, dst)
        self.setPath(path)

    def showRenameDialog(self, parent=None):
        """
        Show the rename dialog.

        :type parent: QtWidgets.QWidget
        """
        parent = parent or self.library()
        name, accepted = QtWidgets.QInputDialog.getText(
            parent,
            "Rename",
            "New Name",
            QtWidgets.QLineEdit.Normal,
            self.name()
        )

        if accepted:
            self.rename(name)

        return accepted

    # -----------------------------------------------------------------
    # Support for meta data
    # -----------------------------------------------------------------

    def description(self):
        """
        :rtype: str
        """
        return self.metaFile().get('description', "")

    def setDescription(self, text):
        """
        :type: str
        """
        self.metaFile().setDescription(text)

    def setOwner(self, text):
        """
        :type text: str
        """
        self.metaFile().set('owner', text)

    def owner(self):
        """
        :rtype: str
        """
        return self.metaFile().get('owner', "")

    def metaPath(self):
        """
        Return the meta path on disc for the item.

        :rtype: str
        """
        path = self.META_PATH
        return studiolibrary.formatPath(self.path(), path)

    def metaFile(self):
        """
        Return the meta file object for the item.

        :rtype: metafile.MetaFile
        """
        path = self.metaPath()

        if self._metaFile:
            if self._metaFile.path() != path:
                self._metaFile.setPath(path)
        else:
            self._metaFile = studiolibrary.MetaFile(path, read=True)

        return self._metaFile

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
