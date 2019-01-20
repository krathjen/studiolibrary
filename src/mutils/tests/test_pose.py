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
