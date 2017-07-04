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

import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


import studioqt

from .combineditemviewmixin import CombinedItemViewMixin


logger = logging.getLogger(__name__)


class CombinedListView(CombinedItemViewMixin, QtWidgets.QListView):

    itemMoved = QtCore.Signal(object)
    itemDropped = QtCore.Signal(object)
    itemClicked = QtCore.Signal(object)
    itemDoubleClicked = QtCore.Signal(object)

    DEFAULT_DRAG_THRESHOLD = 10

    def __init__(self, *args):
        QtWidgets.QListView.__init__(self, *args)
        CombinedItemViewMixin.__init__(self)

        self._treeWidget = None
        self._rubberBand = None
        self._rubberBandStartPos = None
        self._rubberBandColor = QtGui.QColor(QtCore.Qt.white)
        self._customSortOrder = []

        self._drag = None
        self._dragStartPos = None
        self._dragStartIndex = None
        self._dropEnabled = True

        self.setSpacing(5)

        self.setMouseTracking(True)
        self.setSelectionRectVisible(True)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)

        self.clicked.connect(self._indexClicked)
        self.doubleClicked.connect(self._indexDoubleClicked)

    def _indexClicked(self, index):
        """
        Triggered when the user clicks on an index.

        :type index: QtCore.QModelIndex
        :rtype: None
        """
        item = self.itemFromIndex(index)
        item.clicked()
        self.setItemsSelected([item], True)
        self.itemClicked.emit(item)

    def _indexDoubleClicked(self, index):
        """
        Triggered when the user double clicks on an index.

        :type index: QtCore.QModelIndex
        :rtype: None
        """
        item = self.itemFromIndex(index)
        item.doubleClicked()
        self.setItemsSelected([item], True)
        self.itemDoubleClicked.emit(item)

    def treeWidget(self):
        """
        Return the tree widget that contains the item.

        :rtype: QtWidgets.QTreeWidget
        """
        return self._treeWidget

    def setTreeWidget(self, treeWidget):
        """
        Set the tree widget that contains the item.

        :type treeWidget: QtWidgets.QTreeWidget
        :rtype: None
        """
        self._treeWidget = treeWidget
        self.setModel(treeWidget.model())
        self.setSelectionModel(treeWidget.selectionModel())

    def scrollToItem(self, item, pos=None):
        """
        Ensures that the item is visible.

        :type item: QtWidgets.QTreeWidgetItem
        :type pos: QtCore.QPoint or None
        :rtype: None
        """
        index = self.indexFromItem(item)
        pos = pos or QtWidgets.QAbstractItemView.PositionAtCenter

        self.scrollTo(index, pos)

    def items(self):
        """
        Return all the items.

        :rtype: list[QtWidgets.QTreeWidgetItem]
        """
        return self.treeWidget().items()

    def itemAt(self, pos):
        """
        Return a pointer to the item at the coordinates p.

        The coordinates are relative to the tree widget's viewport().

        :type pos: QtCore.QPoint
        :rtype: QtWidgets.QTreeWidgetItem
        """
        index = self.indexAt(pos)
        return self.itemFromIndex(index)

    def indexFromItem(self, item):
        """
        Return the QModelIndex assocated with the given item.

        :type item: QtWidgets.QTreeWidgetItem.
        :rtype: QtCore.QModelIndex
        """
        return self.treeWidget().indexFromItem(item)

    def itemFromIndex(self, index):
        """
        Return a pointer to the QTreeWidgetItem assocated with the given index.

        :type index: QtCore.QModelIndex
        :rtype: QtWidgets.QTreeWidgetItem
        """
        return self.treeWidget().itemFromIndex(index)

    def insertItem(self, row, item):
        """
        Inserts the item at row in the top level in the view.

        :type row: int
        :type item: QtWidgets.QTreeWidgetItem
        :rtype: None
        """
        self.treeWidget().insertTopLevelItem(row, item)

    def takeItems(self, items):
        """
        Removes and returns the items from the view

        :type items: list[QtWidgets.QTreeWidgetItem]
        :rtype: list[QtWidgets.QTreeWidgetItem]
        """
        for item in items:
            row = self.treeWidget().indexOfTopLevelItem(item)
            self.treeWidget().takeTopLevelItem(row)

        return items

    def selectedItem(self):
        """
        Return the last selected non-hidden item.

        :rtype: QtWidgets.QTreeWidgetItem
        """
        return self.treeWidget().selectedItem()

    def selectedItems(self):
        """
        Return a list of all selected non-hidden items.

        :rtype: list[QtWidgets.QTreeWidgetItem]
        """
        return self.treeWidget().selectedItems()

    def setIndexesSelected(self, indexes, value):
        """
        Set the selected state for the given indexes.

        :type indexes: list[QtCore.QModelIndex]
        :type value: bool
        :rtype: None
        """
        items = self.itemsFromIndexes(indexes)
        self.setItemsSelected(items, value)

    def setItemsSelected(self, items, value):
        """
        Set the selected state for the given items.

        :type items: list[studioqt.CombinedWidgetItem]
        :type value: bool
        :rtype: None
        """
        self.treeWidget().blockSignals(True)
        for item in items:
            self.treeWidget().setItemSelected(item, value)
        self.treeWidget().blockSignals(False)

    def moveItems(self, items, itemAt):
        """
        Move the given items to the position of the destination row.

        :type items: list[studioqt.CombinedWidgetItem]
        :type itemAt: studioqt.CombinedWidgetItem
        :rtype: None
        """
        self.treeWidget().moveItems(items, itemAt)
        self.itemMoved.emit(items[-1])

    # ---------------------------------------------------------------------
    # Support for a custom colored rubber band.
    # ---------------------------------------------------------------------

    def createRubberBand(self):
        """
        Create a new instance of the selection rubber band.

        :rtype: QtWidgets.QRubberBand
        """
        rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        palette = QtGui.QPalette()
        color = self.rubberBandColor()
        palette.setBrush(QtGui.QPalette.Highlight, QtGui.QBrush(color))
        rubberBand.setPalette(palette)
        return rubberBand

    def setRubberBandColor(self, color):
        """
        Set the color for the rubber band.

        :type color: QtGui.QColor
        :rtype: None
        """
        self._rubberBand = None
        self._rubberBandColor = color

    def rubberBandColor(self):
        """
        Return the rubber band color for this widget.

        :rtype: QtGui.QColor
        """
        return self._rubberBandColor

    def rubberBand(self):
        """
        Return the selection rubber band for this widget.

        :rtype: QtWidgets.QRubberBand
        """
        if not self._rubberBand:
            self.setSelectionRectVisible(False)
            self._rubberBand = self.createRubberBand()

        return self._rubberBand

    # ---------------------------------------------------------------------
    # Events
    # ---------------------------------------------------------------------

    def validateDragEvent(self, event):
        """
        Validate the drag event.

        :type event: QtWidgets.QMouseEvent
        :rtype: bool
        """
        return QtCore.Qt.LeftButton == event.mouseButtons()

    def mousePressEvent(self, event):
        """
        Triggered when the user presses the mouse button for the viewport.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        item = self.itemAt(event.pos())
        if not item:
            self.clearSelection()

        CombinedItemViewMixin.mousePressEvent(self, event)
        if event.isAccepted():
            QtWidgets.QListView.mousePressEvent(self, event)
            self.combinedWidget().treeWidget().setItemSelected(item, True)

        self.endDrag()
        self._dragStartPos = event.pos()

        isLeftButton = self.mousePressButton() == QtCore.Qt.LeftButton
        isItemDraggable = item and item.dragEnabled()
        isSelectionEmpty = not self.selectedItems()

        if isLeftButton and (isSelectionEmpty or not isItemDraggable):
            self.rubberBandStartEvent(event)

    def mouseMoveEvent(self, event):
        """
        Triggered when the user moves the mouse over the current viewport.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        if not self.isDraggingItems():

            isLeftButton = self.mousePressButton() == QtCore.Qt.LeftButton

            if isLeftButton and self.rubberBand().isHidden() and self.selectedItems():
                self.startDrag(event)
            else:
                CombinedItemViewMixin.mouseMoveEvent(self, event)
                QtWidgets.QListView.mouseMoveEvent(self, event)

            if isLeftButton:
                self.rubberBandMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Triggered when the user releases the mouse button for this viewport.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        item = self.itemAt(event.pos())
        items = self.selectedItems()

        CombinedItemViewMixin.mouseReleaseEvent(self, event)

        if item not in items:
            if event.button() != QtCore.Qt.MidButton:
                QtWidgets.QListView.mouseReleaseEvent(self, event)
        elif not items:
            QtWidgets.QListView.mouseReleaseEvent(self, event)

        self.endDrag()
        self.rubberBand().hide()

    def rubberBandStartEvent(self, event):
        """
        Triggered when the user presses an empty area.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        self._rubberBandStartPos = event.pos()
        rect = QtCore.QRect(self._rubberBandStartPos, QtCore.QSize())

        rubberBand = self.rubberBand()
        rubberBand.setGeometry(rect)
        rubberBand.show()

    def rubberBandMoveEvent(self, event):
        """
        Triggered when the user moves the mouse over the current viewport.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        if self.rubberBand() and self._rubberBandStartPos:
            rect = QtCore.QRect(self._rubberBandStartPos, event.pos())
            rect = rect.normalized()
            self.rubberBand().setGeometry(rect)

    # -----------------------------------------------------------------------
    # Support for drag and drop
    # -----------------------------------------------------------------------

    def rowAt(self, pos):
        """
        Return the row for the given pos.

        :type pos: QtCore.QPoint
        :rtype: int
        """
        return self.treeWidget().rowAt(pos)

    def itemsFromUrls(self, urls):
        """
        Return items from the given url objects.

        :type urls: list[QtCore.QUrl]
        :rtype: list[studioqt.CombinedWidgetItem]
        """
        items = []
        for url in urls:
            item = self.itemFromUrl(url)
            if item:
                items.append(item)
        return items

    def itemFromUrl(self, url):
        """
        Return the item from the given url object.

        :type url: QtCore.QUrl
        :rtype: studioqt.CombinedWidgetItem
        """
        return self.itemFromPath(url.path())

    def itemsFromPaths(self, paths):
        """
        Return the items from the given paths.

        :type paths: list[str]
        :rtype: list[studioqt.CombinedWidgetItem]
        """
        items = []
        for path in paths:
            item = self.itemFromPath(path)
            if item:
                items.append(item)
        return items

    def itemFromPath(self, path):
        """
        Return the item from the given path.

        :type path: str
        :rtype: studioqt.ListWidgetItem
        """
        for item in self.items():
            path_ = item.url().path()
            if path_ and path_ == path:
                return item

    def setDropEnabled(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self._dropEnabled = value

    def dropEnabled(self):
        """
        :rtype: bool
        """
        return self._dropEnabled

    def dragThreshold(self):
        """
        :rtype: int
        """
        return self.DEFAULT_DRAG_THRESHOLD

    def mimeData(self, items):
        """
        :type items: list[studioqt.ListWidgetItem]
        :rtype: QtCore.QMimeData
        """
        mimeData = QtCore.QMimeData()

        urls = [item.url() for item in items]
        text = "\n".join([item.mimeText() for item in items])

        mimeData.setUrls(urls)
        mimeData.setText(text)

        return mimeData

    def dropEvent(self, event):
        """
        This event handler is called when the drag is dropped on this widget.

        :type event: QtWidgets.QDropEvent
        :rtype: None
        """
        item = self.itemAt(event.pos())
        selectedItems = self.selectedItems()

        if selectedItems and item:
            if self.treeWidget().isSortByCustomOrder():
                self.moveItems(selectedItems, item)
            else:
                msg = "You can only re-order items when sorting by custom order."
                logger.info(msg)

        self.itemDropped.emit(event)

    def dragMoveEvent(self, event):
        """
        This event handler is called if a drag is in progress.

        :type event: QtGui.QDragMoveEvent
        :rtype: None
        """
        mimeData = event.mimeData()

        if (mimeData.hasText() or mimeData.hasUrls()) and self.dropEnabled():
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        """
        This event handler is called when the mouse enters this widget
        while a drag is in pregress.

        :type event: QtGui.QDragEnterEvent
        :rtype: None
        """
        mimeData = event.mimeData()

        if (mimeData.hasText() or mimeData.hasUrls()) and self.dropEnabled():
            event.accept()
        else:
            event.ignore()

    def isDraggingItems(self):
        """
        Return true if the user is currently dragging items.

        :rtype: bool
        """
        return bool(self._drag)

    def startDrag(self, event):
        """
        Starts a drag using the given event.

        :type event: QtCore.QEvent
        :rtype: None
        """
        if not self.dragEnabled():
            return

        if self._dragStartPos and hasattr(event, "pos"):

            item = self.itemAt(event.pos())

            if item and item.dragEnabled():

                self._dragStartIndex = self.indexAt(event.pos())

                point = self._dragStartPos - event.pos()
                dt = self.dragThreshold()

                if point.x() > dt or point.y() > dt or point.x() < -dt or point.y() < -dt:

                    items = self.selectedItems()
                    mimeData = self.mimeData(items)

                    pixmap = self.dragPixmap(item, items)
                    hotSpot = QtCore.QPoint(pixmap.width() / 2, pixmap.height() / 2)

                    self._drag = QtGui.QDrag(self)
                    self._drag.setPixmap(pixmap)
                    self._drag.setHotSpot(hotSpot)
                    self._drag.setMimeData(mimeData)
                    self._drag.start(QtCore.Qt.MoveAction)

    def endDrag(self):
        """
        Ends the current drag.

        :rtype: None
        """
        logger.debug("End Drag")
        self._dragStartPos = None
        self._dragStartIndex = None
        if self._drag:
            del self._drag
            self._drag = None

    def dragPixmap(self, item, items):
        """
        Show the drag pixmap for the given item.

        :type item: combinedwidgetitem.CombinedWidgetItem
        :type items: list[combinedwidgetitem.CombinedWidgetItem]
        
        :rtype: QtGui.QPixmap
        """
        rect = self.visualRect(self.indexFromItem(item))

        pixmap = QtGui.QPixmap()
        pixmap = pixmap.grabWidget(self, rect)

        if len(items) > 1:
            cWidth = 35
            cPadding = 5
            cText = str(len(items))
            cX = pixmap.rect().center().x() - float(cWidth / 2)
            cY = pixmap.rect().top() + cPadding
            cRect = QtCore.QRect(cX, cY, cWidth, cWidth)

            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(self.combinedWidget().backgroundSelectedColor())
            painter.drawEllipse(cRect.center(), float(cWidth / 2),
                                float(cWidth / 2))

            font = QtGui.QFont('Serif', 12, QtGui.QFont.Light)
            painter.setFont(font)
            painter.setPen(self.combinedWidget().textSelectedColor())
            painter.drawText(cRect, QtCore.Qt.AlignCenter, str(cText))

        return pixmap
