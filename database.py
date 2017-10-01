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

import studiolibrary

import studioqt
from studioqt import QtCore

__all__ = [
    "Database",
]

logger = logging.getLogger(__name__)


class Database(QtCore.QObject):

    ENABLE_WATCHER = False
    DEFAULT_WATCHER_REPEAT_RATE = 1  # in seconds

    databaseChanged = QtCore.Signal()

    def __init__(self, path):
        QtCore.QObject.__init__(self)

        self._path = path
        self._mtime = None
        self._watcher = None

        self.setDirty(False)
        self.setWatcherEnabled(self.ENABLE_WATCHER)

    def setWatcherEnabled(self, enable, repeatRate=None):
        """
        Enable a watcher that will trigger the database changed signal.

        :type enable: bool
        :type repeatRate: int
        :rtype: None
        """
        if enable:
            self.startWatcher(repeatRate=repeatRate)
        else:
            self.stopWatcher()

    def startWatcher(self, repeatRate=None):
        """
        Create and start a file system watcher for the current database. 

        :type repeatRate: int
        :rtype: None 
        """
        self.stopWatcher()

        repeatRate = repeatRate or self.DEFAULT_WATCHER_REPEAT_RATE

        self._watcher = studioqt.InvokeRepeatingThread(repeatRate)
        self._watcher.triggered.connect(self._fileChanged)
        self._watcher.start()

    def stopWatcher(self):
        """
        Stop watching the current database for changes.
        
        :rtype: None 
        """
        if self._watcher:
            self._watcher.terminate()
            self._watcher = None

    def _fileChanged(self):
        """
        Triggered when the watcher has reached it's repeat rate.

        :rtype: None
        """
        if self.isDirty():
            self.setDirty(False)
            self.databaseChanged.emit()

    def mtime(self):
        """
        Return the time of last modification of db.

        :rtype: float or None
        """
        path = self.path()
        mtime = None

        if os.path.exists(path):
            mtime = os.path.getmtime(path)

        return mtime

    def setDirty(self, value):
        """
        Update the database object with the current timestamp of the db path.

        :rtype: None
        """
        if value:
            self._mtime = None
        else:
            self._mtime = self.mtime()

    def isDirty(self):
        """
        Return True if the database has changed on disc.

        :rtype: bool
        """
        return self._mtime != self.mtime()

    def path(self):
        """
        Return the disc location of the db.

        :rtype: str
        """
        return self._path

    def normPaths(self, paths):
        """
        Normalize all the given paths to a consistent format.

        :type paths: list[str]
        :rtype: list[str]
        """
        return [self.normPath(path) for path in paths]

    def normPath(self, path):
        """
        Normalize the path and make all back slashes to forward slashes.

        :type path: str
        :rtype: str
        """
        return studiolibrary.normPath(path)

    def searchReplace(self, old, new, count=-1):
        """
        Replace the old value with the new value in the database.

        :type old: str
        :type new: str
        :type count: int

        :rtype: None
        """
        path = self.path()

        data = studiolibrary.read(path)
        data = data.replace(old, new, count)

        studiolibrary.write(path, data)

    def readJson(self):
        """
        Return the data from the database as a valid dict object.

        :rtype: dict
        """
        return studiolibrary.readJson(self.path())

    def saveJson(self, data):
        """
        Write the given dict object to disc.

        :type data: dict
        :rtype: None
        """
        studiolibrary.saveJson(self.path(), data)

    def update(self, data):
        """
        Update the database with the given data.

        :type data: dict
        :rtype: None
        """
        data_ = self.readJson()
        data_.update(data)
        self.saveJson(data_)

    def insert(self, key, data):
        """
        Insert the given data at the given key.

        :type key: str
        :type data: dict
        :rtype: None
        """
        self.updateMultiple([key], data)

    def updateMultiple(self, keys, data):
        """
        Update the given keys with the given data.

        :type keys: list
        :type data: dict
        :rtype: None
        """
        data_ = self.readJson()

        keys = self.normPaths(keys)

        for key in keys:
            if key in data_:
                data_[key].update(data)
            else:
                data_[key] = data

        self.saveJson(data_)

    def delete(self, key):
        """
        Delete the given key in the JSON path.

        :type key: str
        :rtype: None
        """
        self.deleteMultiple([key])

    def deleteMultiple(self, keys):
        """
        Delete the given keys in the JSON path.

        :type keys: list[str]
        :rtype: None
        """
        data = self.readJson()

        keys = self.normPaths(keys)

        for key in keys:
            if key in data:
                del data[key]

        self.saveJson(data)

    def renamePath(self, src, dst):
        """
        Rename the given path in the db to the given dst path.

        :type src: str
        :type dst: str
        :rtype: None
        """
        src = '"' + self.normPath(src) + '"'
        dst = '"' + self.normPath(dst) + '"'

        self.searchReplace(src, dst)

    def renameFolder(self, src, dst):
        """
        Rename the given source directory in the db to the given destination.

        :type src: str
        :type dst: str
        :rtype: None
        """
        dst = '"' + self.normPath(dst)
        src = '"' + self.normPath(src)

        # Add a slash as a suffix for better directory matching
        if not src.endswith("/"):
            src += "/"

        if not dst.endswith("/"):
            dst += "/"

        # Replace all values that start with the src value with the dst value
        self.searchReplace(src, dst)
