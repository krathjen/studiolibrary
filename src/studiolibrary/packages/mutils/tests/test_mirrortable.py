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

import mutils.mirrortable


class TestMirrorTable(unittest.TestCase):

    def test_find_left_side(self):
        """
        Test the clamp range command
        """
        msg = "Incorrect Side"

        objects = ["r_cool_ik", "l_arm_cool_l"]
        assert "l_*" == mutils.mirrortable.MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Character:l_arm_cool_ik"]
        assert "l_*" == mutils.mirrortable.MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Group|l_arm_cool_ik"]
        assert "l_*" == mutils.mirrortable.MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Group|arm_cool_l"]
        assert "*_l" == mutils.mirrortable.MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Group|left_arm_cool_ik"]
        assert "left*" == mutils.mirrortable.MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Group|ctlHandLf"]
        assert "*Lf" == mutils.mirrortable.MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "malcolm:ctlArmIkLf"]
        assert "*Lf" == mutils.mirrortable.MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "IKExtraLegFront_L|IKLegFront_L"]
        assert "*_L" == mutils.mirrortable.MirrorTable.findLeftSide(objects), msg

    def test_find_right_side(self):
        """
        Test the clamp range command
        """
        msg = "Incorrect Side"

        objects = ["l_car_ik", "r_arm_car_r"]
        assert "r_*" == mutils.mirrortable.MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "Character:r_arm_car_r"]
        assert "r_*" == mutils.mirrortable.MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "Group|r_arm_car_r"]
        assert "r_*" == mutils.mirrortable.MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "arm_car_r"]
        assert "*_r" == mutils.mirrortable.MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "Group|right_arm_car_ik"]
        assert "right*" == mutils.mirrortable.MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "Group|ctlHandRt"]
        assert "*Rt" == mutils.mirrortable.MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "malcolm:ctlArmIkRt"]
        assert "*Rt" == mutils.mirrortable.MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "IKExtraLegFront_R|IKLegFront_R"]
        assert "*_R" == mutils.mirrortable.MirrorTable.findRightSide(objects), msg


def testSuite():
    """
    Return the test suite for this module.

    :rtype: unittest.TestSuite
    """
    suite = unittest.TestSuite()
    s = unittest.makeSuite(TestMirrorTable, 'test')
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
