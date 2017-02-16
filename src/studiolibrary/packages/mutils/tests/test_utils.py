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

import mutils.animation


class TestUtils(unittest.TestCase):

    def test_clamp_range(self):
        """
        Test the clamp range command
        """
        msg = "Incorrect clamp range"

        # Test clamp range on both min and max
        clampRange = mutils.animation.clampRange((15, 35), (20, 30))
        assert (20, 30) == clampRange, msg

        # Test clamp range on min time
        clampRange = mutils.animation.clampRange((10, 25), (20, 30))
        assert (20, 25) == clampRange, msg

        # Test clamp range on man time
        clampRange = mutils.animation.clampRange((25, 40), (20, 30))
        assert (25, 30) == clampRange, msg

        # Test min out of bounds error
        def test_exception():
            clampRange = mutils.animation.clampRange((5, 15), (20, 30))
        self.assertRaises(mutils.animation.OutOfBoundsError, test_exception)

        # Test max out of bounds error
        def test_exception():
            clampRange = mutils.animation.clampRange((65, 95), (20, 30))
        self.assertRaises(mutils.animation.OutOfBoundsError, test_exception)


def testSuite():
    """
    Return the test suite for this module.

    :rtype: unittest.TestSuite
    """
    suite = unittest.TestSuite()
    s = unittest.makeSuite(TestUtils, 'test')
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
