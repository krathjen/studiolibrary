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
import shutil
import logging

import mutils

from studioqt import QtWidgets

try:
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()

logger = logging.getLogger(__name__)


MIN_TIME_LIMIT = -10000
MAX_TIME_LIMIT = 100000
DEFAULT_FILE_TYPE = "mayaBinary"  # "mayaAscii"


class PasteOption:

    Insert = "insert"
    Replace = "replace"
    ReplaceAll = "replace all"
    ReplaceCompletely = "replaceCompletely"


class AnimationTransferError(Exception):
    """Base class for exceptions in this module."""
    pass


class OutOfBoundsError(AnimationTransferError):
    """Exceptions for clips or ranges that are outside the expected range"""
    pass


def saveAnim(
    path,
    objects=None,
    time=None,
    sampleBy=1,
    metadata=None,
    bakeConnected=False
):
    """
    Save the anim data for the given objects.

    Example:
        anim = "C:/example.anim"
        anim = saveAnim(path, metadata={'description': 'Example anim'})
        print anim.metadata()
        # {'description': 'test', 'user': 'Hovel', 'mayaVersion': u'2016'}

    :type path: str
    :type objects: None or list[str]
    :type time: None or int
    :type sampleBy: int
    :type metadata: dict or None
    :type bakeConnected: bool
    :rtype: mutils.Animation
    """
    step = 1
    objects = objects or maya.cmds.ls(selection=True) or []

    if not objects:
        raise Exception(
            "No objects selected. Please select at least one object."
        )

    if not time:
        time = mutils.selectedObjectsFrameRange(objects)

    start, end = time

    if start >= end:
        msg = "The start frame cannot be greater than or equal to the end frame!"
        raise AnimationTransferError(msg)

    iconPath = path + "/thumbnail.jpg"
    sequencePath = path + "/sequence/thumbnail.jpg"

    sequencePath = mutils.createSnapshot(
        path=sequencePath,
        start=start,
        end=end,
        step=step,
    )

    if iconPath:
        shutil.copyfile(sequencePath, iconPath)

    anim = mutils.Animation.fromObjects(objects)

    if metadata:
        anim.updateMetadata(metadata)

    anim.save(path, time=time, bakeConnected=bakeConnected, sampleBy=sampleBy)
    return anim


def clampRange(srcTime, dstTime):
    """
    Clips the given source time to within the given destination time.

    Example:
        print clampRange((15, 35), (20, 30))
        # 20, 30

        print clampRange((25, 45), (20, 30))
        # 25, 30

    :type srcTime: (int, int)
    :type dstTime: (int, int)
    :rtype: (int, int)
    """
    srcStart, srcEnd = srcTime
    dstStart, dstEnd = dstTime

    if srcStart > dstEnd or srcEnd < dstStart:
        msg = "The src and dst time do not overlap. " \
              "Unable to clamp (src=%s, dest=%s)"
        raise OutOfBoundsError(msg, srcTime, dstTime)

    if srcStart < dstStart:
        srcStart = dstStart

    if srcEnd > dstEnd:
        srcEnd = dstEnd

    return srcStart, srcEnd


def moveTime(time, start):
    """
    Move the given time to the given start time.

    Example:
        print moveTime((15, 35), 5)
        # 5, 20

    :type time: (int, int)
    :type start: int
    :rtype: (int, int)
    """
    srcStartTime, srcEndTime = time
    duration = srcEndTime - srcStartTime

    if start is None:
        startTime = srcStartTime
    else:
        startTime = start

    endTime = startTime + duration

    if startTime == endTime:
        endTime = startTime + 1

    return startTime, endTime


def findFirstLastKeyframes(curves, time=None):
    """
    Return the first and last frame of the given animation curves

    :type curves: list[str]
    :type time: (int, int)
    :rtype: (int, int)
    """
    first = maya.cmds.findKeyframe(curves, which='first')
    last = maya.cmds.findKeyframe(curves, which='last')

    result = (first, last)

    if time:
        
        # It's possible (but unlikely) that the curves will not lie within the 
        # first and last frame
        try:
            result = clampRange(time, result)
        except OutOfBoundsError, e:
            logger.warning(e)
            
    return result


def insertKeyframe(curves, time):
    """
    Insert a keyframe on the given curves at the given time.

    :type curves: list[str]
    :type time: (int, int)
    """
    startTime, endTime = time

    for curve in curves:
        insertStaticKeyframe(curve, time)

    firstFrame = maya.cmds.findKeyframe(curves, time=(startTime, startTime), which='first')
    lastFrame = maya.cmds.findKeyframe(curves, time=(endTime, endTime), which='last')

    if firstFrame < startTime < lastFrame:
        maya.cmds.setKeyframe(curves, insert=True, time=(startTime, startTime))

    if firstFrame < endTime < lastFrame:
        maya.cmds.setKeyframe(curves, insert=True, time=(endTime, endTime))


def insertStaticKeyframe(curve, time):
    """
    Insert a static keyframe on the given curve at the given time.

    :type curve: str
    :type time: (int, int)
    :rtype: None
    """
    startTime, endTime = time

    lastFrame = maya.cmds.findKeyframe(curve, which='last')
    firstFrame = maya.cmds.findKeyframe(curve, which='first')

    if firstFrame == lastFrame:
        maya.cmds.setKeyframe(curve, insert=True, time=(startTime, endTime))
        maya.cmds.keyTangent(curve, time=(startTime, startTime), ott="step")

    if startTime < firstFrame:
        nextFrame = maya.cmds.findKeyframe(curve, time=(startTime, startTime), which='next')
        if startTime < nextFrame < endTime:
            maya.cmds.setKeyframe(curve, insert=True, time=(startTime, nextFrame))
            maya.cmds.keyTangent(curve, time=(startTime, startTime), ott="step")

    if endTime > lastFrame:
        previousFrame = maya.cmds.findKeyframe(curve, time=(endTime, endTime), which='previous')
        if startTime < previousFrame < endTime:
            maya.cmds.setKeyframe(curve, insert=True, time=(previousFrame, endTime))
            maya.cmds.keyTangent(curve, time=(previousFrame, previousFrame), ott="step")


def loadAnims(
    paths,
    spacing=1,
    objects=None,
    option=None,
    connect=False,
    namespaces=None,
    startFrame=None,
    mirrorTable=None,
    currentTime=None,
    showDialog=False,
):
    """
    Load the animations in the given order of paths with the spacing specified.

    :type paths: list[str]
    :type spacing: int
    :type connect: bool
    :type objects: list[str]
    :type namespaces: list[str]
    :type startFrame: int
    :type option: PasteOption
    :type currentTime: bool
    :type mirrorTable: bool
    :type showDialog: bool
    """
    isFirstAnim = True

    if spacing < 1:
        spacing = 1

    if option is None or option == "replace all":
        option = PasteOption.ReplaceCompletely

    if currentTime and startFrame is None:
        startFrame = int(maya.cmds.currentTime(query=True))

    if showDialog:

        msg = "Load the following animation in sequence;\n"

        for i, path in enumerate(paths):
            msg += "\n {0}. {1}".format(i, os.path.basename(path))

        msg += "\n\nPlease choose the spacing between each animation."

        spacing, accepted = QtWidgets.QInputDialog.getInt(
            None,
            "Load animation sequence",
            msg,
            spacing,
            QtWidgets.QInputDialog.NoButtons,
        )

        if not accepted:
            raise Exception("Dialog canceled!")

    for path in paths:

        anim = mutils.Animation.fromPath(path)

        if startFrame is None and isFirstAnim:
            startFrame = anim.startFrame()

        if option == "replaceCompletely" and not isFirstAnim:
            option = "insert"

        anim.load(
            option=option,
            objects=objects,
            connect=connect,
            startFrame=startFrame,
            namespaces=namespaces,
            currentTime=currentTime,
            mirrorTable=mirrorTable,
        )

        duration = anim.endFrame() - anim.startFrame()
        startFrame += duration + spacing
        isFirstAnim = False


class Animation(mutils.Pose):

    IMPORT_NAMESPACE = "REMOVE_IMPORT"

    @classmethod
    def fromPath(cls, path):
        """
        Create and return an Anim object from the give path.

        Example:
            anim = Animation.fromPath("/temp/example.anim")
            print anim.endFrame()
            # 14

        :type path: str
        :rtype: Animation
        """
        anim = cls()
        anim.setPath(path)
        anim.read()
        return anim

    def __init__(self):
        mutils.Pose.__init__(self)

        try:
            timeUnit = maya.cmds.currentUnit(q=True, time=True)
            linearUnit = maya.cmds.currentUnit(q=True, linear=True)
            angularUnit = maya.cmds.currentUnit(q=True, angle=True)

            self.setMetadata("timeUnit", timeUnit)
            self.setMetadata("linearUnit", linearUnit)
            self.setMetadata("angularUnit", angularUnit)
        except NameError, msg:
            logger.exception(msg)

    def startFrame(self):
        """
        Return the start frame for anim object.

        :rtype: int
        """
        return self.metadata().get("startFrame")

    def endFrame(self):
        """
        Return the end frame for anim object.

        :rtype: int
        """
        return self.metadata().get("endFrame")

    def mayaPath(self):
        """
        :rtype: str
        """
        mayaPath = os.path.join(self.path(), "animation.mb")
        if not os.path.exists(mayaPath):
            mayaPath = os.path.join(self.path(), "animation.ma")
        return mayaPath

    def poseJsonPath(self):
        """
        :rtype: str
        """
        return os.path.join(self.path(), "pose.json")

    def paths(self):
        """
        Return all the paths for Anim object.

        :rtype: list[str]
        """
        result = []
        if os.path.exists(self.mayaPath()):
            result.append(self.mayaPath())

        if os.path.exists(self.poseJsonPath()):
            result.append(self.poseJsonPath())

        return result

    def animCurve(self, name, attr, withNamespace=False):
        """
        Return the animCurve for the given object name and attribute.

        :type name: str
        :type attr: str
        :type withNamespace: bool

        :rtype: str
        """
        curve = self.attr(name, attr).get("curve", None)
        if curve and withNamespace:
            curve = Animation.IMPORT_NAMESPACE + ":" + curve
        return curve

    def setAnimCurve(self, name, attr, curve):
        """
        Set the animCurve for the given object name and attribute.

        :type name: str
        :type attr: str
        :type curve: str
        """
        self.objects()[name].setdefault("attrs", {})
        self.objects()[name]["attrs"].setdefault(attr, {})
        self.objects()[name]["attrs"][attr]["curve"] = curve

    def read(self, path=None):
        """
        Read all the data to be used by the Anim object.

        :rtype: None
        """
        path = self.poseJsonPath()

        logger.debug("Reading: " + path)
        mutils.Pose.read(self, path=path)
        logger.debug("Reading Done")

    @mutils.unifyUndo
    @mutils.restoreSelection
    def open(self):
        """
        The reason we use importing and not referencing is because we
        need to modify the imported animation curves and modifying
        referenced animation curves is only supported in Maya 2014+
        """
        self.close()  # Make sure everything is cleaned before importing

        nodes = maya.cmds.file(
            self.mayaPath(),
            i=True,
            groupLocator=True,
            ignoreVersion=True,
            returnNewNodes=True,
            namespace=Animation.IMPORT_NAMESPACE,
        )

        return nodes

    def close(self):
        """
        Clean up all imported nodes, as well as the namespace.
        Should be called in a finally block.
        """
        nodes = maya.cmds.ls(Animation.IMPORT_NAMESPACE + ":*", r=True) or []
        if nodes:
            maya.cmds.delete(nodes)

        # It is important that we remove the imported namespace,
        # otherwise another namespace will be created on next
        # animation open.
        namespaces = maya.cmds.namespaceInfo(ls=True) or []

        if Animation.IMPORT_NAMESPACE in namespaces:
            maya.cmds.namespace(set=':')
            maya.cmds.namespace(rm=Animation.IMPORT_NAMESPACE)

    def cleanMayaFile(self, path):
        """
        Clean up all commands in the exported maya file that are
        not createNode.
        """
        results = []

        with open(path, "r") as f:
            for line in f.readlines():
                if not line.startswith("select -ne"):
                    results.append(line)
                else:
                    results.append("// End")
                    break

        with open(path, "w") as f:
            f.writelines(results)

    @mutils.timing
    @mutils.unifyUndo
    @mutils.showWaitCursor
    @mutils.restoreSelection
    def save(
        self,
        path,
        time=None,
        sampleBy=1,
        fileType="",
        bakeConnected=True
    ):
        """
        Save all animation data from the objects set on the Anim object.

        :type path: str
        :type time: (int, int) or None
        :type sampleBy: int
        :type fileType: str
        :type bakeConnected: bool
        
        :rtype: None
        """
        objects = self.objects().keys()

        fileType = fileType or DEFAULT_FILE_TYPE

        if not time:
            time = mutils.selectedObjectsFrameRange(objects)
        start, end = time

        # Check selected animation layers
        gSelectedAnimLayers = maya.mel.eval('$gSelectedAnimLayers=$gSelectedAnimLayers')
        if len(gSelectedAnimLayers) > 1:
            msg = "More than one animation layer is selected! Please select only one animation layer for export!"
            raise AnimationTransferError(msg)

        # Check frame range
        if start is None or end is None:
            msg = "Please specify a start and end frame!"
            raise AnimationTransferError(msg)

        if start >= end:
            msg = "The start frame cannot be greater than or equal to the end frame!"
            raise AnimationTransferError(msg)

        # Check if animation exists
        if mutils.getDurationFromNodes(nodes=objects or []) <= 0:
            msg = "No animation was found on the specified object/s! Please create a pose instead!"
            raise AnimationTransferError(msg)

        self.setMetadata("endFrame", end)
        self.setMetadata("startFrame", start)

        end += 1
        dstCurves = []
        validAnimCurves = []

        msg = "Animation.save(path={0}, time={1}, bakeConnections={2}, sampleBy={3})"
        msg = msg.format(path, str(time), str(bakeConnected), str(sampleBy))
        logger.debug(msg)

        try:
            if bakeConnected:
                maya.cmds.undoInfo(openChunk=True)
                mutils.bakeConnected(objects, time=(start, end), sampleBy=sampleBy)

            for name in objects:
                if maya.cmds.copyKey(name, time=(start, end), includeUpperBound=False, option="keys"):

                    # Might return more than one object when duplicating shapes or blendshapes
                    transform, = maya.cmds.duplicate(name, name="CURVE", parentOnly=True)

                    dstCurves.append(transform)
                    mutils.disconnectAll(transform)
                    maya.cmds.pasteKey(transform)

                    attrs = maya.cmds.listAttr(transform, unlocked=True, keyable=True) or []
                    attrs = list(set(attrs) - set(['translate', 'rotate', 'scale']))

                    for attr in attrs:
                        fullname = ("%s.%s" % (transform, attr))
                        dstCurve, = maya.cmds.listConnections(fullname, destination=False) or [None]

                        if dstCurve:
                            # Filter to only animCurves since you can have proxy attributes
                            if not maya.cmds.nodeType(dstCurve).startswith("animCurve"):
                                continue

                            dstCurve = maya.cmds.rename(dstCurve, "CURVE")
                            srcCurve = mutils.animCurve("%s.%s" % (name, attr))
                            if srcCurve and "animCurve" in maya.cmds.nodeType(srcCurve):
                                preInfinity = maya.cmds.getAttr(srcCurve + ".preInfinity")
                                postInfinity = maya.cmds.getAttr(srcCurve + ".postInfinity")
                                curveColor = maya.cmds.getAttr(srcCurve + ".curveColor")
                                useCurveColor = maya.cmds.getAttr(srcCurve + ".useCurveColor")

                                maya.cmds.setAttr(dstCurve + ".preInfinity", preInfinity)
                                maya.cmds.setAttr(dstCurve + ".postInfinity", postInfinity)
                                maya.cmds.setAttr(dstCurve + ".curveColor", *curveColor[0])
                                maya.cmds.setAttr(dstCurve + ".useCurveColor", useCurveColor)

                            dstCurves.append(dstCurve)

                            if maya.cmds.keyframe(dstCurve, query=True, time=(start, end), keyframeCount=True):
                                self.setAnimCurve(name, attr, dstCurve)
                                maya.cmds.cutKey(dstCurve, time=(MIN_TIME_LIMIT, start - 1))
                                maya.cmds.cutKey(dstCurve, time=(end + 1, MAX_TIME_LIMIT))
                                validAnimCurves.append(dstCurve)

            fileName = "animation.ma"
            if fileType == "mayaBinary":
                fileName = "animation.mb"

            mayaPath = os.path.join(path, fileName)
            posePath = os.path.join(path, "pose.json")
            mutils.Pose.save(self, posePath)

            if validAnimCurves:
                maya.cmds.select(validAnimCurves)
                logger.info("Saving animation: %s" % mayaPath)
                maya.cmds.file(mayaPath, force=True, options='v=0', type=fileType, uiConfiguration=False, exportSelected=True)
                self.cleanMayaFile(mayaPath)

        finally:
            if bakeConnected:
                # HACK! Undo all baked connections. :)
                maya.cmds.undoInfo(closeChunk=True)
                maya.cmds.undo()
            elif dstCurves:
                maya.cmds.delete(dstCurves)

        self.setPath(path)

    @mutils.timing
    @mutils.showWaitCursor
    def load(
            self,
            objects=None,
            namespaces=None,
            attrs=None,
            startFrame=None,
            sourceTime=None,
            option=None,
            connect=False,
            mirrorTable=None,
            currentTime=None
    ):
        """
        Load the animation data to the given objects or namespaces.

        :type objects: list[str]
        :type namespaces: list[str]
        :type startFrame: int
        :type sourceTime: (int, int)
        :type attrs: list[str]
        :type option: PasteOption
        :type connect: bool
        :type mirrorTable: mutils.MirrorTable
        :type currentTime: bool or None
        """
        connect = bool(connect)  # Make false if connect is None

        if option is None or option == PasteOption.ReplaceAll:
            option = PasteOption.ReplaceCompletely

        objects = objects or []

        logger.debug("Animation.load(objects=%s, option=%s, namespaces=%s, srcTime=%s, currentTime=%s)" %
                     (len(objects), str(option), str(namespaces), str(sourceTime), str(currentTime)))

        srcObjects = self.objects().keys()

        if mirrorTable:
            self.setMirrorTable(mirrorTable)

        valid = False
        matches = list(mutils.matchNames(srcObjects=srcObjects, dstObjects=objects, dstNamespaces=namespaces))

        for srcNode, dstNode in matches:
            if dstNode.exists():
                valid = True
                break

        if not matches or not valid:

            text = "No objects match when loading data. " \
                   "Turn on debug mode to see more details."

            raise mutils.NoMatchFoundError(text)

        # Load the animation data.
        srcCurves = self.open()

        try:
            maya.cmds.flushUndo()
            maya.cmds.undoInfo(openChunk=True)

            if currentTime and startFrame is None:
                startFrame = int(maya.cmds.currentTime(query=True))

            srcTime = findFirstLastKeyframes(srcCurves, sourceTime)
            dstTime = moveTime(srcTime, startFrame)

            if option != PasteOption.ReplaceCompletely:
                insertKeyframe(srcCurves, srcTime)

            for srcNode, dstNode in matches:

                # Remove the first pipe in-case the object has a parent
                dstNode.stripFirstPipe()

                for attr in self.attrs(srcNode.name()):

                    # Filter any attributes if the parameter has been set
                    if attrs is not None and attr not in attrs:
                        continue

                    dstAttr = mutils.Attribute(dstNode.name(), attr)
                    srcCurve = self.animCurve(srcNode.name(), attr, withNamespace=True)

                    # Skip if the destination attribute does not exists.
                    if not dstAttr.exists():
                        logger.debug('Skipping attribute: The destination attribute "%s.%s" does not exist!' %
                                     (dstAttr.name(), dstAttr.attr()))
                        continue

                    if srcCurve:
                        dstAttr.setAnimCurve(
                            srcCurve,
                            time=dstTime,
                            option=option,
                            source=srcTime,
                            connect=connect
                        )
                    else:
                        value = self.attrValue(srcNode.name(), attr)
                        dstAttr.setStaticKeyframe(value, dstTime, option)

        finally:
            self.close()
            maya.cmds.undoInfo(closeChunk=True)

            # Return the focus to the Maya window
            maya.cmds.setFocus("MayaWindow")
