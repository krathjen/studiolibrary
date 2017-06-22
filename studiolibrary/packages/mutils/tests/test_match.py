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

import mutils
import test_base


class TestMatch(test_base.TestBase):

    def setUp(self):
        """
        """
        pass

    def matchNames(self, expectedResult, srcObjects=None, dstObjects=None, dstNamespaces=None):
        """
        """
        result = []
        for srcNode, dstNode in mutils.matchNames(srcObjects, dstObjects=dstObjects, dstNamespaces=dstNamespaces):
            result.append((srcNode.name(), dstNode.name()))

        if result != expectedResult:
            raise Exception("Result does not match the expected result: %s != %s" % (str(result), expectedResult))

    def test_match0(self):
        """
        Test no matches
        """
        srcObjects = ["control2", "control1", "control3"]
        dstObjects = ["control4", "control5", "control6"]
        expectedResult = []
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match1(self):
        """
        Test simple match
        """
        srcObjects = ["control2", "control1", "control3"]
        dstObjects = ["control1", "control2", "control3"]
        expectedResult = [("control2", "control2"),
                          ("control1", "control1"),
                          ("control3", "control3")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match2(self):
        """
        """
        srcObjects = ["control1"]
        dstObjects = ["character1:control1", "character2:control1"]
        expectedResult = [("control1", "character1:control1"),
                          ("control1", "character2:control1")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match3(self):
        """
        """
        srcObjects = ["control1"]
        dstNamespaces = ["character1", "character2"]
        expectedResult = [("control1", "character1:control1"),
                          ("control1", "character2:control1")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match4(self):
        """
        """
        srcObjects = ["character1:control1"]
        dstNamespaces = [""]
        expectedResult = [("character1:control1", "control1")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match5(self):
        """
        Test namespace
        Test short name
        Test multiple namespaces in source objects
        """
        srcObjects = ["character1:control1", "character1:control2"]
        dstNamespaces = ["character2"]
        expectedResult = [("character1:control1", "character2:control1"),
                          ("character1:control2", "character2:control2")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match6(self):
        """
        Test namespace
        Test long name
        Test namespace in source objects
        Test namespace that is not in source objects
        """
        srcObjects = ["character1:group1|character1:control1", "character1:group2|character1:control1"]
        dstNamespaces = ["character2"]
        expectedResult = [("character1:group1|character1:control1", "character2:group1|character2:control1"),
                          ("character1:group2|character1:control1", "character2:group2|character2:control1")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match7(self):
        """
        Test namespace
        Test multiple namespaces in source objects
        Test only one destination namespace
        """
        srcObjects = ["character1:control1", "character2:control1"]
        dstNamespaces = ["character2"]
        expectedResult = [("character2:control1", "character2:control1")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match8(self):
        """
        Test multiple namespaces in source objects
        Test namespace that is not in source objects
        """
        srcObjects = ["character1:control1", "character2:control1"]
        dstNamespaces = ["character3"]
        expectedResult = [("character1:control1", "character3:control1")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match9(self):
        """
        """
        srcObjects = ["character1:group1|character1:control1",
                      "character1:group1|character1:control2"]
        dstObjects = ["group1|control1",
                      "group1|control2"]
        expectedResult = [("character1:group1|character1:control1", "group1|control1"),
                          ("character1:group1|character1:control2", "group1|control2")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match10(self):
        """
        WARNING: The expected result is a little strange.
        It will always match source objects without a namespace first.
        expectedResult = [("group1|control1", "character2:group1|character2:control1")]
        NOT
        expectedResult = [("character1:group1|character1:control1", "character2:group1|character2:control1")]
        """
        srcObjects = ["character1:group1|character1:control1",
                      "group1|control1"]
        dstNamespaces = ["character2"]
        expectedResult = [("group1|control1", "character2:group1|character2:control1")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstNamespaces=dstNamespaces)

    def test_match11(self):
        """
        Match long name to short name.
        """
        srcObjects = ["|grpEyeAllLf|grpLidTpLf|ctlLidTpLf"]
        dstObjects = ["ctlLidTpLf"]

        expectedResult = [("|grpEyeAllLf|grpLidTpLf|ctlLidTpLf", "ctlLidTpLf")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match12(self):
        """
        Match short name to long name.
        """
        srcObjects = ["ctlLidTpLf"]
        dstObjects = ["|grpEyeAllLf|grpLidTpLf|ctlLidTpLf"]

        expectedResult = [("ctlLidTpLf", "|grpEyeAllLf|grpLidTpLf|ctlLidTpLf")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match13(self):
        """
        Match short name to long name with namespace.
        """
        srcObjects = ["ctlLidTpLf"]
        dstObjects = ["|malcolm:grpEyeAllLf|malcolm:grpLidTpLf|malcolm:ctlLidTpLf"]

        expectedResult = [("ctlLidTpLf", "|malcolm:grpEyeAllLf|malcolm:grpLidTpLf|malcolm:ctlLidTpLf")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match14(self):
        """
        Match long name to short name with namespace.
        """
        srcObjects = ["|malcolm:grpEyeAllLf|malcolm:grpLidTpLf|malcolm:ctlLidTpLf"]
        dstObjects = ["ctlLidTpLf"]

        expectedResult = [("|malcolm:grpEyeAllLf|malcolm:grpLidTpLf|malcolm:ctlLidTpLf", "ctlLidTpLf")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match15(self):
        """
        Testing multiple source namespace to only one destination namespace. They should not merge.
        """
        srcObjects = ["character1:group1|character1:control1",
                      "character2:group1|character2:control2"]
        dstObjects = ["group1|control1",
                      "group1|control2"]
        expectedResult = [("character1:group1|character1:control1", "group1|control1")]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match16(self):
        """
        Testing multiple source namespace and destination namespaces
        """
        srcObjects = ["character1:group1|character1:control1",
                      "character2:group1|character2:control1",
                      "character3:group1|character3:control1"]
        dstObjects = ["character3:group1|character3:control1",
                      "character1:group1|character1:control1",
                      "character2:group1|character2:control1"]
        expectedResult = [('character1:group1|character1:control1', 'character1:group1|character1:control1'),
                          ('character3:group1|character3:control1', 'character3:group1|character3:control1'),
                          ('character2:group1|character2:control1', 'character2:group1|character2:control1')]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)

    def test_match17(self):
        """
        Testing multiple source namespace and destination namespaces.
        """
        srcObjects = ["character1:group1|character1:control1",
                      "group1|control1",
                      "character3:group1|character3:control1"]
        dstObjects = ["character3:group1|character3:control1",
                      "character1:group1|character1:control1",
                      "group1|control1"]
        expectedResult = [('group1|control1', 'group1|control1'),
                          ('character1:group1|character1:control1', 'character1:group1|character1:control1'),
                          ('character3:group1|character3:control1', 'character3:group1|character3:control1')]
        self.matchNames(expectedResult, srcObjects=srcObjects, dstObjects=dstObjects)