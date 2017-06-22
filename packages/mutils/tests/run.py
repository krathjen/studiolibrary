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
# RUN TEST SUITE
import mutils.tests
reload(mutils.tests)
mutils.tests.run()
"""
import unittest

import logging


logging.basicConfig(
    filemode='w',
    level=logging.DEBUG,
    format='%(levelname)s: %(funcName)s: %(message)s',
)


def testSuite():
    """
    Return a test suite containing all the tests.

    :rtype: unittest.TestSuite
    """
    import test_pose
    import test_anim
    import test_match
    import test_utils
    import test_attribute
    import test_mirrortable

    suite = unittest.TestSuite()

    s = unittest.makeSuite(test_pose.TestPose, 'test')
    suite.addTest(s)

    s = unittest.makeSuite(test_anim.TestAnim, 'test')
    suite.addTest(s)

    s = unittest.makeSuite(test_utils.TestUtils, 'test')
    suite.addTest(s)

    s = unittest.makeSuite(test_match.TestMatch, 'test')
    suite.addTest(s)

    s = unittest.makeSuite(test_attribute.TestAttribute, 'test')
    suite.addTest(s)

    s = unittest.makeSuite(test_mirrortable.TestMirrorTable, 'test')
    suite.addTest(s)

    return suite


def run():
    """
    Call from within Maya to run all valid tests.
    """
    tests = unittest.TextTestRunner()
    tests.run(testSuite())
