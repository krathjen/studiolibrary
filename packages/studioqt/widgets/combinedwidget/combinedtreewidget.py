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

from functools import partial
from collections import OrderedDict

import studioqt

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

from .combineditemviewmixin import CombinedItemViewMixin


logger = logging.getLogger(__name__)


class CombinedTreeWidget(CombinedItemViewMixin, QtWidgets.QTreeWidget):

    def __init__(self, *args):
        QtWidgets.QTreeWidget.__init__(self, *args)
        CombinedItemViewMixin.__init__(self)

        self._sortColumn = None

        self._groupItems = []
        self._groupColumn = None
        self._groupOrder = QtCore.Qt.AscendingOrder

        self._headerLabels = []
        self._hiddenColumns = {}
        self._validGroupByColumns = []

        self.setAutoScroll(False)
        self.setMouseTracking(True)
        self.setSortingEnabled(True)
        self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        header = self.header()
        header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.showHeaderMenu)

        self.itemClicked.connect(self._itemClicked)
        self.itemDoubleClicked.connect(self._itemDoubleClicked)

    def drawRow(self, painter, options, index):
        item = self.itemFromIndex(index)
        item.paintRow(painter, options, index)

    def settings(self):
        """
        Return the current state of the widget.

        :rtype: dict
        """
        settings = {}

        settings["sortOrder"] = self.sortOrder()
        settings["sortColumn"] = self.sortColumnLabel()
        settings["groupOrder"] = self.groupOrder()
        settings["groupColumn"] = self.groupColumnLabel()
        # settings["headerState"] = self.header().saveState()

        settings["columnSettings"] = self.columnSettings()

        return settings

    def setSettings(self, settings):
        """
        Set the current state of the widget.

        :type settings: dict
        :rtype: None
        """
        # headerState = settings.get("headerState", "")
        # self.header().restoreState(headerState)

        columnSettings = settings.get("columnSettings", {})
        self.setColumnSettings(columnSettings)

        sortOrder = settings.get("sortOrder", 0)
        sortColumn = settings.get("sortColumn")
        groupOrder = settings.get("groupOrder", 0)
        groupColumn = settings.get("groupColumn")

        self.addHeaderLabel(sortColumn)
        self.addHeaderLabel(groupColumn)

        self.sortByColumn(sortColumn, sortOrder, groupColumn, groupOrder)

        return settings

    def _itemClicked(self, item):
        """
        Triggered when the user clicks on an item.

        :type item: QtWidgets.QTreeWidgetItem
        :rtype: None
        """
        item.clicked()

    def _itemDoubleClicked(self, item):
        """
        Triggered when the user double clicks on an item.

        :type item: QtWidgets.QTreeWidgetItem
        :rtype: None
        """
        item.doubleClicked()

    def clear(self, *args):
        """
        Reimplementing so that all dirty objects can be removed.

        :param args:
        :rtype: None
        """
        QtWidgets.QTreeWidget.clear(self, *args)
        self.cleanDirtyObjects()
        self._groupItems = []

    def setItemsSelected(self, items, value, scrollTo=True):
        """
        Select the given items.

        :type items: list[studioqt.CombinedWidget]
        :type value: bool
        :type scrollTo: bool

        :rtype: None
        """
        for item in items:
            self.setItemSelected(item, value)

        if scrollTo:
            self.combinedWidget().scrollToItem(items[-1])

    def selectedItem(self):
        """
        Return the last selected non-hidden item.

        :rtype: studioqt.CombinedWidgetItem
        """
        items = self.selectedItems()

        if items:
            return items[-1]

        return None

    def selectedItems(self):
        """
        Return all the selected items.

        :rtype: list[studioqt.CombinedWidgetItem]
        """
        items = []
        items_ = QtWidgets.QTreeWidget.selectedItems(self)

        for item in items_:
            if not isinstance(item, studioqt.CombinedWidgetItemGroup):
                items.append(item)

        return items

    def rowAt(self, pos):
        """
        Return the row for the given pos.

        :type pos: QtCore.QPoint
        :rtype: int
        """
        item = self.itemAt(pos)
        return self.itemRow(item)

    def itemRow(self, item):
        """
        Return the row for the given item.

        :type item: studioqt.TreeWidgetItem
        :rtype: int
        """
        index = self.indexFromItem(item)
        return index.row()

    def items(self):
        """
        Return a list of all the items in the tree widget.

        :rtype: lsit[studioqt.TreeWidgetItem]
        """
        items = []

        for item in self._items():
            if not isinstance(item, studioqt.CombinedWidgetItemGroup):
                items.append(item)

        return items

    def _items(self):
        """
        Return a list of all the items in the tree widget.

        :rtype: lsit[studioqt.TreeWidgetItem]
        """
        return self.findItems(
            "*",
            QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )

    def takeTopLevelItems(self):
        """
        Take all items from the tree widget.

        :rtype: list[QtWidgets.QTreeWidgetItem]
        """
        items = []
        for item in self._items():
            # For some reason its faster to take from index 1.
            items.append(self.takeTopLevelItem(1))
        items.append(self.takeTopLevelItem(0))
        return items

    def textFromColumn(self, column, split=None, duplicates=False):
        """
        Return all the data for the given column

        :type column: int or str
        :type split: str
        :type duplicates: bool
        :rtype: list[str]
        """
        items = self.items()
        results = self.textFromItems(
            items,
            column,
            split=split,
            duplicates=duplicates,
        )
        return results

    def textFromItems(self, items, column, split=None, duplicates=False):
        """
        Return all the text data for the given items and given column

        :type items: list[CombinedWidgetItem]
        :type column: int or str
        :type split: str
        :type duplicates: bool
        :rtype: list[str]
        """
        results = []

        for item in items:
            text = item.text(column)

            if text and split:
                results.extend(text.split(split))
            elif text:
                results.append(text)

        if not duplicates:
            results = list(set(results))

        return results

    def columnLabels(self):
        """
        Return all header labels for the tree widget.

        :rtype: list[str]
        """
        labels = []

        for column in range(self.columnCount()):
            label = self.headerItem().text(column)
            labels.append(label)

        return labels

    def updateData(self):
        """
        Update all item data to the correct column.

        :rtype: None
        """
        items = self.items()
        for item in items:
            item.updateData()

    def labelFromColumn(self, column):
        """
        Return the column label for the given column.

        :type column: int
        :rtype: str
        """
        if column is not None:
            return self.headerItem().text(column)

    def setHeaderLabels(self, *args):
        """
        Set the header for each item in the given label list.

        :type args:
        :rtype: None
        """
        columnSettings = self.columnSettings()

        QtWidgets.QTreeWidget.setHeaderLabels(self, *args)

        self.updateHeaderLabels()
        self.updateColumnHidden()
        self.updateData()

        self.setColumnSettings(columnSettings)

    def addHeaderLabel(self, label):
        """
        Add the given header label to the table.

        :type label: str
        :rtype: None
        """
        labels = self.headerLabels()
        if label not in labels:
            labels.append(label)
            self.setHeaderLabels(labels)

    def headerLabels(self):
        """
        Return all the header labels.

        :rtype: str
        """
        return self._headerLabels

    def updateHeaderLabels(self):
        """
        Add a column in the header for the data in the items.

        :rtype: None
        """
        self._headerLabels = []

        for column in range(self.columnCount()):
            label = self.headerItem().text(column)
            self._headerLabels.append(label)

    def columnFromLabel(self, label):
        """
        Return the column for the given label.

        :type label: str
        :rtype: int
        """
        if label not in self._headerLabels:
            self.updateHeaderLabels()

        try:
            return self._headerLabels.index(label)
        except ValueError:
            return -1

    def showAllColumns(self):
        """
        Show all available columns.

        :rtype: None
        """
        for column in range(self.columnCount()):
            self.setColumnHidden(column, False)

    def hideAllColumns(self):
        """
        Hide all available columns.

        :rtype: None
        """
        for column in range(1, self.columnCount()):
            self.setColumnHidden(column, True)

    def updateColumnHidden(self):
        self.showAllColumns()
        columnLabels = self._hiddenColumns.keys()

        for columnLabel in columnLabels:
            self.setColumnHidden(columnLabel, self._hiddenColumns[columnLabel])

    def setColumnHidden(self, column, value):
        """
        Set the give column to show or hide depending on the specified value.

        :type column: int or str
        :type value: bool
        :rtype: None
        """
        if isinstance(column, basestring):
            column = self.columnFromLabel(column)

        label = self.labelFromColumn(column)
        self._hiddenColumns[label] = value

        QtWidgets.QTreeWidget.setColumnHidden(self, column, value)

        # Make sure the column is not collapsed
        width = self.columnWidth(column)
        if width < 5:
            width = 100
            self.setColumnWidth(column, width)

    def resizeColumnToContents(self, column):
        """
        Resize the given column to the data of that column.

        :type column: int or text
        :rtype: None
        """
        width = 0
        for item in self.items():
            text = item.text(column)
            font = item.font(column)
            metrics = QtGui.QFontMetricsF(font)
            textWidth = metrics.width(text) + item.padding()
            width = max(width, textWidth)

        self.setColumnWidth(column, width)

    # ----------------------------------------------------------------------
    # Support for custom orders
    # ----------------------------------------------------------------------

    def isSortByCustomOrder(self):
        """
        Return true if items are currently sorted by custom order.

        :rtype: bool
        """
        sortColumnLabel = self.sortColumnLabel()
        return sortColumnLabel == "Custom Order"

    def setItemsCustomOrder(self, items, row=1, padding=5):
        """
        Set the custom order for the given items by their list order.

        :rtype: None
        """
        column = self.columnFromLabel("Custom Order")

        for item in items:
            item.setText(column, str(row).zfill(padding))
            row += 1

    def updateCustomOrder(self):
        """
        Update any empty custom orders.

        :rtype: None
        """
        row = 1
        padding = 5

        items = self.items()
        column = self.columnFromLabel("Custom Order")

        for item in items:
            customOrder = item.text(column)
            if not customOrder:
                item.setText(column, str(row).zfill(padding))
            row += 1

    def itemsCustomOrder(self):
        """
        Return the items sorted by the custom order data.

        :rtype: list[studioqt.CombinedWidgetItem]
        """
        items = self.items()
        column = self.columnFromLabel("Custom Order")
        customOrder = sorted(items, key=lambda item: item.text(column))

        return customOrder

    def moveItems(self, items, itemAt):
        """
        Move the given items to the position of the destination row.

        :type items: list[studioqt.CombinedWidgetItem]
        :type itemAt: studioqt.CombinedWidgetItem
        :rtype: None
        """
        row = 0
        column = self.columnFromLabel("Custom Order")
        orderedItems = self.itemsCustomOrder()

        if itemAt:
            row = orderedItems.index(itemAt)

        removedItems = []
        for item in items:
            index = orderedItems.index(item)
            removedItems.append(orderedItems.pop(index))

        for item in removedItems:
            orderedItems.insert(row, item)

        self.setItemsCustomOrder(orderedItems)
        self.sortByColumn(column, QtCore.Qt.AscendingOrder)

        for item in items:
            self.setItemSelected(item, True)

    # ----------------------------------------------------------------------
    # Support for menus
    # ----------------------------------------------------------------------

    def showHeaderMenu(self, pos):
        """
        Creates and show the header menu at the cursor pos.

        :rtype: QtWidgets.QMenu
        """
        header = self.header()
        column = header.logicalIndexAt(pos)

        menu = self.createHeaderMenu(column)

        menu.addSeparator()

        submenu = self.createHideColumnMenu()
        menu.addMenu(submenu)

        point = QtGui.QCursor.pos()
        menu.exec_(point)

    def createHeaderMenu(self, column):
        """
        Creates a new header menu.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu(self)
        label = self.labelFromColumn(column)

        action = menu.addAction("Hide '{0}'".format(label))
        callback = partial(self.setColumnHidden, column, True)
        action.triggered.connect(callback)

        menu.addSeparator()

        action = menu.addAction('Sort Ascending')
        callback = partial(self.sortByColumn, column, QtCore.Qt.AscendingOrder)
        action.triggered.connect(callback)

        action = menu.addAction('Sort Descending')
        callback = partial(self.sortByColumn, column, QtCore.Qt.DescendingOrder)
        action.triggered.connect(callback)

        menu.addSeparator()

        action = menu.addAction('Resize to Contents')
        callback = partial(self.resizeColumnToContents, column)
        action.triggered.connect(callback)

        return menu

    def columnSettings(self):
        """
        Return the settings for each column.

        :rtype: dict
        """
        columnSettings = {}

        for column in range(self.columnCount()):

            label = self.labelFromColumn(column)
            hidden = self.isColumnHidden(column)
            width = self.columnWidth(column)

            columnSettings[label] = {
                "hidden": hidden,
                "width": width,
                "index": column,
            }

        return columnSettings

    def setColumnSettings(self, settings):
        """
        Set the settings for each column.

        :type settings: dict
        :type: None
        """
        for label in settings:
            column = self.columnFromLabel(label)

            width = settings[label].get("width", 100)
            if width < 5:
                width = 100
            self.setColumnWidth(column, width)

            hidden = settings[label].get("hidden", False)
            self.setColumnHidden(column, hidden)

    def createHideColumnMenu(self):
        """
        Create the hide column menu.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu("Show/Hide Column", self)

        action = menu.addAction("Show All")
        action.triggered.connect(self.showAllColumns)

        action = menu.addAction("Hide All")
        action.triggered.connect(self.hideAllColumns)

        menu.addSeparator()

        for column in range(self.columnCount()):

            label = self.labelFromColumn(column)
            isHidden = self.isColumnHidden(column)

            action = menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(not isHidden)

            callback = partial(self.setColumnHidden, column, not isHidden)
            action.triggered.connect(callback)

        return menu

    # ----------------------------------------------------------------------
    # Support for copying item data to the clipboard.
    # ----------------------------------------------------------------------

    def createCopyTextMenu(self):
        """
        Create a menu to copy the selected items data to the clipboard.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu("Copy Text", self)

        if self.selectedItems():

            for column in range(self.columnCount()):
                label = self.labelFromColumn(column)
                action = menu.addAction(label)
                callback = partial(self.copyText, column)
                action.triggered.connect(callback)

        else:
            action = menu.addAction("No items selected")
            action.setEnabled(False)

        return menu

    def copyText(self, column):
        """
        Copy the given column text to clipboard.

        :type column: int or text
        :rtype: None
        """
        items = self.selectedItems()
        text = "\n".join([item.text(column) for item in items])

        clipBoard = QtWidgets.QApplication.clipboard()
        clipBoard.setText(text, QtGui.QClipboard.Clipboard)

    # ----------------------------------------------------------------------
    # Support for sorting items.
    # ----------------------------------------------------------------------

    def sortBySettings(self):
        """
        Return the current "sortBy" settings as a dictionary. 
        
        
        :rtype: dict 
        """
        settings = {
            "sortOrder": self.sortOrder(),
            "sortColumn": self.labelFromColumn(self.sortColumn()),
            "groupOrder": self.groupOrder(),
            "groupColumn": self.labelFromColumn(self.groupColumn()),
        }

        return settings

    def setSortBySettings(self, settings):
        """
        Set the "sortBy" by settings using the given dictionary. 

        :type settings: dict
        :rtype: None 
        """
        self.sortByColumn(**settings)

    def sortColumnLabel(self):
        """
        Return the current sort column label.

        :rtype: str
        """
        column = self.sortColumn()
        return self.labelFromColumn(column)

    def refreshSortBy(self):
        """
        Refresh the sort order of the current sorted column.

        :rtype: None
        """
        settings = self.sortBySettings()
        self.sortByColumn(**settings)

    def sortOrderToInt(self, sortOrder):
        """
        Convert the sort order to an int.

        :type sortOrder: QtCore.Qt.AscendingOrder or QtCore.Qt.DescendingOrder
        :rtype: int
        """
        if sortOrder == QtCore.Qt.AscendingOrder:
            return 0
        else:
            return 1  # QtCore.Qt.DescendingOrder

    def intToSortOrder(self, value):
        """
        Convert the given int to a sort order.

        :type value: QtCore.Qt
        :rtype: QtCore.Qt.AscendingOrder or QtCore.Qt.DescendingOrder
        """
        if value == 0:
            return QtCore.Qt.AscendingOrder
        else:
            return QtCore.Qt.DescendingOrder

    def sortOrder(self):
        """
        Return the current sort order.

        :rtype: int
        """
        sortOrder = self.header().sortIndicatorOrder()
        return self.sortOrderToInt(sortOrder)

    def sortByColumn(self, sortColumn, sortOrder, groupColumn=False, groupOrder=False):
        """
        Sort by the given column.

        :type sortColumn: int
        :type sortOrder: int
        :type groupColumn: bool
        :type groupOrder: bool

        :rtype: None
        """
        if isinstance(sortColumn, basestring):
            sortColumn = self.columnFromLabel(sortColumn)

        if isinstance(groupColumn, basestring):
            groupColumn = self.columnFromLabel(groupColumn)

        self._sortColumn = sortColumn
        self.setSortingEnabled(True)

        sortColumnLabel = self.labelFromColumn(sortColumn)
        if sortColumnLabel == "Custom Order":
            sortOrder = QtCore.Qt.AscendingOrder

        sortOrder = self.intToSortOrder(sortOrder)
        QtWidgets.QTreeWidget.sortByColumn(self, sortColumn, sortOrder)

        if groupOrder is False:
            groupOrder = self.groupOrder()

        groupOrder = self.intToSortOrder(groupOrder)

        if groupColumn is False:
            groupColumn = self.groupColumn()

        self._groupOrder = groupOrder
        self._groupColumn = groupColumn

        self._groupByColumn(groupColumn, groupOrder)

    def createSortByMenu(self):
        """
        Create a new instance of the sort by menu.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu("Sort By", self)

        sortOrder = self.sortOrder()
        sortColumn = self.sortColumn()

        action = studioqt.SeparatorAction("Sort By", menu)
        menu.addAction(action)

        for column in range(self.columnCount()):

            label = self.labelFromColumn(column)

            action = menu.addAction(label)
            action.setCheckable(True)

            if column == sortColumn:
                action.setChecked(True)
            else:
                action.setChecked(False)

            callback = partial(self.sortByColumn, column, sortOrder)
            action.triggered.connect(callback)

        action = studioqt.SeparatorAction("Sort Order", menu)
        menu.addAction(action)

        action = menu.addAction("Ascending")
        action.setCheckable(True)
        action.setChecked(sortOrder == QtCore.Qt.AscendingOrder)

        callback = partial(self.sortByColumn, sortColumn, QtCore.Qt.AscendingOrder)
        action.triggered.connect(callback)

        action = menu.addAction("Descending")
        action.setCheckable(True)
        action.setChecked(sortOrder == QtCore.Qt.DescendingOrder)

        callback = partial(self.sortByColumn, sortColumn, QtCore.Qt.DescendingOrder)
        action.triggered.connect(callback)

        return menu

    # ----------------------------------------------------------------------
    # Support for grouping items.
    # ----------------------------------------------------------------------

    def groupOrder(self):
        """
        Return the current group order.

        :rtype: int
        """
        return self.sortOrderToInt(self._groupOrder)

    def groupColumn(self):
        """
        Return the current group column.

        :rtype: int
        """
        return self._groupColumn

    def groupColumnLabel(self):
        """
        Return the current group column label.

        :rtype: str or None
        """
        label = None
        column = self.groupColumn()
        if column is not None:
            label = self.labelFromColumn(column)
        return label

    def createGroupItem(self, text, children):
        """
        Create a new group item for the given text and children.

        :type text: str
        :type children: list[studioqt.CombinedWidgetItem]
        :rtype: studioqt.CombinedWidgetItemGroup
        """
        groupItem = studioqt.CombinedWidgetItemGroup()
        groupItem.setName(text)
        groupItem.setStretchToWidget(self.parent())
        groupItem.setChildren(children)
        return groupItem

    def addGroupItem(self, text, children):
        """
        Add a new group item for the given text and children.

        :type text: str
        :type children: list[studioqt.CombinedWidgetItem]
        :rtype: studioqt.CombinedWidgetItemGroup
        """
        groupItem = self.createGroupItem(text, children)
        self.addTopLevelItem(groupItem)
        self._groupItems.append(groupItem)
        return groupItem

    def refreshGroupBy(self):
        """
        Refresh the grouping of the current group column.

        :rtype: None
        """
        for groupItem in self._groupItems:
            groupItem.updateChildren()

    def itemsGroupByColumn(self, groupColumn, groupOrder, items=None):
        """
        Return a list of items grouped by the given column.

        :type groupColumn: int
        :type groupOrder int
        :type items: None or list[studioqt.CombinedWidgetItem]
        :rtype: dict
        """
        items = items or self.items()

        groupItems = {}
        orderedGroups = OrderedDict()

        if isinstance(groupColumn, basestring):
            groupColumn = self.columnFromLabel(groupColumn)

        if groupColumn:
            reverse = groupOrder == QtCore.Qt.DescendingOrder
            items_ = sorted(items, key=lambda item: item.text(groupColumn).lower(), reverse=reverse)

            for item in items_:
                text = item.displayText(groupColumn)
                orderedGroups.setdefault(text, [])
        else:
            orderedGroups.setdefault("None", [])

        for item in items:
            if groupColumn is not None:
                text = item.displayText(groupColumn)
            else:
                text = "None"

            groupItems.setdefault(text, [])
            groupItems[text].append((item, item.isHidden()))

        for key in orderedGroups:
            orderedGroups[key] = groupItems.get(key, [])

        return orderedGroups

    @studioqt.showWaitCursor
    def groupByColumn(self, groupColumn, groupOrder):
        """
        Group the items on the data in the given column.

        :type groupColumn: int
        :type groupOrder: int
        :rtype: None
        """
        sortOrder = self.sortOrder()
        sortColumn = self.sortColumn()

        self.sortByColumn(sortColumn, sortOrder, groupColumn=groupColumn, groupOrder=groupOrder)

    def _groupByColumn(self, groupColumn, groupOrder):
        """
        Group the items on the data in the given column.

        Note: The complexity of this method needs to be simplified!

        :type groupColumn: int
        :type groupOrder: int
        :rtype: None
        """
        if isinstance(groupColumn, basestring):
            column = self.columnFromLabel(groupColumn)

        self._groupItems = []
        self._groupColumn = groupColumn

        groupItems = self.itemsGroupByColumn(groupColumn, groupOrder)

        selectedItems = self.selectedItems()
        self.setSortingEnabled(False)
        self.takeTopLevelItems()

        for groupText in groupItems.keys():

            children = [item[0] for item in groupItems[groupText]]

            if groupColumn is not None:
                groupItem = self.addGroupItem(groupText, children)

            for item, isHidden in groupItems[groupText]:
                self.addTopLevelItem(item)
                item.setHidden(isHidden)

            if groupColumn is not None:
                groupItem.updateChildren()

        if groupColumn is None:
            for groupItem in self._groupItems:
                groupItem.setHidden(True)

        if selectedItems:
            self.setItemsSelected(selectedItems, True)

    def setValidGroupByColumns(self, columns):
        self._validGroupByColumns = columns

    def groupByOrder(self):
        return QtCore.Qt.DescendingOrder

    def createGroupByMenu(self):
        """
        Create a new instance of the group by menu.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu("Group By", self)

        groupOrder = self._groupOrder
        groupColumn = self._groupColumn

        action = studioqt.SeparatorAction("Group By", menu)
        menu.addAction(action)

        action = menu.addAction("None")
        action.setCheckable(True)

        callback = partial(self.groupByColumn, None, groupOrder)
        action.triggered.connect(callback)

        validGroupColumns = self._validGroupByColumns

        currentGroupCollumn = self.groupColumn()
        if currentGroupCollumn is None:
            action.setChecked(True)

        for column in range(self.columnCount()):

            label = self.labelFromColumn(column)

            if validGroupColumns and label not in validGroupColumns:
                continue

            action = menu.addAction(label)
            action.setCheckable(True)

            if currentGroupCollumn == column:
                action.setChecked(True)

            callback = partial(self.groupByColumn, column, groupOrder)
            action.triggered.connect(callback)

        action = studioqt.SeparatorAction("Group Order", menu)
        menu.addAction(action)

        action = menu.addAction("Ascending")
        action.setCheckable(True)
        action.setChecked(groupOrder == QtCore.Qt.AscendingOrder)

        callback = partial(self.groupByColumn, groupColumn, QtCore.Qt.AscendingOrder)
        action.triggered.connect(callback)

        action = menu.addAction("Descending")
        action.setCheckable(True)
        action.setChecked(groupOrder == QtCore.Qt.DescendingOrder)

        callback = partial(self.groupByColumn, groupColumn, QtCore.Qt.DescendingOrder)
        action.triggered.connect(callback)

        return menu

    # ----------------------------------------------------------------------
    # Override events for mixin.
    # ----------------------------------------------------------------------

    def mouseMoveEvent(self, event):
        """
        Triggered when the user moves the mouse over the current viewport.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        CombinedItemViewMixin.mouseMoveEvent(self, event)
        QtWidgets.QTreeWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Triggered when the user releases the mouse button on the viewport.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        CombinedItemViewMixin.mouseReleaseEvent(self, event)
        QtWidgets.QTreeWidget.mouseReleaseEvent(self, event)

