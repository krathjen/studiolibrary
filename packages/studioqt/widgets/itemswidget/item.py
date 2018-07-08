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

import os
import math
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt

logger = logging.getLogger(__name__)


class GlobalSignals(QtCore.QObject):
    """"""
    blendChanged = QtCore.Signal(float)


class IconThread(QtCore.QThread):
    """A convenience class for loading an icon in a thread."""

    triggered = QtCore.Signal(object)

    def __init__(self, path, *args):
        QtCore.QThread.__init__(self, *args)

        self._path = path

    def run(self):
        """
        The starting point for the thread.

        :rtype: None 
        """
        if self._path:
            image = QtGui.QImage(unicode(self._path))
            self.triggered.emit(image)


class Item(QtWidgets.QTreeWidgetItem):
    """The Item is used to hold rows of information for an item view."""

    SortRole = "SortRole"
    DataRole = "DataRole"

    MAX_ICON_SIZE = 256

    DEFAULT_FONT_SIZE = 13
    DEFAULT_PLAYHEAD_COLOR = QtGui.QColor(255, 255, 255, 220)

    THUMBNAIL_COLUMN = 0
    ENABLE_THUMBNAIL_THREAD = False  # Still in development/testing

    _globalSignals = GlobalSignals()
    blendChanged = _globalSignals.blendChanged

    def __init__(self, *args):
        QtWidgets.QTreeWidgetItem.__init__(self, *args)

        self._url = None
        self._path = None
        self._size = None
        self._rect = None
        self._textColumnOrder = []

        self._data = {}

        self._icon = {}
        self._fonts = {}
        self._thread = None
        self._pixmap = {}
        self._pixmapRect = None
        self._pixmapScaled = None

        self._iconPath = ""
        self._thumbnailIcon = None

        self._underMouse = False
        self._searchText = None
        self._infoWidget = None

        self._groupItem = None
        self._groupColumn = 0

        self._mimeText = None
        self._itemsWidget = None
        self._stretchToWidget = None

        self._dragEnabled = True

        self._imageSequence = None
        self._imageSequencePath = None

        self._blendValue = 0.0
        self._blendPreviousValue = 0.0
        self._blendPosition = None
        self._blendingEnabled = False

    def __eq__(self, other):
        return id(other) == id(self)

    def __ne__(self, other):
        return id(other) != id(self)

    def __del__(self):
        """
        Make sure the sequence is stopped when deleted.

        :rtype: None
        """
        self.stop()

    def columnFromLabel(self, label):
        if self.treeWidget():
            return self.treeWidget().columnFromLabel(label)
        else:
            return None

    def labelFromColumn(self, column):
        if self.treeWidget():
            return self.treeWidget().labelFromColumn(column)
        else:
            return None

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
        self.itemsWidget().listView().setRowHidden(row, value)

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

    def setIcon(self, column, icon, color=None):
        """
        Set the icon to be displayed in the given column.

        :type column: int or str
        :type icon: QtGui.QIcon
        :type color: QtGui.QColor or None
        :rtype: None
        """
        # Safe guard for when the class is being used without the gui.
        isAppRunning = bool(QtWidgets.QApplication.instance())
        if not isAppRunning:
            return

        if isinstance(icon, basestring):
            if not os.path.exists(icon):
                color = color or studioqt.Color(255, 255, 255, 20)
                icon = studioqt.resource.icon("image", color=color)
            else:
                icon = QtGui.QIcon(icon)

        if isinstance(column, basestring):
            self._icon[column] = icon
        else:
            self._pixmap[column] = None
            QtWidgets.QTreeWidgetItem.setIcon(self, column, icon)

        self.updateIcon()

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

        if role == self.SortRole:

            if isinstance(column, int):
                column = self.labelFromColumn(column)

            self._data.setdefault(column, {})
            self._data[column]["sortValue"] = value

        elif role == QtCore.Qt.DisplayRole:

            if isinstance(column, int):
                column = self.labelFromColumn(column)

            self._data.setdefault(column, {})
            self._data[column]["displayValue"] = value

        elif role == self.DataRole:

            if isinstance(column, int):
                column = self.labelFromColumn(column)

            self._data.setdefault(column, {})
            self._data[column]["value"] = value

        else:
            QtWidgets.QTreeWidgetItem.setData(self, column, role, value)

    def data(self, column, role):
        """
        Reimplemented to add support for setting the sort data.

        :type column: int or str
        :type role: int
        :rtype: object
        """
        if role == self.SortRole:

            if isinstance(column, int):
                column = self.labelFromColumn(column)

            value = self._data.get(column, {}).get("sortValue")
            if not value:
                value = self._data.get(column, {}).get("value", "")

        elif role == QtCore.Qt.DisplayRole:

            if isinstance(column, int):
                column = self.labelFromColumn(column)

            value = self._data.get(column, {}).get("displayValue")
            if not value:
                value = self._data.get(column, {}).get("value", "")

        elif role == self.DataRole:

            if isinstance(column, int):
                column = self.labelFromColumn(column)

            value = self._data.get(column, {}).get("value") or ""

        else:
            value = QtWidgets.QTreeWidgetItem.data(self, column, role)

        return value

    def setItemData(self, data):
        """
        Set the given dictionary as the data for the item.

        :type data: dict
        :rtype: None
        """
        for column in data:

            self._data.setdefault(column, {})

            columnData = data.get(column, {})

            if isinstance(columnData, dict):
                self._data[column].update(columnData)
            else:
                self._data[column]["value"] = columnData

    def itemData(self):
        """
        Return the item data for this item.

        :rtype: dict
        """
        return self._data

    def setName(self, text):
        """
        Set the name that is shown under the icon and in the Name column.

        :type text: str
        :rtype: None 
        """
        self.setText("icon", text)
        self.setText("name", text)

    def name(self):
        """
        Return text for the Name column.

        :rtype: str
        """
        return self.text("name")

    def setText(self, label, value):
        """
        Set the text to be displayed for the given column.

        :type label: int or str
        :type value: str
        :rtype: None
        """
        self.setData(label, self.DataRole, unicode(value))

    def text(self, label):
        """
        Return the text for the given column.

        :type label: int or str
        :rtype: str
        """
        return self.data(label, self.DataRole)

    def setSortText(self, label, value):
        """
        Set the sort data for the given column.

        :type label: str
        :int value: str
        :rtype: None
        """
        self.setData(label, self.SortRole, unicode(value))

    def sortText(self, label):
        """
        Return the sort data for the given column.

        :type label: str
        :rtype: str
        """
        return self.data(label, self.SortRole)

    def setDisplayText(self, label, value):
        """
        Set the sort data for the given column.

        :type label: str
        :int value: str
        :rtype: None
        """
        self.setData(label, QtCore.Qt.DisplayRole, unicode(value))

    def displayText(self, label):
        """
        Return the sort data for the given column.

        :type label: str
        :rtype: str
        """
        return unicode(self.data(label, QtCore.Qt.DisplayRole))

    def update(self):
        """
        Refresh the visual state of the icon.

        :rtype: None 
        """
        self.updateIcon()
        self.updateFrame()

    def updateIcon(self):
        """
        Clear the pixmap cache for the item.

        :rtype: None 
        """
        self._pixmap = {}
        self._pixmapRect = None
        self._pixmapScaled = None
        self._thumbnailIcon = None

    def dpi(self):
        """
        Used for high resolution devices.

        :rtype: int
        """
        if self.itemsWidget():
            return self.itemsWidget().dpi()
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
        self.resetBlending()

    def doubleClicked(self):
        """
        Triggered when an item is double clicked.

        :rtype: None
        """
        pass

    def setGroupItem(self, groupItem):
        self._groupItem = groupItem

    def groupItem(self):
        return self._groupItem

    def itemsWidget(self):
        """
        Returns the items widget that contains the items.

        :rtype: ItemsWidget
        """
        itemsWidget = None

        if self.treeWidget():
            itemsWidget = self.treeWidget().parent()

        return itemsWidget

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
            self._searchText = unicode(self._data)

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

    def sizeHint(self, column=0):
        """
        Return the current size of the item.

        :type column: int
        :rtype: QtCore.QSize
        """
        if self.stretchToWidget():
            if self._size:
                size = self._size
            else:
                size = self.itemsWidget().iconSize()

            w = self.stretchToWidget().width()
            h = size.height()
            return QtCore.QSize(w - 20, h)

        if self._size:
            return self._size
        else:
            iconSize = self.itemsWidget().iconSize()

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

    def thumbnailPath(self):
        """
        Return the thumbnail path on disk.

        :rtype: None or str
        """
        return ""

    def _thumbnailFromImage(self, image):
        """
        Called after the given image object has finished loading.

        :type image: QtGui.QImage
        :rtype: None  
        """
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        icon = QtGui.QIcon(pixmap)

        self._thumbnailIcon = icon
        self.itemsWidget().update()

    def thumbnailIcon(self):
        """
        Return the thumbnail icon.

        :rtype: QtGui.QIcon
        """
        thumbnailPath = self.thumbnailPath()

        if not os.path.exists(thumbnailPath):
            color = self.textColor()
            thumbnailPath = studioqt.resource.icon("thumbnail", color=color)

        if not self._thumbnailIcon:

            if self.ENABLE_THUMBNAIL_THREAD and not self._thread:
                self._thread = IconThread(thumbnailPath)
                self._thread.triggered.connect(self._thumbnailFromImage)
                self._thread.start()
            else:
                self._thumbnailIcon = QtGui.QIcon(thumbnailPath)

        return self._thumbnailIcon

    def icon(self, column):
        """
        Overriding the icon method to add support for the thumbnail icon.

        :type column: int
        :rtype: QtGui.QIcon
        """
        icon = QtWidgets.QTreeWidgetItem.icon(self, column)

        if not icon and column == self.THUMBNAIL_COLUMN:
            icon = self.thumbnailIcon()

        return icon

    def pixmap(self, column):
        """
        Return the pixmap for the given column.

        :type column: int
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
        return self.itemsWidget().padding()

    def textHeight(self):
        """
        Return the height of the text for the item.

        :rtype: int
        """
        return self.itemsWidget().itemTextHeight()

    def isTextVisible(self):
        """
        Return True if the text is visible.

        :rtype: bool
        """
        return self.itemsWidget().isItemTextVisible()

    def textAlignment(self, column):
        """
        Return the text alignment for the label in the given column.

        :type column: int
        :rtype: QtCore.Qt.AlignmentFlag
        """
        if self.itemsWidget().isIconView():
            return QtCore.Qt.AlignCenter
        else:
            return QtWidgets.QTreeWidgetItem.textAlignment(self, column)

    # -----------------------------------------------------------------------
    # Support for mouse and key events
    # -----------------------------------------------------------------------

    def underMouse(self):
        """Return True if the item is under the mouse cursor."""
        return self._underMouse

    def contextMenu(self, menu):
        """
        Return the context menu for the item.

        Reimplement in a subclass to return a custom context menu for the item.

        :rtype: QtWidgets.QMenu
        """
        pass

    def dropEvent(self, event):
        """
        Reimplement in a subclass to receive drop events for the item.

        :type event: QtWidgets.QDropEvent
        :rtype: None
        """

    def mouseLeaveEvent(self, event):
        """
        Reimplement in a subclass to receive mouse leave events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        self._underMouse = False
        self.stop()

    def mouseEnterEvent(self, event):
        """
        Reimplement in a subclass to receive mouse enter events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        self._underMouse = True
        self.play()

    def mouseMoveEvent(self, event):
        """
        Reimplement in a subclass to receive mouse move events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        self.blendingEvent(event)
        self.imageSequenceEvent(event)

    def mousePressEvent(self, event):
        """
        Reimplement in a subclass to receive mouse press events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        if event.button() == QtCore.Qt.MidButton:
            self._blendPosition = event.pos()

    def mouseReleaseEvent(self, event):
        """
        Reimplement in a subclass to receive mouse release events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        if self.isBlending():
            self._blendPosition = None
            self._blendPreviousValue = self.blendValue()

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
        # This will be changed to use the palette soon.
        # Note: There were problems with older versions of Qt's palette (Maya 2014).
        # Eg:
        # return self.itemsWidget().palette().color(self.itemsWidget().foregroundRole())
        return self.itemsWidget().textColor()

    def textSelectedColor(self):
        """
        Return the selected text color for the item.

        :rtype: QtWidgets.QtColor
        """
        return self.itemsWidget().textSelectedColor()

    def backgroundColor(self):
        """
        Return the background color for the item.

        :rtype: QtWidgets.QtColor
        """
        return self.itemsWidget().backgroundColor()

    def backgroundHoverColor(self):
        """
        Return the background color when the mouse is over the item.

        :rtype: QtWidgets.QtColor
        """
        return self.itemsWidget().backgroundHoverColor()

    def backgroundSelectedColor(self):
        """
        Return the background color when the item is selected.

        :rtype: QtWidgets.QtColor
        """
        return self.itemsWidget().backgroundSelectedColor()

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

    def paintRow(self, painter, option, index):
        """
        Paint performs low-level painting for the item.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        :rtype: None
        """
        QtWidgets.QTreeWidget.drawRow(
            self.treeWidget(),
            painter,
            option,
            index
        )

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

            if index.column() == 0:
                if self.imageSequence():
                    self.paintPlayhead(painter, option)
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

        if self.isTextVisible() and self.itemsWidget().isIconView():
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

    def scalePixmap(self, pixmap, rect):
        """
        Scale the given pixmap to the give rect size.
        
        This method will cache the scaled pixmap if called with the same size.

        :type pixmap: QtGui.QPixmap
        :type rect: QtCore.QRect
        :rtype: QtGui.QPixmap
        """
        rectChanged = True

        if self._pixmapRect:
            widthChanged = self._pixmapRect.width() != rect.width()
            heightChanged = self._pixmapRect.height() != rect.height()

            rectChanged = widthChanged or heightChanged

        if not self._pixmapScaled or rectChanged:

            self._pixmapScaled = pixmap.scaled(
                rect.width(),
                rect.height(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )

            self._pixmapRect = rect

        return self._pixmapScaled

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
        pixmap = self.scalePixmap(pixmap, rect)

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

    def drawIconBorder(self, painter, pixmapRect):
        """
        Draw a border around the icon.

        :type painter: QtWidgets.QPainter
        :type pixmapRect: QtWidgets.QRect
        :rtype: None
        """
        pixmapRect = QtCore.QRect(pixmapRect)
        pixmapRect.setX(pixmapRect.x() - 5)
        pixmapRect.setY(pixmapRect.y() - 5)
        pixmapRect.setWidth(pixmapRect.width() + 5)
        pixmapRect.setHeight(pixmapRect.height() + 5)

        color = QtGui.QColor(255, 255, 255, 10)
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.setBrush(QtGui.QBrush(color))

        painter.drawRect(pixmapRect)

    def fontSize(self):
        """
        Return the font size for the item.

        :rtype: int
        """
        return self.DEFAULT_FONT_SIZE

    def font(self, column):
        """
        Return the font for the given column.

        :type column: int
        :rtype: QtWidgets.QFont
        """
        default = QtWidgets.QTreeWidgetItem.font(self, column)

        font = self._fonts.get(column, default)

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

        if column == 0 and self.itemsWidget().isTableView():
            return

        self._paintText(painter, option, column)

    def textWidth(self, column):
        text = self.text(column)

        font = self.font(column)
        metrics = QtGui.QFontMetricsF(font)
        textWidth = metrics.width(text)
        return textWidth

    def _paintText(self, painter, option, column):

        if self.itemsWidget().isIconView():
            text = self.name()
        else:
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

        font = self.font(column)
        align = self.textAlignment(column)
        metrics = QtGui.QFontMetricsF(font)

        if text:
            textWidth = metrics.width(text)
        else:
            textWidth = 1

        # # Check if the current text fits within the rect.
        if textWidth > visualRect.width() - padding:
            visualWidth = visualRect.width()
            text = metrics.elidedText(text, QtCore.Qt.ElideRight, visualWidth)
            align = QtCore.Qt.AlignLeft

        if self.itemsWidget().isIconView():
            align = align | QtCore.Qt.AlignBottom
        else:
            align = align | QtCore.Qt.AlignVCenter

        pen = QtGui.QPen(color)
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(visualRect, align, text)

    # ------------------------------------------------------------------------
    # Support for middle mouse blending (slider)
    # ------------------------------------------------------------------------

    def setBlendingEnabled(self, enabled):
        """
        Set if middle mouse slider is enabled.

        :type enabled: bool
        :rtype: None
        """
        self._blendingEnabled = enabled

    def isBlendingEnabled(self):
        """
        Return true if middle mouse slider is enabled.

        :rtype: None
        """
        return self._blendingEnabled

    def blendingEvent(self, event):
        """
        Called when the mouse moves while the middle mouse button is held down.

        :param event: QtGui.QMouseEvent
        :rtype: None
        """
        if self.isBlending():
            value = (event.pos().x() - self.blendPosition().x()) / 1.5
            value = math.ceil(value) + self.blendPreviousValue()
            try:
                self.setBlendValue(value)
            except Exception:
                self.stopBlending()

    def startBlendingEvent(self, event):
        """
        Called when the middle mouse button is pressed.

        :param event: QtGui.QMouseEvent
        :rtype: None
        """
        if self.isBlendingEnabled():
            if event.button() == QtCore.Qt.MidButton:
                self._blendPosition = event.pos()

    def stopBlending(self):
        """
        Called when the middle mouse button is released.

        :param event: QtGui.QMouseEvent
        :rtype: None
        """
        self._blendPosition = None
        self._blendPreviousValue = self.blendValue()

    def resetBlending(self):
        """
        Reset the blending value to zero.

        :rtype: None
        """
        self._blendValue = 0.0
        self._blendPreviousValue = 0.0

    def isBlending(self):
        """
        Return True if blending.

        :rtype: bool
        """
        return self.blendPosition() is not None

    def setBlendValue(self, value):
        """
        Set the blend value.

        :type value: float
        :rtype: bool
        """
        if self.isBlendingEnabled():
            self._blendValue = value
            self.blendChanged.emit(value)
            logger.debug("BLENDING:" + str(value))

    def blendValue(self):
        """
        Return the blend value.

        :rtype: float
        """
        return self._blendValue

    def blendPreviousValue(self):
        """
        :rtype: float
        """
        return self._blendPreviousValue

    def blendPosition(self):
        """
        :rtype: QtGui.QPoint
        """
        return self._blendPosition

    # ------------------------------------------------------------------------
    # Support animated image sequence
    # ------------------------------------------------------------------------

    def imageSequenceEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        if self.imageSequence():
            if studioqt.isControlModifier():
                if self.rect():
                    x = event.pos().x() - self.rect().x()
                    width = self.rect().width()
                    percent = 1.0 - (float(width - x) / float(width))
                    frame = int(self.imageSequence().frameCount() * percent)
                    self.imageSequence().jumpToFrame(frame)
                    self.updateFrame()

    def resetImageSequence(self):
        self._imageSequence = None

    def imageSequence(self):
        """
        :rtype: studioqt.ImageSequence
        """
        return self._imageSequence

    def setImageSequence(self, value):
        """
        :type value: studioqt.ImageSequence
        """
        self._imageSequence = value

    def setImageSequencePath(self, path):
        """
        :type path: str
        :rtype: None
        """
        self._imageSequencePath = path

    def imageSequencePath(self):
        """
        :rtype: str
        """
        return self._imageSequencePath

    def stop(self):
        """
        :rtype: None
        """
        if self.imageSequence():
            self.imageSequence().stop()

    def play(self):
        """
        :rtype: None
        """
        self.resetImageSequence()
        path = self.imageSequencePath() or self.thumbnailPath()

        movie = None

        if os.path.isfile(path) and path.lower().endswith(".gif"):

            movie = QtGui.QMovie(path)
            movie.setCacheMode(QtGui.QMovie.CacheAll)
            movie.frameChanged.connect(self._frameChanged)

        elif os.path.isdir(path):

            if not self.imageSequence():
                movie = studioqt.ImageSequence(path)
                movie.frameChanged.connect(self._frameChanged)

        if movie:
            self.setImageSequence(movie)
            self.imageSequence().start()

    def _frameChanged(self, frame):
        """Triggered when the movie object updates to the given frame."""
        if not studioqt.isControlModifier():
            self.updateFrame()

    def updateFrame(self):
        """Triggered when the movie object updates the current frame."""
        if self.imageSequence():
            pixmap = self.imageSequence().currentPixmap()
            self.setIcon(0, pixmap)

    def playheadColor(self):
        """
        Return the playhead color.

        :rtype: QtGui.Color
        """
        return self.DEFAULT_PLAYHEAD_COLOR

    def paintPlayhead(self, painter, option):
        """
        Paint the playhead if the item has an image sequence.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        imageSequence = self.imageSequence()

        if imageSequence and self.underMouse():

            count = imageSequence.frameCount()
            current = imageSequence.currentFrameNumber()

            if count > 0:
                percent = float((count + current) + 1) / count - 1
            else:
                percent = 0

            r = self.iconRect(option)
            c = self.playheadColor()

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(c))

            if percent <= 0:
                width = 0
            elif percent >= 1:
                width = r.width()
            else:
                width = (percent * r.width()) - 1

            height = 3 * self.dpi()
            y = r.y() + r.height() - (height - 1)

            painter.drawRect(r.x(), y, width, height)
