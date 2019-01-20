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

import logging
import platform
import traceback

from studioqt import QtCore
from studioqt import QtWidgets

try:
    import maya.mel
    import maya.cmds
except ImportError:
    traceback.print_exc()

import mutils


logger = logging.getLogger(__name__)


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
    """
    Return the current platform in lowercase.
    
    :rtype: str
    """
    return platform.system().lower()


def isMac():
    """
    Return True if the current OS is Mac.
    
    :rtype: bool
    """
    return system().startswith("os") or \
           system().startswith("mac") or \
           system().startswith("darwin")


def isLinux():
    """    
    Return True if the current OS is linux.
    
    :rtype: bool
    """
    return system().lower().startswith("lin")


def isWindows():
    """
    Return True if the current OS is windows.
    
    :rtype: bool
    """
    return system().lower().startswith("win")


def isMaya():
    """
    Return True if the current python session is in Maya.
    
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
    Return a dictionary of the current key modifiers

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
    List all the node objects for the given options.

    :type args: list
    :type kwargs: dict
    """
    return [mutils.Node(name) for name in maya.cmds.ls(*args, **kwargs) or []]


def listAttr(name, **kwargs):
    """
    List all the attributes for the given object name.
    
    :type name: str
    :type kwargs: str
    :rtype: list[mutils.Attribute]
    """
    attrs = maya.cmds.listAttr(name, **kwargs) or []
    attrs = list(set(attrs))
    return [mutils.Attribute(name, attr) for attr in attrs]


def disconnectAll(name):
    """
    Disconnect all connections from the given object name.
    
    :type name: str
    """
    plugins = maya.cmds.listConnections(name, plugs=True, source=False) or []

    for plug in plugins:
        source, = maya.cmds.listConnections(plug, plugs=True)
        maya.cmds.disconnectAttr(source, plug)


def animCurve(fullname):
    """
    Return the animation curve name for the give attribute.

    :type fullname: str or None
    :rtype: str or None
    """
    attribute = mutils.Attribute(fullname)
    return attribute.animCurve()


def deleteUnknownNodes():
    """Delete all unknown nodes in the Maya scene."""
    nodes = maya.cmds.ls(type="unknown")
    if nodes:
        for node in nodes:
            if maya.cmds.objExists(node) and \
                    maya.cmds.referenceQuery(node, inr=True):
                maya.cmds.delete(node)


def currentModelPanel():
    """
    Get the current model panel name.
    
    :rtype: str or None
    """
    currentPanel = maya.cmds.getPanel(withFocus=True)
    currentPanelType = maya.cmds.getPanel(typeOf=currentPanel)

    if currentPanelType not in ['modelPanel']:
        return None

    return currentPanel


def getBakeAttrs(objects):
    """
    Get the attributes that are not connected to an animation curve.

    :type objects: list[str]
    :rtype: list[str]
    """
    result = []

    if not objects:
        raise Exception("No objects specified")

    connections = maya.cmds.listConnections(
        objects,
        plugs=True,
        source=True,
        connections=True,
        destination=False
    ) or []

    for i in range(0, len(connections), 2):
        dstObj = connections[i]
        srcObj = connections[i + 1]

        nodeType = maya.cmds.nodeType(srcObj)

        if "animCurve" not in nodeType:
            result.append(dstObj)

    return result


def bakeConnected(objects, time, sampleBy=1):
    """
    Bake the given objects.
    
    :type objects: list[str]
    :type time: (int, int)
    :type sampleBy: int
    """
    bakeAttrs = getBakeAttrs(objects)

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
        logger.error("Cannot find any connection to bake!")


def getSelectedObjects():
    """
    Get a list of the selected objects in Maya.    
    
    :rtype: list[str]
    :raises: mutils.SelectionError:
    """
    selection = maya.cmds.ls(selection=True)
    if not selection:
        raise mutils.SelectionError("No objects selected!")
    return selection


def getSelectedAttrs():
    """
    Get the attributes that are selected in the channel box.
    
    :rtype: list[str]
    """
    attributes = maya.cmds.channelBox(
        "mainChannelBox",
        query=True,
        selectedMainAttributes=True
    )

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


def currentFrameRange():
    """
    Get the current first and last frame depending on the context.

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
    Get the first and last frame from the play back options.

    :rtype: (int, int)
    """
    start = maya.cmds.playbackOptions(query=True, min=True)
    end = maya.cmds.playbackOptions(query=True, max=True)
    return start, end


def selectedFrameRange():
    """
    Get the first and last frame from the play back slider.
 
    :rtype: (int, int)
    """
    result = maya.mel.eval("timeControl -q -range $gPlayBackSlider")
    start, end = result.replace('"', "").split(":")
    start, end = int(start), int(end)
    if end - start == 1:
        end = start
    return start, end


def selectedObjectsFrameRange(objects=None):
    """
    Get the first and last animation frame from the given objects.
    
    :type objects: list[str]
    :rtype: (int, int)
    """
    start = 0
    end = 0

    if not objects:
        objects = maya.cmds.ls(selection=True) or []

    if objects:
        start = int(maya.cmds.findKeyframe(objects, which='first'))
        end = int(maya.cmds.findKeyframe(objects, which='last'))

    return start, end


def getDurationFromNodes(objects):
    """
    Get the duration of the animation from the given object names.
    
    :type objects: list[str]
    :rtype: float
    """
    if objects:
        first = maya.cmds.findKeyframe(objects, which='first')
        last = maya.cmds.findKeyframe(objects, which='last')
        if first == last:
            if maya.cmds.keyframe(objects, query=True, keyframeCount=True) > 0:
                return 1
            else:
                return 0
        return last - first
    else:
        return 0
