# Copyright 2020 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or modify it 
# under the terms of the GNU Lesser General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. This library is distributed in the 
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

from studiovendor.Qt import QtGui


COLORS = [
    {"name": "red", "color": "rgb(255, 115, 100)"},
    {"name": "orange", "color": "rgb(255, 150, 100)"},
    {"name": "yellow", "color": "rgb(255, 210, 103)"},
    {"name": "green", "color": "rgb(140, 220, 140)"},
    {"name": "blue", "color": "rgb(110, 175, 255)"},
    {"name": "purple", "color": "rgb(160, 120, 255)"},
    {"name": "pink", "color": "rgb(230, 130, 180)"},
    {"name": "grey", "color": "rgb(125, 125, 140)"},
]

COLORS_INDEXED = {c["name"]: c for c in COLORS}


class Color(QtGui.QColor):

    @classmethod
    def fromColor(cls, color):
        """
        :type color: QtGui.QColor
        """
        color = ('rgba(%d, %d, %d, %d)' % color.getRgb())
        return cls.fromString(color)

    @classmethod
    def fromString(cls, c):
        """
        :type c: str
        """
        a = 255

        c = c.replace(";", "")
        if not c.startswith("rgb"):
            c = COLORS_INDEXED.get(c)
            if c:
                c = c.get("color")
            else:
                return cls(0, 0, 0, 255)

        try:
            r, g, b, a = c.replace("rgb(", "").replace("rgba(", "").replace(")", "").split(",")
        except ValueError:
            r, g, b = c.replace("rgb(", "").replace(")", "").split(",")

        return cls(int(r), int(g), int(b), int(a))

    def __eq__(self, other):
        if isinstance(other, Color):
            return self.toString() == other.toString()
        else:
            return QtGui.QColor.__eq__(self, other)

    def toString(self):
        """
        :type: str
        """
        return 'rgba(%d, %d, %d, %d)' % self.getRgb()

    def isDark(self):
        """
        :type: bool
        """
        return self.red() < 125 and self.green() < 125 and self.blue() < 125
