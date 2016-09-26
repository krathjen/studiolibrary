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
import time
import json
import getpass
import logging

from . import basepath


__all__ = ["MetaFile"]

logger = logging.getLogger(__name__)


class MetaFile(basepath.BasePath):

    def __init__(self, path, read=True):
        """
        :type path: str
        :type read: bool
        """
        super(MetaFile, self).__init__(path)
        self._data = {}

        if read and self.exists():
            self.read()

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
            return super(MetaFile, self).exists()

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
        data = {}
        path = self.jsonPath()

        logger.debug("Reading meta file: {0}".format(path))

        if os.path.isfile(path):
            with open(path, "r") as f:
                data_ = f.read()
                try:
                    data = json.loads(data_)
                except Exception, msg:
                    logger.exception(msg)

        return data

    def readDict(self):
        """
        Read the meta file as a python dict.

        :rtype: dict
        """
        data = {}
        path = self.dictPath()

        logger.debug("Reading meta file: {0}".format(path))

        if os.path.isfile(path):
            with open(path, "r") as f:
                data_ = f.read()
                try:
                    data = eval(data_.strip(), {})
                except Exception, msg:
                    logger.exception(msg)

        return data

    def saveJson(self, data):
        """
        Save the data in the json format.

        :type data: dict
        :rtype: None
        """
        self.mkdir()

        with open(self.jsonPath(), "w") as f:
            data = json.dumps(data, indent=4)
            f.write(data)

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

        logger.debug("Saving Meta File '%s'" % self.path())
        self.mkdir()

        try:
            data_ = eval(str(data), {})  # Validate data before writing
            self._write(data=data_)
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

    def _write(self, data):
        """
        :type data: str
        :rtype: dict
        """
        return self.saveJson(data)
