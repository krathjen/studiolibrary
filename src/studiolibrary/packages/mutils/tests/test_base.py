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
import math
import mutils
import unittest
import maya.cmds


TEST_DATA_DIR = os.path.join(os.path.dirname(mutils.__file__), "tests", "data")


class TestBase(unittest.TestCase):

    def __init__(self, *args):
        """
        @param args:
        """
        unittest.TestCase.__init__(self, *args)

        self.srcPath = os.path.join(TEST_DATA_DIR, "test_pose.ma")
        self.dstPath = os.path.join(TEST_DATA_DIR, "test_pose.pose")

        self.srcObjects = ["srcSphere:lockedNode", "srcSphere:offset", "srcSphere:sphere"]
        self.dstObjects = ["dstSphere:lockedNode", "dstSphere:offset", "dstSphere:sphere"]

        self.srcNamespaces = ["srcSphere"]
        self.dstNamespaces = ["dstSphere"]

    def dataDir(self):
        return os.path.join(os.path.dirname(mutils.__file__), "tests", "data")

    def open(self, path=None):
        """
        """
        if path is None:
            path = self.srcPath
        maya.cmds.file(self.srcPath, open=True, force=True, executeScriptNodes=False, ignoreVersion=True)

    def listAttr(self, srcObjects=None, dstObjects=None):
        """
        :rtype: list[mutils.Attribute]
        """
        results = []
        srcObjects = srcObjects or self.srcObjects
        dstObjects = dstObjects or self.dstObjects

        for i, srcObj in enumerate(srcObjects):
            srcObj = srcObjects[i]
            dstObj = dstObjects[i]

            for srcAttr in maya.cmds.listAttr(srcObj, k=True, unlocked=True, scalar=True) or []:
                srcAttribute = mutils.Attribute(srcObj, srcAttr)
                dstAttribute = mutils.Attribute(dstObj, srcAttr)
                results.append((srcAttribute, dstAttribute))
        return results
