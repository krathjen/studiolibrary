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
import time
import json
import getpass
import logging

from . import utils


__all__ = ["MetaFile"]


logger = logging.getLogger(__name__)


class MetaFile(object):

    def __init__(self, path, read=True):
        """
        :type path: str
        :type read: bool
        """
        self._data = {}
        self._path = ""

        if path:
            self.setPath(path)

        if read and self.exists():
            self.read()

    def dirname(self):
        """
        :rtype: str
        """
        return os.path.dirname(self.path())

    def isFile(self):
        """
        :rtype: bool
        """
        return os.path.isfile(self.path())

    def isFolder(self):
        """
        :rtype: bool
        """
        return os.path.isdir(self.path())

    def mkdir(self):
        """
        :rtype: None
        """
        dirname = self.dirname()
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def openLocation(self):
        """
        :rtype: None
        """
        path = self.path()
        utils.openLocation(path)

    def path(self):
        """
        :rtype: str
        """
        return self._path

    def setPath(self, path):
        """
        :type path: str
        """
        path = path or ""
        path = path.replace("\\", "/")

        self._path = path

    def name(self):
        """
        :rtype: str
        """
        return os.path.basename(self.path())

    def data(self):
        """
        :rtype: dict
        """
        return self._data

    def setData(self, data):
        """
        :type data: dict
        :rtype: None
        """
        self._data = data

    def set(self, key, value):
        """
        :type key: str
        :type value: object
        """
        self.data()[key] = value

    def setdefault(self, key, value):
        """
        :type key: str
        :type value: object
        """
        self.data().setdefault(key, value)

    def get(self, key, default=None):
        """
        :type key: str
        :type default: object
        """
        return self.data().get(key, default)

    def setDescription(self, text):
        """
        :type text: str
        """
        self.set("description", text)

    def description(self,):
        """
        :rtype: str
        """
        return self.get("description", "")

    def owner(self):
        """
        :rtype: str
        """
        return self.get("owner", "")

    def mtime(self):
        """
        :rtype: str
        """
        return self.get("mtime", "")

    def ctime(self):
        """
        :rtype: str
        """
        return self.get("ctime", "")

    def read(self):
        """
        :rtype: dict
        """
        data = self._read()
        self.data().update(data)
        return self.data()

    def delete(self):
        """
        :rtype: None
        """
        if os.path.exists(self.jsonPath()):
            os.remove(self.jsonPath())

        if os.path.exists(self.dictPath()):
            os.remove(self.dictPath())

        if os.path.exists(self.path()):
            os.remove(self.path())

    def exists(self):
        """
        Return True if the meta file exists.

        :rtype: bool
        """
        if os.path.exists(self.jsonPath()):
            return True
        elif os.path.exists(self.dictPath()):
            return True
        else:
            return os.path.exists(self.path())

    def dictPath(self):
        """
        Return the path with a dict extension.

        :rtype: str
        """
        return self.path().replace(".json", ".dict")

    def jsonPath(self):
        """
        Return the path with a json extension.

        :rtype: str
        """
        return self.path().replace(".dict", ".json")

    def readJson(self):
        """
        Read the meta file using json.

        :rtype: dict
        """
        path = self.jsonPath()
        data = utils.readJson(path)
        return data

    def readDict(self):
        """
        Read the meta file as a python dict.

        :rtype: dict
        """
        path = self.dictPath()
        data = utils.readDict(path)
        return data

    def saveJson(self, data):
        """
        Save the data in the json format.

        :type data: dict
        :rtype: None
        """
        utils.saveJson(self.path(), data)

    def save(self):
        """
        :rtype: None
        """
        data = self.data()

        t = str(time.time()).split(".")[0]
        owner = getpass.getuser().lower()

        if "ctime" not in data:
            data["ctime"] = t

        data["mtime"] = t
        data["owner"] = owner

        logger.debug(u'Saving Meta File "{0}"'.format(self.path()))
        self.mkdir()

        try:
            data_ = eval(str(data), {})  # Validate data before writing
            self.saveJson(data_)
        except:
            msg = "An error has occurred when evaluating string: {0}"
            msg = msg.format(str(data))
            raise IOError(msg)

    def _read(self):
        """
        :rtype: dict
        """
        if os.path.isfile(self.jsonPath()):
            return self.readJson()
        else:
            return self.readDict()
