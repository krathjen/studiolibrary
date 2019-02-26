# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
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

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt


class Icon(QtGui.QIcon):

    def setColor(self, color, size=None):
        """
        :type color: QtGui.QColor
        :rtype: None
        """
        icon = self
        size = size or icon.actualSize(QtCore.QSize(256, 256))
        pixmap = icon.pixmap(size)

        if not self.isNull():
            painter = QtGui.QPainter(pixmap)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
            painter.setBrush(color)
            painter.setPen(color)
            painter.drawRect(pixmap.rect())
            painter.end()

        icon = QtGui.QIcon(pixmap)
        self.swap(icon)

    def setBadge(self, x, y, w, h, color=None):
        """
        Set a for the icon.
        
        :type x: int 
        :type y: int 
        :type w: int
        :type h: int 
        :type color: QtGui.QColor or None
        """
        color = color or QtGui.QColor(240, 100, 100)

        size = self.actualSize(QtCore.QSize(256, 256))
        pixmap = self.pixmap(size)

        painter = QtGui.QPainter(pixmap)

        pen = QtGui.QPen(color)
        pen.setWidth(0)
        painter.setPen(pen)

        painter.setBrush(color)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.drawEllipse(x, y, w, h)
        painter.end()

        icon = QtGui.QIcon(pixmap)
        self.swap(icon)
