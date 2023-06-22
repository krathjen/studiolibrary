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

import time
import logging
import functools
import collections

from studiovendor import six
from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt
import studiolibrary
import studiolibrary.widgets

from .sidebarwidgetitem import SidebarWidgetItem


__all__ = ["SidebarWidget"]

logger = logging.getLogger(__name__)


DEFAULT_SEPARATOR = "/"


def pathsToDict(paths, root="", separator=None):
    """
    Return the given paths as a nested dict.

    Example:
        paths = ["/fruit/apple", "/fruit/orange"]
        print pathsToDict(paths)
        # Result: {"fruit" : {"apple":{}}, {"orange":{}}}

    :type paths: list[str]
    :type root: str
    :type separator: str or None
    :rtype: dict
    """
    separator = separator or DEFAULT_SEPARATOR
    results = collections.OrderedDict()
    paths = studiolibrary.normPaths(paths)

    for path in paths:
        p = results

        # This is to add support for grouping by the given root path.
        if root and root in path:
            path = path.replace(root, "")
            p = p.setdefault(root, collections.OrderedDict())

        keys = path.split(separator)[0:]

        for key in keys:
            if key:
                p = p.setdefault(key, collections.OrderedDict())

    return results


def findRoot(paths, separator=None):
    """
    Find the common path for the given paths.
    
    Example:
        paths = [
            '/fruit/apple',
            '/fruit/orange',
            '/fruit/banana'
        ]
        print(findRoot(paths))
        # '/fruit'
    
    :type paths: list[str]
    :type separator: str
    :rtype: str 
    """
    if paths:
        path = list(paths)[0]  # Only need one from the list to verify the common path.
    else:
        path = ""

    result = None
    separator = separator or DEFAULT_SEPARATOR

    tokens = path.split(separator)

    for i, token in enumerate(tokens):
        root = separator.join(tokens[:i+1])
        match = True

        for path in paths:
            if not path.startswith(root + separator):
                match = False
                break

        if not match:
            break

        result = root

    return result



class SidebarWidget(QtWidgets.QWidget):

    itemDropped = QtCore.Signal(object)
    itemRenamed = QtCore.Signal(str, str)
    itemSelectionChanged = QtCore.Signal()
    settingsMenuRequested = QtCore.Signal(object)

    def __init__(self, *args):
        super(SidebarWidget, self).__init__(*args)

        self._dataset = None
        self._lineEdit = None
        self._previousFilterText = ""

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)

        self._treeWidget = TreeWidget(self)
        self._treeWidget.itemDropped = self.itemDropped
        self._treeWidget.itemRenamed = self.itemRenamed
        self._treeWidget.itemSelectionChanged.connect(self._itemSelectionChanged)

        self._titleWidget = self.createTitleWidget()
        self._titleWidget.ui.menuButton.clicked.connect(self.showSettingsMenu)
        self._titleWidget.ui.titleButton.clicked.connect(self.clearSelection)

        self.layout().addWidget(self._titleWidget)
        self.layout().addWidget(self._treeWidget)

        self._treeWidget.installEventFilter(self)

    def _itemSelectionChanged(self, *args):
        self.itemSelectionChanged.emit()

    def eventFilter(self, obj, event):
        """Using an event filter to show the search widget on key press."""
        if event.type() == QtCore.QEvent.KeyPress:
            self._keyPressEvent(event)

        return super(SidebarWidget, self).eventFilter(obj, event)

    def _keyPressEvent(self, event):
        """
        Triggered from the tree widget key press event.

        :type event: QKeyEvent
        """
        text = event.text().strip()

        if not text.isalpha() and not text.isdigit():
            return

        if text and not self._titleWidget.ui.filterEdit.hasFocus():
                self._titleWidget.ui.filterEdit.setText(text)

        self.setFilterVisible(True)

        self._previousFilterText = text

    def _filterVisibleTrigger(self, visible):
        """
        Triggered by the filter visible action.

        :type visible: bool
        """
        self.setFilterVisible(visible)
        self._titleWidget.ui.filterEdit.selectAll()

    def createTitleWidget(self):
        """
        Create a new instance of the title bar widget.

        :rtype: QtWidgets.QFrame
        """

        class UI(object):
            """Proxy class for attaching ui widgets as properties."""
            pass

        titleWidget = QtWidgets.QFrame(self)
        titleWidget.setObjectName("titleWidget")
        titleWidget.ui = UI()

        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.setSpacing(0)
        vlayout.setContentsMargins(0,0,0,0)

        hlayout = QtWidgets.QHBoxLayout(self)
        hlayout.setSpacing(0)
        hlayout.setContentsMargins(0,0,0,0)

        vlayout.addLayout(hlayout)

        titleButton = QtWidgets.QPushButton(self)
        titleButton.setText("Folders")
        titleButton.setObjectName("titleButton")
        titleWidget.ui.titleButton = titleButton

        hlayout.addWidget(titleButton)

        menuButton = QtWidgets.QPushButton(self)
        menuButton.setText("...")
        menuButton.setObjectName("menuButton")
        titleWidget.ui.menuButton = menuButton

        hlayout.addWidget(menuButton)

        self._lineEdit = studiolibrary.widgets.LineEdit(self)
        self._lineEdit.hide()
        self._lineEdit.setObjectName("filterEdit")
        self._lineEdit.setText(self.treeWidget().filterText())
        self._lineEdit.textChanged.connect(self.searchChanged)
        titleWidget.ui.filterEdit = self._lineEdit

        vlayout.addWidget(self._lineEdit)

        titleWidget.setLayout(vlayout)

        return titleWidget

    def _dataChanged(self):
        pass

    def setDataset(self, dataset):
        """
        Set the dataset for the search widget:

        :type dataset: studioqt.Dataset
        """
        self._dataset = dataset
        self._dataset.dataChanged.connect(self._dataChanged)
        self._dataChanged()

    def dataset(self):
        """
        Get the dataset for the search widget.

        :rtype: studioqt.Dataset
        """
        return self._dataset

    def search(self):
        """Run the dataset search."""
        if self.dataset():
            self.dataset().addQuery(self.query())
            self.dataset().search()
        else:
            logger.info('No dataset found for the sidebar widget.')

    def query(self):
        """
        Get the query for the sidebar widget.

        :rtype: dict
        """
        filters = []

        for path in self.selectedPaths():
            if self.isRecursive():
                suffix = "" if path.endswith("/") else "/"

                filter_ = ('folder', 'startswith', path + suffix)
                filters.append(filter_)

            filter_ = ('folder', 'is', path)
            filters.append(filter_)

        uniqueName = 'sidebar_widget_' + str(id(self))
        return {'name': uniqueName, 'operator': 'or', 'filters': filters}

    def searchChanged(self, text):
        """
        Triggered when the search filter has changed.

        :type text: str
        """
        self.refreshFilter()
        if text:
            self.setFilterVisible(True)
        else:
            self.treeWidget().setFocus()
            self.setFilterVisible(False)

    def showSettingsMenu(self):
        """Create and show a new settings menu instance."""

        menu = studioqt.Menu(self)

        self.settingsMenuRequested.emit(menu)

        self.createSettingsMenu(menu)

        point = QtGui.QCursor.pos()
        point.setX(point.x() + 3)
        point.setY(point.y() + 3)
        action = menu.exec_(point)
        menu.close()

    def createSettingsMenu(self, menu):
        """
        Create a new settings menu instance.

        :rtype: QMenu
        """
        action = menu.addAction("Show Filter")
        action.setCheckable(True)
        action.setChecked(self.isFilterVisible())

        callback = functools.partial(self._filterVisibleTrigger, not self.isFilterVisible())
        action.triggered.connect(callback)

        action = menu.addAction("Show Icons")
        action.setCheckable(True)
        action.setChecked(self.iconsVisible())

        callback = functools.partial(self.setIconsVisible, not self.iconsVisible())
        action.triggered.connect(callback)

        action = menu.addAction("Show Root Folder")
        action.setCheckable(True)
        action.setChecked(self.isRootVisible())

        callback = functools.partial(self.setRootVisible, not self.isRootVisible())
        action.triggered.connect(callback)

        return menu

    def setFilterVisible(self, visible):
        """
        Set the filter widget visible

        :type visible: bool
        """
        self._titleWidget.ui.filterEdit.setVisible(visible)
        self._titleWidget.ui.filterEdit.setFocus()

        if not visible and bool(self.treeWidget().filterText()):
            self.treeWidget().setFilterText("")
        else:
            self.refreshFilter()

    def setSettings(self, settings):
        """
        Set the settings for the widget.

        :type settings: dict
        """
        self.treeWidget().setSettings(settings)

        value = settings.get("filterVisible")
        if value is not None:
            self.setFilterVisible(value)

        value = settings.get("filterText")
        if value is not None:
            self.setFilterText(value)

    def settings(self):
        """
        Get the settings for the widget.

        :rtype: dict
        """
        settings = self.treeWidget().settings()

        settings["filterText"]  = self.filterText()
        settings["filterVisible"]  = self.isFilterVisible()

        return settings

    # --------------------------------
    # convenience methods
    # --------------------------------

    def filterText(self):
        return self.treeWidget().filterText()

    def setFilterText(self, text):
        self._titleWidget.ui.filterEdit.setText(text)

    def refreshFilter(self):
        self.treeWidget().setFilterText(self._titleWidget.ui.filterEdit.text())

    def isFilterVisible(self):
        return bool(self.treeWidget().filterText()) or self._titleWidget.ui.filterEdit.isVisible()

    def setIconsVisible(self, visible):
        self.treeWidget().setIconsVisible(visible)

    def iconsVisible(self):
        return self.treeWidget().iconsVisible()

    def setRootVisible(self, visible):
        self.treeWidget().setRootVisible(visible)

    def isRootVisible(self):
        return self.treeWidget().isRootVisible()

    def treeWidget(self):
        return self._treeWidget

    def setDpi(self, dpi):
        self.treeWidget().setDpi(dpi)

    def setRecursive(self, enabled):
        self.treeWidget().setRecursive(enabled)

    def isRecursive(self):
        return self.treeWidget().isRecursive()

    def setData(self, *args, **kwargs):
        self.treeWidget().setData(*args, **kwargs)

    def setItemData(self, id, data):
        self.treeWidget().setPathSettings(id, data)

    def setLocked(self, locked):
        self.treeWidget().setLocked(locked)

    def selectedPath(self):
        return self.treeWidget().selectedPath()

    def selectPaths(self, paths):
        self.treeWidget().selectPaths(paths)

    def selectedPaths(self):
        return self.treeWidget().selectedPaths()

    def clearSelection(self):
        self.treeWidget().clearSelection()


class TreeWidget(QtWidgets.QTreeWidget):

    itemDropped = QtCore.Signal(object)
    itemRenamed = QtCore.Signal(str, str)
    itemSelectionChanged = QtCore.Signal()

    def __init__(self, *args):
        super(TreeWidget, self).__init__(*args)

        self._dpi = 1
        self._data = []
        self._items = []
        self._index = {}
        self._locked = False
        self._dataset = None
        self._recursive = True
        self._filterText = ""
        self._rootVisible = False
        self._iconsVisible = True

        self._options = {
                'field': 'path',
                'separator': '/',
                'recursive': True,
                'autoRootPath': True,
                'rootText': 'FOLDERS',
                'sortBy': None,
                'queries': [{'filters': [('type', 'is', 'Folder')]}]
            }

        self.itemExpanded.connect(self.update)
        self.itemCollapsed.connect(self.update)

        self.setDpi(1)

        self.setAcceptDrops(True)
        self.setHeaderHidden(True)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def filterText(self):
        """
        Get the current filter text.

        :rtype: bool
        """
        return self._filterText

    def setFilterText(self, text):
        """
        Triggered when the search filter has changed.

        :type text: str
        """
        self._filterText = text.strip()
        self.refreshFilter()

    def refreshFilter(self):
        """Refresh the current item filter."""
        items = self.items()

        for item in items:
            if self._filterText.lower() in item.text(0).lower():
                item.setHidden(False)
                for parent in item.parents():
                    parent.setHidden(False)
            else:
                item.setHidden(True)

    def clear(self):
        """Clear all the items from the tree widget."""
        self._items = []
        self._index = {}
        super(TreeWidget, self).clear()

    def setRootVisible(self, visible):
        """
        Set the root item visible.

        :type visible: bool
        """
        self._rootVisible = visible
        self.refreshData()

    def isRootVisible(self):
        """
        Check if the root item is visible

        :rtype: bool
        """
        return self._rootVisible

    def setIconsVisible(self, visible):
        """
        Set all icons visible.

        :type visible: bool
        """
        self._iconsVisible = visible
        self.refreshData()

    def iconsVisible(self):
        """
        Check if all the icons are visible.

        :rtype: bool
        """
        return self._iconsVisible

    def selectionChanged(self, *args):
        """Triggered the current selection has changed."""
        self.parent().search()

    def setRecursive(self, enable):
        """
        Set the search query on the dataset to be recursive.
        
        :type enable: bool
        """
        self._recursive = enable
        self.parent().search()

    def isRecursive(self):
        """
        Get the recursive query enable state.
        
        :rtype: bool 
        """
        return self._recursive

    def sortBy(self):
        """
        Get the sortby field.
        
        :rtype: str 
        """
        return self._options.get('sortBy', [self.field()])

    def field(self):
        """
        Get the field.
        
        :rtype: str 
        """
        return self._options.get('field', '')

    def rootText(self):
        """
        Get the root text.
        
        :rtype: str 
        """
        return self._options.get('rootText')

    def separator(self):
        """
        Get the separator used in the fields to separate level values.

        :rtype: str 
        """
        return self._options.get('separator', DEFAULT_SEPARATOR)

    def _dataChanged(self):
        """Triggered when the data set has changed."""
        pass
        # data = collections.OrderedDict()
        # queries = self._options.get("queries")
        #
        # items = self.dataset().findItems(queries)
        #
        # for item in items:
        #     itemData = item.itemData()
        #     value = itemData.get(self.field())
        #     data[value] = {'iconPath': itemData.get('iconPath')}
        #
        # if data:
        #     root = findRoot(data.keys(), separator=self.separator())
        #     self.setPaths(data, root=root)

    def setLocked(self, locked):
        """
        Set the widget items to read only mode.
        
        :type locked: bool
        :rtype: None 
        """
        self._locked = locked

    def isLocked(self):
        """
        Return True if the items are in read only mode
        
        :rtype: bool 
        """
        return self._locked

    def itemAt(self, pos):
        """
        :type pos: QtGui.QPoint
        :rtype: None or Folder
        """
        index = self.indexAt(pos)
        if not index.isValid():
            return

        item = self.itemFromIndex(index)
        return item

    def dropEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        if self.isLocked():
            logger.debug("Folder is locked! Cannot accept drop!")
            return

        self.itemDropped.emit(event)

    def dragMoveEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        mimeData = event.mimeData()

        if mimeData.hasUrls():
            event.accept()
        else:
            event.ignore()

        item = self.itemAt(event.pos())
        if item:
            self.selectPaths([item.path()])

    def dragEnterEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        event.accept()

    def selectItem(self, item):
        """
        :type item: NavigationWidgetItem
        :rtype: None
        """
        self.selectPaths([item.path()])

    def dpi(self):
        """
        Return the dots per inch multiplier.

        :rtype: float
        """
        return self._dpi

    def setDpi(self, dpi):
        """
        Set the dots per inch multiplier.

        :type dpi: float
        :rtype: None
        """
        self._dpi = dpi

        width = 20 * dpi
        height = 18 * dpi

        self.setIndentation(9 * dpi)
        self.setMinimumWidth(20 * dpi)
        self.setIconSize(QtCore.QSize(width, height))
        self.setStyleSheet("height: {height}px;".format(height=height))

    def update(self, *args):
        """
        :rtype: None
        """
        for item in self.items():
            item.update()

    def items(self):
        """
        Return a list of all the items in the tree widget.

        :rtype: list[NavigationWidgetItem]
        """
        items = self.findItems(
            "*",
            QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )

        return items

    def itemFromUrl(self, url):
        """
        Return the item for the given url.

        :type url: QtCore.QUrl
        :rtype: NavigationWidgetItem
        """
        for item in self.items():
            if url == item.url():
                return item

    def itemFromPath(self, path):
        """
        Return the item for the given path.

        :type path: str
        :rtype: NavigationWidgetItem
        """
        return self._index.get(path)

    def settings(self):
        """
        Return a dictionary of the settings for this widget.

        :rtype: dict
        """
        settings = {}

        scrollBar = self.verticalScrollBar()
        settings["verticalScrollBar"] = {
            "value": scrollBar.value()
        }

        scrollBar = self.horizontalScrollBar()
        settings["horizontalScrollBar"] = {
            "value": scrollBar.value()
        }

        for item in self.items():
            itemSettings = item.settings()
            if itemSettings:
                settings[item.path()] = item.settings()

        return settings

    def setSettings(self, settings):
        """
        Set the settings for this widget

        :type settings: dict
        """
        for path in sorted(settings.keys()):
            s = settings.get(path, None)
            self.setPathSettings(path, s)

        scrollBarSettings = settings.get("verticalScrollBar", {})
        value = scrollBarSettings.get("value")
        if value:
            self.verticalScrollBar().setValue(value)

        scrollBarSettings = settings.get("horizontalScrollBar", {})
        value = scrollBarSettings.get("value")
        if value:
            self.horizontalScrollBar().setValue(value)

        self.setDpi(self.dpi())

    def setPathSettings(self, path, settings):
        """
        Show the context menu at the given position.

        :type path: str
        :type settings: dict
        :rtype: None
        """
        item = self.itemFromPath(path)
        if item and settings:
            item.setSettings(settings)

    def showContextMenu(self, position):
        """
        Show the context menu at the given position.
        
        :type position: QtCore.QPoint
        :rtype: None
        """
        menu = self.createContextMenu()
        menu.exec_(self.viewport().mapToGlobal(position))

    def expandedItems(self):
        """
        Return all the expanded items.

        :rtype:  list[NavigationWidgetItem]
        """
        for item in self.items():
            if self.isItemExpanded(item):
                yield item

    def expandedPaths(self):
        """
        Return all the expanded paths.

        :rtype:  list[NavigationWidgetItem]
        """
        for item in self.expandedItems():
            yield item.url()

    def setExpandedPaths(self, paths):
        """
        Set the given paths to expanded.

        :type paths: list[str]
        """
        for item in self.items():
            if item.url() in paths:
                item.setExpanded(True)

    def selectedItem(self):
        """
        Return the last selected item
        
        :rtype: SidebarWidgetItem
        """
        path = self.selectedPath()
        return self.itemFromPath(path)

    def selectedPath(self):
        """
        Return the last selected path

        :rtype: str or None
        """
        paths = self.selectedPaths()
        if paths:
            return paths[-1]

    def selectedPaths(self):
        """
        Return the paths that are selected.

        :rtype: list[str]
        """
        paths = []
        items = self.selectedItems()
        for item in items:
            path = item.path()
            paths.append(path)
        return studiolibrary.normPaths(paths)


    def selectPath(self, path):
        """
        Select the given path

        :type: str 
        :rtype: None
        """
        self.selectPaths([path])

    def selectPaths(self, paths):
        """
        Select the items with the given paths.

        :type paths: list[str]
        :rtype: None
        """
        paths = studiolibrary.normPaths(paths)
        items = self.items()
        for item in items:
            if studiolibrary.normPath(item.path()) in paths:
                item.setSelected(True)
            else:
                item.setSelected(False)

    def selectUrl(self, url):
        """
        Select the item with the given url.

        :type url: str
        :rtype: None
        """
        items = self.items()

        for item in items:
            if item.url() == url:
                item.setSelected(True)
            else:
                item.setSelected(False)

    def selectedUrls(self):
        """
        Return the urls for the selected items.

        :rtype: list[str]
        """
        urls = []
        items = self.selectedItems()
        for item in items:
            urls.append(item.url())
        return urls

    def setPaths(self, *args, **kwargs):
        """
        This method has been deprecated.
        """
        logger.warning("This method has been deprecated!")
        self.setData(*args, **kwargs)

    def refreshData(self):
        self.setData(self._data)

    def setData(self, data, root="", split=None):
        """
        Set the items to the given items.

        :type data: list[str]
        :type root: str
        :type split: str
        :rtype: None
        """
        self._data = data

        settings = self.settings()

        self.blockSignals(True)

        self.clear()

        if not root:
            root = findRoot(data.keys(), self.separator())

        self.addPaths(data, root=root, split=split)

        self.setSettings(settings)

        self.blockSignals(False)

        self.parent().search()

    def addPaths(self, paths, root="", split=None):
        """
        Set the given items as a flat list.

        :type paths: list[str]
        :type root: str or None
        :type split: str or None
        """
        data = pathsToDict(paths, root=root, separator=split)
        self.createItems(data, split=split)

        if isinstance(paths, dict):
            self.setSettings(paths)

    def createItems(self, data, split=None):
        """ 
        Create the items from the given data dict

        :type data: dict
        :type split: str or None

        :rtype: None
        """
        split = split or DEFAULT_SEPARATOR

        self._index = {}

        for key in data:

            root = split.join([key])

            item = None

            if self.isRootVisible():

                text = key.split(split)
                if text:
                    text = text[-1]
                else:
                    text = key

                item = SidebarWidgetItem(self)
                item.setText(0, six.text_type(text))
                item.setPath(root)
                item.setExpanded(True)

                self._index[root] = item

            def _recursive(parent, children, split=None, root=""):
                for text, val in sorted(children.items()):

                    if not parent:
                        parent = self

                    path = split.join([root, text])
                    path = studiolibrary.normPath(path)

                    child = SidebarWidgetItem(parent)
                    child.setText(0, six.text_type(text))
                    child.setPath(path)

                    self._index[path] = child

                    _recursive(child, val, split=split, root=path)

            _recursive(item, data[key], split=split, root=root)

        self.update()
        self.refreshFilter()


class ExampleWindow(QtWidgets.QWidget):

    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self._lineEdit = QtWidgets.QLineEdit()
        self._lineEdit.textChanged.connect(self.searchChanged)
        self._treeWidget = TreeWidget(self)

        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._slider.valueChanged.connect(self._valueChanged)
        self._slider.setRange(50, 200)
        self._slider.setValue(100)
        self._slider.setFixedHeight(18)

        layout.addWidget(self._slider)
        layout.addWidget(self._lineEdit)
        layout.addWidget(self._treeWidget)

        self._treeWidget.itemClicked.connect(self.itemClicked)
        self._treeWidget.itemSelectionChanged.connect(self.selectionChanged)

        self.update()

    def _valueChanged(self, value):
        self.update()

    def update(self):
        import studiolibrary

        value = self._slider.value()
        value = value / 100.0

        theme = studiolibrary.widgets.Theme()
        theme.setDpi(value)

        self._treeWidget.setDpi(value)
        self._treeWidget.setStyleSheet(theme.styleSheet())

    def setData(self, *args, **kwargs):
        self._treeWidget.setData(*args, **kwargs)

    def itemClicked(self):
        print("ITEM CLICKED")
        print(self._treeWidget.settings())

        items = self._treeWidget.selectedItems()
        for item in items:
            print(item.path())

    def selectionChanged(self, *args):
        print("SELECTION CHANGED", args)

    def searchChanged(self, text):
        print("SEARCH CHANGED", text)

        items = self._treeWidget.items()

        t = time.time()

        self._treeWidget.expandAll()

        for item in items:
            if text.lower() in item.text(0).lower():
                item.setHidden(False)
                for parent in item.parents():
                    parent.setHidden(False)
            else:
                item.setHidden(True)

        print(time.time() - t)


def runTests():

    paths = [
        '/fruit/apple',
        '/fruit/orange',
        '/fruit/banana'
    ]

    assert findRoot(paths) == '/fruit'

    paths = [
        '/fruit/apple',
        '/fruit/orange',
        '/fruit/banana',
        '/tesla/cars'
    ]

    assert findRoot(paths) == ''

    data = pathsToDict(paths)

    assert 'fruit' in data
    assert 'apple' in data.get('fruit')
    assert 'orange' in data.get('fruit')
    assert 'banana' in data.get('fruit')
    assert 'cars' in data.get('tesla')

    paths = [
        '>tesla>car>modelS',
        '>tesla>car>modelX',
        '>tesla>car>model3',
    ]

    assert findRoot(paths, separator='>') == '>tesla>car'

    data = pathsToDict(paths, separator='>')

    assert 'tesla' in data
    assert 'modelS' in data.get('tesla').get('car')
    assert 'modelX' in data.get('tesla').get('car')
    assert 'model3' in data.get('tesla').get('car')


def showExampleWindow():

    data = {
        "P:/production/shared/anim": {
            "text": "FOLDERS",
            "bold": True,
            "isExpanded": True,
            "iconPath": "none",
            "iconColor": "rgb(100, 100, 150)",
            "textColor": "rgba(100, 100, 150, 150)"
        },

        "P:/production/shared/anim/walks/fast.anim": {},
        "P:/production/shared/anim/walks/slow.anim": {},
        "P:/production/shared/anim/rigs/prop.rig": {},
        "P:/production/shared/anim/rigs/character.rig": {},

        "Users/libraries/animation/Character/Boris/stressed.pose": {},
        "Users/libraries/animation/Character/Boris/smile.pose": {},
        "Users/libraries/animation/Character/Cornilous/normal.pose": {},
        "Users/libraries/animation/Character/Cornilous/relaxed.pose": {},
        "Users/libraries/animation/Character/Cornilous/surprised.pose": {},
        "Users/libraries/animation/Character/Figaro/test.anim": {},
        "Users/libraries/animation/Character/Figaro/anim/hiccup.anim": {},

        "props/car/color/red": {},
        "props/car/color/orange": {},
        "props/car/color/yellow": {},
        "props/plane/color/blue": {},
        "props/plane/color/green": {},

        "/": {},
        "/Hello": {},
        "/Hello/World": {},
        "/Test/World": {},

        "tags": {
            "text": "TAGS",
            "bold": True,
            "isExpanded": True,
            "iconPath": "none",
            "iconColor": "rgb(100, 100, 150)",
            "textColor": "rgba(100, 100, 150, 150)"
        },
        "tags/red": {
            "iconColor": "rgb(200, 50, 50)",
            "iconPath": "../../resource/icons/circle.png"
        },
        "tags/orange": {
            "bold": True,
            "textColor": "rgb(250, 150, 50)",
            "iconColor": "rgb(250, 150, 50)",
            "iconPath": "../../resource/icons/circle.png"
        },
        "tags/yellow": {
            "iconColor": "rgb(250, 200, 0)",
            "iconPath": "../../resource/icons/circle.png"
        },
        "tags/blue": {
            "iconColor": "rgb(50, 150, 250)",
            "iconPath": "../../resource/icons/circle.png"
        },
        "tags/green": {
            "iconColor": "rgb(100, 200, 0)",
            "iconPath": "../../resource/icons/circle.png"
        }
    }

    window = ExampleWindow(None)
    window.setData(data)
    window.show()
    window.setGeometry(300, 300, 300, 600)
    return window


if __name__ == "__main__":
    with studioqt.app():
        w = showExampleWindow()
