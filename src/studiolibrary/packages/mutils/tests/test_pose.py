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
# Example:
import mutils.tests.test_pose
reload(mutils.tests.test_pose)
mutils.tests.test_pose.run()
"""
import unittest

import maya.cmds

import mutils
import test_base


class TestPose(test_base.TestBase):

    def setUp(self):
        """
        """
        self.srcPath = self.dataPath("test_pose.ma")
        self.dstPath = self.dataPath("test_pose.pose")

    def test_save(self):
        """
        Test saving a pose to disc.
        """
        self.open()
        pose = mutils.Pose.fromObjects(self.srcObjects)
        pose.save(self.dstPath)

    def test_load(self):
        """
        Test load the pose from disc.
        """
        self.open()
        pose = mutils.Pose.fromPath(self.dstPath)
        pose.load(self.dstObjects)
        self.assertEqualAttributeValues()

    def test_older_version(self):
        """
        Test parsing an older pose format
        """
        srcPath = self.dataPath("test_older_version.dict")
        dstPath = self.dataPath("test_older_version.json")

        pose = mutils.Pose.fromPath(srcPath)
        print pose.objects()

    def test_non_unique_names(self):
        """
        Test loading a pose to objects that do not have unique names.
        """
        srcPath = self.dataPath("test_non_unique_names.ma")
        dstPath = self.dataPath("test_non_unique_names.pose")

        srcObjects = [
            "srcSphere:offset",
            "srcSphere:lockedNode",
            "srcSphere:sphere",
        ]

        dstObjects = [
            'group|offset',
            'group|offset|lockedNode',
            'group|offset|lockedNode|sphere',
        ]

        self.open(path=srcPath)

        pose = mutils.Pose.fromObjects(srcObjects)
        pose.save(dstPath)

        pose = mutils.Pose.fromPath(dstPath)
        pose.load(dstObjects)

        self.assertEqualAttributeValues(srcObjects, dstObjects)

    def test_blend(self):
        """
        Test pose blending for float values when loading a pose.
        """
        self.open()

        for blend in [10, 30, 70, 90]:
            dstObjects = {}
            for srcAttribute, dstAttribute in self.listAttr():
                if srcAttribute.type == "float":
                    values = (srcAttribute.value(), dstAttribute.value())
                    dstObjects[dstAttribute.fullname()] = values

            pose = mutils.Pose.fromPath(self.dstPath)
            pose.load(self.dstObjects, blend=blend)

            for dstFullname in dstObjects.keys():
                srcValue, dstValue = dstObjects[dstFullname]

                value = (srcValue - dstValue) * (blend/100.00)
                value = dstValue + value

                dstValue = maya.cmds.getAttr(dstFullname)

                msg = 'Incorrect value for {0} {1} != {2}'
                msg = msg.format(dstFullname, value, dstValue)
                self.assertEqual(value, maya.cmds.getAttr(dstFullname), msg)

    def test_select(self):
        """
        Test selecting the controls from the pose.
        """
        self.open()

        pose = mutils.Pose.fromPath(self.dstPath)
        pose.select(namespaces=self.dstNamespaces)

        selection = maya.cmds.ls(selection=True)
        for dstName in self.dstObjects:
            msg = "Did not select {0}".format(dstName)
            self.assertIn(dstName, selection, msg)

    def test_count(self):
        """
        Test the object count within in pose.
        """
        self.open()
        pose = mutils.Pose.fromPath(self.dstPath)
        self.assertEqual(pose.count(), len(self.srcObjects))


def testSuite():
    """
    Return the test suite for the test case.

    :rtype: unittest.TestSuite
    """
    suite = unittest.TestSuite()
    s = unittest.makeSuite(TestPose, 'test')
    suite.addTest(s)
    return suite


def run():
    """
    Call from within Maya to run all valid tests.
    """
    tests = unittest.TextTestRunner()
    tests.run(testSuite())
