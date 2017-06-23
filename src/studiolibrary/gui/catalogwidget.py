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
import time
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary

__all__ = [
    "catalog",
    "CatalogWidget"
]

logger = logging.getLogger(__name__)


class PreviewFrame(QtWidgets.QFrame):
    pass


class FoldersFrame(QtWidgets.QFrame):
    pass


def catalog(path, show=True):
    """
    Return the catalog widget for the given path.
    
    :type path: str
    :type show: bool
    :rtype: CatalogWidget
    """
    def onItemsLoaded(w):
        items = w.items()
        paths = [os.path.dirname(item.path()) for item in items]
        w.setNavigationItems(paths, title="FOLDERS")

    w = CatalogWidget.instance(path, onItemsLoaded=onItemsLoaded)

    if show:
        w.show()
        w.raise_()

    return w


class CatalogWidget(QtWidgets.QWidget):

    _instances = {}

    DPI_ENABLED = False  # Still in development
    THEMES_MENU_ENABLED = True
    DEFAULT_GROUP_BY_COLUMNS = ["Category", "Modified", "Type"]

    MIN_SLIDER_DPI = 80
    MAX_SLIDER_DPI = 250
    MAX_SEARCH_LIMIT = 10000

    itemsLoaded = QtCore.Signal(object)
    itemSelectionChanged = QtCore.Signal(object)

    folderSelectionChanged = QtCore.Signal(object)

    @classmethod
    def instance(cls, path, onItemsLoaded=None):
        """
        Return the catalog widget for the given path.
        
        :type path: str
        :type onItemsLoaded: func
        :rtype: CatalogWidget
        """
        w = cls._instances.get(path)

        if not w:
            w = cls(path, onItemsLoaded=onItemsLoaded)
            cls._instances[path] = w

            # TODO: This needs to move to studiolibrarymaya.
            import mutils
            if mutils.isMaya():
                mutils.gui.makeMayaStandaloneWindow(w)

        return w

    def __init__(self, path, onItemsLoaded=None):
        """
        """
        QtWidgets.QWidget.__init__(self, None)

        self.setObjectName("studiolibrary")
        studiolibrary.analytics().logScreen("MainWindow")

        resource = studiolibrary.resource()
        self.setWindowIcon(resource.icon("icon_black"))

        windowTitle = "Studio Library | {version} | {path}"
        windowTitle = windowTitle.format(
            path=path,
            version=studiolibrary.version()
        )
        self.setWindowTitle(windowTitle)

        self._dpi = 1.0
        self._theme = None
        self._library = None
        self._database = None
        self._isLoaded = False
        self._currentItem = None
        self._previewWidget = None

        self._itemsHiddenCount = 0
        self._itemsVisibleCount = 0

        self._foldersWidgetVisible = True
        self._previewWidgetVisible = True
        self._statusBarWidgetVisible = True

        # --------------------------------------------------------------------
        # Create Widgets
        # --------------------------------------------------------------------

        self._foldersFrame = FoldersFrame(self)
        self._previewFrame = PreviewFrame(self)

        self._itemsWidget = studioqt.CombinedWidget(self)
        self._itemsWidget.setIconMode()

        tip = "Search all current items."
        self._searchWidget = studioqt.SearchWidget(self)
        self._searchWidget.setToolTip(tip)
        self._searchWidget.setStatusTip(tip)

        self._statusWidget = studioqt.StatusWidget(self)
        self._menuBarWidget = studioqt.MenuBarWidget()
        self._foldersWidget = studioqt.TreeWidget(self)
        self._foldersWidget.itemClicked.connect(self._folderClicked)

        self.setMinimumWidth(5)

        self.setMinimumHeight(5)

        # --------------------------------------------------------------------
        # Setup the menu bar buttons
        # --------------------------------------------------------------------

        name = "New Item"
        icon = studioqt.icon("add")
        tip = "Add a new item to the selected folder"
        self.addMenuBarAction(name, icon, tip, callback=self.showNewMenu, side="Left")

        name = "Item View"
        icon = studioqt.icon("view_settings")
        tip = "Change the style of the item view"
        self.addMenuBarAction(name, icon, tip, callback=self.showItemViewMenu)

        name = "Group By"
        icon = studioqt.icon("groupby")
        tip = "Group the current items in the view by column"
        self.addMenuBarAction(name, icon, tip, callback=self.showGroupByMenu)

        name = "Sort By"
        icon = studioqt.icon("sortby")
        tip = "Sort the current items in the view by column"
        self.addMenuBarAction(name, icon, tip, callback=self.showSortByMenu)

        name = "View"
        icon = studioqt.icon("view")
        tip = "Choose to show/hide both the preview and navigation pane. " \
              "Click + CTRL will hide the menu bar as well."
        self.addMenuBarAction(name, icon, tip, callback=self.toggleView)

        name = "Settings"
        icon = studioqt.icon("settings")
        tip = "Settings menu"
        self.addMenuBarAction(name, icon, tip, callback=self.showSettingsMenu)

        self._menuBarWidget.layout().insertWidget(1, self._searchWidget)

        # -------------------------------------------------------------------
        # Setup Layout
        # -------------------------------------------------------------------

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 0)
        self._previewFrame.setLayout(layout)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 0)

        self._foldersFrame.setLayout(layout)
        self._foldersFrame.layout().addWidget(self._foldersWidget)

        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self._splitter.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
        self._splitter.setHandleWidth(2)
        self._splitter.setChildrenCollapsible(False)

        self._splitter.insertWidget(0, self._foldersFrame)
        self._splitter.insertWidget(1, self._itemsWidget)
        self._splitter.insertWidget(2, self._previewFrame)

        self._splitter.setStretchFactor(0, False)
        self._splitter.setStretchFactor(1, True)
        self._splitter.setStretchFactor(2, False)

        self.layout().addWidget(self._menuBarWidget)
        self.layout().addWidget(self._splitter)
        self.layout().addWidget(self._statusWidget)

        vbox = QtWidgets.QVBoxLayout()
        self._previewFrame.setLayout(vbox)
        self._previewFrame.layout().setSpacing(0)
        self._previewFrame.layout().setContentsMargins(0, 0, 0, 0)
        self._previewFrame.setMinimumWidth(5)

        # -------------------------------------------------------------------
        # Setup Connections
        # -------------------------------------------------------------------

        searchWidget = self.searchWidget()
        searchWidget.searchChanged.connect(self._searchChanged)

        itemsWidget = self.itemsWidget()
        itemsWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        itemsWidget.itemMoved.connect(self._itemMoved)
        itemsWidget.itemSelectionChanged.connect(self._itemSelectionChanged)
        itemsWidget.customContextMenuRequested.connect(self.showItemsContextMenu)

        if onItemsLoaded:
            self.itemsLoaded.connect(onItemsLoaded)

        self.updateViewButton()
        self.itemsWidget().treeWidget().setValidGroupByColumns(self.DEFAULT_GROUP_BY_COLUMNS)
        self.setDatabasePath(path)

    def selectedFolderPath(self):
        """
        This method is needed when creating a new item.
        
        This will be deprecated in the future.
        
        :rtype: None 
        """
        return None

    def setNavigationItems(self, items, **kwargs):
        """
        Convenience method for setting the navigation items.

        :rtype: None 
        """
        self.foldersWidget().setItems(items, **kwargs)

    def _databaseChanged(self):
        """
        Triggered when the database changes on disc.

        :rtype: None 
        """
        logger.debug("Database changed triggered")
        self.loadItems()

    def _folderClicked(self):
        """
        Triggered when a folder has been clicked.
        
        :rtype: None 
        """
        items = self.foldersWidget().selectedItems()
        for item in items:
            path = item.path()
            self.searchWidget().setText(path)
            break

        self.foldersWidget().clearSelection()

    def _itemMoved(self, item):
        """
        Triggered when an item has been moved.

        :type item: studiolibrary.LibraryItem
        :rtype: None
        """
        pass

        # TODO: Add support for custom ordering
        # self.saveCustomOrder()

    def _itemSelectionChanged(self):
        """
        Triggered when an item is selected or deselected.

        :rtype: None
        """
        item = self.itemsWidget().selectedItem()

        if self._currentItem != item:
            self._currentItem = item
            self.setPreviewWidgetFromItem(item)

        self.itemSelectionChanged.emit(item)

    def addMenuBarAction(self, name, icon, tip, side="Right", callback=None):
        """
        Add a button/action to menu bar widget.

        :type name: str
        :type icon: QtWidget.QIcon
        :param tip: str
        :param side: str
        :param callback: func
        :rtype: QtWidget.QAction
        """
        return self.menuBarWidget().addAction(
            name=name,
            icon=icon,
            tip=tip,
            side=side,
            callback=callback,
        )

    def createNewMenu(self):
        """
        Return the new menu for adding new folders and items.

        :rtype: QtWidgets.QMenu
        """
        iconColor = self.theme().iconColor()

        menu = QtWidgets.QMenu(self)
        menu.setTitle("New")

        for itemClass in studiolibrary.itemClasses():
            action = itemClass.createAction(menu, self)

            icon = studioqt.Icon(action.icon())
            icon.setColor(iconColor)

            action.setIcon(icon)

            if action:
                menu.addAction(action)

        return menu

    def showNewMenu(self):
        """
        Creates and shows the new menu at the new action button.

        :rtype: QtWidgets.QAction
        """
        menu = self.createNewMenu()

        point = self.menuBarWidget().rect().bottomLeft()
        point = self.menuBarWidget().mapToGlobal(point)

        menu.show()
        return menu.exec_(point)

    def showGroupByMenu(self):
        """
        Show the group by menu at the group button.

        :rtype: None
        """
        menu = self.itemsWidget().createGroupByMenu()
        widget = self.menuBarWidget().findToolButton("Group By")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        menu.exec_(point)

    def showSortByMenu(self):
        """
        Show the sort by menu at the sort button.

        :rtype: None
        """
        menu = self.itemsWidget().createSortByMenu()
        widget = self.menuBarWidget().findToolButton("Sort By")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        menu.exec_(point)

    def showItemViewMenu(self):
        """
        Show the item settings menu.

        :rtype: None
        """
        menu = self.itemsWidget().createItemSettingsMenu()
        widget = self.menuBarWidget().findToolButton("Item View")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        menu.exec_(point)

    def foldersWidget(self):
        """
        :rtype: studiolibrary.FoldersWidget
        """
        return self._foldersWidget

    def statusWidget(self):
        """
        :rtype: StatusWidget
        """
        return self._statusWidget

    def searchWidget(self):
        """
        :rtype: SearchWidget
        """
        return self._searchWidget

    def menuBarWidget(self):
        """
        :rtype: MenuBarWidget
        """
        return self._menuBarWidget

    def itemsWidget(self):
        """
        Return the widget the contains all the items.

        :rtype: studioqt.CombinedWidget
        """
        return self._itemsWidget

    # -----------------------------------------------------------------
    # Support for loading and setting items
    # -----------------------------------------------------------------

    def clearItems(self):
        """
        Remove all the loaded items.

        :rtype: list[studiolibrary.LibraryItem]
        """
        self.itemsWidget().clear()

    def items(self):
        """
        Return all the loaded items.

        :rtype: list[studiolibrary.LibraryItem]
        """
        return self.itemsWidget().items()

    def database(self):
        """
        Return the database object.

        :rtype: studiolibrary.Database
        """
        return self._database

    def databasePath(self):
        """
        Return the database location on disc.
        
        :rtype: str 
        """
        return self.database().path()

    def setDatabasePath(self, path):
        """
        Set the database path for the catalog.
        
        :type path: str
        :rtype: None 
        """
        self._database = studiolibrary.Database(path)
        self._database.databaseChanged.connect(self._databaseChanged)
        self._database.setWatcherEnabled(True)
        self.loadItems()

    def path(self):
        """
        Return the library root path.

        :rtype: str
        """
        path = self.database().path()

        # Quick fix for paths that are in the .studiolibrary sub-directory.
        if "/.studiolibrary" in path.lower():
            path = os.path.dirname(path)

        return os.path.dirname(path)

    def setPath(self, path):
        """
        Convenience method to set the root path for the library.

        :type path: str
        :rtype: None
        """
        self.setRootPath(path)

    def setRootPath(self, path):
        """
        Set the root path for the library.

        :type path: str
        :rtype: None
        """
        trashPath = self.trashPath()
        folderWidget = self.foldersWidget()

        folderWidget.clearSelection()
        folderWidget.setRootPath(path)
        folderWidget.setFolderOrderIndex(trashPath, 0)

    @studioqt.showWaitCursor
    def loadItems(self):
        """
        Create the items from the database.

        :rtype: str 
        """
        logger.debug("Loading items")

        db = self.database()
        data = db.read()
        self.setItemData(data)
        self.itemsLoaded.emit(self)

    def setItemData(self, data):
        """
        Load the items from the given data dict.
        
        :type data: dict
        :rtype: None 
        """
        paths = data.keys()
        database = self.database()

        # Returns a iterator
        items_ = studiolibrary.itemsFromPaths(
            paths,
            database=database,
            libraryWidget=self,
        )

        items = list(items_)
        self.setItems(items)

    def setItems(self, items, sortEnabled=False):
        """
        Set the items for the library widget.

        :rtype: list[studiolibrary.LibraryItem]
        """
        selectedItems = self.selectedItems()

        self.clearItems()
        self.clearPreviewWidget()

        self.itemsWidget().setItems(items, sortEnabled=sortEnabled)

        self.loadItemData()

        if selectedItems:
            self.selectItems(selectedItems)

        self.refreshSearch()
        self.itemsWidget().refreshSortBy()

    def loadItemData(self):
        """
        Load the item data to the current items.

        :rtype: None
        """
        logger.debug("Loading item data")

        db = self.database()
        data = db.read()

        try:
            self.itemsWidget().setItemData(data)
        except Exception, msg:
            logger.exception(msg)

        self.refreshSearch()
        self.itemsWidget().refreshSortBy()

    # -----------------------------------------------------------------
    # Support for folder and item context menus
    # -----------------------------------------------------------------

    def createSettingsMenu(self):
        """
        Return the settings menu for changing the library widget.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu("", self)
        menu.setTitle("Settings")

        if self.DPI_ENABLED:
            action = studioqt.SliderAction("Dpi", menu)
            dpi = self.dpi() * 100.0
            action.slider().setRange(self.MIN_SLIDER_DPI, self.MAX_SLIDER_DPI)
            action.slider().setValue(dpi)
            action.valueChanged.connect(self._dpiSliderChanged)
            menu.addAction(action)

        if self.THEMES_MENU_ENABLED:
            menu.addSeparator()

            themesMenu = studioqt.ThemesMenu(menu)
            themesMenu.setCurrentTheme(self.theme())
            themesMenu.themeTriggered.connect(self.setTheme)

            menu.addMenu(themesMenu)

        menu.addSeparator()

        action = QtWidgets.QAction("Show menu", menu)
        action.setCheckable(True)
        action.setChecked(self.isMenuBarWidgetVisible())
        action.triggered[bool].connect(self.setMenuBarWidgetVisible)
        menu.addAction(action)

        action = QtWidgets.QAction("Show folders", menu)
        action.setCheckable(True)
        action.setChecked(self.isFoldersWidgetVisible())
        action.triggered[bool].connect(self.setFoldersWidgetVisible)
        menu.addAction(action)

        action = QtWidgets.QAction("Show preview", menu)
        action.setCheckable(True)
        action.setChecked(self.isPreviewWidgetVisible())
        action.triggered[bool].connect(self.setPreviewWidgetVisible)
        menu.addAction(action)

        action = QtWidgets.QAction("Show status", menu)
        action.setCheckable(True)
        action.setChecked(self.isStatusBarWidgetVisible())
        action.triggered[bool].connect(self.setStatusBarWidgetVisible)
        menu.addAction(action)

        menu.addSeparator()

        viewMenu = self.itemsWidget().createSettingsMenu()
        menu.addMenu(viewMenu)

        menu.addSeparator()

        action = QtWidgets.QAction("Help", menu)
        action.triggered.connect(self.help)
        menu.addAction(action)

        return menu

    def showSettingsMenu(self):
        """
        Show the settings menu at the current cursor position.

        :rtype: QtWidgets.QAction
        """
        menu = self.createSettingsMenu()

        point = self.menuBarWidget().rect().bottomRight()
        point = self.menuBarWidget().mapToGlobal(point)

        # Align menu to the left of the cursor.
        menu.show()
        x = point.x() - menu.width()
        point.setX(x)

        return menu.exec_(point)

    def showItemsContextMenu(self, pos=None):
        """
        Show the item context menu at the current cursor position.

        :type pos: QtGui.QPoint
        :rtype QtWidgets.QAction
        """
        items = self.itemsWidget().selectedItems()

        menu = self.createItemContextMenu(items)

        point = QtGui.QCursor.pos()
        point.setX(point.x() + 3)
        point.setY(point.y() + 3)
        action = menu.exec_(point)
        menu.close()

        return action

    def createItemEditMenu(self):
        """
        Return the edit menu for deleting, renaming items.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu(self)
        menu.setTitle("Edit")

        action = QtWidgets.QAction("Rename", menu)
        action.triggered.connect(self.renameSelectedItem)
        menu.addAction(action)

        action = QtWidgets.QAction("Show in folder", menu)
        action.triggered.connect(self.showItemsInFolder)
        menu.addAction(action)

        return menu

    def createItemContextMenu(self, items):
        """
        Return the item context menu for the given items.

        :type items: list[studiolibrary.LibraryItem]
        :rtype: studiolibrary.ContextMenu
        """
        menu = studioqt.ContextMenu(self)

        if items:
            item = items[-1]
            item.contextMenu(menu)

            editMenu = studioqt.ContextMenu(menu)
            editMenu.setTitle("Edit")
            menu.addMenu(editMenu)

            item.contextEditMenu(editMenu)

        menu.addSeparator()
        menu.addMenu(self.createSettingsMenu())

        return menu

    # -----------------------------------------------------------------------
    # Support for search
    # -----------------------------------------------------------------------

    def isPreviewWidgetVisible(self):
        """
        :rtype: bool
        """
        return self._previewWidgetVisible

    def isFoldersWidgetVisible(self):
        """
        :rtype: bool
        """
        return self._foldersWidgetVisible

    def isStatusBarWidgetVisible(self):
        """
        :rtype: bool
        """
        return self._statusBarWidgetVisible

    def isMenuBarWidgetVisible(self):
        """
        :rtype: bool
        """
        return self.menuBarWidget().isExpanded()

    def setPreviewWidgetVisible(self, value):
        """
        :type value: bool
        """
        value = bool(value)
        self._previewWidgetVisible = value

        if value:
            self._previewFrame.show()
        else:
            self._previewFrame.hide()

        self.updateViewButton()

    def setFoldersWidgetVisible(self, value):
        """
        :type value: bool
        """
        value = bool(value)
        self._foldersWidgetVisible = value

        if value:
            self._foldersFrame.show()
        else:
            self._foldersFrame.hide()

        self.updateViewButton()

    def setMenuBarWidgetVisible(self, value):
        """
        :type value: bool
        """
        value = bool(value)

        if value:
            self.menuBarWidget().expand()
        else:
            self.menuBarWidget().collapse()

    def setStatusBarWidgetVisible(self, value):
        """
        :type value: bool
        """
        value = bool(value)

        self._statusBarWidgetVisible = value
        if value:
            self.statusWidget().show()
        else:
            self.statusWidget().hide()

    # -----------------------------------------------------------------------
    # Support for search
    # -----------------------------------------------------------------------

    def filterItems(self, items, limit=None):
        """
        Filter the given items using the search filter.

        :rtype: list[studiolibrary.LibraryItem]
        """
        limit = limit or CatalogWidget.MAX_SEARCH_LIMIT

        searchFilter = self.searchWidget().searchFilter()

        column = self.itemsWidget().treeWidget().columnFromLabel("Search Order")

        max = 0

        for item in items:
            if max > limit:
                break

            if searchFilter.match(item.searchText()):
                max += 1
                item.setText(column, str(searchFilter.matches()))
                yield item

        if self.itemsWidget().sortColumn() == column:
            self.itemsWidget().refreshSortBy()

    def setSearchText(self, text):
        """
        Set the search widget text..

        :type text: str
        :rtype: None
        """
        self.searchWidget().setText(text)

    def refreshSearch(self):
        """
        Refresh the search results.

        :rtype: None
        """
        self._searchChanged()

    def itemsVisibleCount(self):
        """
        Return the number of items visible.

        :rtype:  int
        """
        return self._itemsVisibleCount

    def itemsHiddenCount(self):
        """
        Return the number of items hidden.

        :rtype:  int
        """
        return self._itemsHiddenCount

    def _searchChanged(self):
        """
        Triggered when the search widget has changed.

        :rtype: None
        """
        t = time.time()

        items = self.items()

        if self.searchWidget().text().strip() == "":
            validItems = []
        else:
            validItems = list(self.filterItems(items))

        invalidItems = list(set(items) - set(validItems))

        self._itemsVisibleCount = len(validItems)
        self._itemsHiddenCount = len(invalidItems)

        self.itemsWidget().setItemsHidden(validItems, False)
        self.itemsWidget().setItemsHidden(invalidItems, True)

        item = self.itemsWidget().selectedItem()

        if not item or item.isHidden():
            self.itemsWidget().clearSelection()

        if item:
            self.itemsWidget().scrollToItem(item)

        t = time.time() - t

        plural = ""
        if self._itemsVisibleCount > 1:
            plural = "s"

        self.itemsWidget().treeWidget().refreshGroupBy()

        msg = "Found {0} item{1} in {2:.3f} seconds."
        msg = msg.format(self._itemsVisibleCount, plural, t)
        self.statusWidget().setInfo(msg)

    # -----------------------------------------------------------------------
    # Support for custom preview widgets
    # -----------------------------------------------------------------------

    def setCreateWidget(self, widget):
        """
        :type widget: QtWidgets.QWidget
        :rtype: None
        """
        self.setPreviewWidgetVisible(True)
        self.itemsWidget().clearSelection()
        self.setPreviewWidget(widget)

    def clearPreviewWidget(self):
        """
        Set the default preview widget.
        """
        widget = studiolibrary.PreviewWidget(None)
        self.setPreviewWidget(widget)

    def setPreviewWidgetFromItem(self, item):
        """
        :type item: studiolibrary.LibraryItem
        :rtype: None
        """
        if item:
            try:
                previewWidget = item.previewWidget(self)
                self.setPreviewWidget(previewWidget)
            except Exception, msg:
                self.setError(msg)
                raise
        else:
            self.clearPreviewWidget()

    def previewWidget(self):
        """
        Return the current preview widget.

        :rtype: QtWidgets.QWidget
        """
        return self._previewWidget

    def setPreviewWidget(self, widget):
        """
        Set the preview widget.

        :type widget: QtWidgets.QWidget
        :rtype: None
        """
        if self._previewWidget == widget:
            msg = 'Preview widget already contains widget "{0}"'
            msg.format(widget)
            logger.debug(msg)
        else:
            self.closePreviewWidget()
            self._previewWidget = widget
            if self._previewWidget:
                self._previewFrame.layout().addWidget(self._previewWidget)
                self._previewWidget.show()

    def closePreviewWidget(self):
        """
        Close and delete the preview widget.

        :rtype: None
        """
        if self._previewWidget:
            self._previewWidget.close()

        layout = self._previewFrame.layout()
        while layout.count():
            item = layout.takeAt(0)
            item.widget().hide()
            item.widget().close()
            item.widget().deleteLater()

        self._previewWidget = None

    # -----------------------------------------------------------------------
    # Support for saving and loading the widget state
    # -----------------------------------------------------------------------

    def settingsPath(self):
        """
        :rtype: str
        """
        return os.path.join(studiolibrary.HOME_PATH, "Catalog", "library.json")

    def settings(self):
        """
        :rtype: dict
        """
        geometry = (
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width(),
            self.geometry().height()
        )
        settings = {}

        settings['dpi'] = self.dpi()
        settings['geometry'] = geometry
        settings['sizes'] = self._splitter.sizes()

        if self.theme():
            settings['theme'] = self.theme().settings()

        settings["foldersWidgetVisible"] = self.isFoldersWidgetVisible()
        settings["previewWidgetVisible"] = self.isPreviewWidgetVisible()
        settings["menuBarWidgetVisible"] = self.isMenuBarWidgetVisible()
        settings["statusBarWidgetVisible"] = self.isStatusBarWidgetVisible()

        settings['searchWidget'] = self.searchWidget().settings()
        settings['foldersWidget'] = self.foldersWidget().settings()
        settings['itemsWidget'] = self.itemsWidget().settings()

        return settings

    def setSettings(self, settings):
        """
        :type settings: dict
        """
        themeSettings = settings.get("theme", None)
        if themeSettings:
            theme = studioqt.Theme()
            theme.setSettings(themeSettings)
            self.setTheme(theme)

        self.itemsWidget().setToastEnabled(False)

        dpi = settings.get("dpi", 1.0)
        self.setDpi(dpi)

        sizes = settings.get('sizes', [140, 280, 180])
        if len(sizes) == 3:
            self.setSizes(sizes)

        x, y, width, height = settings.get("geometry", [200, 200, 860, 680])
        self.setGeometry(x, y, width, height)

        # Make sure the window is on the screen.
        screenGeometry = QtWidgets.QApplication.desktop().screenGeometry()
        if x < 0 or y < 0 or x > screenGeometry.x() or y > screenGeometry.y():
            self.centerWindow()

        # Reload the stylesheet before loading the dock widget settings.
        # Otherwise the widget will show docked without a stylesheet.
        self.reloadStyleSheet()

        value = settings.get("foldersWidgetVisible", True)
        self.setFoldersWidgetVisible(value)

        value = settings.get("menuBarWidgetVisible", True)
        self.setMenuBarWidgetVisible(value)

        value = settings.get("previewWidgetVisible", True)
        self.setPreviewWidgetVisible(value)

        value = settings.get("statusBarWidgetVisible", True)
        self.setStatusBarWidgetVisible(value)

        searchWidgetSettings = settings.get('searchWidget', {})
        self.searchWidget().setSettings(searchWidgetSettings)

        foldersWidgetSettings = settings.get('foldersWidget', {})
        self.foldersWidget().setSettings(foldersWidgetSettings)

        itemsWidgetSettings = settings.get('itemsWidget', {})
        self.itemsWidget().setSettings(itemsWidgetSettings)

        self.itemsWidget().setToastEnabled(True)

    def saveSettings(self):
        """
        Save the settings dictionary to a local json location.

        :rtype: None
        """
        data = self.settings()
        path = self.settingsPath()

        studiolibrary.saveJson(path, data)

    def loadSettings(self):
        """
        Read the settings dict from the local json location.

        :rtype: None
        """
        path = self.settingsPath()

        self.reloadStyleSheet()

        data = studiolibrary.readJson(path)
        self.setSettings(data)

    def setSizes(self, sizes):
        """
        :type sizes: (int, int, int)
        :rtype: None
        """
        fSize, cSize, pSize = sizes

        if pSize == 0:
            pSize = 200

        if fSize == 0:
            fSize = 120

        self._splitter.setSizes([fSize, cSize, pSize])
        self._splitter.setStretchFactor(1, 1)

    def centerWindow(self):
        """
        Center the widget to the center of the desktop.

        :rtype: None
        """
        geometry = self.frameGeometry()
        pos = QtWidgets.QApplication.desktop().cursor().pos()
        screen = QtWidgets.QApplication.desktop().screenNumber(pos)
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        geometry.moveCenter(centerPoint)
        self.move(geometry.topLeft())

    # -----------------------------------------------------------------------
    # Overloading events
    # -----------------------------------------------------------------------

    def event(self, event):
        """
        :type event: QtWidgets.QEvent
        :rtype: QtWidgets.QEvent
        """
        if isinstance(event, QtGui.QKeyEvent):
            if studioqt.isControlModifier() and event.key() == QtCore.Qt.Key_F:
                self.searchWidget().setFocus()

        if isinstance(event, QtGui.QStatusTipEvent):
            self.statusWidget().setInfo(event.tip())

        return QtWidgets.QWidget.event(self, event)

    def keyReleaseEvent(self, event):
        """
        :type event: QtGui.QKeyEvent
        :rtype: None
        """
        for item in self.selectedItems():
            item.keyReleaseEvent(event)
        QtWidgets.QWidget.keyReleaseEvent(self, event)

    def closeEvent(self, event):
        """
        :type event: QtWidgets.QEvent
        :rtype: None
        """
        self.saveSettings()
        QtWidgets.QWidget.closeEvent(self, event)

    def showEvent(self, event):
        """
        :type event: QtWidgets.QEvent
        :rtype: None
        """
        QtWidgets.QWidget.showEvent(self, event)

        if not self._isLoaded:
            self.loadSettings()

        self._isLoaded = True

    # -----------------------------------------------------------------------
    # Support for themes and custom style sheets
    # -----------------------------------------------------------------------

    def dpi(self):
        """
        Return the current dpi for the library widget.

        :rtype: float
        """
        return float(self._dpi)

    def setDpi(self, dpi):
        """
        Set the current dpi for the library widget.

        :rtype: float
        """
        if not self.DPI_ENABLED:
            dpi = 1.0

        self._dpi = dpi

        self.itemsWidget().setDpi(dpi)
        self.menuBarWidget().setDpi(dpi)
        self.foldersWidget().setDpi(dpi)
        self.statusWidget().setFixedHeight(20 * dpi)

        self._splitter.setHandleWidth(2 * dpi)

        self.itemsWidget().setToast("DPI: {0}".format(int(dpi * 100)))

        self.reloadStyleSheet()

    def _dpiSliderChanged(self, value):
        """
        Triggered the dpi action changes value.

        :rtype: float
        """
        dpi = value / 100.0
        self.setDpi(dpi)

    def setTheme(self, theme):
        """
        Set the theme for the catalog widget.
        
        :type theme: studioqt.Theme 
        :rtype: None 
        """
        self._theme = theme
        self.reloadStyleSheet()

    def theme(self):
        """
        Return the current theme for the catalog widget.
        
        :rtype: studioqt.Theme 
        """
        return self._theme or studioqt.Theme()

    def reloadStyleSheet(self):
        """
        Reload the style sheet to the current theme.

        :rtype: None
        """
        theme = self.theme()
        theme.setDpi(self.dpi())

        options = theme.options()
        styleSheet = theme.styleSheet()

        color = studioqt.Color.fromString(options["ITEM_TEXT_COLOR"])
        self.itemsWidget().setTextColor(color)

        color = studioqt.Color.fromString(options["ITEM_TEXT_SELECTED_COLOR"])
        self.itemsWidget().setTextSelectedColor(color)

        color = studioqt.Color.fromString(options["ITEM_BACKGROUND_COLOR"])
        self.itemsWidget().setBackgroundColor(color)

        color = studioqt.Color.fromString(options["ITEM_BACKGROUND_SELECTED_COLOR"])
        self.itemsWidget().setBackgroundSelectedColor(color)

        self.setStyleSheet(styleSheet)

        self.foldersWidget().update()
        self.searchWidget().update()
        self.menuBarWidget().update()

    # -----------------------------------------------------------------------
    # Support for message boxes
    # -----------------------------------------------------------------------

    def setInfo(self, text):
        self.statusWidget().setInfo(text)

    def setError(self, text):
        self.statusWidget().setError(unicode(text))
        self.setStatusBarWidgetVisible(True)

    def setWarning(self, text):
        self.statusWidget().setWarning(text)
        self.setStatusBarWidgetVisible(True)

    def setToast(self, text, duration=500):
        self.itemsWidget().setToast(text, duration)

    def criticalDialog(self, message, title="Error"):
        self.setError(message)
        return studioqt.MessageBox.critical(self, title, message)

    def questionDialog(self, message, title="Question"):
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel
        return studioqt.MessageBox.question(self, title, str(message), buttons)

    def updateWindowTitle(self):
        """
        Update the window title with the version the lock status.

        :rtype: None
        """
        title = "Studio Library - "

        if self.isDocked():
            title += self.library().name()
        else:
            title += studiolibrary.__version__ + " - " + self.library().name()

        if self.isLocked():
            title += " (Locked)"

        self.setWindowTitle(title)

    def isCompactView(self):
        """
        Return True if both the folder and preview widget are hidden

        :rtype: bool
        """
        return not self.isFoldersWidgetVisible() and not self.isPreviewWidgetVisible()

    def toggleView(self):
        """
        Toggle the preview widget and folder widget visible.

        :rtype: None
        """
        compact = self.isCompactView()

        if studioqt.isControlModifier():
            compact = False
            self.setMenuBarWidgetVisible(compact)

        self.setPreviewWidgetVisible(compact)
        self.setFoldersWidgetVisible(compact)

    def updateViewButton(self):
        """
        Update/referesh the icon on the view button.

        :rtype: None
        """
        compact = self.isCompactView()
        action = self.menuBarWidget().findAction("View")

        if not compact:
            icon = studioqt.icon("view_all")
        else:
            icon = studioqt.icon("view_compact")

        action.setIcon(icon)

        self.menuBarWidget().update()

    def showItemsInFolder(self):
        """
        Show the selected items in the system file explorer.

        :rtype: None 
        """
        items = self.selectedItems()

        for item in items:
            item.showInFolder()

        if not items:
            for folder in self.selectedFolders():
                folder.showInFolder()

    def selectPath(self, path):
        """
        Select the items with the given path.
        
        :type path: str
        :rtype: None 
        """
        self.selectPaths([path])

    def selectPaths(self, paths):
        """
        Select the items with the given paths.
        
        :type paths: list[str]
        :rtype: None 
        """
        selection = self.selectedItems()
        self.itemsWidget().selectPaths(paths)

        if self.selectedItems() != selection:
            self._itemSelectionChanged()

    def selectItems(self, items):
        """
        Select the given items.

        :type items: list[studiolibrary.LibraryItem]
        :rtype: None 
        """
        paths = [item.path() for item in items]
        self.selectPaths(paths)

    def selectedItems(self):
        """
        Return the given items that are selected.

        :rtype: list[studiolibrary.LibraryItem]
        """
        return self._itemsWidget.selectedItems()

    @staticmethod
    def help():
        """
        Launch the web browser to the help url.
        
        :rtype: None
        """
        import webbrowser
        webbrowser.open(studiolibrary.HELP_URL)


if __name__ == "__main__":

    path = u'C:/Users/Hovel/Dropbox/libraries/animation/.studioLibrary/item_data.json'

    with studioqt.app():
        c = catalog(path)