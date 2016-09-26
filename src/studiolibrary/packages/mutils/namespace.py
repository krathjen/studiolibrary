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
