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

import traceback

try:
    import maya.cmds
except ImportError:
    traceback.print_exc()


__all__ = [
    "setNamespace",
    "getFromDagPath",
    "getFromDagPaths",
    "getFromSelection",
]


def setNamespace(dagPath, namespace):
    """
    Return the given dagPath with the given namespace.

    setNamespace("|group|control", "character")
    result: |character:group|character:control

    setNamespace("|character:group|character:control", "")
    result: |group|control

    :type namespace: str
    """
    result = dagPath
    currentNamespace = getFromDagPath(dagPath)

    # Ignore any further processing if the namespace is the same.
    if namespace == currentNamespace:
        pass

    # Replace the current namespace with the specified one
    elif currentNamespace and namespace:
        result = dagPath.replace(currentNamespace + ":", namespace + ":")

    # Remove existing namespace
    elif currentNamespace and not namespace:
        result = dagPath.replace(currentNamespace + ":", "")

    # Set namespace if a current namespace doesn't exists
    elif not currentNamespace and namespace:
        result = dagPath.replace("|", "|" + namespace + ":")
        if namespace and not result.startswith("|"):
            result = namespace + ":" + result

    return result


def getFromDagPaths(dagPaths):
    """
    :type dagPaths: list[str]
    :rtype: list[str]
    """
    namespaces = []

    for dagPath in dagPaths:
        namespace = getFromDagPath(dagPath)
        namespaces.append(namespace)

    return list(set(namespaces))


def getFromDagPath(dagPath):
    """
    :type dagPath: str
    :rtype: str
    """
    shortName = dagPath.split("|")[-1]
    namespace = ":".join(shortName.split(":")[:-1])
    return namespace


def getFromSelection():
    """
    :rtype: list[str]
    """
    dagPaths = maya.cmds.ls(selection=True)
    return getFromDagPaths(dagPaths)
