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
import shutil
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studiolibrary


__all__ = ["Record"]

logger = logging.getLogger(__name__)


class RecordError(Exception):
    """"""


class RecordSaveError(RecordError):
    """"""


class RecordLoadError(RecordError):
    """"""


class RecordSignal(QtCore.QObject):
    """"""
    onSaved = QtCore.Signal(object)
    onSaving = QtCore.Signal(object)
    onLoaded = QtCore.Signal(object)
    onDeleted = QtCore.Signal(object)
    onDeleting = QtCore.Signal(object)


class Record(studiolibrary.BasePath, studiolibrary.LibraryItem):

    META_PATH = "{path}/.studioLibrary/record.json"

    signal = RecordSignal()
    onSaved = signal.onSaved
    onSaving = signal.onSaving
    onLoaded = signal.onLoaded
    onDeleted = signal.onDeleted
    onDeleting = signal.onDeleting

    @classmethod
    def fromPath(cls, path, **kwargs):
        """
        :type path: str
        :rtype: Record
        """
        return cls(path, **kwargs)

    def __init__(
        self,
        path=None,
        plugin=None,
        library=None,
    ):
        """
        :type path: str or None
        :type plugin: studiolibrary.Plugin or None
        :type library: studiolibrary.Library or None
        """
        self._error = ""
        self._plugin = plugin
        self._library = library
        self._metaFile = None
        self._iconPath = None

        self.setPlugin(plugin)

        studiolibrary.LibraryItem.__init__(self)
        studiolibrary.BasePath.__init__(self, path)

        self.setPlugin(plugin)  # So that the type icon is set

    def library(self):
        """
        :rtype: studiolibrary.Library
        """
        return self._library or self.plugin().library()

    def libraryWidget(self):
        """
        :rtype: studiolibrary.MainWindow
        """
        if self.library():
            return self.library().libraryWidget()

    def setIconPath(self, path):
        """
        Set the icon path for the current record.

        :type path: str
        :rtype: None
        """
        self._iconPath = path
        self.setIcon("Icon", path)

    def iconPath(self):
        """
        Return the icon path for the current record.

        :type path: str
        :rtype: None
        """
        return self._iconPath

    def errorString(self):
        """
        Return the text string that explains why the record didn't save.

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

    def delete(self):
        """
        :rtype: None
        """
        raise Exception("Deleting files is not supported!")

    def mimeText(self):
        return self.text("Path")

    def url(self):
        """
        :rtype: str
        """
        return QtCore.QUrl.fromLocalFile(self.path())

    def infoWidget(self, parent=None):
        """
        :rtype: str
        """
        if self.plugin():
            return self.plugin().infoWidget(parent=parent, record=self)

    def setPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        if not path:
            raise RecordError('Cannot set empty record path.')

        plugin = self.plugin()

        dirname, basename, extension = studiolibrary.splitPath(path)

        iconPath = path + "/thumbnail.jpg"

        name = os.path.basename(path)
        category = os.path.basename(dirname)

        self.setIconPath(iconPath)
        self.setText("Icon", name)
        self.setText("Name", name)
        self.setText("Path", path)
        self.setText("Category", category)

        if os.path.exists(path):
            modified = os.path.getmtime(path)
            timeAgo = studiolibrary.timeAgo(modified)

            self.setText("Modified", timeAgo)
            self.setSortText("Modified", str(modified))

        if extension:
            if plugin:
                if extension != plugin.extension():
                    path += plugin.extension()
        else:
            if plugin:
                path += plugin.extension()
            else:
                raise RecordSaveError('No extension found!')

        if plugin:
            self.setText("Type", plugin.extension())

        studiolibrary.BasePath.setPath(self, path)

    def plugin(self):
        """
        :rtype: studiolibrary.Plugin
        """
        return self._plugin

    def setPlugin(self, plugin):
        """
        :type plugin: studiolibrary.Plugin
        """
        self._plugin = plugin
        if plugin:
            self.setTypeIconPath(plugin.iconPath())

    def load(self):
        """
        :rtype: None
        """
        logger.debug('Loading "{0}"'.format(self.name()))
        Record.onLoaded.emit(self)

    def moveContents(self, contents):
        """
        :type contents: list[str]
        """
        path = self.path()

        for src in contents or []:
            basename = os.path.basename(src)
            dst = path + "/" + basename
            logger.info('Moving Content: {0} => {1}'.format(src, dst))
            shutil.move(src, dst)

    def save(self, path=None, contents=None):
        """
        :type path: str
        :type contents: list[str]
        :rtype: None
        """
        path = path or self.path()
        contents = contents or []

        self.setPath(path)
        self.setErrorString("")  # Clear the existing error string.

        logger.debug('Record Saving: {0}'.format(path))
        Record.onSaving.emit(self)

        if self.errorString():
            raise RecordSaveError(self.errorString())

        elif os.path.exists(self.path()):
            raise RecordSaveError("Record already exists!")

        self.metaFile().save()
        self.moveContents(contents)

        Record.onSaved.emit(self)
        logger.debug('Record Saved: {0}'.format(self.path()))

    # -----------------------------------------------------------------
    # Support for renaming
    # -----------------------------------------------------------------

    def rename(self, name, extension=None, force=True):
        """
        :type name: str
        :type force: bool
        :type extension: bool or None
        :rtype: None
        """
        extension = extension or self.extension()
        if name and extension not in name:
            name += extension
        studiolibrary.BasePath.rename(self, name, force=force)

    def showRenameDialog(self, parent=None):
        """
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
            self.rename(str(name))

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
        :rtype: str
        """
        path = self.META_PATH
        return self.resolvePath(path)

    def metaFile(self):
        """
        :rtype: metafile.MetaFile
        """
        path = self.metaPath()

        if self._metaFile:
            if self._metaFile.path() != path:
                self._metaFile.setPath(path)
        else:
            self._metaFile = studiolibrary.MetaFile(path, read=True)

        return self._metaFile