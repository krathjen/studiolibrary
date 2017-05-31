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
from treewidgetitemgroup import TreeWidgetItemGroup

__all__ = ["TreeWidget"]


logger = logging.getLogger(__name__)


def commonPrefix(s):
    """
    Return the longest common leading string from the given list.

    Example:
    
    a = ["c:/production/anim/fred", "c:/production/anim/bill"]
    print commonPrefix(a)
    # Result: c:/production/

    :type s: list[str]
    :rtype: str
    """
    if not s:
        return ''

    s1 = min(s)
    s2 = max(s)

    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]

    return s1


def commonPath(paths):
    """
    Return the longest common path.

    :type paths: list[str]
    :rtype: str
    """
    path = commonPrefix(paths)
    return path


def replaceCommonPath(paths, replace="", split="/"):
    """
    Replace the common path in the given paths.

    :type paths: list[str]
    :type replace: str
    :rtype: list[str]
    """
    result = []
    commonPath_ = commonPath(paths)
    commonDirname = split.join(commonPath_.split(split)[:-2]) + split

    for path in paths:
        path = path.replace(commonDirname, replace)
        result.append(path)

    return result


def pathsToDict(paths, split="/"):
    """
    Return the given paths as a nested dict.
    
    Example:
    
    paths = ["/fruit/apple", "/fruit/orange"]
    print pathsToDict(paths)
    # Result: {"fruit" : {"apple":{}}, {"orange":{}}} 
    
    :type paths: list[str]
    :type split: str

    :rtype: dict
    """
    results = {}

    for path in paths:
        p = results

        for key in path.split(split)[0:]:
            p = p.setdefault(key, {})

    return results


class TreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, *args):
        QtWidgets.QTreeWidget.__init__(self, *args)

        self._dpi = 1
        self._items = []

        self.setHeaderHidden(True)
        self.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)

        self.itemExpanded.connect(self.update)
        self.itemCollapsed.connect(self.update)

        self.setDpi(1)

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
        # QtWidgets.QTreeWidget.update(self, *args)

    def items(self):
        """
        Return a list of all the items in the tree widget.

        :rtype: list[studioqt.TreeWidgetItem]
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
        :rtype: studioqt.TreeWidgetItem
        """
        for item in self.items():
            if url == item.url():
                return item

    def itemFromPath(self, path):
        """
        Return the item for the given path.

        :type path: str
        :rtype: studioqt.TreeWidgetItem
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
        for path in settings:
            item = self.itemFromPath(path)
            if item:
                itemSettings = settings[path]
                item.setSettings(itemSettings)

    def showContextMenu(self, position):
        """
        :type position: QtCore.QPoint
        :rtype: None
        """
        menu = self.createContextMenu()
        menu.exec_(self.viewport().mapToGlobal(position))

    def expandedItems(self):
        """
        Return all the expanded items.
        
        :rtype:  list[studioqt.TreeWidgetItem]
        """
        for item in self.items():
            if self.isItemExpanded(item):
                yield item

    def expandedPaths(self):
        """
        Return all the expanded paths.

        :rtype:  list[studioqt.TreeWidgetItem]
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

    def selectPaths(self, paths):
        """
        Select the items with the given paths.
        
        :type paths: list[str]
        :rtype: None 
        """
        items = self.items()
        for item in items:
            if item.url().path() in paths:
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

    def setItems(self, items, view="tree", title=None):
        """
        Set the items to the given items.
        
        :type items: list[studioqt.TreeWidgetItem]
        :type view: str
        :type title: str
        :rtype: None 
        """
        settings = self.settings()
        self.clear()
        self.addItems(items=items, view=view, title=title)
        self.setSettings(settings)

    def addItems(self, items, view="tree", title=None):
        """
        Add the given items to the tree widget.
        
        :type items: list[studioqt.TreeWidgetItem]
        :type view: str
        :type title: str or None
        
        :rtype: None
        """
        if view == "list":
            self.setList(items, title=title)
        else:
            self.setTree(items, title=title)

    def setList(self, items, title=None):
        """
        Set the given items as a flat list.
        
        :type items: list[studioqt.TreeWidgetItem]
        :type title: str or None
        
        :rtype: None
        """
        if title is not None:
            item = TreeWidgetItemGroup(self, title)

        self.fillItem(None, items)
        self.setIndentation(5 * self.dpi())
        self.update()

    def setTree(self, items, title=None, split="/"):
        """
        Set the given items as a flat list.

        :type items: list[studioqt.TreeWidgetItem]
        :type title: str or None
        :type split: str

        :rtype: None
        """
        items = list(set(items))
        items = replaceCommonPath(items)

        if title is not None:
            item = TreeWidgetItemGroup(self, title)

        data = pathsToDict(items, split=split)

        self.fillItem(None, data)
        self.setIndentation(12 * self.dpi())

    def fillItem(self, item, data):
        """
        Update the treewidget with the given data.

        :type item: None or studioqt.TreeWidgetItem
        :type data: dict

        :rtype: None
        """
        if type(data) is list:
            for child in data:
                listItem = TreeWidgetItem(self)
                listItem.setText(0, str(child))

        if type(data) is dict:
            for key, val in sorted(data.iteritems()):

                if not item:
                    item = TreeWidgetItem(self)
                    item.setText(0, str(key))
                    child = item
                else:
                    child = TreeWidgetItem()
                    child.setText(0, str(key))
                    item.addChild(child)

                self.fillItem(child, val)

        if item:
            item.update()


class ExampleWindow(QtWidgets.QWidget):

    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        layout = QtGui.QVBoxLayout(self)
        self.setLayout(layout)

        self._lineEdit = QtGui.QLineEdit()
        self._lineEdit.textChanged.connect(self.searchChanged)
        self._treeWidget = TreeWidget(self)

        self._listWidget = QtGui.QListView(self)
        self._listWidget.setModel(self._treeWidget.model())
        self._listWidget.setViewMode(QtGui.QListView.IconMode)
        self._listWidget.setResizeMode(QtGui.QListView.Adjust)
        self._listWidget.setLayoutMode(QtGui.QListView.Batched)
        self._listWidget.setSelectionMode(QtGui.QListView.ExtendedSelection)
        self._listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        layout.addWidget(self._lineEdit)
        layout.addWidget(self._treeWidget)
        layout.addWidget(self._listWidget)

        self._treeWidget.itemClicked.connect(self.itemClicked)

    def setItems(self, paths):
        self._treeWidget.setItems(paths, title="FOLDERS", view="tree")

    def itemClicked(self):
        items = self._treeWidget.selectedItems()
        for item in items:
            print item.path()

    def searchChanged(self, text):

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


def showWxampleWindow():

    paths = [
    "Users/Hovel/Dropbox/libraries/animation/.studioLibrary/Boris/Boris.0001/4.pose",
    "Users/Hovel/Dropbox/libraries/animation/.studioLibrary/Boris/Boris.0001/5.pose",
    "Users/Hovel/Dropbox/libraries/animation/.studioLibrary/Boris/Boris.0001/w.pose",
    "Users/Hovel/Dropbox/libraries/animation/Boris/test.anim",
    "Users/Hovel/Dropbox/libraries/animation/Character/Boris/BORIS_BROWS_stressed.pose",
    "Users/Hovel/Dropbox/libraries/animation/Character/Boris/BORIS_MOUTH_smile_normal.pose",
    "Users/Hovel/Dropbox/libraries/animation/Character/Cornilous/CORNILOUS_BROWS_normal.pose",
    "Users/Hovel/Dropbox/libraries/animation/Character/Cornilous/CORNILOUS_BROWS_relaxed.pose",
    "Users/Hovel/Dropbox/libraries/animation/Character/Cornilous/surprised.pose",
    "Users/Hovel/Dropbox/libraries/animation/Character/Figaro/test.anim",
    "Users/Hovel/Dropbox/libraries/animation/Character/Figaro/anim/FIGARO_ hiccup.anim",
]

    paths = [
        "smile",
        "angry",
        "happy",
    ]

    window = ExampleWindow(None)
    window.setItems(paths)
    window.show()

    return window


if __name__ == "__main__":

    with studioqt.app():

        theme = studioqt.Theme()

        w = showWxampleWindow()
        w.setStyleSheet(theme.styleSheet())
