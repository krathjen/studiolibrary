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
import logging

import mutils

try:
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()


logger = logging.getLogger(__name__)


class SelectionSet(mutils.TransferBase):

    def __init__(self):
        mutils.TransferBase.__init__(self)
        self._namespaces = None

    def namespaces(self):
        """
        :rtype: list[str]
        """
        if self._namespaces is None:
            group = mutils.groupObjects(self.objects())
            self._namespaces = group.keys()

        return self._namespaces

    def iconPath(self):
        """
        Return the icon path for this transfer object.

        :rtype: str
        """
        return os.path.dirname(self.path()) + "/thumbnail.jpg"

    def setPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        if path.endswith(".set"):
            path += "/set.json"

        mutils.TransferBase.setPath(self, path)

    def load(self, objects=None, namespaces=None, **kwargs):
        """
        :type objects:
        :type namespaces: list[str]
        :type kwargs:
        """
        validNodes = []
        dstObjects = objects
        srcObjects = self.objects()

        matches = mutils.matchNames(
                srcObjects,
                dstObjects=dstObjects,
                dstNamespaces=namespaces
        )

        for srcNode, dstNode in matches:
            # Support for wild cards eg: ['*_control'].
            if "*" in dstNode.name():
                validNodes.append(dstNode.name())
            else:
                # Remove the first pipe in-case the object has a parent.
                dstNode.stripFirstPipe()

                # Try to get the short name. Much faster than the long
                # name when selecting objects.
                try:
                    dstNode = dstNode.toShortName()

                except mutils.NoObjectFoundError, msg:
                    logger.debug(msg)
                    continue

                except mutils.MoreThanOneObjectFoundError, msg:
                    logger.debug(msg)

                validNodes.append(dstNode.name())

        if validNodes:
            maya.cmds.select(validNodes, **kwargs)
        else:
            raise mutils.NoMatchFoundError("No objects match when loading data")

    def select(self, objects=None, namespaces=None, **kwargs):
        """
        :type objects:
        :type namespaces: list[str]
        :type kwargs:
        """
        SelectionSet.load(self, objects=objects, namespaces=namespaces, **kwargs)

    @mutils.showWaitCursor
    def save(self,  *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        self.setMetadata("mayaVersion", maya.cmds.about(v=True))
        self.setMetadata("mayaSceneFile", maya.cmds.file(q=True, sn=True))
        mutils.TransferBase.save(self, *args, **kwargs)