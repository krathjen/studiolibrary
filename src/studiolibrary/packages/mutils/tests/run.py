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
    import test_attribute

    suite = unittest.TestSuite()

    s = unittest.makeSuite(test_pose.TestPose, 'test')
    suite.addTest(s)

    s = unittest.makeSuite(test_anim.TestAnim, 'test')
    suite.addTest(s)

    s = unittest.makeSuite(test_match.TestMatch, 'test')
    suite.addTest(s)

    s = unittest.makeSuite(test_attribute.TestAttribute, 'test')
    suite.addTest(s)

    return suite


def run():
    """
    Call from within Maya to run all valid tests.
    """
    tests = unittest.TextTestRunner()
    tests.run(testSuite())
