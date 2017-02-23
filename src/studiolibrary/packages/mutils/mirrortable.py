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
#
# mirrortable.py
import mutils

# Example 1:
# Create mirror table from objects
mt = mutils.MirrorTable.fromObjects(objects, "_l_", "_r_", MirrorPlane.YZ)

# Example 2:
# Create mirror table from selected objects
objects = maya.cmds.ls(selection=True)
mt = mutils.MirrorTable.fromObjects(objects, "_l_", "_r_", MirrorPlane.YZ)

# Example 3:
# Save to file
path = "/tmp/test.mt"
mt.save(path)

# Example 4:
# Load from file
path = "/tmp/test.mt"
mt = mutils.MirrorTable.fromPath(path)

# load to objects from file
mt.load()

# load to selected objects
objects = maya.cmds.ls(selection=True) or []
mt.load(objects=objects)

# loat to namespaces
mt.load(namespaces=["character1", "character2"])

# load to specified objects
mt.load(objects=["Character1:Hand_L", "Character1:Finger_L"])
mt.leftToRight()
mt.rightToLeft()
"""

import re
import mutils
import logging

try:
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()


__all__ = ["MirrorTable", "MirrorPlane", "MirrorOption", "Axis"]
logger = logging.getLogger(__name__)


RE_LEFT_SIDE = "Lf|lt_|_lt|lf_|_lf|_l_|_L|L_|left|Left|\|l_|:l_|^l_|_l$"
RE_RIGHT_SIDE = "Rt|rt_|_rt|_r_|_R|R_|right|Right|\|r_|:r_|^r_|_r$"


class MirrorPlane:
    YZ = [-1, 1, 1]
    XZ = [1, -1, 1]
    XY = [1, 1, -1]


class MirrorOption:
    Swap = 0
    RightToLeft = 1
    LeftToRight = 2


class MirrorTable(mutils.SelectionSet):

    @classmethod
    @mutils.restoreSelection
    def fromObjects(cls, objects, leftSide=None, rightSide=None, mirrorPlane=MirrorPlane.YZ):
        """
        :type objects: list[str]
        """
        mirrorTable = cls()
        mirrorTable.setMetadata("left", leftSide)
        mirrorTable.setMetadata("right", rightSide)
        mirrorTable.setMetadata("mirrorPlane", mirrorPlane)

        for obj in objects:
            if maya.cmds.nodeType(obj) == "transform":
                mirrorTable.add(obj)

        return mirrorTable

    @staticmethod
    def findLeftSide(objects):
        """
        :type objects: str
        :rtype: str
        """
        return MirrorTable.findSide(objects, RE_LEFT_SIDE)

    @staticmethod
    def findRightSide(objects):
        """
        :type objects: str
        :rtype: str
        """
        return MirrorTable.findSide(objects, RE_RIGHT_SIDE)

    @staticmethod
    def findSide(names, reSide):
        """
        :type names: list[str]
        :type reSide: str
        :rtype: str
        """
        reSide = re.compile(reSide)
        for n in names:
            m = reSide.search(n)
            if m:
                side = m.group()
                side = side.replace(":", "")
                side = side.replace("|", "")

                if n.startswith(side) or ":" + side in n or "|" + side in n:
                    side += "*"

                if n.endswith(side):
                    side = "*" + side

                return side
        return ""

    @staticmethod
    def animCurve(obj, attr):
        """
        :type obj: str
        :type attr: str
        :rtype: str
        """
        connections = maya.cmds.listConnections(obj + "." + attr, d=False, s=True)
        if connections:
            return connections[0]
        return None

    @staticmethod
    def scaleKey(obj, attr):
        """
        :type obj: str
        :type attr: str
        """
        curve = MirrorTable.animCurve(obj, attr)
        if curve:
            maya.cmds.selectKey(curve)
            maya.cmds.scaleKey(iub=False, ts=1, fs=1, vs=-1, vp=0, animation="keys")

    @staticmethod
    def formatValue(attr, value, mirrorAxis):
        """
        :type attr: str
        :type value: float
        :type mirrorAxis: list[int]
        :rtype: float
        """
        if MirrorTable.isAttrMirrored(attr, mirrorAxis):
            return value * -1
        return value

    @staticmethod
    def maxIndex(numbers):
        """
        Finds the largest number in a list
        :type numbers: list[float] or list[str]
        :rtype: int
        """
        m = 0
        result = 0
        for i in numbers:
            v = abs(float(i))
            if v > m:
                m = v
                result = numbers.index(i)
        return result

    @staticmethod
    def axisWorldPosition(obj, axis):
        """
        :type obj: str
        :type axis: (int, int, int)
        :rtype: list[float]
        """
        transform1 = maya.cmds.createNode("transform", name="transform1")
        try:
            transform1, = maya.cmds.parent(transform1, obj, r=True)
            maya.cmds.setAttr(transform1 + ".t", *axis)
            maya.cmds.setAttr(transform1 + ".r", 0, 0, 0)
            maya.cmds.setAttr(transform1 + ".s", 1, 1, 1)
            return maya.cmds.xform(transform1, q=True, ws=True, piv=True)
        finally:
            maya.cmds.delete(transform1)

    @staticmethod
    def isAttrMirrored(attr, mirrorAxis):
        """
        :type attr: str
        :type mirrorAxis: list[int]
        :rtype: float
        """
        if mirrorAxis == [-1, 1, 1]:
            if attr == "translateX" or attr == "rotateY" or attr == "rotateZ":
                return True

        elif mirrorAxis == [1, -1, 1]:
            if attr == "translateY" or attr == "rotateX" or attr == "rotateZ":
                return True

        elif mirrorAxis == [1, 1, -1]:
            if attr == "translateZ" or attr == "rotateX" or attr == "rotateY":
                return True

        elif mirrorAxis == [-1, -1, -1]:
            if attr == "translateX" or attr == "translateY" or attr == "translateZ":
                return True
        return False

    @staticmethod
    def isAxisMirrored(srcObj, dstObj, axis, mirrorPlane):
        """
        :type srcObj: str
        :type dstObj: str
        :type axis: (int, int, int)
        :type mirrorPlane: list[int]
        :rtype: int
        """
        old1 = maya.cmds.xform(srcObj, q=True, ws=True, piv=True)
        old2 = maya.cmds.xform(dstObj, q=True, ws=True, piv=True)

        new1 = MirrorTable.axisWorldPosition(srcObj, axis)
        new2 = MirrorTable.axisWorldPosition(dstObj, axis)

        mp = mirrorPlane
        v1 = mp[0]*(new1[0]-old1[0]), mp[1]*(new1[1]-old1[1]), mp[2]*(new1[2]-old1[2])
        v2 = new2[0]-old2[0], new2[1]-old2[1], new2[2]-old2[2]

        d = sum(p*q for p, q in zip(v1, v2))

        if d >= 0.0:
            return False
        return True

    @staticmethod
    def _calculateMirrorAxis(obj, mirrorPlane):
        """
        :type obj: str
        :rtype: list[int]
        """
        result = [1, 1, 1]
        transform0 = maya.cmds.createNode("transform", name="transform0")

        try:
            transform0, = maya.cmds.parent(transform0, obj, r=True)
            transform0, = maya.cmds.parent(transform0, w=True)
            maya.cmds.setAttr(transform0 + ".t", 0, 0, 0)

            t1 = MirrorTable.axisWorldPosition(transform0, [1, 0, 0])
            t2 = MirrorTable.axisWorldPosition(transform0, [0, 1, 0])
            t3 = MirrorTable.axisWorldPosition(transform0, [0, 0, 1])

            t1 = "%.3f" % t1[0], "%.3f" % t1[1], "%.3f" % t1[2]
            t2 = "%.3f" % t2[0], "%.3f" % t2[1], "%.3f" % t2[2]
            t3 = "%.3f" % t3[0], "%.3f" % t3[1], "%.3f" % t3[2]

            if mirrorPlane == MirrorPlane.YZ:  # [-1, 1, 1]:
                x = [t1[0], t2[0], t3[0]]
                i = MirrorTable.maxIndex(x)
                result[i] = -1

            if mirrorPlane == MirrorPlane.XZ:  # [1, -1, 1]:
                y = [t1[1], t2[1], t3[1]]
                i = MirrorTable.maxIndex(y)
                result[i] = -1

            if mirrorPlane == MirrorPlane.XY:  # [1, 1, -1]:
                z = [t1[2], t2[2], t3[2]]
                i = MirrorTable.maxIndex(z)
                result[i] = -1

        finally:
            maya.cmds.delete(transform0)

        return result

    def setPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        if path.endswith(".mirror"):
            path += "/mirrortable.json"

        mutils.TransferBase.setPath(self, path)

    def leftSide(self):
        """
        :rtype: str | None
        """
        return self.metadata().get("left")

    def rightSide(self):
        """
        :rtype: str | None
        """
        return self.metadata().get("right")

    def mirrorPlane(self):
        """
        :rtype: str | None
        """
        return self.metadata().get("mirrorPlane")

    def mirrorAxis(self, name):
        """
        :rtype: list[int]
        """
        return self.objects()[name]["mirrorAxis"]

    def leftCount(self, objects=None):
        """
        :type objects: list[str]
        :rtype: int
        """
        if objects is None:
            objects = self.objects()
        return len([obj for obj in objects if self.isLeftSide(obj)])

    def rightCount(self, objects=None):
        """
        :type objects: list[str]
        :rtype: int
        """
        if objects is None:
            objects = self.objects()
        return len([obj for obj in objects if self.isRightSide(obj)])

    def createObjectData(self, name):
        """
        :type name:
        :rtype:
        """
        result = {"mirrorAxis": self.calculateMirrorAxis(name)}
        return result

    def matchObjects(self,  objects=None, namespaces=None, selection=False, callback=None):
        """
        :type objects: list[str]
        :type namespaces: list[str]
        :type selection: bool
        :type callback: func
        :rtype: list[str]
        """
        results = {}
        srcObjects = self.objects().keys()

        matches = mutils.matchNames(
            srcObjects=srcObjects,
            dstObjects=objects,
            dstNamespaces=namespaces,
        )

        for srcNode, dstNode in matches:
            dstObj = dstNode.name()
            mirrorAxis = self.mirrorAxis(srcNode.name())
            callback(srcNode.name(), dstObj, mirrorAxis)

        return results

    def rightToLeft(self):
        """
        """
        self.load(option=MirrorOption.RightToLeft)

    def leftToRight(self):
        """
        """
        self.load(option=MirrorOption.LeftToRight)

    @mutils.timing
    @mutils.unifyUndo
    @mutils.showWaitCursor
    @mutils.restoreSelection
    def load(self, objects=None, namespaces=None, option=None, animation=True, time=None):
        """
        :type objects: list[str]
        :type namespaces: list[str]
        :type option: mirrorOptions
        """
        results = {}
        foundObject = False
        srcObjects = self.objects().keys()

        if option is None:
            option = MirrorOption.Swap

        matches = mutils.matchNames(
            srcObjects=srcObjects,
            dstObjects=objects,
            dstNamespaces=namespaces,
        )

        for srcNode, dstNode in matches:
            dstObj = dstNode.name()
            dstObj2 = self.mirrorObject(dstObj) or dstObj

            if dstObj2 not in results:
                results[dstObj] = dstObj2

                mirrorAxis = self.mirrorAxis(srcNode.name())
                dstObjExists = maya.cmds.objExists(dstObj)
                dstObj2Exists = maya.cmds.objExists(dstObj2)

                if dstObjExists and dstObj2Exists:
                    foundObject = True
                    if animation:
                        self.transferAnimation(dstObj, dstObj2, mirrorAxis=mirrorAxis, option=option, time=time)
                    else:
                        self.transferStatic(dstObj, dstObj2, mirrorAxis=mirrorAxis, option=option)
                else:
                    if not dstObjExists:
                        msg = "Cannot find destination object {0}"
                        msg = msg.format(dstObj)
                        logger.debug(msg)

                    if not dstObj2Exists:
                        msg = "Cannot find mirrored destination object {0}"
                        msg = msg.format(dstObj2)
                        logger.debug(msg)

        if not foundObject:
            raise mutils.NoMatchFoundError("No objects match when loading data")

    def transferStatic(self, srcObj, dstObj, mirrorAxis=None, attrs=None, option=MirrorOption.Swap):
        """
        :type srcObj: str
        :type dstObj: str
        :type mirrorAxis: int
        :type attrs: None | str
        :type option: MirrorOption
        """
        srcValue = None
        dstValue = None
        srcValid = self.isValidMirror(srcObj, option)
        dstValid = self.isValidMirror(dstObj, option)

        if attrs is None:
            attrs = maya.cmds.listAttr(srcObj, keyable=True) or []

        for attr in attrs:
            dstAttr = dstObj + "." + attr
            srcAttr = srcObj + "." + attr
            if maya.cmds.objExists(dstAttr):
                if dstValid:
                    srcValue = maya.cmds.getAttr(srcAttr)

                if srcValid:
                    dstValue = maya.cmds.getAttr(dstAttr)

                if dstValid:
                    self.setAttr(dstObj, attr, srcValue, mirrorAxis=mirrorAxis)

                if srcValid:
                    self.setAttr(srcObj, attr, dstValue, mirrorAxis=mirrorAxis)
            else:
                logger.debug("Cannot find destination attribute %s" % dstAttr)

    def setAttr(self, name, attr, value, mirrorAxis=None):
        """
        :type name: str
        :type: attr: str
        :type: value: int | float
        :type mirrorAxis: Axis
        """
        if mirrorAxis is not None:
            value = self.formatValue(attr, value, mirrorAxis)
        try:
            maya.cmds.setAttr(name + "." + attr, value)
        except RuntimeError:
            msg = "Cannot mirror static attribute {name}.{attr}"
            msg = msg.format(name=name, attr=attr)
            logger.debug(msg)

    def transferAnimation(self, srcObj, dstObj, mirrorAxis=None, option=MirrorOption.Swap, time=None):
        """
        :type srcObj: str
        :type dstObj: str
        :type mirrorAxis: Axis
        """
        srcValid = self.isValidMirror(srcObj, option)
        dstValid = self.isValidMirror(dstObj, option)

        tmpObj, = maya.cmds.duplicate(srcObj, name='DELETE_ME', parentOnly=True)
        try:
            if dstValid:
                self._transferAnimation(srcObj, tmpObj, time=time)
            if srcValid:
                self._transferAnimation(dstObj, srcObj, mirrorAxis=mirrorAxis, time=time)
            if dstValid:
                self._transferAnimation(tmpObj, dstObj, mirrorAxis=mirrorAxis, time=time)
        finally:
            maya.cmds.delete(tmpObj)

    def _transferAnimation(self, srcObj, dstObj, attrs=None, mirrorAxis=None, time=None):
        """
        :type srcObj: str
        :type dstObj: str
        :type attrs: list[str]
        :type mirrorAxis: (int, int, int)
        """
        maya.cmds.cutKey(dstObj, time=time or ())  # remove keys
        if maya.cmds.copyKey(srcObj, time=time or ()):
            if not time:
                maya.cmds.pasteKey(dstObj, option="replaceCompletely")
            else:
                maya.cmds.pasteKey(dstObj, time=time, option="replace")

        if attrs is None:
            attrs = maya.cmds.listAttr(srcObj, keyable=True) or []

        for attr in attrs:
            srcAttribute = mutils.Attribute(srcObj, attr)
            dstAttribute = mutils.Attribute(dstObj, attr)

            if dstAttribute.exists():
                if dstAttribute.isConnected():
                    if self.isAttrMirrored(attr, mirrorAxis):
                        maya.cmds.scaleKey(dstAttribute.name(), valueScale=-1, attribute=attr)
                else:
                    value = srcAttribute.value()
                    self.setAttr(dstObj, attr, value, mirrorAxis)

    def isValidMirror(self, obj, option):
        """
        :type obj: str
        :type option: MirrorOption
        :rtype: bool
        """
        if option == MirrorOption.Swap:
            return True

        elif option == MirrorOption.RightToLeft and self.isLeftSide(obj):
            return False

        elif option == MirrorOption.LeftToRight and self.isRightSide(obj):
            return False

        else:
            return True

    def replacePrefix(self, name, search, replace):
        """
        Replace the given search prefix with the given replace prefix.
        It should also support long names.

        # Example:
        self.replacePrefix("R_footRoll", "R", "L")
        # Result: "L_footRoll" and not "L_footLoll".

        # Long name example:
        Group|Character1:R_footRollExtra|Character1:R_footRoll

        :type name: str
        :type search: str
        :type replace: str
        :rtype: str
        """
        dstName = name
        search = search.replace("*", "")
        replace = replace.replace("*", "")

        # Support for the prefix with namespaces
        # Group|Character1:LfootRollExtra|Character1:LfootRoll
        if ":" in name:
            dstName = name.replace(":" + search, ":" + replace)
            if name != dstName:
                return dstName

        # Support for the prefix with long names
        # Group|LfootRollExtra|LfootRoll
        if "|" in name:
            dstName = name.replace("|" + search, "|" + replace)

        return dstName

    def replaceSuffix(self, name, search, replace):
        """
        Replace the given search suffix with the given replace suffix.
        It should also support long names.

        # Example:
        self.replaceSuffix("footRoll_R", "R", "L")
        # Eesult: "footRoll_L" and not "footLoll_L".

        # Long name example:
        Group|Character1:footRollExtra_R|Character1:footRoll_R

        :type name: str
        :type search: str
        :type replace: str
        :rtype: str
        """
        dstName = name
        search = search.replace("*", "")
        replace = replace.replace("*", "")

        # Support for the suffix with long name
        # Group|Character1:footRollExtraR|Character1:footRollR
        if "|" in name:
            dstName = name.replace(search + "|", replace + "|")

        # Eg: Character1:footRollR
        if dstName.endswith(search):
            dstName = dstName[:-len(search)] + replace

        return dstName

    def isLeftSide(self, name):
        """
        Return True if the object contains the left side string.

        # Group|Character1:footRollExtra_L|Character1:footRoll_L
        # Group|footRollExtra_L|footRoll_LShape
        # footRoll_L
        # footRoll_LShape

        :type obj: str
        :rtype: bool
        """
        side = self.leftSide()
        return self.matchSide(name, side)

    def isRightSide(self, name):
        """
        Return True if the object contains the right side string.

        # Group|Character1:footRollExtra_R|Character1:footRoll_R
        # Group|footRollExtra_R|footRoll_RShape
        # footRoll_R
        # footRoll_RShape

        :type name: str
        :rtype: bool
        """
        side = self.rightSide()
        return self.matchSide(name, side)

    def matchSide(self, name, side):
        """
        Return True if the name contains the given side.

        :type name: str
        :type side: str
        :rtype: bool
        """
        if side:
            # Support for prefix naming convention.
            if side.endswith("*"):
                return self.replacePrefix(name, side, "X") != name

            # Support for suffix naming convention.
            elif side.startswith("*"):
                return self.replaceSuffix(name, side, "X") != name

            # Support for all other naming conventions.
            else:
                return side in name

        return False

    def mirrorObject(self, name):
        """
        Return the other/opposite side for the given name.

        Example:
            print self.mirrorObject("FKSholder_L")
            # FKShoulder_R

        :type name: str
        :rtype: str or None
        """
        leftSide = self.leftSide()
        rightSide = self.rightSide()

        # Support for the prefix naming convention.
        if leftSide.endswith("*") or rightSide.endswith("*"):
            dstName = self.replacePrefix(name, leftSide, rightSide)

            if name == dstName:
                dstName = self.replacePrefix(name, rightSide, leftSide)

            if dstName != name:
                return dstName

        # Support for the suffix naming convention.
        elif leftSide.startswith("*") or rightSide.startswith("*"):

            dstName = self.replaceSuffix(name, leftSide, rightSide)

            if name == dstName:
                dstName = self.replaceSuffix(name, rightSide, leftSide)

            if dstName != name:
                return dstName

        # Support for all other naming conventions.
        else:

            dstName = name.replace(leftSide, rightSide)

            if dstName == name:
                dstName = name.replace(rightSide, leftSide)

            if dstName != name:
                return dstName

        # Return None as the given name is probably a center control
        # and doesn't have an opposite side.
        return None

    def calculateMirrorAxis(self, srcObj):
        """
        :type srcObj: str
        :rtype: (int, int int)
        """
        result = [1, 1, 1]
        dstObj = self.mirrorObject(srcObj) or srcObj
        mirrorPlane = self.mirrorPlane()

        if dstObj == srcObj or not maya.cmds.objExists(dstObj):
            # The source object does not have an opposite side
            result = MirrorTable._calculateMirrorAxis(srcObj, mirrorPlane)
        else:
            # The source object does have an opposite side
            if MirrorTable.isAxisMirrored(srcObj, dstObj, [1, 0, 0], mirrorPlane):
                result[0] = -1

            if MirrorTable.isAxisMirrored(srcObj, dstObj, [0, 1, 0], mirrorPlane):
                result[1] = -1

            if MirrorTable.isAxisMirrored(srcObj, dstObj, [0, 0, 1], mirrorPlane):
                result[2] = -1

        return result
