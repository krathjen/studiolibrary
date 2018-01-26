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
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt

from .combinedlistview import CombinedListView
from .combinedtreewidget import CombinedTreeWidget

from .combinedwidgetitem import CombinedWidgetItem
from .combineditemdelegate import CombinedItemDelegate


logger = logging.getLogger(__name__)


class CombinedWidget(QtWidgets.QWidget):

    IconMode = "icon"
    TableMode = "table"

    DEFAULT_PADDING = 5

    DEFAULT_ZOOM_AMOUNT = 90
    DEFAULT_TEXT_HEIGHT = 20
    DEFAULT_WHEEL_SCROLL_STEP = 2

    DEFAULT_MIN_SPACING = 0
    DEFAULT_MAX_SPACING = 50

    DEFAULT_MIN_LIST_SIZE = 15
    DEFAULT_MIN_ICON_SIZE = 50

    itemClicked = QtCore.Signal(object)
    itemDoubleClicked = QtCore.Signal(object)

    zoomChanged = QtCore.Signal(object)
    spacingChanged = QtCore.Signal(object)

    groupClicked = QtCore.Signal(object)

    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        self._dpi = 1
        self._padding = self.DEFAULT_PADDING

        w, h = self.DEFAULT_ZOOM_AMOUNT, self.DEFAULT_ZOOM_AMOUNT

        self._iconSize = QtCore.QSize(w, h)
        self._zoomAmount = self.DEFAULT_ZOOM_AMOUNT
        self._isItemTextVisible = True

        self._treeWidget = CombinedTreeWidget(self)

        self._listView = CombinedListView(self)
        self._listView.setTreeWidget(self._treeWidget)

        self._delegate = CombinedItemDelegate()
        self._delegate.setCombinedWidget(self)

        self._listView.setItemDelegate(self._delegate)
        self._treeWidget.setItemDelegate(self._delegate)

        self._toastWidget = studioqt.ToastWidget(self)
        self._toastWidget.hide()
        self._toastEnabled = True

        self._textColor = QtGui.QColor(255, 255, 255, 200)
        self._textSelectedColor = QtGui.QColor(255, 255, 255, 200)
        self._backgroundColor = QtGui.QColor(255, 255, 255, 30)
        self._backgroundHoverColor = QtGui.QColor(255, 255, 255, 35)
        self._backgroundSelectedColor = QtGui.QColor(30, 150, 255)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._treeWidget)
        layout.addWidget(self._listView)

        header = self.treeWidget().header()
        header.sortIndicatorChanged.connect(self._sortIndicatorChanged)

        self.setLayout(layout)

        self.listView().itemClicked.connect(self._itemClicked)
        self.listView().itemDoubleClicked.connect(self._itemDoubleClicked)

        self.treeWidget().itemClicked.connect(self._itemClicked)
        self.treeWidget().itemDoubleClicked.connect(self._itemDoubleClicked)

        self.itemMoved = self._listView.itemMoved
        self.itemDropped = self._listView.itemDropped
        self.itemSelectionChanged = self._treeWidget.itemSelectionChanged

    def _sortIndicatorChanged(self):
        """
        Triggered when the sort indicator changes.

        :rtype: None
        """
        pass

    def _itemClicked(self, item):
        """
        Triggered when the given item has been clicked.

        :type item: studioqt.CombinedWidgetItem
        :rtype: None
        """
        if isinstance(item, studioqt.CombinedWidgetItemGroup):
            self.groupClicked.emit(item)
        else:
            self.itemClicked.emit(item)

    def _itemDoubleClicked(self, item):
        """
        Triggered when the given item has been double clicked.

        :type item: studioqt.CombinedWidgetItem
        :rtype: None
        """
        self.itemDoubleClicked.emit(item)

    def setToastEnabled(self, enabled):
        """
        :type enabled: bool
        :rtype: None
        """
        self._toastEnabled = enabled

    def toastEnabled(self):
        """
        :rtype: bool
        """
        return self._toastEnabled

    def showToastMessage(self, text, duration=500):
        """
        Show a toast with the given text for the given duration.

        :type text: str
        :type duration: None or int
        :rtype: None
        """
        if self.toastEnabled():
            self._toastWidget.setDuration(duration)
            self._toastWidget.setText(text)
            self._toastWidget.show()

    def sortOrder(self):
        """
        Reimplemented for convenience.

        Calls self.treeWidget().sortOrder()
        """
        return self.treeWidget().sortOrder()

    def sortColumn(self):
        """
        Reimplemented for convenience.

        Calls self.treeWidget().sortColumn()
        """
        return self.treeWidget().sortColumn()

    def sortByColumn(self, *args, **kwargs):
        """
        Reimplemented for convenience.

        Calls self.treeWidget().sortByColumn(*args)
        """
        self.treeWidget().sortByColumn(*args, **kwargs)

    def groupOrder(self):
        """
        Reimplemented for convenience.

        Calls self.treeWidget().groupOrder()
        """
        return self.treeWidget().groupOrder()

    def groupColumn(self):
        """
        Reimplemented for convenience.

        Calls self.treeWidget().groupColumn()
        """
        return self.treeWidget().groupColumn()

    def groupByColumn(self, *args):
        """
        Reimplemented for convenience.

        Calls self.treeWidget().groupByColumn(*args)
        """
        self.treeWidget().groupByColumn(*args)

    def columnFromLabel(self, *args):
        """
        Reimplemented for convenience.
        
        :return: int 
        """
        return self.treeWidget().columnFromLabel(*args)

    def setColumnHidden(self, column, hidden):
        """
        Reimplemented for convenience.

        Calls self.treeWidget().setColumnHidden(column, hidden)
        """
        self.treeWidget().setColumnHidden(column, hidden)

    def setLocked(self, value):
        """
        Disables drag and drop.

        :Type value: bool
        :rtype: None
        """
        self.listView().setDragEnabled(not value)
        self.listView().setDropEnabled(not value)

    def scrollToItem(self, item):
        """
        Ensures that the item is visible.

        :type item: QtWidgets.QTreeWidgetItem
        :rtype: None
        """
        if self.isTableView():
            self.treeWidget().scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtCenter)
        elif self.isIconView():
            self.listView().scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtCenter)

    def scrollToSelectedItem(self):
        """
        Ensures that the item is visible.

        :rtype: None
        """
        item = self.selectedItem()
        if item:
            self.scrollToItem(item)

    def dpi(self):
        """
        return the zoom multiplier.

        Used for high resolution devices.

        :rtype: int
        """
        return self._dpi

    def setDpi(self, dpi):
        """
        Set the zoom multiplier.

        Used for high resolution devices.

        :type dpi: int
        """
        self._dpi = dpi
        self.refreshSize()

    def itemAt(self, pos):
        """
        Return the current item at the given pos.

        :type pos: QtWidgets.QPoint
        :rtype: studioqt.CombinedWidgetItem
        """
        if self.isIconView():
            return self.listView().itemAt(pos)
        else:
            return self.treeView().itemAt(pos)

    def insertItems(self, items, itemAt=None):
        """
        Insert the given items at the given itemAt position.

        :type items: list[studioqt.CombinedWidgetItem]
        :type itemAt: studioqt.CombinedWidgetItem
        :rtype: Nones
        """
        self.addItems(items)
        self.moveItems(items, itemAt=itemAt)
        self.treeWidget().setItemsSelected(items, True)

    def moveItems(self, items, itemAt=None):
        """
        Move the given items to the given itemAt position.

        :type items: list[studioqt.CombinedWidgetItem]
        :type itemAt: studioqt.CombinedWidgetItem
        :rtype: None
        """
        self.listView().moveItems(items, itemAt=itemAt)

    def listView(self):
        """
        Return the list view that contains the items.

        :rtype: ListView
        """
        return self._listView

    def treeWidget(self):
        """
        Return the tree widget that contains the items.

        :rtype: TreeWidget
        """
        return self._treeWidget

    def clear(self):
        """
        Reimplemented for convenience.

        Calls self.treeWidget().clear()
        """
        self.treeWidget().clear()

    def refresh(self):
        """
        Refresh the sorting and size of the items.

        :rtype: None
        """
        self.refreshSortBy()
        self.refreshSize()

    def refreshSize(self):
        """
        Refresh the size of the items.

        :rtype: None
        """
        self.setZoomAmount(self.zoomAmount() + 1)
        self.setZoomAmount(self.zoomAmount() - 1)
        self.repaint()

    def refreshSortBy(self):
        """
        Refresh the sorting of the items.

        :rtype: None
        """
        self.treeWidget().refreshSortBy()

    def itemFromIndex(self, index):
        """
        Return a pointer to the QTreeWidgetItem assocated with the given index.

        :type index: QtCore.QModelIndex
        :rtype: QtWidgets.QTreeWidgetItem
        """
        return self._treeWidget.itemFromIndex(index)

    def textFromItems(self, *args, **kwargs):
        """
        Return all data for the given items and given column.

        :rtype: list[str]
        """
        return self.treeWidget().textFromItems(*args, **kwargs)

    def textFromColumn(self, *args, **kwargs):
        """
        Return all data for the given column.

        :rtype: list[str]
        """
        return self.treeWidget().textFromColumn(*args, **kwargs)

    def toggleTextVisible(self):
        """
        Toggle the item text visibility.

        :rtype: None
        """
        if self.isItemTextVisible():
            self.setItemTextVisible(False)
        else:
            self.setItemTextVisible(True)

    def setItemTextVisible(self, value):
        """
        Set the visibility of the item text.

        :type value: bool
        :rtype: None
        """
        self._isItemTextVisible = value
        self.refreshSize()

    def isItemTextVisible(self):
        """
        Return the visibility of the item text.

        :rtype: bool
        """
        if self.isIconView():
            return self._isItemTextVisible
        else:
            return True

    def itemTextHeight(self):
        """
        Return the height of the item text.

        :rtype: int
        """
        return self.DEFAULT_TEXT_HEIGHT * self.dpi()

    def itemDelegate(self):
        """
        Return the item delegate for the views.

        :rtype: CombinedItemDelegate
        """
        return self._delegate

    def settings(self):
        """
        Return the current state of the widget.

        :rtype: dict
        """
        settings = {}

        settings["columnLabels"] = self.columnLabels()
        settings["padding"] = self.padding()
        settings["spacing"] = self.spacing()
        settings["zoomAmount"] = self.zoomAmount()
        settings["selectedPaths"] = self.selectedPaths()
        settings["textVisible"] = self.isItemTextVisible()
        settings.update(self.treeWidget().settings())

        return settings

    def setSettings(self, settings):
        """
        Set the current state of the widget.

        :type settings: dict
        :rtype: None
        """
        self.setToastEnabled(False)

        padding = settings.get("padding", 5)
        self.setPadding(padding)

        spacing = settings.get("spacing", 2)
        self.setSpacing(spacing)

        zoomAmount = settings.get("zoomAmount", 100)
        self.setZoomAmount(zoomAmount)

        selectedPaths = settings.get("selectedPaths", [])
        self.selectPaths(selectedPaths)

        itemTextVisible = settings.get("textVisible", True)
        self.setItemTextVisible(itemTextVisible)

        self.treeWidget().setSettings(settings)

        self.setToastEnabled(True)

        return settings

    def createSortByMenu(self):
        return self.treeWidget().createSortByMenu()

    def createGroupByMenu(self):
        return self.treeWidget().createGroupByMenu()

    def createCopyTextMenu(self):
        return self.treeWidget().createCopyTextMenu()

    def createItemSettingsMenu(self):

        menu = QtWidgets.QMenu("Item View", self)

        action = studioqt.SeparatorAction("View Settings", menu)
        menu.addAction(action)

        action = studioqt.SliderAction("Size", menu)
        action.slider().setMinimum(10)
        action.slider().setMaximum(200)
        action.slider().setValue(self.zoomAmount())
        action.slider().valueChanged.connect(self.setZoomAmount)
        menu.addAction(action)

        action = studioqt.SliderAction("Border", menu)
        action.slider().setMinimum(0)
        action.slider().setMaximum(20)
        action.slider().setValue(self.padding())
        action.slider().valueChanged.connect(self.setPadding)
        menu.addAction(action)
        #
        action = studioqt.SliderAction("Spacing", menu)
        action.slider().setMinimum(self.DEFAULT_MIN_SPACING)
        action.slider().setMaximum(self.DEFAULT_MAX_SPACING)
        action.slider().setValue(self.spacing())
        action.slider().valueChanged.connect(self.setSpacing)
        menu.addAction(action)

        action = studioqt.SeparatorAction("Item Options", menu)
        menu.addAction(action)

        action = QtWidgets.QAction("Show labels", menu)
        action.setCheckable(True)
        action.setChecked(self.isItemTextVisible())
        action.triggered[bool].connect(self.setItemTextVisible)
        menu.addAction(action)

        return menu

    def createSettingsMenu(self):
        """
        Create and return the settings menu for the widget.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu("Item View", self)

        menu.addSeparator()

        action = QtWidgets.QAction("Show labels", menu)
        action.setCheckable(True)
        action.setChecked(self.isItemTextVisible())
        action.triggered[bool].connect(self.setItemTextVisible)
        menu.addAction(action)

        menu.addSeparator()

        sortByMenu = self.treeWidget().createSortByMenu()
        menu.addMenu(sortByMenu)

        groupByMenu = self.treeWidget().createGroupByMenu()
        menu.addMenu(groupByMenu)

        copyTextMenu = self.treeWidget().createCopyTextMenu()
        menu.addMenu(copyTextMenu)

        menu.addSeparator()

        action = studioqt.SliderAction("Size", menu)
        action.slider().setMinimum(10)
        action.slider().setMaximum(200)
        action.slider().setValue(self.zoomAmount())
        action.slider().valueChanged.connect(self.setZoomAmount)
        menu.addAction(action)

        action = studioqt.SliderAction("Border", menu)
        action.slider().setMinimum(0)
        action.slider().setMaximum(20)
        action.slider().setValue(self.padding())
        action.slider().valueChanged.connect(self.setPadding)
        menu.addAction(action)
        #
        action = studioqt.SliderAction("Spacing", menu)
        action.slider().setMinimum(self.DEFAULT_MIN_SPACING)
        action.slider().setMaximum(self.DEFAULT_MAX_SPACING)
        action.slider().setValue(self.spacing())
        action.slider().valueChanged.connect(self.setSpacing)
        menu.addAction(action)

        return menu

    def createItemsMenu(self, items=None):
        """
        Create the item menu for given item.

        :rtype: QtWidgets.QMenu
        """
        item = items or self.selectedItem()

        menu = QtWidgets.QMenu(self)

        if item:
            try:
                item.contextMenu(menu)
            except Exception, msg:
                logger.exception(msg)
        else:
            action = QtWidgets.QAction(menu)
            action.setText("No Item selected")
            action.setDisabled(True)

            menu.addAction(action)

        return menu

    def createContextMenu(self):
        """
        Create and return the context menu for the widget.

        :rtype: QtWidgets.QMenu
        """
        menu = self.createItemsMenu()

        settingsMenu = self.createSettingsMenu()
        menu.addMenu(settingsMenu)

        return menu

    def contextMenuEvent(self, event):
        """
        Show the context menu.

        :type event: QtCore.QEvent
        :rtype: None
        """
        menu = self.createContextMenu()
        point = QtGui.QCursor.pos()
        return menu.exec_(point)

    # ------------------------------------------------------------------------
    # Support for saving the current item order.
    # ------------------------------------------------------------------------

    def itemData(self, columnLabels):
        """
        Return all column data for the given column labels.

        :type columnLabels: list[str]
        :rtype: dict
                
        """
        data = {}

        for item in self.items():
            key = item.id()

            for columnLabel in columnLabels:
                column = self.treeWidget().columnFromLabel(columnLabel)
                value = item.data(column, QtCore.Qt.EditRole)

                data.setdefault(key, {})
                data[key].setdefault(columnLabel, value)

        return data

    def setItemData(self, data):
        """
        Set the item data for all the current items.

        :type data: dict
        :rtype: None
        """
        for item in self.items():
            key = item.id()

            if key in data:

                for column in data[key]:
                    value = data[key].get(column)

                    if value is not None:
                        item.setText(column, value)

                item.updateData()

        self.refreshSortBy()

    def updateColumns(self):
        """
        Update the column labels with the current item data.

        :rtype: None
        """
        self.treeWidget().updateHeaderLabels()

    def columnLabels(self):
        """
        Set all the column labels.

        :rtype: list[str]
        """
        return self.treeWidget().columnLabels()

    def _removeDuplicates(self, labels):
        """
        Removes duplicates from a list in Python, whilst preserving order.

        :type labels: list[str]
        :rtype: list[str]
        """
        s = set()
        sadd = s.add
        return [x for x in labels if not (x in s or sadd(x))]

    def setColumnLabels(self, labels):
        """
        Set the columns for the widget.

        :type labels: list[str]
        :rtype: None
        """
        labels = self._removeDuplicates(labels)

        if "Custom Order" not in labels:
            labels.append("Custom Order")

        if "Search Order" not in labels:
            labels.append("Search Order")

        self.treeWidget().setHeaderLabels(labels)

        self.setColumnHidden("Custom Order", True)
        self.setColumnHidden("Search Order", True)

    def items(self):
        """
        Return all the items in the widget.

        :rtype: list[CombinedWidgetItem]
        """
        return self._treeWidget.items()

    def addItems(self, items):
        """
        Add the given items to the combined widget.

        :type items: list[studioqt.CombinedWidgetItem]
        :rtype: None
        """
        self._treeWidget.addTopLevelItems(items)
        for item in items:
            item.updateData()

    def addItem(self, item):
        """
        Add the item to the tree widget.

        :type item: CombinedWidgetItem
        :rtype: None
        """
        self.addItems([item])

    def columnLabelsFromItems(self):
        """
        Return the column labels from all the items.

        :rtype: list[str]
        """

        seq = []
        for item in self.items():
            seq.extend(item.textColumnOrder)

        seen = set()
        return [x for x in seq if x not in seen and not seen.add(x)]

    def setItems(self, items, data=None, sortEnabled=True):
        """
        Sets the items to the widget.

        :type items: list[CombinedWidgetItem]
        :type data: dict
        :type sortEnabled: bool
        
        :rtype: None
        """

        if sortEnabled:
            settings = self.treeWidget().sortBySettings()

        self.treeWidget().clear()
        self.treeWidget().addTopLevelItems(items)

        self.setColumnLabels(self.columnLabelsFromItems())

        if data:
            self.setItemData(data)

        if sortEnabled:
            self.treeWidget().setSortBySettings(settings)

    def padding(self):
        """
        Return the item padding.

        :rtype: int
        """
        return self._padding

    def setPadding(self, value):
        """
        Set the item padding.

        :type: int
        :rtype: None
        """
        if value % 2 == 0:
            self._padding = value
        else:
            self._padding = value + 1
        self.repaint()

        self.showToastMessage("Border: " + str(value))

    def spacing(self):
        """
        Return the spacing between the items.

        :rtype: int
        """
        return self._listView.spacing()

    def setSpacing(self, spacing):
        """
        Set the spacing between the items.

        :type spacing: int
        :rtype: None
        """
        self._listView.setSpacing(spacing)
        self.scrollToSelectedItem()

        self.showToastMessage("Spacing: " + str(spacing))

    def iconSize(self):
        """
        Return the icon size for the views.

        :rtype: QtCore.QSize
        """
        return self._iconSize

    def setIconSize(self, size):
        """
        Set the icon size for the views.

        :type size: QtCore.QSize
        :rtype: None
        """
        self._iconSize = size
        self._listView.setIconSize(size)
        self._treeWidget.setIconSize(size)

    def clearSelection(self):
        """
        Clear the user selection.

        :rtype: None
        """
        self._treeWidget.clearSelection()

    def wheelScrollStep(self):
        """
        Return the wheel scroll step amount.

        :rtype: int
        """
        return self.DEFAULT_WHEEL_SCROLL_STEP

    def model(self):
        """
        Return the model that this view is presenting.

        :rtype: QAbstractItemModel
        """
        return self._treeWidget.model()

    def indexFromItem(self, item):
        """
        Return the QModelIndex assocated with the given item.

        :type item: QtWidgets.QTreeWidgetItem.
        :rtype: QtCore.QModelIndex
        """
        return self._treeWidget.indexFromItem(item)

    def selectionModel(self):
        """
        Return the current selection model.

        :rtype: QtWidgets.QItemSelectionModel
        """
        return self._treeWidget.selectionModel()

    def selectedItem(self):
        """
        Return the last selected non-hidden item.

        :rtype: QtWidgets.QTreeWidgetItem
        """
        return self._treeWidget.selectedItem()

    def selectedItems(self):
        """
        Return a list of all selected non-hidden items.

        :rtype: list[QtWidgets.QTreeWidgetItem]
        """
        return self._treeWidget.selectedItems()

    def setItemHidden(self, item, value):
        """
        Set the visibility of given item.

        :type item: QtWidgets.QTreeWidgetItem
        :type value: bool
        :rtype: None
        """
        item.setHidden(value)

    def setItemsHidden(self, items, value):
        """
        Set the visibility of given items.

        :type items: list[QtWidgets.QTreeWidgetItem]
        :type value: bool
        :rtype: None
        """
        for item in items:
            self.setItemHidden(item, value)

    def selectedPaths(self):
        """
        Return the selected item paths.

        :rtype: list[str]
        """
        paths = []
        for item in self.selectedItems():
            path = item.url().toLocalFile()
            paths.append(path)
        return paths

    def selectPaths(self, paths):
        """
        Selected the items that have the given paths.

        :type paths: list[str]
        :rtype: None
        """
        for item in self.items():
            path = item.url().toLocalFile()
            if path in paths:
                item.setSelected(True)

    def isIconView(self):
        """
        Return True if widget is in Icon mode.

        :rtype: bool
        """
        return not self._listView.isHidden()

    def isTableView(self):
        """
        Return True if widget is in List mode.

        :rtype: bool
        """
        return not self._treeWidget.isHidden()

    def setViewMode(self, mode):
        """
        Set the view mode for this widget.

        :type mode: str
        :rtype: None
        """
        if mode == self.IconMode:
            self.setZoomAmount(self.DEFAULT_MIN_ICON_SIZE)
        elif mode == self.TableMode:
            self.setZoomAmount(self.DEFAULT_MIN_ICON_SIZE)

    def _setViewMode(self, mode):
        """
        Set the view mode for this widget.

        :type mode: str
        :rtype: None
        """
        if mode == self.IconMode:
            self.setIconMode()
        elif mode == self.TableMode:
            self.setListMode()

    def setListMode(self):
        """
        Set the tree widget visible.

        :rtype: None
        """
        self._listView.hide()
        self._treeWidget.show()
        self._treeWidget.setFocus()

    def setIconMode(self):
        """
        Set the list view visible.

        :rtype: None
        """
        self._treeWidget.hide()
        self._listView.show()
        self._listView.setFocus()

    def zoomAmount(self):
        """
        Return the zoom amount for the widget.

        :rtype: int
        """
        return self._zoomAmount

    def setZoomAmount(self, value):
        """
        Set the zoom amount for the widget.

        :type value: int
        :rtype: None
        """
        if value < self.DEFAULT_MIN_LIST_SIZE:
            value = self.DEFAULT_MIN_LIST_SIZE

        self._zoomAmount = value
        size = QtCore.QSize(value * self.dpi(), value * self.dpi())
        self.setIconSize(size)

        if value >= self.DEFAULT_MIN_ICON_SIZE:
            self._setViewMode(self.IconMode)
        else:
            self._setViewMode(self.TableMode)

        self._treeWidget.setIndentation(0)
        self._treeWidget.setColumnWidth(0, value * self.dpi() + self.itemTextHeight())
        self.scrollToSelectedItem()

        msg = "Size: {0}%".format(value)
        self.showToastMessage(msg)

    def wheelEvent(self, event):
        """
        Triggered on any wheel events for the current viewport.

        :type event: QtWidgets.QWheelEvent
        :rtype: None
        """
        modifiers = QtWidgets.QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.ControlModifier or modifiers == QtCore.Qt.AltModifier:
            numDegrees = event.delta() / 8
            numSteps = numDegrees / 15

            delta = (numSteps * self.wheelScrollStep())
            value = self.zoomAmount() + delta
            self.setZoomAmount(value)

    def setTextColor(self, color):
        """
        Set the item text color.

        :type color: QtWidgets.QtColor
        """
        self._textColor = color

    def setTextSelectedColor(self, color):
        """
        Set the text color when an item is selected.

        :type color: QtWidgets.QtColor
        """
        self._textSelectedColor = color

    def setBackgroundColor(self, color):
        """
        Set the item background color.

        :type color: QtWidgets.QtColor
        """
        self._backgroundColor = color

    def setBackgroundHoverColor(self, color):
        """
        Set the background color when the mouse hovers over the item.

        :type color: QtWidgets.QtColor
        """
        self._backgroundHoverColor = color

    def setBackgroundSelectedColor(self, color):
        """
        Set the background color when an item is selected.

        :type color: QtWidgets.QtColor
        """
        self._backgroundSelectedColor = color
        self._listView.setRubberBandColor(QtGui.QColor(200, 200, 200, 255))

    def textColor(self):
        """
        Return the item text color.

        :rtype: QtGui.QColor
        """
        return self._textColor

    def textSelectedColor(self):
        """
        Return the item text color when selected.

        :rtype: QtGui.QColor
        """
        return self._textSelectedColor

    def backgroundColor(self):
        """
        Return the item background color.

        :rtype: QtWidgets.QtColor
        """
        return self._backgroundColor

    def backgroundHoverColor(self):
        """
        Return the background color for when the mouse is over an item.

        :rtype: QtWidgets.QtColor
        """
        return self._backgroundHoverColor

    def backgroundSelectedColor(self):
        """
        Return the background color when an item is selected.

        :rtype: QtWidgets.QtColor
        """
        return self._backgroundSelectedColor
