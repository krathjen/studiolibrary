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
import unittest

import maya.cmds

import mutils


TEST_DATA_DIR = os.path.join(os.path.dirname(mutils.__file__), "tests", "data")


class TestBase(unittest.TestCase):

    def __init__(self, *args):
        """
        :type args: list
        """
        unittest.TestCase.__init__(self, *args)

        self.srcPath = os.path.join(TEST_DATA_DIR, "test_pose.ma")
        self.dstPath = os.path.join(TEST_DATA_DIR, "test_pose.pose")

        self.srcObjects = [
            "srcSphere:lockedNode",
            "srcSphere:offset",
            "srcSphere:sphere",
        ]

        self.dstObjects = [
            "dstSphere:lockedNode",
            "dstSphere:offset",
            "dstSphere:sphere",
        ]

        self.srcNamespaces = ["srcSphere"]
        self.dstNamespaces = ["dstSphere"]

    def dataDir(self):
        """
        Return the location on disc to the test data.

        :rtype: str
        """
        return os.path.join(os.path.dirname(mutils.__file__), "tests", "data")

    def dataPath(self, fileName):
        """
        Return data location with the given fileName.

        :rtype: str
        """
        return os.path.join(self.dataDir(), fileName)

    def open(self, path=None):
        """
        Open the specified file in Maya.

        :type path: str | None
        """
        if path is None:
            path = self.srcPath

        maya.cmds.file(
            path,
            open=True,
            force=True,
            ignoreVersion=True,
            executeScriptNodes=False,
        )

    def listAttr(self, srcObjects=None, dstObjects=None):
        """
        Return the source & destination attributes for the given objects.

        :rtype: list[(mutils.Attribute, mutils.Attribute)]
        """
        attrs = []
        srcObjects = srcObjects or self.srcObjects
        dstObjects = dstObjects or self.dstObjects

        for i, srcObj in enumerate(srcObjects):
            srcObj = srcObjects[i]
            dstObj = dstObjects[i]

            srcAttrs = maya.cmds.listAttr(srcObj, keyable=True, unlocked=True, scalar=True) or []

            for srcAttr in srcAttrs:
                srcAttribute = mutils.Attribute(srcObj, srcAttr)
                dstAttribute = mutils.Attribute(dstObj, srcAttr)
                attrs.append((srcAttribute, dstAttribute))

        return attrs

    def assertEqualAnimation(
        self,
        srcObjects=None,
        dstObjects=None,
    ):
        """
        Test that the animation for the given objects is equal.

        If the animation curves do not compare equal, the test will fail.

        :type srcObjects: list[str] | None
        :type dstObjects: list[str] | None
        """
        for frame in [1, 10, 24]:
            maya.cmds.currentTime(frame)
            self.assertEqualAttributeValues(srcObjects, dstObjects)

    def assertEqualAttributeValues(
        self,
        srcObjects=None,
        dstObjects=None,
    ):
        """
        Test that the attribute values for the given objects are equal.

        If the values do not compare equal, the test will fail.

        :type srcObjects: list[str] | None
        :type dstObjects: list[str] | None
        """
        for srcAttribute, dstAttribute in self.listAttr(srcObjects, dstObjects):

            if not dstAttribute.exists():
                continue

            msg = "Attribute value is not equal! {0} != {1}"
            msg = msg.format(srcAttribute.fullname(), dstAttribute.fullname())
            self.assertEqual(srcAttribute.value(), dstAttribute.value(), msg)
