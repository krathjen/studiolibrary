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
import logging
import traceback
from collections import OrderedDict

try:
    import maya.cmds
except ImportError:
    traceback.print_exc()


logger = logging.getLogger(__name__)


__all__ = [
    "getAll",
    "getFromDagPath",
    "getFromDagPaths",
    "getFromSelection",
]


def getFromDagPaths(dagPaths):
    """
    :type dagPaths: list[str]
    :rtype: list[str]
    """
    namespaces = []

    for dagPath in dagPaths:
        namespace = getFromDagPath(dagPath)
        namespaces.append(namespace)

    # Remove any duplicates while retaining the order
    return list(OrderedDict.fromkeys(namespaces))


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
    Get the current namespaces from the selected objects in Maya.

    :rtype: list[str]
    """
    namespaces = [""]

    try:
        names = maya.cmds.ls(selection=True)
        namespaces = getFromDagPaths(names) or namespaces
    except NameError as error:
        # Catch any errors when running this command outside of Maya
        logger.exception(error)

    return namespaces


def getAll():
    """
    Get all the available namespaces in the scene

    :rtype: list[str]
    """
    IGNORE_NAMESPACES = ['UI', 'shared']

    namespaces = maya.cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
    namespaces = list(set(namespaces) - set(IGNORE_NAMESPACES))
    namespaces = sorted(namespaces)

    return namespaces
