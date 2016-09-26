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

import os

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


import studioqt


class CombinedWidgetItem(QtWidgets.QTreeWidgetItem):

    """
    Combined Widget items are used to hold rows of information for a
    combined widget.
    """

    MAX_ICON_SIZE = 256

    def __init__(self, *args):
        QtWidgets.QTreeWidgetItem.__init__(self, *args)

        self._url = None
        self._path = None
        self._size = None
        self._rect = None
        self.textColumnOrder = []

        self._text = {}
        self._sortText = {}
        self._displayText = {}

        self._icon = {}

        self._fonts = {}
        self._pixmap = {}
        self._iconPath = ""
        self._searchText = None
        self._infoWidget = None
        self._groupColumn = 0
        self._mimeText = None
        self._combinedWidget = None
        self._stretchToWidget = None

        self._dragEnabled = True

    def __eq__(self, other):
        return id(other) == id(self)

    def mimeText(self):
        """
        Return the mime text for drag and drop.

        :rtype: str
        """
        return self._mimeText or self.text(0)

    def setMimeText(self, text):
        """
        Set the mime text for drag and drop.

        :type text: str
        :rtype: None
        """
        self._mimeText = text

    def setHidden(self, value):
        """
        Set the item hidden.

        :type value: bool
        :rtype: None
        """
        QtWidgets.QTreeWidgetItem.setHidden(self, value)
        row = self.treeWidget().indexFromItem(self).row()
        self.combinedWidget().listView().setRowHidden(row, value)

    def setDragEnabled(self, value):
        """
        Set True if the item can be dragged.

        :type value: bool
        :rtype: None
        """
        self._dragEnabled = value

    def dragEnabled(self):
        """
        Return True if the item can be dragged.

        :rtype: bool
        """
        return self._dragEnabled

    def setData(self, column, role, value):
        """
        Reimplemented to set the search text to dirty.

        Set the value for the item's column and role to the given value.

        :type column: int or str
        :type role: int
        :type value: QtCore.QVariant
        :rtype: None
        """
        self._searchText = None
        QtWidgets.QTreeWidgetItem.setData(self, column, role, value)

    def setIcon(self, column, icon, color=None):
        """
        Set the icon to be displayed in the given column.

        :type column: int or str
        :type icon: QtGui.QIcon
        :rtype: None
        """
        if isinstance(icon, basestring):
            if not os.path.exists(icon):
                color = color or studioqt.Color(255, 255, 255, 20)
                icon = studioqt.resource().icon("image", color=color)
            else:
                icon = QtGui.QIcon(icon)

        if isinstance(column, basestring):
            self._icon[column] = icon
        
        else:
            self._pixmap[column] = None
            QtWidgets.QTreeWidgetItem.setIcon(self, column, icon)

    def data(self, column, role, **kwargs):
        """
        Reimplemented to add support for setting the sort data.

        :type column: int
        :type role: int
        :type kwargs: dict
        :rtype: object
        """
        if role == QtCore.Qt.DisplayRole:

            text = self.sortText(column)
            if not text:
                text = QtWidgets.QTreeWidgetItem.data(self, column, role)

        else:
            text = QtWidgets.QTreeWidgetItem.data(self, column, role)

        return text

    def setText(self, column, value, alignment=None):
        """
        Set the text to be displayed for the given column.

        :type column: int or str
        :type value: str
        :rtype: None
        """
        self.textColumnOrder.append(column)

        if isinstance(column, basestring):
            self._text[column] = value, alignment
        else:
            QtWidgets.QTreeWidgetItem.setText(self, column, value)

    def text(self, column):
        """
        Return the text for the given column.

        :type column: int or str
        :rtype: str
        """
        # if isinstance(column, int):
        #     column = self.treeWidget().labelFromColumn(column)

        if isinstance(column, basestring):
            text = self._sortText.get(column, None)
            if not text:
                text, alignment = self._text.get(column, ("", None))
        else:
            text = QtWidgets.QTreeWidgetItem.text(self, column)

        return text

    def setSortText(self, column, value):
        """
        Set the sort data for the given column.

        :type column: int
        :int value: str
        :rtype: None
        """
        self._sortText[column] = value

    def sortText(self, column):
        """
        Return the sort data for the given column.

        :type column: int
        :rtype: str
        """

        if isinstance(column, int):
            column = self.treeWidget().labelFromColumn(column)

        text = self._sortText.get(column, None)
        if not text:
            text, alignment = self._text.get(column, ("", None))

        return text

    def displayText(self, column):
        """
        Return the data to be displayed for the given column.

        :type column: int
        :rtype: str
        """
        text = None

        if isinstance(column, int):
            label = self.treeWidget().labelFromColumn(column)
            text, alignment = self._text.get(label, ("", None))

        if not text:
            text = QtWidgets.QTreeWidgetItem.data(self, column, QtCore.Qt.DisplayRole)

        return text

    def updateData(self):
        """
        Update the text data to the corresponding column.

        :rtype: None
        """
        treeWidget = self.treeWidget()

        for label in self._text:
            column = treeWidget.columnFromLabel(label)
            text, alignment = self._text[label]
            self.setText(column, text)

            if not alignment and label in self._icon:
                alignment = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom

            if alignment:
                self.setTextAlignment(column, alignment)

        for label in self._icon:
            column = treeWidget.columnFromLabel(label)
            self.setIcon(column, self._icon[label])

    def dpi(self):
        """
        Used for high resolution devices.

        :rtype: int
        """
        if self.combinedWidget():
            return self.combinedWidget().dpi()
        else:
            return 1

    def clicked(self):
        """
        Triggered when an item is clicked.

        :rtype: None
        """
        pass

    def takeFromTree(self):
        """
        Takes this item from the tree.
        """
        tree = self.treeWidget()
        parent = self.parent()

        if parent:
            parent.takeChild(parent.indexOfChild(self))
        else:
            tree.takeTopLevelItem(tree.indexOfTopLevelItem(self))

    def selectionChanged(self):
        """
        Triggered when an item has been either selected or deselected.

        :rtype: None
        """
        pass

    def doubleClicked(self):
        """
        Triggered when an item is double clicked.

        :rtype: None
        """
        pass

    def combinedWidget(self):
        """
        Returns the combined widget that contains the item.

        :rtype: CombinedWidget
        """
        combinedWidget = None

        if self.treeWidget():
            combinedWidget = self.treeWidget().parent()

        return combinedWidget

    def url(self):
        """
        Return the url object for the given item.

        :rtype: QtCore.QUrl or None
        """
        if not self._url:
            self._url = QtCore.QUrl(self.text(0))
        return self._url

    def setUrl(self, url):
        """
        Set the url object for the item.

        :type: QtCore.QUrl or None
        :rtype: None
        """
        self._url = url

    def searchText(self):
        """
        Return the search string used for finding the item.

        :rtype: str
        """
        if not self._searchText:
            searchText = []
            for column in range(self.columnCount()):
                text = self.data(column, QtCore.Qt.DisplayRole)
                if text:
                    searchText.append(text)
            self._searchText = " ".join(searchText)

        return self._searchText

    def setStretchToWidget(self, widget):
        """
        Set the width of the item to the width of the given widget.

        :type widget: QtWidgets.QWidget
        :rtype: None
        """
        self._stretchToWidget = widget

    def stretchToWidget(self):
        """
        Return the sretchToWidget.

        :rtype: QtWidgets.QWidget
        """
        return self._stretchToWidget

    def setSize(self, size):
        """
        Set the size for the item.

        :type size: QtCore.QSize
        :rtype: None
        """
        self._size = size

    def sizeHint(self):
        """
        Return the current size of the item.

        :rtype: QtCore.QSize
        """
        if self.stretchToWidget():
            if self._size:
                size = self._size
            else:
                size = self.combinedWidget().iconSize()

            w = self.stretchToWidget().width()
            h = size.height()
            return QtCore.QSize(w-20, h)

        if self._size:
            return self._size
        else:
            iconSize = self.combinedWidget().iconSize()

            if self.isTextVisible():
                w = iconSize.width()
                h = iconSize.width() + self.textHeight()
                iconSize = QtCore.QSize(w, h)

            return iconSize

    def setPixmap(self, column, pixmap):
        """
        Set the pixmap to be displayed in the given column.

        :type column: int
        :type pixmap: QtWidgets.QPixmap
        :rtype: None
        """
        self._pixmap[column] = pixmap

    def pixmap(self, column):
        """
        Return the pixmap for the given column.

        :type column:
        :rtype: QtWidgets.QPixmap
        """
        if not self._pixmap.get(column):
            icon = self.icon(column)
            if icon:
                size = QtCore.QSize(self.MAX_ICON_SIZE, self.MAX_ICON_SIZE)
                iconSize = icon.actualSize(size)
                self._pixmap[column] = icon.pixmap(iconSize)
        return self._pixmap.get(column)

    def padding(self):
        """
        Return the padding/border size for the item.

        :rtype: int
        """
        return self.combinedWidget().padding()

    def textHeight(self):
        """
        Return the height of the text for the item.

        :rtype: int
        """
        return self.combinedWidget().itemTextHeight()

    def isTextVisible(self):
        """
        Return True if the text is visible.

        :rtype: bool
        """
        return self.combinedWidget().isItemTextVisible()

    def textAlignment(self, column):
        """
        Return the text alignment for the label in the given column.

        :type column: int
        :rtype: QtCore.Qt.AlignmentFlag
        """
        defaultAlignment = QtCore.Qt.AlignVCenter
        alignment = QtWidgets.QTreeWidgetItem.textAlignment(self, column)
        if alignment == 0:
            return defaultAlignment
        else:
            return alignment

    # -----------------------------------------------------------------------
    # Support for mouse and key events
    # -----------------------------------------------------------------------

    def contextMenu(self, menu):
        """
        Return the context menu for the item.

        Reimplement in a subclass to return a custom context menu for the item.

        :rtype: QtWidgets.QMenu
        """
        pass

    def mouseLeaveEvent(self, event):
        """
        Reimplement in a subclass to receive mouse leave events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        pass

    def mouseEnterEvent(self, event):
        """
        Reimplement in a subclass to receive mouse enter events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        pass

    def mouseMoveEvent(self, event):
        """
        Reimplement in a subclass to receive mouse move events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        pass

    def mousePressEvent(self, event):
        """
        Reimplement in a subclass to receive mouse press events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        pass

    def mouseReleaseEvent(self, event):
        """
        Reimplement in a subclass to receive mouse release events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        pass

    def keyPressEvent(self, event):
        """
        Reimplement in a subclass to receive key press events for the item.

        :type event: QtWidgets.QKeyEvent
        :rtype: None
        """
        pass

    def keyReleaseEvent(self, event):
        """
        Reimplement in a subclass to receive key release events for the item.

        :type event: QtWidgets.QKeyEvent
        :rtype: None
        """
        pass

    # -----------------------------------------------------------------------
    # Support for custom painting
    # -----------------------------------------------------------------------

    def textColor(self):
        """
        Return the text color for the item.

        :rtype: QtWidgets.QtColor
        """
        return self.combinedWidget().textColor()

    def textSelectedColor(self):
        """
        Return the selected text color for the item.

        :rtype: QtWidgets.QtColor
        """
        return self.combinedWidget().textSelectedColor()

    def backgroundColor(self):
        """
        Return the background color for the item.

        :rtype: QtWidgets.QtColor
        """
        return self.combinedWidget().backgroundColor()

    def backgroundHoverColor(self):
        """
        Return the background color when the mouse is over the item.

        :rtype: QtWidgets.QtColor
        """
        return self.combinedWidget().backgroundHoverColor()

    def backgroundSelectedColor(self):
        """
        Return the background color when the item is selected.

        :rtype: QtWidgets.QtColor
        """
        return self.combinedWidget().backgroundSelectedColor()

    def rect(self):
        """
        Return the rect for the current paint frame.

        :rtype: QtCore.QRect
        """
        return self._rect

    def setRect(self, rect):
        """
        Set the rect for the current paint frame.

        :type rect: QtCore.QRect
        :rtype: None
        """
        self._rect = rect

    def visualRect(self, option):
        """
        Return the visual rect for the item.

        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: QtCore.QRect
        """
        rect = QtCore.QRect(option.rect)
        return rect

    def repaint(self):
        self.update(self.rect())

    def paintRow(self, painter, option, index):
        """
        Paint performs low-level painting for the item.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        :rtype: None
        """
        QtWidgets.QTreeWidget.drawRow(self.treeWidget(), painter, option, index)

    def paint(self, painter, option, index):
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
                self.paintText(painter, option, index)

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
        isSelected = option.state & QtWidgets.QStyle.State_Selected
        isMouseOver = option.state & QtWidgets.QStyle.State_MouseOver
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        visualRect = self.visualRect(option)

        if isSelected:
            color = self.backgroundSelectedColor()
            painter.setBrush(QtGui.QBrush(color))
        elif isMouseOver:
            color = self.backgroundHoverColor()
            painter.setBrush(QtGui.QBrush(color))
        else:
            color = self.backgroundColor()
            painter.setBrush(QtGui.QBrush(color))

        painter.drawRect(visualRect)

    def iconRect(self, option):
        """
        Return the icon rect for the item.

        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: QtCore.QRect
        """
        padding = self.padding()
        rect = self.visualRect(option)
        width = rect.width()
        height = rect.height()

        if self.isTextVisible() and self.combinedWidget().isIconView():
            height -= self.textHeight()

        width -= padding
        height -= padding

        rect.setWidth(width)
        rect.setHeight(height)

        x = 0
        x += float(padding) / 2
        x += float((width - rect.width())) / 2

        y = float((height - rect.height())) / 2
        y += float(padding) / 2

        rect.translate(x, y)
        return rect

    def paintIcon(self, painter, option, index, align=None):
        """
        Draw the icon for the item.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        column = index.column()
        pixmap = self.pixmap(column)

        if not pixmap:
            return

        rect = self.iconRect(option)

        pixmap = pixmap.scaled(
            rect.width(),
            rect.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )

        pixmapRect = QtCore.QRect(rect)
        pixmapRect.setWidth(pixmap.width())
        pixmapRect.setHeight(pixmap.height())

        align = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter

        x, y = 0, 0

        isAlignBottom = align == QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft \
                        or align == QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter \
                        or align == QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight

        isAlignHCenter = align == QtCore.Qt.AlignHCenter \
                         or align == QtCore.Qt.AlignCenter \
                         or align == QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom \
                         or align == QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop

        isAlignVCenter = align == QtCore.Qt.AlignVCenter \
                         or align == QtCore.Qt.AlignCenter \
                         or align == QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft \
                         or align == QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight

        if isAlignHCenter:
            x += float(rect.width() - pixmap.width()) / 2

        if isAlignVCenter:
            y += float(rect.height() - pixmap.height()) / 2

        elif isAlignBottom:
            y += float(rect.height() - pixmap.height())

        pixmapRect.translate(x, y)
        painter.drawPixmap(pixmapRect, pixmap)

    def fontSize(self):
        """
        Return the font size for the item.

        :rtype: int
        """
        return 11

    def font(self, column):
        """
        Return the font for the given column.

        :type column: int
        :rtype: QtWidgets.QFont
        """
        font = self._fonts.get(column, QtWidgets.QTreeWidgetItem.font(self, column))
        font.setPixelSize(self.fontSize() * self.dpi())
        return font

    def setFont(self, column, font):
        """
        Set the font for the given column.

        :type column: int
        :type font: QtWidgets.QFont
        :rtype: Noen
        """
        self._fonts[column] = font

    def paintText(self, painter, option, index):
        """
        Draw the text for the item.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        column = index.column()

        if column == 0 and self.combinedWidget().isTableView():
            return

        self._paintText(painter, option, column)

    def textWidth(self, column):
        text = self.displayText(column)

        font = self.font(column)
        metrics = QtGui.QFontMetricsF(font)
        textWidth = metrics.width(text)
        return textWidth

    def _paintText(self, painter, option, column):

        # text = self.text(column)
        # label = self.treeWidget().labelFromColumn(column)
        text = self.displayText(column)

        isSelected = option.state & QtWidgets.QStyle.State_Selected

        if isSelected:
            color = self.textSelectedColor()
        else:
            color = self.textColor()

        visualRect = self.visualRect(option)

        width = visualRect.width()
        height = visualRect.height()

        padding = self.padding()
        x = padding / 2
        y = padding / 2

        visualRect.translate(x, y)
        visualRect.setWidth(width - padding)
        visualRect.setHeight(height - padding)

        # textWidth = self.textWidth(column)
        align = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter

        font = self.font(column)
        metrics = QtGui.QFontMetricsF(font)
        textWidth = metrics.width(text)

        # # Check if the current text fits within the rect.
        if textWidth > visualRect.width() - padding:
            text = metrics.elidedText(text, QtCore.Qt.ElideRight, visualRect.width())
            if self.textAlignment(column) == QtCore.Qt.AlignLeft:
                align = self.textAlignment(column)
            else:
                align = QtCore.Qt.AlignLeft | self.textAlignment(column)
        else:
            align = self.textAlignment(column)

        pen = QtGui.QPen(color)
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(visualRect, align, text)