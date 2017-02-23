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

from studioqt import QtGui


class Color(QtGui.QColor):

    @classmethod
    def fromColor(cls, color):
        """
        :type color: QtGui.QColor
        """
        color = ('rgb(%d, %d, %d, %d)' % color.getRgb())
        return cls.fromString(color)

    @classmethod
    def fromString(cls, text):
        """
        :type text: str
        """
        a = 255
        try:
            r, g, b, a = text.replace("rgb(", "").replace(")", "").split(",")
        except ValueError:
            r, g, b = text.replace("rgb(", "").replace(")", "").split(",")

        return cls(int(r), int(g), int(b), int(a))

    def __eq__(self, other):
        if other == self:
            return True
        elif isinstance(other, Color):
            return self.toString() == other.toString()
        else:
            return False

    def toString(self):
        """
        :type: str
        """
        return 'rgb(%d, %d, %d, %d)' % self.getRgb()

    def isDark(self):
        """
        :type: bool
        """
        return self.red() < 125 and self.green() < 125 and self.blue() < 125
