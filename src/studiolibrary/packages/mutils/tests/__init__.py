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
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(funcName)s: %(message)s',
                    # filename='/tmp/myapp.log',
                    filemode='w')


def suite():
    """
    :rtype: unittest.TestSuite
    """
    import test_pose
    import test_anim
    import test_match
    suite_ = unittest.TestSuite()
    suite_.addTest(test_match.TestMatch('test_match1'))
    suite_.addTest(test_match.TestMatch('test_match2'))
    suite_.addTest(test_match.TestMatch('test_match3'))
    suite_.addTest(test_match.TestMatch('test_match4'))
    suite_.addTest(test_match.TestMatch('test_match5'))
    suite_.addTest(test_match.TestMatch('test_match6'))
    suite_.addTest(test_match.TestMatch('test_match7'))
    suite_.addTest(test_match.TestMatch('test_match8'))
    suite_.addTest(test_match.TestMatch('test_match9'))
    suite_.addTest(test_match.TestMatch('test_match10'))
    suite_.addTest(test_match.TestMatch('test_match11'))
    suite_.addTest(test_match.TestMatch('test_match12'))
    suite_.addTest(test_match.TestMatch('test_match13'))
    suite_.addTest(test_match.TestMatch('test_match14'))
    suite_.addTest(test_match.TestMatch('test_match15'))
    suite_.addTest(test_match.TestMatch('test_match16'))
    suite_.addTest(test_match.TestMatch('test_match17'))

    suite_.addTest(test_pose.TestPose('test_save'))
    suite_.addTest(test_pose.TestPose('test_load'))
    suite_.addTest(test_pose.TestPose('test_blend'))
    suite_.addTest(test_pose.TestPose('test_select'))
    suite_.addTest(test_pose.TestPose('test_older_version'))
    """
    # Should add the following tests
    # suite_.addTest(test_pose.TestPose('test_count'))
    # suite_.addTest(test_pose.TestPose('test_non_unique_names'))
    # suite_.addTest(test_pose.TestPose('test_get_namespaces'))
    # suite_.addTest(test_pose.TestPose('test_more_than_one_namespace'))
    # suite_.addTest(test_anim.TestAnim('test_select'))
    """
    suite_.addTest(test_anim.TestAnim('test_load_insert'))
    suite_.addTest(test_anim.TestAnim('test_older_version'))
    suite_.addTest(test_anim.TestAnim('test_load_replace'))
    suite_.addTest(test_anim.TestAnim('test_bake_connected'))
    suite_.addTest(test_anim.TestAnim('test_load_replace_completely'))
    return suite_


def run():
    """
    """
    tests = unittest.TextTestRunner()
    tests.run(suite())





























