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

from mutils.mirrortable import MirrorTable


class TestMirrorTable(unittest.TestCase):

    def test_find_left_side(self):
        """
        Test the clamp range command
        """
        msg = "Cannot find the left side from the given objects"

        objects = ["Character3_Ctrl_LeftForeArm"]
        assert "Left" == MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "l_arm_cool_l"]
        assert "l_*" == MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Character:l_arm_cool_ik"]
        assert "l_*" == MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Group|l_arm_cool_ik"]
        assert "l_*" == MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Group|arm_cool_l"]
        assert "*_l" == MirrorTable.findLeftSide(objects), msg

        objects = ["leftArm1_ArmCon"]
        assert "left*" == MirrorTable.findLeftSide(objects), msg

        objects = ["LLegCON", "LhandCON"]
        assert "L*" == MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Group|left_arm_cool_ik"]
        assert "left*" == MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "Group|ctlHandLf"]
        assert "*Lf" == MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "malcolm:ctlArmIkLf"]
        assert "*Lf" == MirrorTable.findLeftSide(objects), msg

        objects = ["r_cool_ik", "IKExtraLegFront_L|IKLegFront_L"]
        assert "*_L" == MirrorTable.findLeftSide(objects), msg

    def test_find_right_side(self):
        """
        Test the clamp range command
        """
        msg = "Cannot find the right side from the given objects"

        objects = ["Character3_Ctrl_RightForeArm"]
        assert "Right" == MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "r_arm_car_r"]
        assert "r_*" == MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "Character:r_arm_car_r"]
        assert "r_*" == MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "Group|r_arm_car_r"]
        assert "r_*" == MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "arm_car_r"]
        assert "*_r" == MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "Group|right_arm_car_ik"]
        assert "right*" == MirrorTable.findRightSide(objects), msg

        objects = ["CHR1:RIG:RLegCON", "CHR1:RIG:RhandCON"]
        assert "R*" == MirrorTable.findRightSide(objects), msg

        objects = ["RLegCON", "RhandCON"]
        assert "R*" == MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "Group|ctlHandRt"]
        assert "*Rt" == MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "malcolm:ctlArmIkRt"]
        assert "*Rt" == MirrorTable.findRightSide(objects), msg

        objects = ["l_car_ik", "IKExtraLegFront_R|IKLegFront_R"]
        assert "*_R" == MirrorTable.findRightSide(objects), msg

        objects = ["Rig_v01_ref:Rig_v01:leftArm1_UpperArmControl"]
        assert "" == MirrorTable.findRightSide(objects), msg

    def test_match_side(self):

        msg = "Incorrect result from match side"

        result = MirrorTable.matchSide("ctlArmIkRt", "*Rt")
        assert result is True, msg

        result = MirrorTable.matchSide("ctlArmIkRt", "Rt")
        assert result is True, msg

        result = MirrorTable.matchSide("CHR1:RIG:LRollCON", "L*")
        assert result is True, msg

        result = MirrorTable.matchSide("CHR1:RIG:LRollCON", "RIG:L*")
        assert result is True, msg

        result = MirrorTable.matchSide("Group|right_arm_car_ik", "right*")
        assert result is True, msg

        result = MirrorTable.matchSide("Group|IKLegFront_R", "*_R")
        assert result is True, msg

    def test_mirror_object(self):

        msg = "Incorrect mirror name for object"

        result = MirrorTable._mirrorObject("malcolm:ctlArmIkRt", "Rt", "Lf")
        assert "malcolm:ctlArmIkLf" == result, msg

        result = MirrorTable._mirrorObject("malcolm:ctlArmIkRt", "*Rt", "*Lf")
        assert "malcolm:ctlArmIkLf" == result, msg

        result = MirrorTable._mirrorObject("IKLegFront_R", "*_R", "*_L")
        assert "IKLegFront_L" == result, msg

        result = MirrorTable._mirrorObject("CHR1:RIG:RLegCON", "R*", "L*")
        assert "CHR1:RIG:LLegCON" == result, msg

        result = MirrorTable._mirrorObject("CHR1:RIG:RRollCON", "R*", "L*")
        assert "CHR1:RIG:LRollCON" == result, msg

        result = MirrorTable._mirrorObject("leftArm1_ArmCon", "left*", "right*")
        assert "rightArm1_ArmCon" == result, msg

        result = MirrorTable._mirrorObject("Rig:RArm1_UpperArmControl", "R*", "L*")
        assert "Rig:LArm1_UpperArmControl" == result, msg

        result = MirrorTable._mirrorObject("Group|Ch1:RIG:Offset|Ch1:RIG:RRoll", "R*", "L*")
        assert "Group|Ch1:RIG:Offset|Ch1:RIG:LRoll" == result, msg

        result = MirrorTable._mirrorObject("Group|Ch1:RIG:RExtra|Ch1:RIG:RRoll", "RIG:R", "RIG:L")
        assert "Group|Ch1:RIG:LExtra|Ch1:RIG:LRoll" == result, msg

        # # WARNING: The following condition is not supported yet!
        # result = MirrorTable._mirrorObject("Group|Ch1:RIG:RExtra|Ch1:RIG:RRoll", "R*", "L*")
        # assert "Group|Ch1:RIG:LExtra|Ch1:RIG:LRoll" == result, msg


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


if __name__ == "__main__":
    run()