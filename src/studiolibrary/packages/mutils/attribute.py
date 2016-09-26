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

import logging

try:
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()


logger = logging.getLogger(__name__)


class Attribute(object):

    def __init__(self, name, attr, value=None, type=None):
        """
        :type name: str
        """
        try:
            self._name = name.encode('ascii')
            self._attr = attr.encode('ascii')
        except UnicodeEncodeError:
            raise UnicodeEncodeError('Not a valid ascii name "%s.%s"' % (name, attr))

        self._type = type
        self._value = value
        self._fullname = None

    def name(self):
        """
        :rtype: str
        """
        return self._name

    def attr(self):
        """
        :rtype: str
        """
        return self._attr

    def update(self):
        """
        """
        self._type = None
        self._value = None

    def fullname(self):
        """
        :rtype: str
        """
        if self._fullname is None:
            self._fullname = "%s.%s" % (self.name(), self.attr())
        return self._fullname

    def value(self):
        """
        :rtype: float | str | list[]
        """
        if self._value is None:
            try:
                self._value = maya.cmds.getAttr(self.fullname())
            except Exception:
                logger.exception("Cannot GET attribute VALUE for {0}:".format(self.fullname()))
        return self._value

    def type(self):
        """
        :rtype: str
        """
        if self._type is None:
            try:
                self._type = maya.cmds.getAttr(self.fullname(), type=True)
                self._type = self._type.encode('ascii')
            except Exception:
                logger.exception("Cannot GET attribute TYPE for %s: {0}:".format(self.fullname()))
        return self._type

    def set(self, value, blend=100, key=False, **kwargs):
        """
        :type value: float | str | list[]
        :type blend: float
        """
        try:
            if int(blend) == 0:
                value = self.value()
            else:
                _value = (value - self.value()) * (blend/100.00)
                value = self.value() + _value
        except TypeError, msg:
            logger.debug("Cannot BLEND attribute %s: Error: %s" % (self.fullname(), msg))

        try:
            if self.type() in ["string"]:
                maya.cmds.setAttr(self.fullname(), value, type=self.type())
            elif self.type() in ["list", "matrix"]:
                maya.cmds.setAttr(self.fullname(), *value, type=self.type())
            else:
                maya.cmds.setAttr(self.fullname(), value)

            if key:
                try:
                    self.key(value=value, **kwargs)
                except TypeError, msg:
                    logger.debug("Cannot KEY attribute %s: Error: %s" % (self.fullname(), msg))
        except (ValueError, RuntimeError), msg:
            logger.debug("Cannot SET attribute %s: Error: %s" % (self.fullname(), msg))

    def key(self, value, **kwargs):
        """
        """
        if kwargs:
            maya.cmds.setKeyframe(self.fullname(), value=value, **kwargs)
        else:
            maya.cmds.setKeyframe(self.fullname(), value=value)

    def insertStaticKeyframe(self, value, time):
        """
        :type value: float | str
        :type time: (int, int)
        """
        startTime, endTime = time
        duration = endTime - startTime
        try:
            maya.cmds.keyframe(self.fullname(), relative=True, time=(startTime, 100000), timeChange=duration)
            maya.cmds.setKeyframe(self.fullname(), value=value, time=(startTime, startTime), ott='step')
            maya.cmds.setKeyframe(self.fullname(), value=value, time=(endTime, endTime), itt='flat', ott='flat')
            nextFrame = maya.cmds.findKeyframe(self.fullname(), time=(endTime, endTime), which='next')
            maya.cmds.keyTangent(self.fullname(), time=(nextFrame, nextFrame), itt='flat')
        except TypeError, msg:
            logger.debug("Cannot insert static key frame for attribute %s: Error: %s" % (self.fullname(), msg))

    def animCurve(self):
        try:
            return maya.cmds.listConnections(self.fullname(), destination=False,
                                             type="animCurve")[0]
        except IndexError, e:
            return None

    def isConnected(self, ignoreConnections=None):
        """
        :type ignoreConnections: list[str]
        :rtype: bool
        """
        if ignoreConnections is None:
            ignoreConnections = []
        try:
            connection = maya.cmds.listConnections(self.fullname(),
                                                   destination=False)
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
        :rtype: bool
        """
        return self.type() in ["float", "doubleLinear", "doubleAngle",
                               "double", "long", "int", "short"]

    def isSettable(self, validConnections=None):
        """
        :type validConnections: list[str]
        :rtype: bool
        """
        if validConnections is None:
            validConnections = ["animCurve", "animBlend", "pairBlend", "character"]

        if not self.exists():
            return False

        if not maya.cmds.listAttr(self.fullname(), unlocked=True, keyable=True, multi=True, scalar=True):
            return False

        connection = maya.cmds.listConnections(self.fullname(), destination=False)
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
        :rtype: bool
        """
        return maya.cmds.getAttr(self.fullname(), lock=True)

    def isUnlocked(self):
        """
        :rtype: bool
        """
        return not self.isLocked()

    def toDict(self):
        """
        :rtype: dict[]
        """
        result = {"type": self.type(), "value": self.value(), "fullname": self.fullname()}
        return result

    def isValid(self):
        """
        :rtype: bool
        """
        return self.type() in ["string", "enum", "bool", "float", "doubleLinear",
                               "doubleAngle", "double", "long", "int", "short"]

    def __str__(self):
        """
        :rtype: str
        """
        return str(self.toDict())

    def exists(self):
        """
        :rtype: bool
        """
        return maya.cmds.objExists(self.fullname())

    def prettyPrint(self):
        """
        """
        print('maya.cmds.setAttr("%s", %s)' % (self.fullname(), self.value()))