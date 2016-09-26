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
