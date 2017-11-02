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

    def __init__(self, path, *args):
        QtCore.QObject.__init__(self, *args)

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

    def find(self, keys=None):
        """
        Return all the data for the given keys.

        :type keys: list[str]
        :rtype: dict
        """
        data = self.read()

        if keys:
            keys = self.normPaths(keys)
            results = {key: data[key] for key in keys if key in data}
        else:
            results = data

        return results

    def dataFromColumn(self, column, keys=None, sort=True, split=""):
        """
        Return the data in the given column for the given keys.

        :type column: str
        :type keys: list[str]
        :type sort: bool
        :type split: str
        :rtype: list[str]
        """
        data = self.find(keys)
        results = []

        for item in data.values():

            text = item.get(column)

            if text and split:
                results.extend(text.split(split))
            elif text:
                results.append(text)

        results = list(set(results))

        if sort:
            results = sorted(results)

        return results

    def read(self):
        """
        Read the database from disc and return a dict object.

        :rtype: dict
        """
        return studiolibrary.readJson(self.path())

    def save(self, data):
        """
        Write the given dict object to the database on disc.

        :type data: dict
        :rtype: None
        """
        studiolibrary.saveJson(self.path(), data)

    def update(self, data):
        """
        Update the database with the given data.

        :type data: dict
        :rtype: dict
        """
        return studiolibrary.updateJson(self.path(), data)

    def replace(self, old, new, count=-1):
        """
        Replace the old value with the new value in the database.

        :type old: str
        :type new: str
        :type count: int

        :rtype: dict
        """
        return studiolibrary.replaceJson(self.path(), old, new, count)

    def updateMultiple(self, keys, data):
        """
        Update the given keys with the given data.

        :type keys: list
        :type data: dict
        :rtype: None
        """
        data_ = self.read()
        keys = self.normPaths(keys)

        for key in keys:
            if key in data_:
                data_[key].update(data)
            else:
                data_[key] = data

        self.save(data_)

    def updateItems(self, items, data):
        """
        Update the given items in the database with the given data.
        
        :type items: list[studiolibrary.LibraryItem]
        :type data: dict
        
        :rtype: None
        """
        keys = [item.id() for item in items]

        self.updateMultiple(keys, data)

        # Update the item data
        for item in items:
            for column in data:
                item.setText(column, data[column])
                item.updateData()

    def deleteMultiple(self, keys):
        """
        Delete the given keys in the JSON path.

        :type keys: list[str]
        :rtype: None
        """
        data = self.read()

        keys = self.normPaths(keys)

        for key in keys:
            if key in data:
                del data[key]

        self.save(data)

    def addPath(self, path, data=None):
        """
        Add the given path and data to the database.    
    
        :type path: str
        :type data: dict or None
        :rtype: None 
        """
        data = data or {}
        self.updateMultiple([path], data)

    def removePath(self, path):
        """
        Remove the given path from the database.

        :type path: str
        :rtype: None
        """
        self.deleteMultiple([path])

    def renamePath(self, src, dst):
        """
        Rename the given path in the database to the given dst path.

        :type src: str
        :type dst: str
        :rtype: None
        """
        src = self.normPath(src)
        dst = self.normPath(dst)

        src1 = '"' + src + '"'
        dst2 = '"' + dst + '"'

        # Replace paths that match exactly the given src and dst strings
        self.replace(src1, dst2)

        src2 = '"' + src
        dst2 = '"' + dst

        # Add a slash as a suffix for better directory matching
        if not src2.endswith("/"):
            src2 += "/"

        if not dst2.endswith("/"):
            dst2 += "/"

        # Replace all paths that start with the src path with the dst path
        self.replace(src2, dst2)
