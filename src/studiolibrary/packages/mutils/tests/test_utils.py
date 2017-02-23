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
