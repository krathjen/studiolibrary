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
# pose.py
import pose

# Example 1:
# Create pose from objects
p = mutils.Pose.fromObjects(objects)

# Example 2:
# Create from selected objects
objects = maya.cmds.ls(selection=True)
p = mutils.Pose.fromObjects(objects)

# Example 3:
# Save to file
path = "/tmp/pose.json"
p.save(path)

# Example 4:
# Load from file
path = "/tmp/pose.json"
p = mutils.Pose.fromPath(path)

# load to objects from file
p.load()

# load to selected objects
objects = maya.cmds.ls(selection=True)
p.load(objects=objects)

# load to namespaces
p.load(namespaces=["character1", "character2"])

# load to specified objects
p.load(objects=["Character1:Hand_L", "Character1:Finger_L"])

"""
import shutil
import mutils
import logging

try:
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()


__all__ = ["Pose"]

logger = logging.getLogger(__name__)


def savePose(path, objects=None, iconPath=None, metadata=None):
    """
    Save the pose data for the given objects.

    Example:
        path = "C:/example.pose"
        pose = savePose(path, metadata={'description': 'Example pose'})
        print pose.metadata()
        # {'description': 'Example pose', 'user': 'Hovel', 'mayaVersion': u'2016'}

    :type path: str
    :type objects: list[str]
    :rtype: mutils.Pose
    """
    objects = objects or maya.cmds.ls(selection=True) or []

    if not objects:
        raise Exception(
            "No objects selected. Please select at least one object."
        )

    posePath = path + "/pose.json"
    iconPath_ = path + "/thumbnail.jpg"

    if iconPath:
        shutil.move(iconPath, iconPath_)
    else:
        mutils.createSnapshot(iconPath_)

    pose = mutils.Pose.fromObjects(objects)

    if metadata:
        pose.updateMetadata(metadata)

    pose.save(posePath)
    return pose


class Pose(mutils.SelectionSet):

    def __init__(self):
        """
        """
        mutils.SelectionSet.__init__(self)
        self._cache = None
        self._cacheKey = None
        self._isLoading = False
        self._selection = None
        self._mirrorTable = None
        self._autoKeyFrame = None

    def cache(self):
        """
        :rtype: list[(Attribute, Attribute)]
        """
        return self._cache

    def createObjectData(self, name):
        """
        :type name: name
        :rtype: list[Attribute]
        """
        attrs = maya.cmds.listAttr(name, unlocked=True, keyable=True) or []
        attrs = list(set(attrs))
        attrs = [mutils.Attribute(name, attr) for attr in attrs]
        result = {"attrs": self.attrs(name)}

        for attr in attrs:
            if attr.isValid():
                if attr.value() is None:
                    logger.warning("Cannot save the attribute %s with value None." % attr.fullname())
                else:
                    result["attrs"][attr.attr()] = {"type": attr.type(), "value": attr.value()}

        return result

    def attrs(self, name):
        """
        :type name: str
        :rtype: dict
        """
        return self.object(name).get("attrs", {})

    def attr(self, name, attr):
        """
        :type name: str
        :rtype: dict
        """
        return self.attrs(name).get(attr, {})

    def attrType(self, name, attr):
        """
        :type name: str
        :type attr: str
        :rtype: str
        """
        return self.attr(name, attr).get("type", None)

    def attrValue(self, name, attr):
        """
        :type name: str
        :type attr: str
        :rtype: str | int | float
        """
        return self.attr(name, attr).get("value", None)

    def beforeLoad(self, clearSelection=True):
        """
        :type clearSelection: bool
        """
        logger.debug("Open Load '%s'" % self.path())

        if not self._isLoading:

            self._isLoading = True
            maya.cmds.undoInfo(openChunk=True)

            self._selection = maya.cmds.ls(selection=True) or []
            self._autoKeyFrame = maya.cmds.autoKeyframe(query=True, state=True)

            maya.cmds.autoKeyframe(edit=True, state=False)
            maya.cmds.select(clear=clearSelection)

    def afterLoad(self):
        """
        :rtype: None
        """
        if not self._isLoading:
            return

        self._isLoading = False
        if self._selection:
            maya.cmds.select(self._selection)
            self._selection = None

        maya.cmds.autoKeyframe(edit=True, state=self._autoKeyFrame)
        maya.cmds.undoInfo(closeChunk=True)

        logger.debug("Close Load '%s'" % self.path())

    @mutils.timing
    def load(
        self,
        objects=None,
        namespaces=None,
        attrs=None,
        blend=100,
        key=False,
        cache=True,
        mirror=False,
        refresh=False,
        batchMode=False,
        mirrorTable=None,
        onlyConnected=False,
        clearSelection=False,
        ignoreConnected=False,
        search=None,
        replace=None,
    ):
        """
        :type objects: list[str]
        :type namespaces: list[str]
        :type attrs: list[str]
        :type blend: float
        :type key: bool
        :type refresh: bool
        :type mirrorTable: mutils.MirrorTable
        """
        if mirror and not mirrorTable:
            logger.warning("Cannot mirror pose without a mirror table!")
            mirror = False

        if batchMode:
            key = False

        self.updateCache(
            objects=objects,
            namespaces=namespaces,
            cache=cache,
            dstAttrs=attrs,
            mirrorTable=mirrorTable,
            onlyConnected=onlyConnected,
            ignoreConnected=ignoreConnected,
            search=search,
            replace=replace,
        )

        self.beforeLoad(clearSelection=clearSelection)

        try:
            self.loadCache(blend=blend, key=key, mirror=mirror)
        finally:
            if not batchMode:
                self.afterLoad()

                # Return the focus to the Maya window
                maya.cmds.setFocus("MayaWindow")

        if refresh:
            maya.cmds.refresh(cv=True)

    def updateCache(self, objects=None, namespaces=None, dstAttrs=None, ignoreConnected=False,
                    onlyConnected=False, cache=True, mirrorTable=None, search=None, replace=None):
        """
        :type objects: list[str]
        :type namespaces: list[str]
        :type dstAttrs: list[str]
        """
        cacheKey = str(objects) + str(namespaces) + str(dstAttrs) + \
                   str(ignoreConnected) + str(maya.cmds.currentTime(query=True))

        if self._cacheKey != cacheKey or not cache:
            self._cache = []
            self._cacheKey = cacheKey

            dstObjects = objects
            srcObjects = self.objects()
            usingNamespaces = not objects and namespaces

            if mirrorTable:
                self.setMirrorTable(mirrorTable)

            matches = mutils.matchNames(
                srcObjects,
                dstObjects=dstObjects,
                dstNamespaces=namespaces,
                search=search,
                replace=replace,
            )

            for srcNode, dstNode in matches:

                self.cacheNode(
                    srcNode,
                    dstNode,
                    dstAttrs=dstAttrs,
                    onlyConnected=onlyConnected,
                    ignoreConnected=ignoreConnected,
                    usingNamespaces=usingNamespaces,
                )

        if not self.cache():
            text = "No objects match when loading data. " \
                   "Turn on debug mode to see more details."

            raise mutils.NoMatchFoundError(text)

    def setMirrorAxis(self, name, mirrorAxis):
        """
        :type name: str
        :type mirrorAxis: list[int]
        """
        if name in self.objects():
            self.object(name).setdefault("mirrorAxis", mirrorAxis)
        else:
            logger.debug("Object does not exist in pose. Cannot set mirror axis for %s" % name)

    def mirrorAxis(self, name):
        """
        :rtype: list[int] | None
        """
        result = None
        if name in self.objects():
            result = self.object(name).get("mirrorAxis", None)

        if result is None:
            logger.debug("Cannot find mirror axis in pose for %s" % name)
        return result

    def mirrorTable(self):
        """
        :rtype: mutils.MirrorTable
        """
        return self._mirrorTable

    def setMirrorTable(self, mirrorTable):
        """
        :type mirrorTable: mutils.MirrorTable
        """
        self._mirrorTable = mirrorTable
        mirrorTable.matchObjects(objects=self.objects().keys(), callback=self.updateMirrorAxis)

    def updateMirrorAxis(self, srcNode, dstNode, mirrorAxis):
        """
        :type srcNode: mutils.Node
        :type dstNode: mutils.Node
        :type mirrorAxis: list[int]
        """
        self.setMirrorAxis(dstNode, mirrorAxis)

    def cacheNode(self, srcNode, dstNode, dstAttrs=None, ignoreConnected=None, onlyConnected=None, usingNamespaces=None):
        """
        :type srcNode: mutils.Node
        :type dstNode: mutils.Node
        """
        mirrorAxis = None
        mirrorObject = None

        # Remove the first pipe in-case the object has a parent
        dstNode.stripFirstPipe()

        if self.mirrorTable():
            mirrorObject = self.mirrorTable().mirrorObject(srcNode.name())
            if not mirrorObject:
                mirrorObject = srcNode.name()
                logger.debug("Cannot find mirror object in pose for %s" % srcNode.name())

            # Check if a mirror axis exists for the mirrorObject otherwise check the srcNode
            mirrorAxis = self.mirrorAxis(mirrorObject) or self.mirrorAxis(srcNode.name())
            if mirrorObject and not maya.cmds.objExists(mirrorObject):
                logger.debug("Mirror object does not exist in the scene %s" % mirrorObject)

        if usingNamespaces:
             # Try to get the short name. Much faster than the long name when setting attributes.
            try:
                dstNode = dstNode.toShortName()
            except mutils.NoObjectFoundError, msg:
                logger.debug(msg)
                return
            except mutils.MoreThanOneObjectFoundError, msg:
                logger.debug(msg)
                return

        for attr in self.attrs(srcNode.name()):

            if dstAttrs and attr not in dstAttrs:
                continue

            dstAttribute = mutils.Attribute(dstNode.name(), attr)
            isConnected = dstAttribute.isConnected()
            if (ignoreConnected and isConnected) or (onlyConnected and not isConnected):
                continue

            type_ = self.attrType(srcNode.name(), attr)
            value = self.attrValue(srcNode.name(), attr)
            srcMirrorValue = self.attrMirrorValue(mirrorObject, attr, mirrorAxis=mirrorAxis)

            srcAttribute = mutils.Attribute(dstNode.name(), attr, value=value, type=type_)
            dstAttribute.update()

            self._cache.append((srcAttribute, dstAttribute, srcMirrorValue))

    def attrMirrorValue(self, name, attr, mirrorAxis):
        """
        :type name: str
        :type attr: str
        :type mirrorAxis: list[]
        :rtype: None | int | float
        """
        value = None
        if self.mirrorTable() and name:
            value = self.attrValue(name, attr)
            if value is not None:
                value = self.mirrorTable().formatValue(attr, value, mirrorAxis)
            else:
                logger.debug("cannot find mirror value for %s.%s" % (name, attr))
        return value

    def loadCache(self, blend=100, key=False, mirror=False):
        """
        :type blend: float
        :type key: bool
        """
        cache = self.cache()
        for i in range(0, len(cache)):
            srcAttribute, dstAttribute, srcMirrorValue = cache[i]
            if srcAttribute and dstAttribute:
                if mirror and srcMirrorValue is not None:
                    value = srcMirrorValue
                else:
                    value = srcAttribute.value()
                try:
                    dstAttribute.set(value, blend=blend, key=key)
                except (ValueError, RuntimeError):
                    cache[i] = (None, None)
                    logger.debug("Ignoring %s." % dstAttribute.fullname())
