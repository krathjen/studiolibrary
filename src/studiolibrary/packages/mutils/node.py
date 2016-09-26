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

import mutils

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
            self._name = name.encode('ascii')
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
        :rtype: None
        """
        # Try to reduce any long names to short names when using namespaces
        names = maya.cmds.ls(self.shortname())
        if len(names) == 1:
            return Node(names[0])
        elif len(names) > 1:
            raise mutils.MoreThanOneObjectFoundError("More than one object found %s" % str(names))
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
        print n.name()
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
        Sets the namespace for a node.

        setNamespace("character", "|group|control")
        result: |character:group|character:control

        setNamespace("", "|character:group|character:control")
        result: |group|control

        :type namespace: str
        """
        if namespace == self.namespace():
            return

        if self.namespace() and namespace:
            self._name = self.name().replace(self.namespace() + ":", namespace + ":")

        elif self.namespace() and not namespace:
            self._name = self.name().replace(self.namespace() + ":", "")

        elif not self.namespace() and namespace:
            self._name = self.name().replace("|", "|" + namespace + ":")
            if namespace and not self.name().startswith("|"):
                self._name = namespace + ":" + self.name()

        self._shortname = None
        self._namespace = None
        return self.name()