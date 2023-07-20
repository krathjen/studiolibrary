# Copyright 2020 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or modify it 
# under the terms of the GNU Lesser General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. This library is distributed in the 
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import mutils

from studiovendor import six

try:
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()


class Node(object):

    @classmethod
    def ls(cls, objects=None, selection=False):
        """
        nodes = Node.ls(selection=True)
        :rtype: list[Node]
        """

        if objects is None and not selection:
            objects = maya.cmds.ls()
        else:
            objects = objects or []
            if selection:
                objects.extend(maya.cmds.ls(selection=True) or [])

        return [cls(name) for name in objects]

    def __init__(self, name, attributes=None):
        """
        :type attributes: [Attribute]
        :type name: str
        """
        try:
            self._name = six.text_type(name)  # .encode('ascii')
        except UnicodeEncodeError:
            raise UnicodeEncodeError('Not a valid ascii name "%s".' % name)

        # Cached properties
        self._shortname = None
        self._namespace = None
        self._mirrorAxis = None
        self._attributes = attributes

    def __str__(self):
        return self.name()

    def name(self):
        """
        :rtype: str
        """
        return self._name

    def attributes(self):
        """
        :rtype: str
        """
        return self._attributes

    def shortname(self):
        """
        :rtype: str
        """
        if self._shortname is None:
            self._shortname = self.name().split("|")[-1]
        return self._shortname

    def toShortName(self):
        """
        :rtype: None or str
        """
        # Try to reduce any long names to short names when using namespaces
        names = maya.cmds.ls(self.shortname())
        if len(names) == 1:
            return Node(names[0])
        elif len(names) > 1:
            # Return the original name if the short name is not unique
            return Node(self.name())
        else:
            raise mutils.NoObjectFoundError("No object found %s" % str(self.shortname()))

    def namespace(self):
        """
        :rtype: str
        """
        if self._namespace is None:
            self._namespace = ":".join(self.shortname().split(":")[:-1])
        return self._namespace

    def stripFirstPipe(self):
        """
        n = Node("|pSphere")
        n.stripFirstPipe()
        print(n.name())
        # Result: pSphere
        """
        if self.name().startswith("|"):
            self._name = self.name()[1:]

    def exists(self):
        """
        :rtype: bool
        """
        return maya.cmds.objExists(self.name())

    def isLong(self):
        """
        :rtype: bool
        """
        return "|" in self.name()

    def isReferenced(self):
        """
        :rtype: bool
        """
        return maya.cmds.referenceQuery(self.name(), isNodeReferenced=True)

    def setMirrorAxis(self, mirrorAxis):
        """
        :type mirrorAxis: list[int]
        """
        self._mirrorAxis = mirrorAxis

    def setNamespace(self, namespace):
        """
        Sets the namespace for a current node in Maya.

        node.setNamespace("character", "|group|control")
        result: |character:group|character:control

        setNamespace("", "|character:group|character:control")
        result: |group|control

        :type namespace: str
        """
        newName = self.name()
        oldName = self.name()

        newNamespace = namespace
        oldNamespace = self.namespace()

        # Ignore any further processing if the namespace is the same.
        if newNamespace == oldNamespace:
            return self.name()

        # Replace the current namespace with the specified one
        if oldNamespace and newNamespace:
            newName = oldName.replace(oldNamespace + ":", newNamespace + ":")

        # Remove existing namespace
        elif oldNamespace and not newNamespace:
            newName = oldName.replace(oldNamespace + ":", "")

        # Set namespace if the current namespace doesn't exists
        elif not oldNamespace and newNamespace:
            newName = oldName.replace("|", "|" + newNamespace + ":")
            if newNamespace and not newName.startswith("|"):
                newName = newNamespace + ":" + newName

        self._name = newName

        self._shortname = None
        self._namespace = None

        return self.name()
