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

import utils


__all__ = [
    "Database",
]


class Database(object):

    def __init__(self, path):

        self._path = path

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
        return utils.readJson(self.path())

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

    def updateKeys(self, keys, data):
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

    def renameFolder(self, src, dst):
        """
        Rename the given source directory to the given destination.
            
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

        # Replace all keys that start with the src value with the dst value.
        for oldKey in data:
            if oldKey.startswith(src):
                newKey = oldKey.replace(src, dst, 1)
                data[newKey] = data[oldKey]
                del data[oldKey]

        self.write(data)
