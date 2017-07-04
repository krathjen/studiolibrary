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

import studioqt

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


class CombinedWidgetItemGroup(studioqt.CombinedWidgetItem):

    DEFAULT_FONT_SIZE = 24

    def __init__(self, *args):
        studioqt.CombinedWidgetItem.__init__(self, *args)

        self._children = []

        font = self.font(0)
        font.setBold(True)

        self.setFont(0, font)
        self.setFont(1, font)
        self.setDragEnabled(False)

    def setChildren(self, children):
        """
        Set the children for the group.

        :type children: list[CombinedWidgetItem]
        :rtype: None
        """
        self._children = children

    def children(self):
        """
        Return the children for the group.

        :rtype: list[CombinedWidgetItem]
        """
        return self._children

    def childrenHidden(self):
        """
        Return True if all children are hidden.

        :rtype: bool
        """
        for child in self.children():
            if not child.isHidden():
                return False
        return True

    def updateChildren(self):
        """
        Update the visibility if all children are hidden.

        :rtype: bool
        """
        if self.childrenHidden():
            self.setHidden(True)
        else:
            self.setHidden(False)

    def textAlignment(self, column):
        """
        Return the font alignment for the given column.

        :type column: int
        """
        return QtWidgets.QTreeWidgetItem.textAlignment(self, column)

    def sizeHint(self, column=0):
        """
        Return the size of the item.

        :rtype: QtCore.QSize
        """
        width = self.combinedWidget().width() - 20
        return QtCore.QSize(width, 40 * self.dpi())

    def visualRect(self, option):
        """
        Return the visual rect for the item.

        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: QtCore.QRect
        """
        rect = QtCore.QRect(option.rect)
        rect.setX(10 * self.dpi())
        rect.setWidth(self.sizeHint().width())
        return rect

    def isTextVisible(self):
        """
        Return True if the text is visible.

        :rtype: bool
        """
        return True

    def textSelectedColor(self):
        """
        Return the selected text color for the item.

        :rtype: QtWidgets.QtColor
        """
        return self.combinedWidget().textColor()

    def backgroundColor(self):
        """
        Return the background color for the item.

        :rtype: QtWidgets.QtColor
        """
        return QtGui.QColor(0, 0, 0, 0)

    def backgroundHoverColor(self):
        """
        Return the background color when the mouse is over the item.

        :rtype: QtWidgets.QtColor
        """
        return QtGui.QColor(0, 0, 0, 0)

    def backgroundSelectedColor(self):
        """
        Return the background color when the item is selected.

        :rtype: QtWidgets.QtColor
        """
        return QtGui.QColor(0, 0, 0, 0)

    def paintRow(self, painter, option, index):
        """
        Paint performs low-level painting for the item.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        :rtype: None
        """
        self.setRect(QtCore.QRect(option.rect))

        painter.save()

        try:
            self.paintBackground(painter, option, index)

            if self.isTextVisible():
                self._paintText(painter, option, 1)

            self.paintIcon(painter, option, index)
        finally:
            painter.restore()

    def icon(self, *args):
        """
        Overriding the icon method, so that an icon is not displayed.
        """
        return None

    def paintBackground(self, painter, option, index):
        """
        Draw the background for the item.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        :rtype: None
        """
        studioqt.CombinedWidgetItem.paintBackground(self, painter, option, index)

        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        visualRect = self.visualRect(option)

        textWidth = self.textWidth(0)

        padding = (20 * self.dpi())

        visualRect.setX(textWidth + padding)
        visualRect.setY(visualRect.y() + (visualRect.height() / 2))
        visualRect.setHeight(2 * self.dpi())
        visualRect.setWidth(visualRect.width() - padding)

        color = QtGui.QColor(
            self.textColor().red(),
            self.textColor().green(),
            self.textColor().blue(), 10
        )
        painter.setBrush(QtGui.QBrush(color))

        painter.drawRect(visualRect)
