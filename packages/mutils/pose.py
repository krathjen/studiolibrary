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
import mutils

# Example 1:
# Save and load a pose from the selected objects
objects = maya.cmds.ls(selection=True)
mutils.savePose("/tmp/pose.json", objects)

mutils.loadPose("/tmp/pose.json")

# Example 2:
# Create a pose object from a list of object names
pose = mutils.Pose.fromObjects(objects)

# Example 3:
# Create a pose object from the selected objects
objects = maya.cmds.ls(selection=True)
pose = mutils.Pose.fromObjects(objects)

# Example 4:
# Save the pose object to disc
path = "/tmp/pose.json"
pose.save(path)

# Example 5:
# Create a pose object from disc
path = "/tmp/pose.json"
pose = mutils.Pose.fromPath(path)

# Load the pose on to the objects from file
pose.load()

# Load the pose to the selected objects
objects = maya.cmds.ls(selection=True)
pose.load(objects=objects)

# Load the pose to the specified namespaces
pose.load(namespaces=["character1", "character2"])

# Load the pose to the specified objects
pose.load(objects=["Character1:Hand_L", "Character1:Finger_L"])

"""
import logging

import mutils

try:
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()


__all__ = ["Pose", "savePose", "loadPose"]

logger = logging.getLogger(__name__)

_pose_ = None


def savePose(path, objects, metadata=None):
    """
    Convenience function for saving a pose to disc for the given objects.

    Example:
        path = "C:/example.pose"
        pose = savePose(path, metadata={'description': 'Example pose'})
        print pose.metadata()
        # {
        'user': 'Hovel', 
        'mayaVersion': '2016', 
        'description': 'Example pose'
        }

    :type path: str
    :type objects: list[str]
    :type metadata: dict or None
    :rtype: Pose
    """
    pose = mutils.Pose.fromObjects(objects)

    if metadata:
        pose.updateMetadata(metadata)

    pose.save(path)

    return pose


def loadPose(path, *args, **kwargs):
    """
    Convenience function for loading the given pose path.
    
    :type path: str
    :type args: list
    :type kwargs: dict 
    :rtype: Pose 
    """
    global _pose_

    clearCache = kwargs.get("clearCache")

    if not _pose_ or _pose_.path() != path or clearCache:
        _pose_ = Pose.fromPath(path)

    _pose_.load(*args, **kwargs)

    return _pose_


class Pose(mutils.TransferObject):

    def __init__(self):
        mutils.TransferObject.__init__(self)

        self._cache = None
        self._mtime = None
        self._cacheKey = None
        self._isLoading = False
        self._selection = None
        self._mirrorTable = None
        self._autoKeyFrame = None

    def createObjectData(self, name):
        """
        Create the object data for the given object name.
        
        :type name: str
        :rtype: dict
        """
        attrs = maya.cmds.listAttr(name, unlocked=True, keyable=True) or []
        attrs = list(set(attrs))
        attrs = [mutils.Attribute(name, attr) for attr in attrs]

        data = {"attrs": self.attrs(name)}

        for attr in attrs:
            if attr.isValid():
                if attr.value() is None:
                    msg = "Cannot save the attribute %s with value None."
                    logger.warning(msg, attr.fullname())
                else:
                    data["attrs"][attr.attr()] = {
                        "type": attr.type(),
                        "value": attr.value()
                    }

        return data

    def select(self, objects=None, namespaces=None, **kwargs):
        """
        Select the objects contained in the pose file.
        
        :type objects: list[str] or None
        :type namespaces: list[str] or None
        :rtype: None
        """
        selectionSet = mutils.SelectionSet.fromPath(self.path())
        selectionSet.load(objects=objects, namespaces=namespaces, **kwargs)

    def cache(self):
        """
        Return the current cached attributes for the pose.
        
        :rtype: list[(Attribute, Attribute)]
        """
        return self._cache

    def attrs(self, name):
        """
        Return the attribute for the given name.
        
        :type name: str
        :rtype: dict
        """
        return self.object(name).get("attrs", {})

    def attr(self, name, attr):
        """
        Return the attribute data for the given name and attribute.

        :type name: str
        :type attr: str
        :rtype: dict
        """
        return self.attrs(name).get(attr, {})

    def attrType(self, name, attr):
        """
        Return the attribute type for the given name and attribute.
        
        :type name: str
        :type attr: str
        :rtype: str
        """
        return self.attr(name, attr).get("type", None)

    def attrValue(self, name, attr):
        """
        Return the attribute value for the given name and attribute.
        
        :type name: str
        :type attr: str
        :rtype: str | int | float
        """
        return self.attr(name, attr).get("value", None)

    def setMirrorAxis(self, name, mirrorAxis):
        """
        Set the mirror axis for the given name.
        
        :type name: str
        :type mirrorAxis: list[int]
        """
        if name in self.objects():
            self.object(name).setdefault("mirrorAxis", mirrorAxis)
        else:
            msg = "Object does not exist in pose. " \
                  "Cannot set mirror axis for %s"

            logger.debug(msg, name)

    def mirrorAxis(self, name):
        """
        Return the mirror axis for the given name.
        
        :rtype: list[int] | None
        """
        result = None
        if name in self.objects():
            result = self.object(name).get("mirrorAxis", None)

        if result is None:
            logger.debug("Cannot find mirror axis in pose for %s", name)

        return result

    def updateMirrorAxis(self, name, mirrorAxis):
        """
        Update the mirror axis for the given object name.
        
        :type name: str
        :type mirrorAxis: list[int]
        """
        self.setMirrorAxis(name, mirrorAxis)

    def mirrorTable(self):
        """
        Return the Mirror Table for the pose.
        
        :rtype: mutils.MirrorTable
        """
        return self._mirrorTable

    def setMirrorTable(self, mirrorTable):
        """
        Set the Mirror Table for the pose.
        
        :type mirrorTable: mutils.MirrorTable
        """
        objects = self.objects().keys()
        self._mirrorTable = mirrorTable

        for srcName, dstName, mirrorAxis in mirrorTable.matchObjects(objects):
            self.updateMirrorAxis(dstName, mirrorAxis)

    def mirrorValue(self, name, attr, mirrorAxis):
        """
        Return the mirror value for the given name, attribute and mirror axis.
        
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
                logger.debug("Cannot find mirror value for %s.%s", name, attr)

        return value

    def beforeLoad(self, clearSelection=True):
        """
        Called before loading the pose.
        
        :type clearSelection: bool
        """
        logger.debug('Before Load "%s"', self.path())

        if not self._isLoading:
            self._isLoading = True
            maya.cmds.undoInfo(openChunk=True)

            self._selection = maya.cmds.ls(selection=True) or []
            self._autoKeyFrame = maya.cmds.autoKeyframe(query=True, state=True)

            maya.cmds.autoKeyframe(edit=True, state=False)
            maya.cmds.select(clear=clearSelection)

    def afterLoad(self):
        """Called after loading the pose."""
        if not self._isLoading:
            return

        logger.debug("After Load '%s'", self.path())

        self._isLoading = False
        if self._selection:
            maya.cmds.select(self._selection)
            self._selection = None

        maya.cmds.autoKeyframe(edit=True, state=self._autoKeyFrame)
        maya.cmds.undoInfo(closeChunk=True)

        logger.debug('Loaded "%s"', self.path())

    @mutils.timing
    def load(
            self,
            objects=None,
            namespaces=None,
            attrs=None,
            blend=100,
            key=False,
            mirror=False,
            refresh=False,
            batchMode=False,
            clearCache=False,
            mirrorTable=None,
            onlyConnected=False,
            clearSelection=False,
            ignoreConnected=False,
            search=None,
            replace=None,
    ):
        """
        Load the pose to the given objects or namespaces.
        
        :type objects: list[str]
        :type namespaces: list[str]
        :type attrs: list[str]
        :type blend: float
        :type key: bool
        :type refresh: bool
        :type mirror: bool
        :type mirrorTable: mutils.MirrorTable
        :type batchMode: bool
        :type clearCache: bool
        :type ignoreConnected: bool
        :type onlyConnected: bool
        :type clearSelection: bool
        :type search: str or None
        :type replace: str or None
        """
        if mirror and not mirrorTable:
            logger.warning("Cannot mirror pose without a mirror table!")
            mirror = False

        if batchMode:
            key = False

        self.updateCache(
            objects=objects,
            namespaces=namespaces,
            attrs=attrs,
            batchMode=batchMode,
            clearCache=clearCache,
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

    def updateCache(
            self,
            objects=None,
            namespaces=None,
            attrs=None,
            ignoreConnected=False,
            onlyConnected=False,
            mirrorTable=None,
            search=None,
            replace=None,
            batchMode=False,
            clearCache=True
    ):
        """
        Update the pose cache.
        
        :type objects: list[str] or None 
        :type namespaces: list[str] or None
        :type attrs: list[str] or None
        :type ignoreConnected: bool
        :type onlyConnected: bool
        :type clearCache: bool
        :type batchMode: bool
        :type mirrorTable: mutils.MirrorTable
        :type search: str or None
        :type replace: str or None
        """
        if clearCache or not batchMode or not self._mtime:
            self._mtime = self.mtime()

        mtime = self._mtime

        cacheKey = \
            str(mtime) + \
            str(objects) + \
            str(attrs) + \
            str(namespaces) + \
            str(ignoreConnected) + \
            str(maya.cmds.currentTime(query=True))

        if self._cacheKey != cacheKey or clearCache:
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
                    attrs=attrs,
                    onlyConnected=onlyConnected,
                    ignoreConnected=ignoreConnected,
                    usingNamespaces=usingNamespaces,
                )

        if not self.cache():
            text = "No objects match when loading data. " \
                   "Turn on debug mode to see more details."

            raise mutils.NoMatchFoundError(text)

    def cacheNode(
            self,
            srcNode,
            dstNode,
            attrs=None,
            ignoreConnected=None,
            onlyConnected=None,
            usingNamespaces=None
    ):
        """
        Cache the given pair of nodes.
        
        :type srcNode: mutils.Node
        :type dstNode: mutils.Node
        :type attrs: list[str] or None 
        :type ignoreConnected: bool or None
        :type onlyConnected: bool or None
        :type usingNamespaces: none or list[str]
        """
        mirrorAxis = None
        mirrorObject = None

        # Remove the first pipe in-case the object has a parent
        dstNode.stripFirstPipe()

        srcName = srcNode.name()

        if self.mirrorTable():
            mirrorObject = self.mirrorTable().mirrorObject(srcName)

            if not mirrorObject:
                mirrorObject = srcName
                msg = "Cannot find mirror object in pose for %s"
                logger.debug(msg, srcName)

            # Check if a mirror axis exists for the mirrorObject otherwise
            # check the srcNode
            mirrorAxis = self.mirrorAxis(mirrorObject) or self.mirrorAxis(srcName)

            if mirrorObject and not maya.cmds.objExists(mirrorObject):
                msg = "Mirror object does not exist in the scene %s"
                logger.debug(msg, mirrorObject)

        if usingNamespaces:
            # Try and use the short name.
            # Much faster than the long name when setting attributes.
            try:
                dstNode = dstNode.toShortName()
            except mutils.NoObjectFoundError as msg:
                logger.debug(msg)
                return
            except mutils.MoreThanOneObjectFoundError as msg:
                logger.debug(msg)
                return

        for attr in self.attrs(srcName):

            if attrs and attr not in attrs:
                continue

            dstAttribute = mutils.Attribute(dstNode.name(), attr)
            isConnected = dstAttribute.isConnected()

            if (ignoreConnected and isConnected) or (onlyConnected and not isConnected):
                continue

            type_ = self.attrType(srcName, attr)
            value = self.attrValue(srcName, attr)
            srcMirrorValue = self.mirrorValue(mirrorObject, attr, mirrorAxis=mirrorAxis)

            srcAttribute = mutils.Attribute(dstNode.name(), attr, value=value, type=type_)
            dstAttribute.update()

            self._cache.append((srcAttribute, dstAttribute, srcMirrorValue))

    def loadCache(self, blend=100, key=False, mirror=False):
        """
        Load the pose from the current cache.
        
        :type blend: float
        :type key: bool
        :type mirror: bool
        :rtype: None
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
                    logger.debug('Ignoring %s', dstAttribute.fullname())
