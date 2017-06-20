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
import utils
import logging

import studioqt
from studioqt import QtCore


__all__ = [
    "Database",
]


logger = logging.getLogger(__name__)


class Database(QtCore.QObject):

    ENABLE_WATCHER = False

    databaseChanged = QtCore.Signal()

    def __init__(self, path):
        QtCore.QObject.__init__(self)

        self._path = path
        self._mtime = None
        self._watcher = None

        self.setDirty(False)
        if self.ENABLE_WATCHER:
            self.setWatcherEnabled(True)

    def setWatcherEnabled(self, enable, repeatRate=1):
        """
        Enable a watcher that will trigger the database changed signal.
        
        :type enable: bool
        :type repeatRate: int
        :rtype: None 
        """
        if enable:
            if not self._watcher:
                self._watcher = studioqt.InvokeRepeatingThread(repeatRate)
                self._watcher.triggered.connect(self._watcherTrggered)
                self._watcher.start()
        elif self._watcher:
                self._watcher.terminate()
                self._watcher = None

    def _watcherTrggered(self):
        """
        Triggered when the watcher has reached it's repeat rate.
        
        :rtype: None 
        """
        print self._mtime
        if self.isDirty():
            self.setDirty(False)
            self.databaseChanged.emit()

    def setDirty(self, value):
        """
        Update the database object with the current timestamp of the db path.
        
        :rtype: None 
        """
        if value:
            self._mtime = None
        else:
            self._mtime = os.path.getmtime(self.path())

    def isDirty(self):
        """
        Return True if the database has changed on disc.

        :rtype: bool 
        """
        return self._mtime != os.path.getmtime(self.path())

    def path(self):
        """
        Return the disc location of the db.

        :rtype: str 
        """
        return self._path

    def read(self):
        """
        Read the database and return the data.

        :rtype: dict
        """
        path = self.path()
        data = utils.readJson(path)
        return data

    def write(self, data):
        """
        Write the given data to the database.

        :type data: dict
        :rtype: None 
        """
        utils.saveJson(self.path(), data)

    def update(self, data):
        """
        Update the database with the given data.

        :type data: dict
        :rtype: None 
        """
        data_ = self.read()
        data_.update(data)
        self.write(data_)

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
        data_ = self.read()

        for key in keys:
            if key in data_:
                data_[key].update(data)
            else:
                data_[key] = data

        self.write(data_)

    def renameItem(self, src, dst):
        """
        Rename the given path in the db to the given dst path.

        :type src: str
        :type dst: str
        :rtype: None
        """
        data = self.read()

        # Replace the old key with the new dst value
        if src in data:

            data_ = data.get(src, {})

            # If the dst path already exists then we just update the data
            if dst in data:
                data[dst].update(data_)
            else:
                data[dst] = data_

            # Remove the old path from the database
            if src in data:
                del data[src]

            self.write(data)

    def renameFolder(self, src, dst):
        """
        Rename the given source directory in the db to the given destination.

        :type src: str
        :type dst: str
        :rtype: None
        """
        data = self.read()

        # Add a slash as a suffix for better directory matching
        if not src.endswith("/"):
            src += "/"

        if not dst.endswith("/"):
            dst += "/"

        # Replace all keys that start with the src value with the dst value
        for oldKey in data:
            if oldKey.startswith(src):
                newKey = oldKey.replace(src, dst, 1)
                data[newKey] = data[oldKey]
                del data[oldKey]

        self.write(data)
