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

import re
import os
import time
import copy
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary

__all__ = ["LibraryWidget"]

logger = logging.getLogger(__name__)


class PreviewFrame(QtWidgets.QFrame):
    pass


class FoldersFrame(QtWidgets.QFrame):
    pass


class GlobalSignal(QtCore.QObject):
    """
    Triggered for all library instance.
    """
    debugModeChanged = QtCore.Signal(object, object)
    folderSelectionChanged = QtCore.Signal(object, object)


class LibraryWidget(QtWidgets.QWidget):
    _instances = {}

    DEFAULT_NAME = "Default"
    DEFAULT_SETTINGS = {
        "paneSizes": [160, 280, 180],
        "geometry": [-1, -1, 860, 720],
        "foldersWidgetVisible": True,
        "previewWidgetVisible": True,
        "menuBarWidgetVisible": True,
        "statusBarWidgetVisible": True,
        "recursiveSearchEnabled": False,
        "itemsWidget": {
                "spacing": 2,
                "padding": 6,
                "sortOrder": 0,
                "sortColumn": "Custom Order",
                "groupOrder": 0,
                "groupColumn": "Category",
                "zoomAmount": 80,
                "textVisible": True,
            },
        "searchWidget": {
                "text": "",
            },
        "theme": {
                "accentColor": "rgb(0, 175, 240, 255)",
                "backgroundColor": "rgb(60, 60, 80, 255)",
            }
        }

    DATABASE_PATH = "{path}/.studiolibrary/database.json"
    SETTINGS_PATH = "{local}/StudioLibrary/LibraryWidget.json"

    TRASH_ENABLED = True
    DEFAULT_GROUP_BY_COLUMNS = ["Category", "Modified", "Type"]

    RECURSIVE_SEARCH_DEPTH = 3
    RECURSIVE_SEARCH_ENABLED = False

    IGNORE_PATHS = studiolibrary.IGNORE_PATHS

    # Still in development
    DPI_ENABLED = False
    DPI_MIN_VALUE = 80
    DPI_MAX_VALUE = 250

    globalSignal = GlobalSignal()

    # Local signal
    loaded = QtCore.Signal()
    lockChanged = QtCore.Signal(object)
    debugModeChanged = QtCore.Signal(object)

    itemRenamed = QtCore.Signal(str, str)
    itemSelectionChanged = QtCore.Signal(object)

    folderRenamed = QtCore.Signal(str, str)
    folderSelectionChanged = QtCore.Signal(object)

    @classmethod
    def instances(cls):
        """
        Return all the LibraryWidget instances that have been initialised.

        :rtype: list[LibraryWidget]
        """
        return cls._instances.values()

    @classmethod
    def instance(
            cls,
            name="",
            path="",
            show=True,
            lock=False,
            superusers=None,
            lockRegExp=None,
            unlockRegExp=None,
    ):
        """
        Return the library widget for the given name.

        :type name: str
        :type path: str
        :type show: bool
        :type lock: bool
        :type superusers: list[str]
        :type lockRegExp: str
        :type unlockRegExp: str
        
        :rtype: LibraryWidget
        """
        name = name or cls.DEFAULT_NAME

        libraryWidget = cls._instances.get(name)

        if not libraryWidget:
            libraryWidget = cls(name=name)
            cls._instances[name] = libraryWidget

        libraryWidget.setLocked(lock)
        libraryWidget.setSuperusers(superusers)
        libraryWidget.setLockRegExp(lockRegExp)
        libraryWidget.setUnlockRegExp(unlockRegExp)

        if path:
            libraryWidget.setPath(path)

        if show:
            libraryWidget.show()

        return libraryWidget

    def __init__(self, parent=None, name="", path=""):
        """
        Create a new instance of the Library Widget.

        :type parent: QtWidgets.QWidget or None
        :type name: str
        :type path: str
        """
        QtWidgets.QWidget.__init__(self, parent)

        self.setObjectName("studiolibrary")

        studiolibrary.sendEvent("MainWindow", version=studiolibrary.version())

        resource = studiolibrary.resource()
        self.setWindowIcon(resource.icon("icon_black"))

        self._dpi = 1.0
        self._path = ""
        self._name = name or self.DEFAULT_NAME
        self._theme = None
        self._database = None
        self._isDebug = False
        self._isLocked = False
        self._isLoaded = False
        self._previewWidget = None
        self._currentItem = None
        self._refreshEnabled = False

        self._superusers = None
        self._lockRegExp = None
        self._unlockRegExp = None

        self._trashEnabled = self.TRASH_ENABLED
        self._recursiveSearchEnabled = self.RECURSIVE_SEARCH_ENABLED

        self._itemsHiddenCount = 0
        self._itemsVisibleCount = 0

        self._isTrashFolderVisible = False
        self._foldersWidgetVisible = True
        self._previewWidgetVisible = True
        self._statusBarWidgetVisible = True

        # --------------------------------------------------------------------
        # Create Widgets
        # --------------------------------------------------------------------

        self._foldersFrame = FoldersFrame(self)
        self._previewFrame = PreviewFrame(self)

        self._itemsWidget = studioqt.CombinedWidget(self)

        tip = "Search all current items."
        self._searchWidget = studioqt.SearchWidget(self)
        self._searchWidget.setToolTip(tip)
        self._searchWidget.setStatusTip(tip)

        self._statusWidget = studioqt.StatusWidget(self)
        self._menuBarWidget = studioqt.MenuBarWidget()
        self._foldersWidget = studioqt.TreeWidget(self)

        self.setMinimumWidth(5)
        self.setMinimumHeight(5)

        # --------------------------------------------------------------------
        # Setup the menu bar buttons
        # --------------------------------------------------------------------

        name = "New Item"
        icon = studioqt.resource.icon("add")
        tip = "Add a new item to the selected folder"
        self.addMenuBarAction(name, icon, tip, callback=self.showNewMenu)

        self._menuBarWidget.addWidget(self._searchWidget)

        name = "Item View"
        icon = studioqt.resource.icon("view_settings")
        tip = "Change the style of the item view"
        self.addMenuBarAction(name, icon, tip, callback=self.showItemViewMenu)

        name = "Group By"
        icon = studioqt.resource.icon("groupby")
        tip = "Group the current items in the view by column"
        self.addMenuBarAction(name, icon, tip, callback=self.showGroupByMenu)

        name = "Sort By"
        icon = studioqt.resource.icon("sortby")
        tip = "Sort the current items in the view by column"
        self.addMenuBarAction(name, icon, tip, callback=self.showSortByMenu)

        name = "View"
        icon = studioqt.resource.icon("view")
        tip = "Choose to show/hide both the preview and navigation pane. " \
              "Click + CTRL will hide the menu bar as well."
        self.addMenuBarAction(name, icon, tip, callback=self.toggleView)

        name = "Settings"
        icon = studioqt.resource.icon("settings")
        tip = "Settings menu"
        self.addMenuBarAction(name, icon, tip, callback=self.showSettingsMenu)

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
        self._splitter.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                     QtWidgets.QSizePolicy.Expanding)
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
        itemsWidget.itemDropped.connect(self._itemDropped)
        itemsWidget.itemSelectionChanged.connect(self._itemSelectionChanged)
        itemsWidget.customContextMenuRequested.connect(self.showItemsContextMenu)
        itemsWidget.treeWidget().setValidGroupByColumns(self.DEFAULT_GROUP_BY_COLUMNS)

        folderWidget = self.foldersWidget()
        folderWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        folderWidget.itemDropped.connect(self._itemDropped)
        folderWidget.itemSelectionChanged.connect(self._folderSelectionChanged)
        folderWidget.customContextMenuRequested.connect(self.showFolderMenu)

        self.folderSelectionChanged.connect(self.updateLock)

        self.updateViewButton()

        if path:
            self.setPath(path)

    def _searchChanged(self):
        """
        Triggered when the search text has changed.

        :rtype: None
        """
        self.refreshSearch()

    def _itemMoved(self, item):
        """
        Triggered when the custom order has changed.

        :type item: studiolibrary.LibraryItem
        :rtype: None
        """
        self.saveCustomOrder()

    def _itemSelectionChanged(self):
        """
        Triggered when an item is selected or deselected.

        :rtype: None
        """
        item = self.itemsWidget().selectedItem()

        self.setPreviewWidgetFromItem(item)
        self.itemSelectionChanged.emit(item)

    def _itemDropped(self, event):
        """
        Triggered when items are dropped on the items widget or folders widget.

        :type event: QtCore.QEvent
        :rtype: None
        """
        mimeData = event.mimeData()

        if mimeData.hasUrls():
            urls = mimeData.urls()
            path = self.selectedFolderPath()
            items = self.createItemsFromUrls(urls)

            if self.isMoveItemsEnabled():
                self.showMoveItemsDialog(items, dst=path)

            elif not self.isCustomOrderEnabled():
                msg = 'Please sort by "Custom Order" to reorder items!'
                self.showInfoMessage(msg)

    def _folderSelectionChanged(self):
        """
        Triggered when a folder is selected or deselected.

        :rtype: None
        """
        path = self.selectedFolderPath()
        self.refreshItems()

        self.folderSelectionChanged.emit(path)
        self.globalSignal.folderSelectionChanged.emit(self, path)

    def statusWidget(self):
        """
        Return the status widget.
        
        :rtype: studioqt.StatusWidget
        """
        return self._statusWidget

    def searchWidget(self):
        """
        Return the search widget.
        
        :rtype: studioqt.SearchWidget
        """
        return self._searchWidget

    def menuBarWidget(self):
        """
        Return the menu bar widget.
        
        :rtype: MenuBarWidget
        """
        return self._menuBarWidget

    def name(self):
        """
        Return the name of the library.

        :rtype: str
        """
        return self._name

    def path(self):
        """
        Return the root path for the library.

        :rtype: str
        """
        return self._path

    def setPath(self, path):
        """
        Set the root path for the library.

        :type path: str
        :rtype: None
        """
        path = studiolibrary.realPath(path)

        if path == self.path():
            logger.debug("The root path is already set.")
            return

        self._path = path

        databasePath = studiolibrary.formatPath(self.DATABASE_PATH, path=path)
        database = studiolibrary.Database(databasePath)

        self.setDatabase(database)

        self.refresh()

    @studioqt.showArrowCursor
    def showPathErrorDialog(self):
        """
        Called when the current root path doesn't exist on refresh.

        :rtype: None
        """
        path = self.path()

        title = "Path Error"

        text = 'The current root path does not exist "{path}". ' \
               'Please select a new root path to continue.'

        text = text.format(path=path)

        dialog = studioqt.createMessageBox(self, title, text)

        dialog.setHeaderColor("rgb(230, 80, 80)")
        dialog.show()

        dialog.accepted.connect(self.showChangePathDialog)

    @studioqt.showArrowCursor
    def showWelcomeDialog(self):
        """
        Called when there is no root path set for the library.

        :rtype: None
        """
        name = self.name()

        title = "Welcome"
        title = title.format(studiolibrary.version(), name)

        text = "Before you get started please choose a folder " \
               "location for storing the data. A network folder is " \
               "recommended for sharing within a studio."

        dialog = studioqt.createMessageBox(self, title, text)
        dialog.show()

        dialog.accepted.connect(self.showChangePathDialog)

    def showChangePathDialog(self):
        """
        Show a file browser dialog for changing the root path.

        :rtype: None
        """
        path = self._showChangePathDialog()
        self.setPath(path)

    @studioqt.showArrowCursor
    def _showChangePathDialog(self):
        """
        Open the file dialog for setting a new root path.

        :rtype: str
        """
        path = self.path()
        title = "Choose the root location"
        directory = path

        if not directory:
            directory = os.path.expanduser("~")

        dialog = QtWidgets.QFileDialog(None, QtCore.Qt.WindowStaysOnTopHint)

        dialog.setWindowTitle(title)
        dialog.setDirectory(directory)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            selectedFiles = dialog.selectedFiles()
            if selectedFiles:
                path = selectedFiles[0]

        path = studiolibrary.normPath(path)
        return path

    def isRefreshEnabled(self):
        """
        Return True if the LibraryWidget can be refreshed.
        
        :rtype: bool 
        """
        return self._refreshEnabled

    def setRefreshEnabled(self, enable):
        """
        If enable is False, all updates will be ignored.

        :rtype: bool 
        """
        self._refreshEnabled = enable

    def refresh(self):
        """
        Refresh all folders and items.
        
        :rtype: None 
        """
        if self.isRefreshEnabled():
            self.refreshFolders()
            self.refreshItems()
            self.updateWindowTitle()

    # -----------------------------------------------------------------
    # Methods for the folders widget
    # -----------------------------------------------------------------

    def foldersWidget(self):
        """
        Return the folders widget.
        
        :rtype: studioqt.TreeWidget
        """
        return self._foldersWidget

    def selectedFolderPath(self):
        """
        Return the selected folder items.

        :rtype: str or None
        """
        return self.foldersWidget().selectedPath()

    def selectedFolderPaths(self):
        """
        Return the selected folder items.

        :rtype: list[str]
        """
        return self.foldersWidget().selectedPaths()

    def selectFolderPath(self, path):
        """
        Select the given folder paths.

        :type path: str
        :rtype: None
        """
        self.selectFolderPaths([path])

    def selectFolderPaths(self, paths):
        """
        Select the given folder paths.

        :type paths: list[str]
        :rtype: None
        """
        self.foldersWidget().selectPaths(paths)

    def showInFolder(self):
        """
        Show the selected folder in the file explorer.

        :rtype: None 
        """
        path = self.selectedFolderPath()
        studiolibrary.showInFolder(path)

    def createFolder(self, *args):
        """
        Create a new folder on disc at the given path.
        
        :type args: list[str]
        :rtype: str 
        """
        path = os.path.join(*args)
        path = studiolibrary.normPath(path)

        if not os.path.exists(path):
            os.makedirs(path)

        db = self.database()
        db.addPath(path)

        self.refresh()
        self.selectFolderPath(path)

        return path

    def renameFolder(self, src, dst):
        """
        Rename the given src path to the given dst path.

        :type src: str 
        :type dst: str 
        :rtype: str 
        """
        try:
            dst = studiolibrary.renamePath(src, dst)

            db = self.database()
            db.renamePath(src, dst)

            self.refresh()
            self.selectFolderPath(dst)

        except Exception, e:
            self.showExceptionDialog("Rename Path Error", e)
            raise

        return dst

    @studioqt.showWaitCursor
    def refreshFolders(self):
        """
        Refresh the state of the folders widget.
        
        :rtype: None 
        """
        path = self.path()

        if not path:
            return self.showWelcomeDialog()
        elif not os.path.exists(path):
            return self.showPathErrorDialog()

        self.updateFolders()

    def updateFolders(self):
        """
        Update the folders to be shown in the folders widget.
        
        :rtype: None 
        """
        root = self.path()
        ignore = self.isInvalidFolderPath
        trashPath = self.trashPath()

        paths = {
            root: {
                "iconPath": "none",
                "bold": True,
                "text": "FOLDERS",
            }
        }

        for p in studiolibrary.findPaths(root, ignore=ignore):

            paths[p] = {}

            if trashPath == p:
                iconPath = studioqt.resource.get("icons", "delete.png")
                paths[p] = {
                    "iconPath": iconPath
                }

        self.foldersWidget().setPaths(paths, root=root)

        # Force the root folder item to be expanded
        folder = self.foldersWidget().itemFromPath(root)
        folder.setExpanded(True)

    def isInvalidFolderPath(self, path):
        """
        Return True if the given path is an invalid folder path.

        :type path: str
        :rtype: bool 
        """
        return not self.isValidFolderPath(path)

    def isValidFolderPath(self, path):
        """
        Return True if the given path is a valid folder.
        
        :type path: str
        :rtype: bool 
        """
        if not self.isTrashFolderVisible() and self.isPathInTrash(path):
            return False

        if os.path.isfile(path):
            return False

        if studiolibrary.isValidItemPath(path):
            return False

        for ignore in self.IGNORE_PATHS:
            if ignore.lower() in path.lower():
                return False

        return True

    def createFolderMenu(self):
        """
        Return the folder menu for the selected folders.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu(self)

        if self.isLocked():
            action = menu.addAction("Locked")
            action.setEnabled(False)
        else:
            menu.addMenu(self.createNewMenu())

            folders = self.selectedFolderPaths()

            if folders:
                m = self.createFolderEditMenu(menu)
                menu.addMenu(m)

            menu.addSeparator()
            menu.addMenu(self.createSettingsMenu())

        return menu

    def createFolderEditMenu(self, parent):
        """
        Create the menu for editing the folders.
        
        :type parent: QtWidgets.QMenu
        :rtype: QtWidgets.QMenu
        """
        selectedFolders = self.selectedFolderPaths()

        menu = QtWidgets.QMenu(parent)
        menu.setTitle("Edit")

        if len(selectedFolders) == 1:
            action = QtWidgets.QAction("Rename", menu)
            action.triggered.connect(self.showRenameFolderDialog)
            menu.addAction(action)

            action = QtWidgets.QAction("Show in Folder", menu)
            action.triggered.connect(self.showInFolder)
            menu.addAction(action)

            if self.trashEnabled():
                menu.addSeparator()

                action = QtWidgets.QAction("Move to Trash", menu)
                action.setEnabled(not self.isTrashSelected())
                action.triggered.connect(self.showMoveFoldersToTrashDialog)
                menu.addAction(action)

        return menu

    def showRenameFolderDialog(self, parent=None):
        """
        Show the dialog for renaming the selected folder.
        
        :rtype: None
        """
        parent = parent or self

        path = self.selectedFolderPath()

        name, button = studioqt.MessageBox.input(
            parent,
            "Rename Folder",
            "Rename the selected folder to:",
            inputText=os.path.basename(path),
        )
        name = name.strip()

        if name and button == QtWidgets.QDialogButtonBox.Ok:
            self.renameFolder(path, name)

    def showCreateFolderDialog(self, parent=None):
        """
        Show the dialog for creating a new folder.
        
        :rtype: None
        """
        parent = parent or self

        path = self.selectedFolderPath() or self.path()

        name, button = studioqt.MessageBox.input(
            parent,
            "Create a new folder",
            "Create a new folder with the name:",
        )
        name = name.strip()

        if name and button == QtWidgets.QDialogButtonBox.Ok:
            self.createFolder(path, name)

    # -----------------------------------------------------------------
    # Methods for the items widget
    # -----------------------------------------------------------------

    def itemsWidget(self):
        """
        Return the widget the contains all the items.

        :rtype: studioqt.CombinedWidget
        """
        return self._itemsWidget

    def selectPath(self, path):
        """
        Select the item with the given path.

        :type path: str
        :rtype: None
        """
        self.selectPaths([path])

    def selectPaths(self, paths):
        """
        Select items with the given paths.

        :type paths: list[str]
        :rtype: None
        """
        selection = self.selectedItems()

        self.clearPreviewWidget()
        self.itemsWidget().clearSelection()
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

    def scrollToSelectedItem(self):
        """
        Scroll the item widget to the selected item.

        :rtype: None
        """
        self.itemsWidget().scrollToSelectedItem()

    def refreshSelection(self):
        """
        Refresh the current item selection.

        :rtype: None
        """
        items = self.selectedItems()
        self.itemsWidget().clearSelection()
        self.selectItems(items)

    def selectedItems(self):
        """
        Return the selected items.

        :rtype: list[studiolibrary.LibraryItem]
        """
        return self._itemsWidget.selectedItems()

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

    def addItem(self, item, select=False):
        """
        Add the given item to the itemsWidget.

        :type item: studiolibrary.LibraryItem
        :type select: bool

        :rtype: None
        """
        self.addItems([item], select=select)

    def addItems(self, items, select=False):
        """
        Add the given items to the itemsWidget.

        :type items: list[studiolibrary.LibraryItem]
        :type select: bool
        
        :rtype: None
        """
        self.itemsWidget().addItems(items)
        self.refreshItemData()

        if select:
            self.selectItems(items)
            self.scrollToSelectedItem()

    def setItems(self, items):
        """
        Set the items for the library widget.

        :rtype: list[studiolibrary.LibraryItem]
        """
        selectedItems = self.selectedItems()

        data = self.readItemData()

        self.itemsWidget().setItems(items, data=data, sortEnabled=True)

        self.refreshSearch()

        if selectedItems:
            self.selectItems(selectedItems)

    @studioqt.showWaitCursor
    def refreshItems(self):
        """
        Refresh the items for the library widget.

        :rtype: list[studiolibrary.LibraryItem]
        """
        elapsedTime = time.time()

        paths = self.itemsWidget().selectedPaths()

        self.updateItems()

        self.itemsWidget().selectPaths(paths)

        elapsedTime = time.time() - elapsedTime
        self.showRefreshMessage(elapsedTime)

    def updateItems(self):
        """
        Update the items to be shown in the items widget.

        :rtype: list[studiolibrary.LibraryItem]
        """
        paths = self.selectedFolderPaths()

        self.clearItems()

        depth = 1
        if self.isRecursiveSearchEnabled():
            depth = self.RECURSIVE_SEARCH_DEPTH

        items = list(studiolibrary.findItemsInFolders(
            paths,
            depth,
            libraryWidget=self,
            )
        )

        self.setItems(items)

    def createItemsFromUrls(self, urls):
        """
        Return a new instance of the items to be shown from the given urls.

        :rtype: list[studiolibrary.LibraryItem]
        """
        return studiolibrary.itemsFromUrls(urls, libraryWidget=self)

    # -----------------------------------------------------------------
    # Support for custom context menus
    # -----------------------------------------------------------------

    def addMenuBarAction(self, name, icon, tip, callback=None):
        """
        Add a button/action to menu bar widget.

        :type name: str
        :type icon: QtWidget.QIcon
        :type tip: str
        :type callback: func
        :type: QtWidget.QAction
        """

        # The method below is needed to fix an issue with PySide2.
        def _callback():
            callback()

        action = self.menuBarWidget().addAction(name)

        if icon:
            action.setIcon(icon)

        if tip:
            action.setToolTip(tip)
            action.setStatusTip(tip)

        if callback:
            action.triggered.connect(_callback)

        return action

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

    def createNewMenu(self):
        """
        Return the new menu for adding new folders and items.

        :rtype: QtWidgets.QMenu
        """
        color = self.iconColor()

        icon = studiolibrary.resource().icon("add", color=color)
        menu = QtWidgets.QMenu(self)
        menu.setIcon(icon)
        menu.setTitle("New")

        icon = studiolibrary.resource().icon("folder", color=color)
        action = QtWidgets.QAction(icon, "Folder", menu)
        action.triggered.connect(self.showCreateFolderDialog)
        menu.addAction(action)

        separator = QtWidgets.QAction("", menu)
        separator.setSeparator(True)
        menu.addAction(separator)

        for itemClass in studiolibrary.itemClasses():
            action = itemClass.createAction(menu, self)

            if action:
                icon = studioqt.Icon(action.icon())
                icon.setColor(self.iconColor())

                action.setIcon(icon)
                menu.addAction(action)

        return menu

    def createSettingsMenu(self):
        """
        Return the settings menu for changing the library widget.

        :rtype: studioqt.Menu
        """
        menu = studioqt.Menu("", self)
        menu.setTitle("Settings")

        action = menu.addAction("Refresh")
        action.triggered.connect(self.refresh)
        menu.addSeparator()

        if self.DPI_ENABLED:
            action = studioqt.SliderAction("Dpi", menu)
            dpi = self.dpi() * 100.0
            action.slider().setRange(self.DPI_MIN_VALUE, self.DPI_MAX_VALUE)
            action.slider().setValue(dpi)
            action.valueChanged.connect(self._dpiSliderChanged)
            menu.addAction(action)

        action = QtWidgets.QAction("Change Root Path", menu)
        action.triggered.connect(self.showChangePathDialog)
        menu.addAction(action)

        menu.addSeparator()
        themesMenu = studioqt.ThemesMenu(menu)
        themesMenu.setCurrentTheme(self.theme())
        themesMenu.themeTriggered.connect(self.setTheme)
        menu.addMenu(themesMenu)

        menu.addSeparator()

        action = QtWidgets.QAction("Show Menu", menu)
        action.setCheckable(True)
        action.setChecked(self.isMenuBarWidgetVisible())
        action.triggered[bool].connect(self.setMenuBarWidgetVisible)
        menu.addAction(action)

        action = QtWidgets.QAction("Show Folders", menu)
        action.setCheckable(True)
        action.setChecked(self.isFoldersWidgetVisible())
        action.triggered[bool].connect(self.setFoldersWidgetVisible)
        menu.addAction(action)

        action = QtWidgets.QAction("Show Preview", menu)
        action.setCheckable(True)
        action.setChecked(self.isPreviewWidgetVisible())
        action.triggered[bool].connect(self.setPreviewWidgetVisible)
        menu.addAction(action)

        action = QtWidgets.QAction("Show Status", menu)
        action.setCheckable(True)
        action.setChecked(self.isStatusBarWidgetVisible())
        action.triggered[bool].connect(self.setStatusBarWidgetVisible)
        menu.addAction(action)

        menu.addSeparator()
        action = QtWidgets.QAction("Reset Settings", menu)
        action.triggered.connect(self.resetSettings)
        menu.addAction(action)

        if self.trashEnabled():
            menu.addSeparator()
            action = QtWidgets.QAction("Show Trash Folder", menu)
            action.setEnabled(self.trashFolderExists())
            action.setCheckable(True)
            action.setChecked(self.isTrashFolderVisible())
            action.triggered[bool].connect(self.setTrashFolderVisible)
            menu.addAction(action)

        menu.addSeparator()

        action = QtWidgets.QAction("Enable Recursive Search", menu)
        action.setCheckable(True)
        action.setChecked(self.isRecursiveSearchEnabled())
        action.triggered[bool].connect(self.setRecursiveSearchEnabled)
        menu.addAction(action)

        menu.addSeparator()

        viewMenu = self.itemsWidget().createSettingsMenu()
        menu.addMenu(viewMenu)

        menu.addSeparator()

        action = QtWidgets.QAction("Debug Mode", menu)
        action.setCheckable(True)
        action.setChecked(self.isDebug())
        action.triggered[bool].connect(self.setDebugMode)
        menu.addAction(action)

        action = QtWidgets.QAction("Help", menu)
        action.triggered.connect(self.help)
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

    def showFolderMenu(self, pos=None):
        """
        Show the folder context menu at the current cursor position.

        :type pos: None or QtCore.QPoint
        :rtype: QtWidgets.QAction
        """
        menu = self.createFolderMenu()

        point = QtGui.QCursor.pos()
        point.setX(point.x() + 3)
        point.setY(point.y() + 3)
        action = menu.exec_(point)
        menu.close()

        return action

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

    def createItemContextMenu(self, items):
        """
        Return the item context menu for the given items.

        :type items: list[studiolibrary.LibraryItem]
        :rtype: studiolibrary.ContextMenu
        """
        menu = studioqt.Menu(self)

        item = None

        if items:
            item = items[-1]
            item.contextMenu(menu)

        if not self.isLocked():
            menu.addMenu(self.createNewMenu())

            if item:
                editMenu = studioqt.Menu(menu)
                editMenu.setTitle("Edit")
                menu.addMenu(editMenu)

                item.contextEditMenu(editMenu)

                if self.trashEnabled():
                    editMenu.addSeparator()

                    action = QtWidgets.QAction("Move to Trash", editMenu)
                    action.setEnabled(not self.isTrashSelected())
                    action.triggered.connect(self.showMoveItemsToTrashDialog)
                    editMenu.addAction(action)

        menu.addSeparator()
        menu.addMenu(self.createSettingsMenu())

        return menu

    # -------------------------------------------------------------------
    # Support for reading and writing to the item database
    # -------------------------------------------------------------------

    def database(self):
        """
        Return the database object.

        :rtype: studiolibrary.Database
        """
        return self._database

    def setDatabase(self, database):
        """
        Set the database path for the catalog.

        :type database: studiolibrary.Database
        :rtype: None
        """
        self._database = database

    def refreshItemData(self):
        """
        Update the current items with the data from the database.
        
        :rtype: None 
        """
        self.loadItemData()
        self.refreshSearch()

    def readItemData(self):
        """
        Read and return all the item data from the database.

        :rtype: dict
        """
        data = {}
        db = self.database()

        if db:
            data = db.read()

        return data

    def loadItemData(self):
        """
        Load the item data to the current items.

        :rtype: None
        """
        logger.debug("Loading item data")

        data = self.readItemData()

        try:
            self.itemsWidget().setItemData(data)
        except Exception, msg:
            logger.exception(msg)

    def saveItemData(self, columns):
        """
        Save the given column data for the current items.

        :rtype: None
        """
        logger.debug("Saving item data")

        data = self.itemsWidget().itemData(columns)

        db = self.database()
        db.update(data)

        self.refreshItemData()

    def saveCustomOrder(self):
        """
        Convenience method for saving the custom order.

        :rtype:  None
        """
        self.saveItemData(["Custom Order"])

    # -------------------------------------------------------------------
    # Support for moving items with drag and drop
    # -------------------------------------------------------------------

    def isCustomOrderEnabled(self):
        """
        Return True if sorting by "Custom Order" is enabled.

        :rtype: bool 
        """
        sortColumn = self.itemsWidget().sortColumn()
        customOrderColumn = self.itemsWidget().columnFromLabel("Custom Order")

        return sortColumn == customOrderColumn

    def isMoveItemsEnabled(self):
        """
        Return True if moving items via drag and drop is enabled.

        :rtype: bool 
        """
        paths = self.selectedFolderPaths()

        if len(paths) != 1:
            return False

        if self.selectedItems():
            return False

        return True

    def createMoveItemsDialog(self):
        """
        Create and return a dialog for moving items.
        
        :rtype: studioqt.MessageBox
        """
        text = 'Would you like to copy or move the selected item/s?'

        dialog = studioqt.createMessageBox(self, "Move or Copy items?", text)
        dialog.buttonBox().clear()

        dialog.addButton(u'Copy', QtWidgets.QDialogButtonBox.AcceptRole)
        dialog.addButton(u'Move', QtWidgets.QDialogButtonBox.AcceptRole)
        dialog.addButton(u'Cancel', QtWidgets.QDialogButtonBox.RejectRole)

        return dialog

    def showMoveItemsDialog(self, items, dst):
        """
        Show the move items dialog for the given items.
        
        :type items: list[studiolibrary.LibraryItem]
        :type dst: str
        :rtype: None
        """
        Copy = 0
        Cancel = 2

        # Check if the items are moving to another folder.
        for item in items:
            if item.dirname() == dst:
                return

        dialog = self.createMoveItemsDialog()
        action = dialog.exec_()
        dialog.close()

        if action == Cancel:
            return

        copy = action == Copy

        self.moveItems(items, dst, copy=copy)

    def moveItems(self, items, dst, copy=False, force=False):
        """
        Move the given items to the destination folder path.
        
        :type items: list[studiolibrary.LibraryItem]
        :type dst: str
        :type copy: bool
        :type force: bool
        :rtype: None 
        """
        self.itemsWidget().clearSelection()

        movedItems = []

        try:
            for item in items:

                path = dst + "/" + item.name()

                if force:
                    path = studiolibrary.generateUniquePath(path)

                if copy:
                    item.copy(path)
                else:
                    item.rename(path)

                movedItems.append(item)

        except Exception, e:
            self.showExceptionDialog("Move Error", e)
            raise
        finally:
            self.refreshItems()
            self.selectItems(movedItems)

    # -----------------------------------------------------------------------
    # Support for search
    # -----------------------------------------------------------------------

    def isPreviewWidgetVisible(self):
        """
        Return True if the PreviewWidget is visible, otherwise return False.
        
        :rtype: bool
        """
        return self._previewWidgetVisible

    def isFoldersWidgetVisible(self):
        """
        Return True if the FoldersWidget is visible, otherwise return False.
        
        :rtype: bool
        """
        return self._foldersWidgetVisible

    def isStatusBarWidgetVisible(self):
        """
        Return True if the StatusWidget is visible, otherwise return False.

        :rtype: bool
        """
        return self._statusBarWidgetVisible

    def isMenuBarWidgetVisible(self):
        """
        Return True if the MenuBarWidget is visible, otherwise return False.
        
        :rtype: bool
        """
        return self.menuBarWidget().isExpanded()

    def setPreviewWidgetVisible(self, value):
        """
        If the value is True then show the PreviewWidget, otherwise hide.

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
        If the value is True then show the FoldersWidget, otherwise hide.
        
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
        If the value is True then show the tMenuBarWidget, otherwise hide.

        :type value: bool
        """
        value = bool(value)

        if value:
            self.menuBarWidget().expand()
        else:
            self.menuBarWidget().collapse()

    def setStatusBarWidgetVisible(self, value):
        """
        If the value is True then show the StatusBarWidget, otherwise hide.
        
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
        if not self.isRefreshEnabled():
            logger.debug('Refresh search is disabled!')
            return

        t = time.time()

        self.updateSearch()

        t = time.time() - t

        plural = ""
        if self._itemsVisibleCount > 1:
            plural = "s"

        msg = "Found {0} item{1} in {2:.3f} seconds."
        msg = msg.format(self._itemsVisibleCount, plural, t)
        self.statusWidget().showInfoMessage(msg)

    def updateSearch(self):
        """
        Update the items with the search filter.
        
        :rtype: None 
        """
        items = self.items()
        self.filterItems(items)

    def filterItems(self, items):
        """
        Filter the given items using the search filter.

        :rtype: list[studiolibrary.LibraryItem]
        """
        searchFilter = self.searchWidget().searchFilter()

        column = self.itemsWidget().treeWidget().columnFromLabel(
            "Search Order")

        validItems = []
        for item in items:
            if searchFilter.match(item.searchText()):
                item.setText(column, str(searchFilter.matches()))
                validItems.append(item)

        if self.itemsWidget().sortColumn() == column:
            self.itemsWidget().refreshSortBy()

        self.showItems(validItems, hideOthers=True)

    def showItems(self, items, hideOthers=True):
        """
        Only show the given items in the items widget.
        
        :type items: list[studiolibrary.LibraryItem]
        :type hideOthers: bool
        :rtype: None 
        """
        items_ = self.items()

        hiddenItems = list(set(items_) - set(items))

        self._itemsVisibleCount = len(items)
        self._itemsHiddenCount = len(hiddenItems)

        self.itemsWidget().setItemsHidden(items, False)

        if hideOthers:
            self.itemsWidget().setItemsHidden(hiddenItems, True)

        item = self.itemsWidget().selectedItem()

        if not item or item.isHidden():
            self.itemsWidget().clearSelection()

        if item:
            self.itemsWidget().scrollToItem(item)

        self.itemsWidget().treeWidget().refreshGroupBy()

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
        widget = QtWidgets.QWidget(None)
        self.setPreviewWidget(widget)

    def setPreviewWidgetFromItem(self, item):
        """
        :type item: studiolibrary.LibraryItem
        :rtype: None
        """
        if self._currentItem == item:
            logger.debug("The current item preview widget is already set.")
            return

        self._currentItem = item

        if item:
            try:
                item.showPreviewWidget(self)
            except Exception, e:
                self.showErrorMessage(e)
                self.clearPreviewWidget()
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

    def resetSettings(self):
        """
        Reset the settings to the default settings.

        :rtype: str
        """
        self.setSettings(self.DEFAULT_SETTINGS)

    def settingsPath(self):
        """
        Return the settings path for the LibraryWidget.

        :rtype: str
        """
        return studiolibrary.formatPath(self.SETTINGS_PATH)

    def geometrySettings(self):
        """
        Return the geometry values as a list.

        :rtype: list[int]
        """
        settings = (
            self.window().geometry().x(),
            self.window().geometry().y(),
            self.window().geometry().width(),
            self.window().geometry().height()
        )
        return settings

    def setGeometrySettings(self, settings):
        """
        Set the geometry of the widget with the given values.

        :type settings: list[int]
        :rtype: None
        """
        x, y, width, height = settings

        screenGeometry = QtWidgets.QApplication.desktop().screenGeometry()
        screenWidth = screenGeometry.width()
        screenHeight = screenGeometry.height()

        if x <= 0 or y <= 0 or x >= screenWidth or y >= screenHeight:
            self.centerWindow(width, height)
        else:
            self.window().setGeometry(x, y, width, height)

    def settings(self):
        """
        Return a dictionary with the widget settings.

        :rtype: dict
        """
        settings = {}

        settings['dpi'] = self.dpi()
        settings['geometry'] = self.geometrySettings()
        settings['paneSizes'] = self._splitter.sizes()

        if self.theme():
            settings['theme'] = self.theme().settings()

        settings["foldersWidgetVisible"] = self.isFoldersWidgetVisible()
        settings["previewWidgetVisible"] = self.isPreviewWidgetVisible()
        settings["menuBarWidgetVisible"] = self.isMenuBarWidgetVisible()
        settings["statusBarWidgetVisible"] = self.isStatusBarWidgetVisible()

        settings["recursiveSearchEnabled"] = self.isRecursiveSearchEnabled()

        settings['itemsWidget'] = self.itemsWidget().settings()
        settings['searchWidget'] = self.searchWidget().settings()
        settings['foldersWidget'] = self.foldersWidget().settings()

        settings["path"] = self.path()

        return settings

    def setSettings(self, settings):
        """
        Set the widget settings from the given dictionary.

        :type settings: dict
        """
        defaults = copy.deepcopy(self.DEFAULT_SETTINGS)
        settings = studiolibrary.update(defaults, settings)

        isRefreshEnabled = self.isRefreshEnabled()

        try:
            self.setRefreshEnabled(False)
            self.itemsWidget().setToastEnabled(False)

            geometry = settings.get("geometry")
            if geometry:
                self.setGeometrySettings(geometry)

            themeSettings = settings.get("theme")
            if themeSettings:
                self.setThemeSettings(themeSettings)

            if not self.path():
                path = settings.get("path")
                if path and os.path.exists(path):
                    self.setPath(path)

            dpi = settings.get("dpi", 1.0)
            self.setDpi(dpi)

            sizes = settings.get('paneSizes')
            if sizes and len(sizes) == 3:
                self.setSizes(sizes)

            value = settings.get("foldersWidgetVisible")
            if value is not None:
                self.setFoldersWidgetVisible(value)

            value = settings.get("menuBarWidgetVisible")
            if value is not None:
                self.setMenuBarWidgetVisible(value)

            value = settings.get("previewWidgetVisible")
            if value is not None:
                self.setPreviewWidgetVisible(value)

            value = settings.get("statusBarWidgetVisible")
            if value is not None:
                self.setStatusBarWidgetVisible(value)

            value = settings.get('searchWidget')
            if value is not None:
                self.searchWidget().setSettings(value)

            value = settings.get("recursiveSearchEnabled")
            if value is not None:
                self.setRecursiveSearchEnabled(value)

        finally:
            self.reloadStyleSheet()

            self.setRefreshEnabled(isRefreshEnabled)
            self.refresh()

        foldersWidgetSettings = settings.get('foldersWidget', {})
        self.foldersWidget().setSettings(foldersWidgetSettings)

        itemsWidgetSettings = settings.get('itemsWidget', {})
        self.itemsWidget().setSettings(itemsWidgetSettings)

        self.itemsWidget().setToastEnabled(True)

    def updateSettings(self, settings):
        """
        Save the given path to the settings on disc.

        :type settings: dict
        :rtype: None 
        """
        data = self.readSettings()
        data.update(settings)
        self.saveSettings(data)

    def saveSettings(self, settings=None):
        """
        Save the settings to the self.settingsPath() as a json format.

        :type settings: dict or None
        :rtype: None
        """
        settings = settings or self.settings()

        key = self.name()
        path = self.settingsPath()

        data = studiolibrary.readJson(path)
        data[key] = settings

        logger.debug("Saving settings {path}".format(path=path))
        studiolibrary.saveJson(path, data)

    @studioqt.showWaitCursor
    def loadSettings(self):
        """
        Load the settings

        :rtype: None
        """
        self.reloadStyleSheet()
        settings = self.readSettings()
        self.setSettings(settings)

    def readSettings(self):
        """
        Read the settings from the self.settingsPath().

        :rtype: dict
        """
        key = self.name()
        path = self.settingsPath()
        data = {}

        logger.debug("Reading settings {path}".format(path=path))

        try:
            data = studiolibrary.readJson(path)
        except Exception, e:
            logging.exception(e)

        return data.get(key, {})

    def isLoaded(self):
        """
        Return True if the Studio Library has been shown

        :rtype: bool
        """
        return self._isLoaded

    def setLoaded(self, loaded):
        """
        Set if the widget has been shown.

        :type loaded: bool
        :rtype: None
        """
        self._isLoaded = loaded

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

    def centerWindow(self, width=None, height=None):
        """
        Center the widget to the center of the desktop.

        :rtype: None
        """
        geometry = self.frameGeometry()

        if width:
            geometry.setWidth(width)

        if height:
            geometry.setHeight(height)

        pos = QtWidgets.QApplication.desktop().cursor().pos()
        screen = QtWidgets.QApplication.desktop().screenNumber(pos)
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        geometry.moveCenter(centerPoint)
        self.window().setGeometry(geometry)

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
            self.statusWidget().showInfoMessage(event.tip())

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

    def show(self):
        """
        Overriding this method to always raise_ the widget on show.

        :rtype: None
        """
        QtWidgets.QWidget.show(self)
        self.setWindowState(QtCore.Qt.WindowNoState)
        self.raise_()

    def showEvent(self, event):
        """
        :type event: QtWidgets.QEvent
        :rtype: None
        """
        QtWidgets.QWidget.showEvent(self, event)

        if not self.isLoaded():
            self.setLoaded(True)
            self.setRefreshEnabled(True)
            self.loadSettings()

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

        self.showToastMessage("DPI: {0}".format(int(dpi * 100)))

        self.reloadStyleSheet()

    def _dpiSliderChanged(self, value):
        """
        Triggered the dpi action changes value.

        :rtype: float
        """
        dpi = value / 100.0
        self.setDpi(dpi)

    def iconColor(self):
        """
        Return the icon color.

        :rtype: studioqt.Color
        """
        return self.theme().iconColor()

    def setThemeSettings(self, settings):
        """
        Set the theme from the given settings.

        :type settings: dict
        :rtype: None
        """
        theme = studioqt.Theme()
        theme.setSettings(settings)
        self.setTheme(theme)

    def setTheme(self, theme):
        """
        Set the theme.

        :type theme: studioqt.Theme
        :rtype: None
        """
        self._theme = theme
        self.reloadStyleSheet()

    def theme(self):
        """
        Return the current theme.

        :rtype: studioqt.Theme
        """
        if not self._theme:
            self._theme = studioqt.Theme()

        return self._theme

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

        color = studioqt.Color.fromString(
            options["ITEM_BACKGROUND_HOVER_COLOR"])
        self.itemsWidget().setBackgroundHoverColor(color)

        color = studioqt.Color.fromString(
            options["ITEM_BACKGROUND_SELECTED_COLOR"])
        self.itemsWidget().setBackgroundSelectedColor(color)

        self.setStyleSheet(styleSheet)

        self.searchWidget().update()
        self.menuBarWidget().update()
        self.foldersWidget().update()

    # -----------------------------------------------------------------------
    # Support for the Trash folder.
    # -----------------------------------------------------------------------

    def trashEnabled(self):
        """
        Return True if moving items to trash.
        
        :rtype: bool 
        """
        return self._trashEnabled

    def setTrashEnabled(self, enable):
        """
        Enable items to be trashed.

        :type enable: bool
        :rtype: None 
        """
        self._trashEnabled = enable

    def isPathInTrash(self, path):
        """
        Return True if the given path is in the Trash path.

        :rtype: bool
        """
        return "trash" in path.lower()

    def trashPath(self):
        """
        Return the trash path for the library.
        
        :rtype: str
        """
        path = self.path()
        return u'{0}/{1}'.format(path, "Trash")

    def trashFolderExists(self):
        """
        Return True if the trash folder exists.
        
        :rtype: bool
        """
        return os.path.exists(self.trashPath())

    def createTrashFolder(self):
        """
        Create the trash folder if it does not exist.
        
        :rtype: None
        """
        path = self.trashPath()
        if not os.path.exists(path):
            os.makedirs(path)

    def isTrashFolderVisible(self):
        """
        Return True if the trash folder is visible to the user.
        
        :rtype: bool
        """
        return self._isTrashFolderVisible

    def setTrashFolderVisible(self, visible):
        """
        Enable the trash folder to be visible to the user.
        
        :type visible: str
        :rtype: None
        """
        self._isTrashFolderVisible = visible
        self.refreshFolders()

    def isTrashSelected(self):
        """
        Return True if the selected folders is in the trash.
        
        :rtype: bool
        """
        folders = self.selectedFolderPaths()
        for folder in folders:
            if self.isPathInTrash(folder):
                return True

        items = self.selectedItems()
        for item in items:
            if self.isPathInTrash(item.path()):
                return True

        return False

    def moveItemsToTrash(self, items):
        """
        Move the given items to trash path.

        :items items: list[studiolibrary.LibraryItem]
        :rtype: None
        """
        self.createTrashFolder()
        self.moveItems(items, dst=self.trashPath(), force=True)

    def moveFolderToTrash(self, folder):
        """
        Move the given folder item to the trash path.

        :type folder: studioqt.TreeWidgetItem
        :rtype: None
        """
        self.foldersWidget().clearSelection()
        self.createTrashFolder()

        src = folder.path()
        dst = os.path.join(self.trashPath(), os.path.basename(src))
        dst = studiolibrary.generateUniquePath(dst)

        self.renameFolder(src, dst=dst)

    def showMoveItemsToTrashDialog(self):
        """
        Show the "Move to trash" dialog for the selected items.

        :rtype: None
        """
        items = self.selectedItems()

        if items:
            title = "Move to trash?"
            text = "Are you sure you want to move the selected" \
                   "item/s to the trash?"

            result = self.showQuestionDialog(title, text)

            if result == QtWidgets.QMessageBox.Yes:
                self.moveItemsToTrash(items)

    def showMoveFoldersToTrashDialog(self):
        """
        Show the "Move to trash" dialog for the selected folders.
        
        :rtype: None
        """
        item = self.foldersWidget().selectedItem()

        if item:
            title = "Move to trash?"
            text = "Are you sure you want to move the selected " \
                   "folder/s to the trash?"

            result = self.showQuestionDialog(title, text)

            if result == QtWidgets.QMessageBox.Yes:
                self.moveFolderToTrash(item)

    # -----------------------------------------------------------------------
    # Support for message boxes
    # -----------------------------------------------------------------------

    def showToastMessage(self, text, duration=500):
        """
        A convenience method for showing the toast widget with the given text.

        :type text: str
        :type duration: int
        :rtype: None
        """
        self.itemsWidget().showToastMessage(text, duration)

    def showInfoMessage(self, text):
        """
        A convenience method for showing an info message to the user.

        :type text: str
        :rtype: None
        """
        self.statusWidget().showInfoMessage(text)

    def showErrorMessage(self, text):
        """
        A convenience method for showing an error message to the user.

        :type text: str
        :rtype: None
        """
        self.statusWidget().showErrorMessage(text)
        self.setStatusBarWidgetVisible(True)

    def showWarningMessage(self, text):
        """
        A convenience method for showing a warning message to the user.

        :type text: str
        :rtype: None
        """
        self.statusWidget().showWarningMessage(text)
        self.setStatusBarWidgetVisible(True)

    def showRefreshMessage(self, elapsedTime):
        """
        Show how long the current refresh took with the given elapsedTime.

        :type elapsedTime: time.time
        :rtype None
        """
        itemCount = len(self._itemsWidget.items())
        hiddenCount = self.itemsHiddenCount()

        plural = ""
        if itemCount > 1:
            plural = "s"

        hiddenText = ""
        if hiddenCount > 0:

            hiddenPlural = ""
            if hiddenCount > 1:
                hiddenPlural = "s"

            hiddenText = "{0} item{1} hidden."
            hiddenText = hiddenText.format(hiddenCount, hiddenPlural)

        msg = "Displayed {0} item{1} in {2:.3f} seconds. {3}"
        msg = msg.format(itemCount, plural, elapsedTime, hiddenText)
        self.statusWidget().showInfoMessage(msg)

        logger.debug(msg)

    def showInfoDialog(self, title, text):
        """
        A convenience method for showing an information dialog to the user.

        :type title: str
        :type text: str
        :rtype: QMessageBox.StandardButton
        """
        buttons = QtWidgets.QMessageBox.Ok

        return studioqt.MessageBox.question(self, title, text, buttons=buttons)

    def showErrorDialog(self, title, text):
        """
        A convenience method for showing an error dialog to the user.

        :type title: str
        :type text: str
        :rtype: QMessageBox.StandardButton
        """
        self.showErrorMessage(text)
        return studioqt.MessageBox.critical(self, title, text)

    def showExceptionDialog(self, title, error):
        """
        A convenience method for showing an error dialog to the user.

        :type title: str
        :type error: Exception
        :rtype: QMessageBox.StandardButton
        """
        logger.exception(error)
        self.showErrorDialog(title, error)

    def showQuestionDialog(self, title, text):
        """
        A convenience method for showing a question dialog to the user.

        :type title: str
        :type text: str
        :rtype: QMessageBox.StandardButton
        """
        buttons = QtWidgets.QMessageBox.Yes | \
                  QtWidgets.QMessageBox.No | \
                  QtWidgets.QMessageBox.Cancel

        return studioqt.MessageBox.question(self, title, text, buttons=buttons)

    def updateWindowTitle(self):
        """
        Update the window title with the version and lock status.

        :rtype: None
        """
        title = "Studio Library - "
        title += studiolibrary.version() + " - " + self.name()

        if self.isLocked():
            title += " (Locked)"

        self.setWindowTitle(title)

    # -----------------------------------------------------------------------
    # Support for locking via regex
    # -----------------------------------------------------------------------

    def updateCreateItemButton(self):
        """
        Update the plus icon depending on if the library widget is locked.

        :rtype: None
        """
        action = self.menuBarWidget().findAction("New Item")

        if self.isLocked():
            pixmap = studioqt.resource.pixmap("lock")
            action.setEnabled(False)
            action.setIcon(pixmap)
        else:
            pixmap = studioqt.resource.pixmap("add")
            action.setEnabled(True)
            action.setIcon(pixmap)

        self.menuBarWidget().refresh()

    def isLocked(self):
        """
        Return lock state of the library.

        :rtype: bool
        """
        return self._isLocked

    def setLocked(self, value):
        """
        Set the state of the widget to not editable.

        :type value: bool
        :rtype: None
        """
        self._isLocked = value

        self.foldersWidget().setLocked(value)
        self.itemsWidget().setLocked(value)

        self.updateCreateItemButton()
        self.updateWindowTitle()

        self.lockChanged.emit(value)

    def superusers(self):
        """
        Return the superusers for the widget.

        :rtype: list[str]
        """
        return self._superusers

    def setSuperusers(self, superusers):
        """
        Set the valid superusers for the library widget.

        This will lock all folders unless you're a superuser.

        :type superusers: list[str]
        :rtype: None
        """
        self._superusers = superusers
        self.updateLock()

    def lockRegExp(self):
        """
        Return the lock regexp used for locking the widget.

        :rtype: str
        """
        return self._lockRegExp

    def setLockRegExp(self, regExp):
        """
        Set the lock regexp used for locking the widget.

        Lock only folders that contain the given regExp in their path.

        :type regExp: str
        :rtype: None
        """
        self._lockRegExp = regExp
        self.updateLock()

    def unlockRegExp(self):
        """
        Return the unlock regexp used for unlocking the widget.

        :rtype: str
        """
        return self._unlockRegExp

    def setUnlockRegExp(self, regExp):
        """
        Return the unlock regexp used for locking the widget.

        Unlock only folders that contain the given regExp in their path.

        :type regExp: str
        :rtype: None
        """
        self._unlockRegExp = regExp
        self.updateLock()

    def isLockRegExpEnabled(self):
        """
        Return True if either the lockRegExp or unlockRegExp has been set.

        :rtype: bool
        """
        return not (
            self.superusers() is None
            and self.lockRegExp() is None
            and self.unlockRegExp() is None
        )

    def updateLock(self):
        """
        Update the lock state for the library.

        This is triggered when the user clicks on a folder.

        :rtype: None
        """
        if not self.isLockRegExpEnabled():
            return

        superusers = self.superusers() or []
        reLocked = re.compile(self.lockRegExp() or "")
        reUnlocked = re.compile(self.unlockRegExp() or "")

        if studiolibrary.user() in superusers:
            self.setLocked(False)

        elif reLocked.match("") and reUnlocked.match(""):

            if superusers:
                # Lock if only the superusers arg is used
                self.setLocked(True)
            else:
                # Unlock if no keyword arguments are used
                self.setLocked(False)

        else:
            folders = self.selectedFolderPaths()

            # Lock the selected folders that match the reLocked regx
            if not reLocked.match(""):
                for folder in folders:
                    if reLocked.search(folder):
                        self.setLocked(True)
                        return

                self.setLocked(False)

            # Unlock the selected folders that match the reUnlocked regx
            if not reUnlocked.match(""):
                for folder in folders:
                    if reUnlocked.search(folder):
                        self.setLocked(False)
                        return

                self.setLocked(True)

    # -----------------------------------------------------------------------
    # Misc
    # -----------------------------------------------------------------------

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
            icon = studioqt.resource.icon("view_all")
        else:
            icon = studioqt.resource.icon("view_compact")

        action.setIcon(icon)

        self.menuBarWidget().refresh()

    def isRecursiveSearchEnabled(self):
        """
        Return True if recursive search is enabled.

        :rtype: bool
        """
        return self._recursiveSearchEnabled

    def setRecursiveSearchEnabled(self, value):
        """
        Enable recursive search for searching sub folders.

        :type value: int

        :rtype: None
        """
        self._recursiveSearchEnabled = value
        self.refresh()

    @staticmethod
    def help():
        """
        :rtype: None
        """
        import webbrowser
        webbrowser.open(studiolibrary.HELP_URL)

    def setDebugMode(self, value):
        """
        :type value: bool
        """
        self._isDebug = value

        logger_ = logging.getLogger("studiolibrary")

        if value:
            logger_.setLevel(logging.DEBUG)
        else:
            logger_.setLevel(logging.INFO)

        self.debugModeChanged.emit(value)
        self.globalSignal.debugModeChanged.emit(self, value)

    def isDebug(self):
        """
        :rtype: bool
        """
        return self._isDebug
