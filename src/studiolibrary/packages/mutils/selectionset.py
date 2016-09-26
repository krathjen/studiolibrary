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