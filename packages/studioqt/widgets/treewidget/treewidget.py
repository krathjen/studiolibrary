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

from treewidgetitem import TreeWidgetItem


__all__ = ["TreeWidget"]

logger = logging.getLogger(__name__)


SPLIT_TOKEN = "/"


def pathsToDict(paths, root="", split=None):
    """
    Return the given paths as a nested dict.

    Example:

    paths = ["/fruit/apple", "/fruit/orange"]
    print pathsToDict(paths)
    # Result: {"fruit" : {"apple":{}}, {"orange":{}}}

    :type paths: list[str]
    :type root: str
    :type split: str

    :rtype: dict
    """
    split = split or SPLIT_TOKEN
    results = {}

    for path in paths:
        p = results

        # This is to add support for grouping by the given root path.
        if root and root in path:
            path = path.replace(root, "")
            p = p.setdefault(root, {})

        keys = path.split(split)[0:]

        for key in keys:
            if key:
                p = p.setdefault(key, {})

    return results


class TreeWidget(QtWidgets.QTreeWidget):

    itemDropped = QtCore.Signal(object)
    itemRenamed = QtCore.Signal(str, str)
    itemSelectionChanged = QtCore.Signal()

    def __init__(self, *args):
        super(TreeWidget, self).__init__(*args)

        self._dpi = 1
        self._items = []
        self._locked = False

        self.itemExpanded.connect(self.update)
        self.itemCollapsed.connect(self.update)

        self.setDpi(1)

        self.setAcceptDrops(True)
        self.setHeaderHidden(True)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

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
        size = 24 * dpi
        self.setIndentation(15 * dpi)
        self.setMinimumWidth(35 * dpi)
        self.setIconSize(QtCore.QSize(size, size))
        self.setStyleSheet("height: {size}".format(size=size))

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
        for item in self.items():
            if path == item.path():
                return item

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
        value = scrollBarSettings.get("value", None)
        if value:
            self.verticalScrollBar().setValue(value)

        scrollBarSettings = settings.get("horizontalScrollBar", {})
        value = scrollBarSettings.get("value", None)
        if value:
            self.horizontalScrollBar().setValue(value)

        self.setIndentation(18 * self.dpi())

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
        
        :rtype: TreeWidgetItem 
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
        return paths

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
        paths = self.normPaths(paths)
        items = self.items()
        for item in items:
            if item.path() in paths:
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

    def normPaths(self, paths):
        return [path.replace("\\", "/") for path in paths]

    def setPaths(self, paths, root="", split=None):
        """
        Set the items to the given items.

        :type paths: list[str]
        :type root: str
        :rtype: None
        """
        settings = self.settings()

        self.blockSignals(True)

        self.clear()
        self.addPaths(paths, root=root, split=split)

        self.blockSignals(False)

        self.setSettings(settings)

    def addPaths(self, paths, root="", split=None):
        """
        Set the given items as a flat list.

        :type paths: list[str]
        :type root: str or None
        :type split: str or None

        :rtype: None
        """
        data = pathsToDict(paths, root=root, split=split)
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
        split = split or SPLIT_TOKEN

        for key in data:

            path = split.join([key])

            item = TreeWidgetItem(self)
            item.setText(0, unicode(key))
            item.setPath(path)

            def _recursive(parent, children, split=None):
                for text, val in sorted(children.iteritems()):

                    path = parent.path()
                    path = split.join([path, text])

                    child = TreeWidgetItem()
                    child.setText(0, unicode(text))
                    child.setPath(path)

                    parent.addChild(child)

                    _recursive(child, val, split=split)

            _recursive(item, data[key], split=split)

        self.update()


class ExampleWindow(QtWidgets.QWidget):

    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        layout = QtGui.QVBoxLayout(self)
        self.setLayout(layout)

        self._lineEdit = QtGui.QLineEdit()
        self._lineEdit.textChanged.connect(self.searchChanged)
        self._treeWidget = TreeWidget(self)

        self._slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self._slider.valueChanged.connect(self._valueChanged)
        self._slider.setRange(50, 200)
        self._slider.setValue(100)
        self._slider.setFixedHeight(18)

        layout.addWidget(self._slider)
        layout.addWidget(self._lineEdit)
        layout.addWidget(self._treeWidget)

        self._treeWidget.itemClicked.connect(self.itemClicked)
        self._treeWidget.itemSelectionChanged.connect(self.selectionChanged)

    def _valueChanged(self, value):

        value = value / 100.0

        theme = studioqt.Theme()
        theme.setDpi(value)
        theme.setLight()

        self._treeWidget.setDpi(value)
        self._treeWidget.setStyleSheet(theme.styleSheet())

    def setData(self, data):
        self._treeWidget.setPaths(data)

    def itemClicked(self):
        print "ITEM CLICKED"
        print self._treeWidget.settings()

        items = self._treeWidget.selectedItems()
        for item in items:
            print item.path()

    def selectionChanged(self, *args):
        print "SELECTION CHANGED", args

    def searchChanged(self, text):
        print "SEARCH CHANGED", text

        items = self._treeWidget.items()

        for item in items:
            item.setHidden(True)
            item.setExpanded(False)

        for item in items:
            if text in item.path():
                for parent in item.parents():
                    parent.setHidden(False)
                    parent.setExpanded(True)
                    parent.setSelected(True)


def showExampleWindow():

    data = {
        "P:/production/shared/anim": {
            "text": "FOLDERS",
            "bold": True,
            "isExpanded": True,
            "iconPath": "none",
            "iconColor": "rgb(100, 100, 150)",
            "textColor": "rgb(100, 100, 150, 150)"
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

        "tags": {
            "text": "TAGS",
            "bold": True,
            "isExpanded": True,
            "iconPath": "none",
            "iconColor": "rgb(100, 100, 150)",
            "textColor": "rgb(100, 100, 150, 150)"
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
