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
import mutils
import maya.cmds

import test_base


class TestPose(test_base.TestBase):

    def setUp(self):
        """
        """
        self.srcPath = os.path.join(self.dataDir(), "test_pose.ma")
        self.dstPath = os.path.join(self.dataDir(), "test_pose.pose")

    def test_save(self):
        """
        Test save pose.
        """
        self.open()
        pose = mutils.Pose.fromObjects(self.srcObjects)
        pose.save(self.dstPath)

    def test_load(self):
        """
        Test load types.
        """
        self.open()
        pose = mutils.Pose.fromPath(self.dstPath)
        pose.load(self.dstObjects)

        # Check attributes
        for srcAttribute, dstAttribute in self.listAttr():
            self.assertEqual(srcAttribute.value(), dstAttribute.value(),
                             'Incorrect value for %s %s != %s' %
                             (dstAttribute.fullname(), dstAttribute.value(), srcAttribute.value()))

    def test_older_version(self):
        """
        """
        srcPath = os.path.join(self.dataDir(), "test_older_version.dict")
        dstPath = os.path.join(self.dataDir(), "test_older_version.json")

        pose = mutils.Pose.fromPath(srcPath)
        print pose.objects()
        # Check attributes
        # for srcAttribute, dstAttribute in self.listAttr():
        #     self.assertEqual(srcAttribute.value(), dstAttribute.value(),
        #                      'Incorrect value for %s %s != %s' %
        #                      (dstAttribute.fullname(), dstAttribute.value(), srcAttribute.value()))

    def test_non_unique_names(self):
        """
        """
        srcPath = os.path.join(self.dataDir(), "test_non_unique_names.ma")
        dstPath = os.path.join(self.dataDir(), "test_non_unique_names.pose")

        srcObjects = ["srcSphere:lockedNode", "srcSphere:offset", "srcSphere:sphere"]
        dstObjects = ["lockedNode", "offset", "sphere"]

        self.open(path=srcPath)

        pose = mutils.Pose.fromObjects(srcObjects)
        pose.save(dstPath)

        pose = mutils.Pose.fromPath(dstPath)
        pose.load(dstObjects)

        # Check attributes
        for srcAttribute, dstAttribute in self.listAttr(srcObjects, dstObjects):
            self.assertEqual(srcAttribute.value(), dstAttribute.value(),
                             'Incorrect value for %s %s != %s' %
                             (dstAttribute.fullname(), dstAttribute.value(), srcAttribute.value()))

    def test_blend(self):
        """
        Test pose blending. At the moment this only tests float attribute types
        """
        self.open()

        for blend in [10, 30, 70, 90]:
            dstObjects = {}
            for srcAttribute, dstAttribute in self.listAttr():
                if srcAttribute.type == "float":
                    dstObjects[dstAttribute.fullname()] = (srcAttribute.value(), dstAttribute.value())

            pose = mutils.Pose.fromPath(self.dstPath)
            pose.load(self.dstObjects, blend=blend)

            for dstFullname in dstObjects.keys():
                srcValue, dstValue = dstObjects[dstFullname]

                value = (srcValue - dstValue) * (blend/100.00)
                value = dstValue + value

                self.assertEqual(value, maya.cmds.getAttr(dstFullname),
                                 'Incorrect value for %s %s != %s' %
                                 (dstFullname, value, maya.cmds.getAttr(dstFullname)))

    def test_select(self):
        """
        Test select content
        """
        self.open()
        pose = mutils.Pose.fromPath(self.dstPath)
        pose.select(namespaces=self.dstNamespaces)

        # Check Selection
        selection = maya.cmds.ls(selection=True)
        for dstName in self.dstObjects:
            if dstName not in selection:
                self.assertEqual(False)
                print "Did not select %s" % dstName

    def test_count(self):
        """
        Test select content
        """
        self.open()
        pose = mutils.Pose.fromPath(self.dstPath)
        self.assertEqual(pose.count(), len(self.srcObjects))
