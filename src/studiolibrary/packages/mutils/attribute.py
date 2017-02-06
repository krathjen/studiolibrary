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

    def __init__(self, name, attr, value=None, type=None):
        """
        :type name: str
        """
        try:
            self._name = name.encode('ascii')
            self._attr = attr.encode('ascii')
        except UnicodeEncodeError:
            msg = 'Not a valid ascii name "{0}.{1}"'.format(name, attr)
            raise UnicodeEncodeError(msg)

        self._type = type
        self._value = value
        self._fullname = None

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

    def update(self):
        """
        Make attribute dirty
        """
        self._type = None
        self._value = None

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
        if self._value is None:

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

    def animCurve(self):
        """
        Return the connected animCurve.

        :rtype: str | None
        """
        try:
            return self.listConnections(destination=False, type="animCurve")[0]
        except IndexError, e:
            return None

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

    def __str__(self):
        """
        :rtype: str
        """
        return str(self.toDict())

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
