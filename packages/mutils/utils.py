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

import shutil
import platform
import traceback

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


try:
    import maya.mel
    import maya.cmds
except ImportError:
    traceback.print_exc()

import mutils


class MayaUtilsError(Exception):
    """Base class for exceptions in this module."""


class ObjectsError(MayaUtilsError):
    pass


class SelectionError(MayaUtilsError):
    pass


class NoMatchFoundError(MayaUtilsError):
    pass


class NoObjectFoundError(MayaUtilsError):
    pass


class MoreThanOneObjectFoundError(MayaUtilsError):
    pass


class ModelPanelNotInFocusError(MayaUtilsError):
    pass


def system():
    return platform.system().lower()


def isMac():
    return system().startswith("mac") or system().startswith("os") \
        or system().startswith("darwin")


def isWindows():
    return system().lower().startswith("win")


def isLinux():
    return system().lower().startswith("lin")


def isMaya():
    """
    :rtype: bool
    """
    try:
        import maya.cmds
        maya.cmds.about(batch=True)
        return True
    except ImportError:
        return False


def selectionModifiers():
    """
    Return the current selection modifiers.

    :rtype: dict
    """
    result = {"add": False, "deselect": False}
    modifiers = QtWidgets.QApplication.keyboardModifiers()

    if modifiers == QtCore.Qt.ShiftModifier:
        result["deselect"] = True
    elif modifiers == QtCore.Qt.ControlModifier:
        result["add"] = True

    return result


def ls(*args, **kwargs):
    """
    :rtype: list[Node]
    """
    return [mutils.Node(name) for name in maya.cmds.ls(*args, **kwargs) or []]


def listAttr(node, **kwargs):
    """
    :type node: mutils.Node
    :type kwargs: dict
    :rtype: list[mutils.Attribute]
    """
    attrs = maya.cmds.listAttr(node.name(), **kwargs)
    return [mutils.Attribute(node.name(), attr) for attr in attrs or []]


def currentFrameRange():
    """
    :rtype: (int, int)
    """
    start, end = selectedFrameRange()

    if end == start:
        start, end = selectedObjectsFrameRange()
        if start == end:
            start, end = playbackFrameRange()

    return start, end


def playbackFrameRange():
    """
    :rtype: (int, int)
    """
    start = maya.cmds.playbackOptions(query=True, min=True)
    end = maya.cmds.playbackOptions(query=True, max=True)
    return start, end


def selectedFrameRange():
    """
    :rtype: (int, int)
    """
    result = maya.mel.eval("timeControl -q -range $gPlayBackSlider")
    start, end = result.replace('"', "").split(":")
    start, end = int(start), int(end)
    if end - start == 1:
        end = start
    return start, end


def selectedObjectsFrameRange(dagPaths=None):
    """
    :rtype : (int, int)
    """
    start = 0
    end = 0

    if not dagPaths:
        dagPaths = maya.cmds.ls(selection=True) or []

    if dagPaths:
        start = int(maya.cmds.findKeyframe(dagPaths, which='first'))
        end = int(maya.cmds.findKeyframe(dagPaths, which='last'))

    return start, end


def connectedAttrs(objects):
    """
    """
    result = []
    if not objects:
        raise Exception("No objects specified")

    connections = maya.cmds.listConnections(objects, connections=True, p=True, d=False, s=True) or []
    for i in range(0, len(connections), 2):
        dstObj = connections[i]
        srcObj = connections[i+1]
        nodeType = maya.cmds.nodeType(srcObj)
        if "animCurve" not in nodeType:
            result.append(dstObj)
    return result


def currentModelPanel():
    """
    :rtype: str or None
    """
    currentPanel = maya.cmds.getPanel(withFocus=True)
    currentPanelType = maya.cmds.getPanel(typeOf=currentPanel)

    if currentPanelType not in ['modelPanel']:
        return None

    return currentPanel


def bakeConnected(objects, time, sampleBy=1):
    """
    """
    bakeAttrs = connectedAttrs(objects)

    if bakeAttrs:
        maya.cmds.bakeResults(
            bakeAttrs,
            time=time,
            shape=False,
            simulation=True,
            sampleBy=sampleBy,
            controlPoints=False,
            minimizeRotation=True,
            bakeOnOverrideLayer=False,
            preserveOutsideKeys=False,
            sparseAnimCurveBake=False,
            disableImplicitControl=True,
            removeBakedAttributeFromLayer=False,
        )
    else:
        print "cannot find connection to bake!"


def disconnectAll(name):
    """
    :type name: str
    """
    for destination in maya.cmds.listConnections(name, plugs=True, source=False) or []:
        source, = maya.cmds.listConnections(destination, plugs=True)
        maya.cmds.disconnectAttr(source, destination)


def getSelectedObjects():
    """
    :rtype: list[str]
    :raise mutils.SelectionError:
    """
    selection = maya.cmds.ls(selection=True)
    if not selection:
        raise mutils.SelectionError("No objects selected!")
    return selection


def animCurve(fullname):
    """
    Return the animation curve for the give attribute.

    :type fullname:
    :rtype: None | str
    """
    attribute = mutils.Attribute(fullname)
    return attribute.animCurve()


def deleteUnknownNodes():
    """
    """
    nodes = maya.cmds.ls(type="unknown")
    if nodes:
        for node in nodes:
            if maya.cmds.objExists(node) and \
                    maya.cmds.referenceQuery(node, inr=True):
                maya.cmds.delete(node)


def getSelectedAttrs():
    """
    :rtype: list[str]
    """
    attributes = maya.cmds.channelBox("mainChannelBox", q=True, selectedMainAttributes=True)

    if attributes is not None:
        attributes = str(attributes)
        attributes = attributes.replace("tx", "translateX")
        attributes = attributes.replace("ty", "translateY")
        attributes = attributes.replace("tz", "translateZ")
        attributes = attributes.replace("rx", "rotateX")
        attributes = attributes.replace("ry", "rotateY")
        attributes = attributes.replace("rz", "rotateZ")
        attributes = eval(attributes)

    return attributes


def getDurationFromNodes(nodes):
    """
    :type nodes: list[str]
    :rtype: float
    """
    if nodes:
        s = maya.cmds.findKeyframe(nodes, which='first')
        l = maya.cmds.findKeyframe(nodes, which='last')
        if s == l:
            if maya.cmds.keyframe(nodes, query=True, keyframeCount=True) > 0:
                return 1
            else:
                return 0
        return l - s
    else:
        return 0
