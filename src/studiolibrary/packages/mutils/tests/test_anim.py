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

import unittest

import mutils

import test_base


class TestAnim(test_base.TestBase):

    def setUp(self):
        """
        """

    def save(self, bakeConnected=False):
        """
        Test saving the animation to disc.
        """
        self.open()
        anim = mutils.Animation.fromObjects(self.srcObjects)
        anim.save(self.dstPath, bakeConnected=bakeConnected)

    def test_older_version(self):
        """
        Test animation parser for an older animation format
        """
        srcPath = self.dataPath("test_older_version.anim")
        a = mutils.Animation.fromPath(srcPath)

    def test_load_replace_completely(self):
        """
        Test loading the animation with replace completely option.
        """
        self.srcPath = self.dataPath("test_anim.ma")
        self.dstPath = self.dataPath("test_load_replace_completely.anim")
        self.save()

        anim = mutils.Animation.fromPath(self.dstPath)
        anim.load(self.dstObjects)

        self.assertEqualAnimation()

    def test_bake_connected(self):
        """
        Test saving animation with the option bake connected.
        """
        srcPath = self.dataPath("test_bake_connected.ma")
        dstPath = self.dataPath("test_bake_connected.anim")

        srcObjects = [
            "srcSphere:group",
            "srcSphere:lockedNode",
            "srcSphere:offset",
            "srcSphere:sphere"
        ]

        dstObjects = [
            "dstSphere:group",
            "dstSphere:lockedNode",
            "dstSphere:offset",
            "dstSphere:sphere"
        ]

        self.open(path=srcPath)

        anim = mutils.Animation.fromObjects(srcObjects)
        anim.save(dstPath, bakeConnected=True)

        anim = mutils.Animation.fromPath(dstPath)
        anim.load(dstObjects)

        self.assertEqualAnimation()

    def test_load_replace(self):
        """
        Test loading the animation with the option Replace.
        """
        self.srcPath = self.dataPath("test_anim.ma")
        self.dstPath = self.dataPath("test_load_replace.anim")
        self.save()

        anim = mutils.Animation.fromPath(self.dstPath)
        anim.load(self.dstObjects, option=mutils.PasteOption.Replace, startFrame=5)

    def test_load_insert(self):
        """
        Test loading the animation with the option Insert.
        """
        self.srcPath = self.dataPath("test_anim.ma")
        self.dstPath = self.dataPath("test_load_insert.anim")
        self.save()

        anim = mutils.Animation.fromPath(self.dstPath)
        anim.load(self.dstObjects, option=mutils.PasteOption.Insert, startFrame=5)


def testSuite():
    """
    Return the test suite for the test case.

    :rtype: unittest.TestSuite
    """
    suite = unittest.TestSuite()
    s = unittest.makeSuite(TestAnim, 'test')
    suite.addTest(s)
    return suite


def run():
    """
    Call from within Maya to run all valid tests.
    """
    tests = unittest.TextTestRunner()
    tests.run(testSuite())
