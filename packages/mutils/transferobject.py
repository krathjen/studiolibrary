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
"""
Base object for saving poses, animation, selection sets and mirror tables.

Example:
    import mutils
    
    t = mutils.TransferObject.fromPath("/tmp/pose.json")
    t = mutils.TransferObject.fromObjects(["object1", "object2"])
    
    t.load(selection=True)
    t.load(objects=["obj1", "obj2"])
    t.load(namespaces=["namespace1", "namespace2"])
    
    t.save("/tmp/pose.json")
    t.read("/tmp/pose.json")
"""
import os
import abc
import json
import time
import getpass
import logging


import mutils

try:
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()


logger = logging.getLogger(__name__)


class TransferObject(object):

    @classmethod
    def fromPath(cls, path):
        """
        Return a new transfer instance for the given path.
        
        :type path: str
        :rtype: TransferObject
        """
        t = cls()
        t.setPath(path)
        t.read()
        return t

    @classmethod
    def fromObjects(cls, objects, **kwargs):
        """
        Return a new transfer instance for the given objects.
        
        :type objects: list[str]
        :rtype: TransferObject
        """
        t = cls(**kwargs)
        for obj in objects:
            t.add(obj)
        return t

    @staticmethod
    def readJson(path):
        """
        Read the given json path

        :type path: str
        :rtype: dict
        """
        with open(path, "r") as f:
            data = f.read() or "{}"

        data = json.loads(data)

        return data

    @staticmethod
    def readList(path):
        """
        Legacy method for reading older .list file type.

        :rtype: dict 
        """
        with open(path, "r") as f:
            data = f.read()

        data = eval(data, {})
        result = {}
        for obj in data:
            result.setdefault(obj, {})

        return {"objects": result}

    @staticmethod
    def readDict(path):
        """
        Legacy method for reading older .dict file type.

        :rtype: dict 
        """
        with open(path, "r") as f:
            data = f.read()

        data = eval(data, {})
        result = {}
        for obj in data:
            result.setdefault(obj, {"attrs": {}})
            for attr in data[obj]:
                typ, val = data[obj][attr]
                result[obj]["attrs"][attr] = {"type": typ, "value": val}

        return {"objects": result}

    def __init__(self):
        self._path = None
        self._namespaces = None
        self._data = {"metadata": {}, "objects": {}}

    def path(self):
        """
        Return the disc location for the transfer object.
        
        :rtype: str
        """
        return self._path

    def setPath(self, path):
        """
        Set the disc location for loading and saving the transfer object.

        :type path: str
        """
        dictPath = path.replace(".json", ".dict")
        listPath = path.replace(".json", ".list")

        if not os.path.exists(path):

            if os.path.exists(dictPath):
                path = dictPath

            elif os.path.exists(listPath):
                path = listPath

        self._path = path

    def mtime(self):
        """
        Return the modification datetime of self.path().
        
        :rtype: float
        """
        return os.path.getmtime(self.path())

    def ctime(self):
        """
        Return the creation datetime of self.path().
        
        :rtype: float
        """
        return os.path.getctime(self.path())

    def data(self):
        """
        Return all the data for the transfer object.
        
        :rtype: dict
        """
        return self._data

    def setData(self, data):
        """
        Set the data for the transfer object.
        
        :type data:
        """
        self._data = data

    def objects(self):
        """
        Return all the object data.
        
        :rtype: dict
        """
        return self.data().get("objects", {})

    def object(self, name):
        """
        Return the data for the given object name.
        
        :type name: str
        :rtype: dict
        """
        return self.objects().get(name, {})

    def createObjectData(self, name):
        """
        Create the object data for the given object name.
        
        :type name: str
        :rtype: dict
        """
        return {}

    def namespaces(self):
        """
        Return the namespaces contained in the transfer object

        :rtype: list[str]
        """
        if self._namespaces is None:
            group = mutils.groupObjects(self.objects())
            self._namespaces = group.keys()

        return self._namespaces

    def count(self):
        """
        Return the number of objects in the transfer object.
        
        :rtype: int
        """
        return len(self.objects() or [])

    def add(self, objects):
        """
        Add the given objects to the transfer object.

        :type objects: str | list[str]
        """
        if isinstance(objects, basestring):
            objects = [objects]

        for name in objects:
            self.objects()[name] = self.createObjectData(name)

    def remove(self, objects):
        """
        Remove the given objects to the transfer object.

        :type objects: str | list[str]
        """
        if isinstance(objects, basestring):
            objects = [objects]

        for obj in objects:
            del self.objects()[obj]

    def setMetadata(self, key, value):
        """
        Set the given key and value in the metadata.
        
        :type key: str
        :type value: int | str | float | dict
        """
        self.data()["metadata"][key] = value

    def updateMetadata(self, metadata):
        """
        Update the given key and value in the metadata.
        
        :type metadata: dict
        """
        self.data()["metadata"].update(metadata)

    def metadata(self):
        """
        Return the current metadata for the transfer object.
        
        Example: print self.metadata()
            Result # {
                "User": "",
                "Scene": "",
                "Reference": {"filename": "", "namespace": ""},
                "Description": "",
            }
        
        :rtype: dict
        """
        return self.data().get("metadata", {})

    def read(self, path=""):
        """
        Return the data from the path set on the Transfer object.

        :type path: str
        :rtype: dict
        """
        path = path or self.path()

        if path.endswith(".dict"):
            data = self.readDict(path)

        elif path.endswith(".list"):
            data = self.readList(path)

        else:
            data = self.readJson(path)

        self.setData(data)

    @abc.abstractmethod
    def load(self, *args, **kwargs):
        pass

    @mutils.showWaitCursor
    def save(self, path):
        """
        Save the current metadata and object data to the given path.
        
        :type path: str
        :rtype: None
        """
        logger.info("Saving pose: %s" % path)

        user = getpass.getuser()
        ctime = str(time.time()).split(".")[0]

        self.setMetadata("user", user)
        self.setMetadata("ctime", ctime)
        self.setMetadata("version", "1.0.0")
        self.setMetadata("mayaVersion", maya.cmds.about(v=True))
        self.setMetadata("mayaSceneFile", maya.cmds.file(q=True, sn=True))

        # Move the metadata information to the top of the file
        metadata = {"metadata": self.metadata()}
        data = self.dump(metadata)[:-1] + ","

        # Move the objects information to after the metadata
        objects = {"objects": self.objects()}
        data += self.dump(objects)[1:]

        # Create the given directory if it doesn't exist
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(path, "w") as f:
            f.write(str(data))

        logger.info("Saved pose: %s" % path)

    def dump(self, data=None):
        """
        :type data: str | dict
        :rtype: str
        """
        if data is None:
            data = self.data()

        return json.dumps(data, indent=2)
