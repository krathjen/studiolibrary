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

import studioqt

from studioqt import QtGui
from studioqt import QtCore


class CombinedWidgetItemGroup(studioqt.CombinedWidgetItem):

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

    def fontSize(self):
        """
        Return the font size for the item.

        :rtype: int
        """
        return 24

    def sizeHint(self):
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
        width = self.combinedWidget().width() - 20

        rect = QtCore.QRect(option.rect)
        rect.setWidth(width)
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

        color = QtGui.QColor(250,250,250, 20)
        painter.setBrush(QtGui.QBrush(color))

        painter.drawRect(visualRect)
