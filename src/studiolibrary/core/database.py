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

    def data(self, keys=None):
        """
        Return the data from the database filtering by the given keys.

        :type keys: list
        :rtype: dict 
        """
        data = self.read()
        if keys:
            data = [data[key] for key in data if key in keys]
        return data

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

    def _rreplace(self, name, old, new, maxReplace=1):
        """
        Helper to replace the first instance going from right to left.
    
        Example:
            'XXX'.join('mississippi'.rsplit('iss', 1))
            missXXXippi
    
        :type name: str
        :type old: str
        :type new: str
        :rtype: str
        """
        return new.join(name.rsplit(old, maxReplace))

    def rreplaceKeys(self, search, replace):
        """
        Replace the keys with the give search option with the given replace.
            
        :str search: str
        :str replace: str
        :rtype: None
        """
        data = self.data()

        for oldKey in data:
            if oldKey.startswith(search):
                newKey = self._rreplace(oldKey, search, replace)
                data[newKey] = data[oldKey]
                del data[oldKey]

        self.write(data)
