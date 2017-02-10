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
import mutils.tests.test_attribute
reload(mutils.tests.test_attribute)
mutils.tests.test_attribute.run()
"""
import os
import unittest

import maya.cmds

import mutils


class TestAttribute(unittest.TestCase):

    def setUp(self):
        """
        Open an existing maya test scene for testing.
        """
        dirname = os.path.dirname(mutils.__file__)
        dirname = os.path.join(dirname, "tests", "data")
        path = os.path.join(dirname, "sphere.ma")

        maya.cmds.file(
            path,
            open=True,
            force=True,
            ignoreVersion=True,
            executeScriptNodes=False,
        )

    def test_attribute_limit(self):
        """
        Test the attribute limit when setting the attribute value.
        """
        range = (-100, 100)
        maya.cmds.cutKey("sphere", cl=True, time=range, f=range, at="testLimit")

        attr = mutils.Attribute("sphere", "testLimit")
        attr.set(200)

        value = maya.cmds.getAttr("sphere.testLimit")
        assert value == 10, "Maximum attibute limit was ignored when setting the attribute value"

    def test_attribute_limit2(self):
        """
        Test the maximum attribute limit when setting a keyframe.
        """
        attr = mutils.Attribute("sphere", "testLimit")
        attr.setKeyframe(200)

        value = maya.cmds.keyframe("sphere.testLimit", query=True, eval=True)[0]
        assert value == 10, "Maximum attibute limit was ignored when setting animation keyframe"

    def test_attribute_limit3(self):
        """
        Test the minimum attribute limit when setting a keyframe.
        """
        attr = mutils.Attribute("sphere", "testLimit")
        attr.setKeyframe(-200)

        value = maya.cmds.keyframe("sphere.testLimit", query=True, eval=True)[0]
        assert value == -10, "Minimum attibute limit was ignored when setting animation keyframe"

    def test_non_keyable(self):
        """
        Test if non-keyable attributes can be keyed.
        """
        range = (-100, 100)
        maya.cmds.cutKey("sphere", cl=True, time=range, f=range, at="testNonKeyable")

        attr = mutils.Attribute("sphere", "testNonKeyable")
        attr.setKeyframe(200)

        value = maya.cmds.keyframe("sphere.testNonKeyable", query=True, eval=True)
        assert value is None, "Non keyable attribute was keyed"

    def test_anim_curve(self):
        """
        Test if get anim curve returns the right value.
        """
        msg = "Incorrect anim curve was returned when using attr.animCurve "

        attr = mutils.Attribute("sphere", "testFloat")
        curve = attr.animCurve()
        assert curve is None, msg + "1"

        attr = mutils.Attribute("sphere", "testConnected")
        curve = attr.animCurve()
        assert curve is None, msg + "2"

        attr = mutils.Attribute("sphere", "testAnimated")
        curve = attr.animCurve()
        assert curve == "sphere_testAnimated", msg + "3"

    def test_set_anim_curve(self):
        """
        Test if set anim curve
        """
        msg = "No anim curve was set"

        attr = mutils.Attribute("sphere", "testAnimated")
        srcCurve = attr.animCurve()

        attr = mutils.Attribute("sphere", "testFloat")
        attr.setAnimCurve(srcCurve, time=(1, 15), option="replace")
        curve = attr.animCurve()
        assert curve is not None, msg

        attr = mutils.Attribute("sphere", "testFloat")
        attr.setAnimCurve(srcCurve, time=(15, 15), option="replaceCompletely")
        curve = attr.animCurve()
        assert curve is not None, msg

    def test_set_static_keyframe(self):
        """
        Test set static keyframes
        """
        msg = "The inserted static keys have different values"

        attr = mutils.Attribute("sphere", "testAnimated", cache=False)
        attr.setStaticKeyframe(value=2, time=(4, 6), option="replace")

        maya.cmds.currentTime(4)
        value1 = attr.value()

        maya.cmds.currentTime(6)
        value2 = attr.value()

        assert value1 == value2, msg


def testSuite():
    """
    Return the test suite for the TestAttribute.

    :rtype: unittest.TestSuite
    """
    suite = unittest.TestSuite()
    s = unittest.makeSuite(TestAttribute, 'test')
    suite.addTest(s)
    return suite


def run():
    """
    Call from within Maya to run all valid tests.

    Example:

        import mutils.tests.test_attribute
        reload(mutils.tests.test_attribute)
        mutils.tests.test_attribute.run()
    """
    tests = unittest.TextTestRunner()
    tests.run(testSuite())
