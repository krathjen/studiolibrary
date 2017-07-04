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
Example:

import mutils

attr = mutils.Attribute("sphere1", "translateX")
attr.set(100)
"""
import logging

try:
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()


logger = logging.getLogger(__name__)


VALID_CONNECTIONS = [
    "animCurve",
    "animBlend",
    "pairBlend",
    "character"
]

VALID_BLEND_ATTRIBUTES = [
    "int",
    "long",
    "float",
    "short",
    "double",
    "doubleAngle",
    "doubleLinear",
]

VALID_ATTRIBUTE_TYPES = [
    "int",
    "long",
    "enum",
    "bool",
    "string",
    "float",
    "short",
    "double",
    "doubleAngle",
    "doubleLinear",
]


class AttributeError(Exception):
    """Base class for exceptions in this module."""
    pass


class Attribute(object):

    @classmethod
    def listAttr(cls, name, **kwargs):
        """
        Return a list of Attribute from the given name and matching criteria.

        If no flags are specified all attributes are listed.

        :rtype: list[Attribute]
        """
        attrs = maya.cmds.listAttr(name, **kwargs) or []
        return [cls(name, attr) for attr in attrs]

    def __init__(self, name, attr=None, value=None, type=None, cache=True):
        """
        :type name: str
        :type attr: str | None
        :type type: str | None
        :type value: object | None
        :type cache: bool
        """
        if "." in name:
            name, attr = name.split(".")

        if attr is None:
            msg = "Cannot initialise attribute instance without a given attr."
            raise AttributeError(msg)

        # For now this is on by default, however in a future update
        # this will be off by default.
        self._cache = cache

        try:
            self._name = name.encode('ascii')
            self._attr = attr.encode('ascii')
        except UnicodeEncodeError:
            msg = 'Not a valid ascii name "{0}.{1}"'.format(name, attr)
            raise UnicodeEncodeError(msg)

        self._type = type
        self._value = value
        self._fullname = None

    def __str__(self):
        """
        :rtype: str
        """
        return str(self.toDict())

    def name(self):
        """
        Return the Maya object name for the attribute.

        :rtype: str
        """
        return self._name

    def attr(self):
        """
        Return the attribute name.

        :rtype: str
        """
        return self._attr

    def isLocked(self):
        """
        Return true if the attribute is locked.

        :rtype: bool
        """
        return maya.cmds.getAttr(self.fullname(), lock=True)

    def isUnlocked(self):
        """
        Return true if the attribute is unlocked.

        :rtype: bool
        """
        return not self.isLocked()

    def toDict(self):
        """
        Return a dictionary of the attribute object.

        :rtype: dict
        """
        result = {
            "type": self.type(),
            "value": self.value(),
            "fullname": self.fullname(),
        }
        return result

    def isValid(self):
        """
        Return true if the attribute type is valid.

        :rtype: bool
        """
        return self.type() in VALID_ATTRIBUTE_TYPES

    def exists(self):
        """
        Return true if the object and attribute exists in the scene.

        :rtype: bool
        """
        return maya.cmds.objExists(self.fullname())

    def prettyPrint(self):
        """
        Print the command for setting the attribute value
        """
        msg = 'maya.cmds.setAttr("{0}", {1})'
        msg = msg.format(self.fullname(), self.value())
        print(msg)

    def clearCache(self):
        """
        Clear all cached values
        """
        self._type = None
        self._value = None

    def update(self):
        """
        This method will be deprecated.
        """
        self.clearCache()

    def query(self, **kwargs):
        """
        Convenience method for Maya's attribute query command

        :rtype: object
        """
        return maya.cmds.attributeQuery(self.attr(), node=self.name(), **kwargs)

    def listConnections(self, **kwargs):
        """
        Convenience method for Maya's list connections command

        :rtype: list[str]
        """
        return maya.cmds.listConnections(self.fullname(), **kwargs)

    def sourceConnection(self, **kwargs):
        """
        Return the source connection for this attribute.

        :rtype: str | None
        """
        try:
            return self.listConnections(destination=False, **kwargs)[0]
        except IndexError, e:
            return None

    def fullname(self):
        """
        Return the name with the attr name.

        :rtype: str
        """
        if self._fullname is None:
            self._fullname = '{0}.{1}'.format(self.name(), self.attr())
        return self._fullname

    def value(self):
        """
        Return the value of the attribute.

        :rtype: float | str | list
        """
        if self._value is None or not self._cache:

            try:
                self._value = maya.cmds.getAttr(self.fullname())
            except Exception:
                msg = 'Cannot GET attribute VALUE for "{0}"'
                msg = msg.format(self.fullname())
                logger.exception(msg)

        return self._value

    def type(self):
        """
        Return the type of data currently in the attribute.

        :rtype: str
        """
        if self._type is None:

            try:
                self._type = maya.cmds.getAttr(self.fullname(), type=True)
                self._type = self._type.encode('ascii')
            except Exception:
                msg = 'Cannot GET attribute TYPE for "{0}"'
                msg = msg.format(self.fullname())
                logger.exception(msg)

        return self._type

    def set(self, value, blend=100, key=False, clamp=True):
        """
        Set the value for the attribute.

        :type key: bool
        :type clamp: bool
        :type value: float | str | list
        :type blend: float
        """
        try:
            if int(blend) == 0:
                value = self.value()
            else:
                _value = (value - self.value()) * (blend/100.00)
                value = self.value() + _value
        except TypeError, e:
            msg = 'Cannot BLEND attribute {0}: Error: {1}'
            msg = msg.format(self.fullname(), e)
            logger.debug(msg)

        try:
            if self.type() in ["string"]:
                maya.cmds.setAttr(self.fullname(), value, type=self.type())
            elif self.type() in ["list", "matrix"]:
                maya.cmds.setAttr(self.fullname(), *value, type=self.type())
            else:
                maya.cmds.setAttr(self.fullname(), value, clamp=clamp)
        except (ValueError, RuntimeError), e:
            msg = "Cannot SET attribute {0}: Error: {1}"
            msg = msg.format(self.fullname(), e)
            logger.debug(msg)

        try:
            if key:
                self.setKeyframe(value=value)
        except TypeError, e:
            msg = 'Cannot KEY attribute {0}: Error: {1}'
            msg = msg.format(self.fullname(), e)
            logger.debug(msg)

    def setKeyframe(self, value, respectKeyable=True, **kwargs):
        """
        Set a keyframe with the given value.

        :value: object
        :respectKeyable: bool
        :rtype: None
        """
        if self.query(minExists=True):
            minimum = self.query(minimum=True)[0]
            if value < minimum:
                value = minimum

        if self.query(maxExists=True):
            maximum = self.query(maximum=True)[0]
            if value > maximum:
                value = maximum

        kwargs.setdefault("value", value)
        kwargs.setdefault("respectKeyable", respectKeyable)

        maya.cmds.setKeyframe(self.fullname(), **kwargs)

    def setStaticKeyframe(self, value, time, option):
        """
        Set a static keyframe at the given time.

        :type value: object
        :type time: (int, int)
        :type option: PasteOption
        """
        if option == "replaceCompletely":
            maya.cmds.cutKey(self.fullname())
            self.set(value, key=False)

        # This should be changed to only look for animation.
        # Also will need to support animation layers ect...
        elif self.isConnected():

            # TODO: Should also support static attrs when there is animation.
            if option == "replace":
                maya.cmds.cutKey(self.fullname(), time=time)
                self.insertStaticKeyframe(value, time)

            elif option == "replace":
                self.insertStaticKeyframe(value, time)

        else:
            self.set(value, key=False)

    def insertStaticKeyframe(self, value, time):
        """
        Insert a static keyframe at the given time with the given value.

        :type value: float | str
        :type time: (int, int)
        :rtype: None
        """
        startTime, endTime = time
        duration = endTime - startTime
        try:
            # Offset all keyframes from the start position.
            maya.cmds.keyframe(self.fullname(), relative=True, time=(startTime, 1000000), timeChange=duration)

            # Set a key at the given start and end time
            self.setKeyframe(value, time=(startTime, startTime), ott='step')
            self.setKeyframe(value, time=(endTime, endTime), itt='flat', ott='flat')

            # Set the tangent for the next keyframe to flat
            nextFrame = maya.cmds.findKeyframe(self.fullname(), time=(endTime, endTime), which='next')
            maya.cmds.keyTangent(self.fullname(), time=(nextFrame, nextFrame), itt='flat')
        except TypeError, e:
            msg = "Cannot insert static key frame for attribute {0}: Error: {1}"
            msg = msg.format(self.fullname(), e)
            logger.debug(msg)

    def setAnimCurve(self, curve, time, option, source=None, connect=False):
        """
        Set/Paste the give animation curve to this attribute.

        :type curve: str
        :type option: PasteOption
        :type time: (int, int)
        :type source: (int, int)
        :type connect: bool
        :rtype: None
        """
        fullname = self.fullname()
        startTime, endTime = time

        if not self.exists():
            logger.debug("Attr does not exists")
            return

        if self.isLocked():
            logger.debug("Cannot set anim curve when the attr locked")
            return

        if source is None:
            first = maya.cmds.findKeyframe(curve, which='first')
            last = maya.cmds.findKeyframe(curve, which='last')
            source = (first, last)

        # We run the copy key command twice to check we have a valid curve.
        # It needs to run before the cutKey command, otherwise if it fails
        # we have cut keys for no reason!
        success = maya.cmds.copyKey(curve, time=source)
        if not success:
            msg = "Cannot copy keys from the anim curve {0}"
            msg = msg.format(curve)
            logger.debug(msg)
            return

        if option == "replace":
            maya.cmds.cutKey(fullname, time=time)
        else:
            time = (startTime, startTime)

        try:
            # Update the clip board with the give animation curve
            maya.cmds.copyKey(curve, time=source)

            # Note: If the attribute is connected to referenced
            # animation then the following command will not work.
            maya.cmds.pasteKey(fullname, option=option, time=time, connect=connect)

            if option == "replaceCompletely":

                # The pasteKey cmd doesn't support all anim attributes
                # so we need to manually set theses.
                dstCurve = self.animCurve()
                if dstCurve:
                    curveColor = maya.cmds.getAttr(curve + ".curveColor")
                    preInfinity = maya.cmds.getAttr(curve + ".preInfinity")
                    postInfinity = maya.cmds.getAttr(curve + ".postInfinity")
                    useCurveColor = maya.cmds.getAttr(curve + ".useCurveColor")

                    maya.cmds.setAttr(dstCurve + ".preInfinity", preInfinity)
                    maya.cmds.setAttr(dstCurve + ".postInfinity", postInfinity)
                    maya.cmds.setAttr(dstCurve + ".curveColor", *curveColor[0])
                    maya.cmds.setAttr(dstCurve + ".useCurveColor", useCurveColor)

        except RuntimeError:
            msg = 'Cannot paste anim curve "{0}" to attribute "{1}"'
            msg = msg.format(curve, fullname)
            logger.exception(msg)

    def animCurve(self):
        """
        Return the connected animation curve.

        :rtype: str | None
        """
        result = None

        if self.exists():

            n = self.listConnections(plugs=True, destination=False)

            if n and "animCurve" in maya.cmds.nodeType(n):
                result = n

            elif n and "character" in maya.cmds.nodeType(n):
                n = maya.cmds.listConnections(n, plugs=True,
                                              destination=False)
                if n and "animCurve" in maya.cmds.nodeType(n):
                    result = n

            if result:
                return result[0].split(".")[0]

    def isConnected(self, ignoreConnections=None):
        """
        Return true if the attribute is connected.

        :type ignoreConnections: list[str]
        :rtype: bool
        """
        if ignoreConnections is None:
            ignoreConnections = []
        try:
            connection = self.listConnections(destination=False)
        except ValueError:
            return False

        if connection:
            if ignoreConnections:
                connectionType = maya.cmds.nodeType(connection)
                for ignoreType in ignoreConnections:
                    if connectionType.startswith(ignoreType):
                        return False
            return True
        else:
            return False

    def isBlendable(self):
        """
        Return true if the attribute can be blended.

        :rtype: bool
        """
        return self.type() in VALID_BLEND_ATTRIBUTES

    def isSettable(self, validConnections=None):
        """
        Return true if the attribute can be set.

        :type validConnections: list[str]
        :rtype: bool
        """
        if validConnections is None:
            validConnections = VALID_CONNECTIONS

        if not self.exists():
            return False

        if not maya.cmds.listAttr(self.fullname(), unlocked=True, keyable=True, multi=True, scalar=True):
            return False

        connection = self.listConnections(destination=False)
        if connection:
            connectionType = maya.cmds.nodeType(connection)
            for validType in validConnections:
                if connectionType.startswith(validType):
                    return True
            return False
        else:
            return True
