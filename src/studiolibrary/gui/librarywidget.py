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

import re
import os
import time
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


class LibraryWidget(studiolibrary.MayaDockWidgetMixin, QtWidgets.QWidget):

    DPI_ENABLED = False  # Still in development
    TRASH_ENABLED = True
    THEMES_MENU_ENABLED = False  # Still in development
    RECURSIVE_SEARCH_ENABLED = False
    DEFAULT_GROUP_BY_COLUMNS = ["Category", "Modified", "Type"]

    MIN_SLIDER_DPI = 80
    MAX_SLIDER_DPI = 250

    globalSignal = GlobalSignal()

    # Local signal
    loaded = QtCore.Signal()
    lockChanged = QtCore.Signal(object)
    debugModeChanged = QtCore.Signal(object)
    folderSelectionChanged = QtCore.Signal(object)

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        QtWidgets.QWidget.__init__(self, None)
        studiolibrary.MayaDockWidgetMixin.__init__(self, None)

        msg = u'Loading library window "{0}"'.format(library.name())
        logger.info(msg)

        self.setObjectName("studiolibrary")
        studiolibrary.analytics().logScreen("MainWindow")

        resource = studiolibrary.resource()
        self.setWindowIcon(resource.icon("icon_black"))

        self._dpi = 1.0
        self._library = None
        self._isDebug = False
        self._isLocked = False
        self._isLoaded = False
        self._previewWidget = None
        self._loaderEnabled = True
        self._currentItem = None

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
        self._foldersWidget = studioqt.FoldersWidget(self)

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
        tip = "Choose to show/hide both the preview and navigation pane"
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

        self.dockingChanged.connect(self.updateWindowTitle)

        searchWidget = self.searchWidget()
        searchWidget.searchChanged.connect(self._searchChanged)

        studiolibrary.LibraryItem.saved.connect(self._itemSaved)
        studiolibrary.LibraryItem.saving.connect(self._itemSaving)

        itemsWidget = self.itemsWidget()
        itemsWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        itemsWidget.itemMoved.connect(self._itemMoved)
        itemsWidget.itemSelectionChanged.connect(self._itemSelectionChanged)
        itemsWidget.customContextMenuRequested.connect(self.showItemsContextMenu)

        folderWidget = self.foldersWidget()
        folderWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        folderWidget.itemDropped.connect(self._folderDropped)
        folderWidget.itemSelectionChanged.connect(self._folderSelectionChanged)
        folderWidget.customContextMenuRequested.connect(self.showFolderContextMenu)

        self.folderSelectionChanged.connect(self.updateLock)

        self.setLibrary(library)
        self.updateViewButton()

        self.itemsWidget().treeWidget().setValidGroupByColumns(self.DEFAULT_GROUP_BY_COLUMNS)

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

    def showGroupByMenu(self):
        """
        Show the group by menu at the group button.

        :rtype: None
        """
        menu = self.itemsWidget().createGroupByMenu()
        widget = self.menuBarWidget().findToolButton("Group By")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        action = menu.exec_(point)

    def showSortByMenu(self):
        """
        Show the sort by menu at the sort button.

        :rtype: None
        """
        menu = self.itemsWidget().createSortByMenu()
        widget = self.menuBarWidget().findToolButton("Sort By")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        action = menu.exec_(point)

    def showItemViewMenu(self):
        """
        Show the item settings menu.

        :rtype: None
        """
        menu = self.itemsWidget().createItemSettingsMenu()
        widget = self.menuBarWidget().findToolButton("Item View")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        action = menu.exec_(point)

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

    def path(self):
        """
        Return the library root path.

        :rtype: str
        """
        return self.library().path()

    def library(self):
        """
        :rtype: studiolibrary.Library
        """
        return self._library

    def setLibrary(self, library):
        """
        :type library: studiolibrary.Library
        """
        self._library = library
        self.reload()

    def _itemSelectionChanged(self):
        """
        Triggered when an item is selected or deselected.

        :rtype: None
        """
        item = self.itemsWidget().selectedItem()

        if self._currentItem != item:
            self._currentItem = item
            self.setPreviewWidgetFromItem(item)

    def _folderSelectionChanged(self):
        """
        Triggered when an item is selected or deselected.

        :type selectedFolders: list[studiolibrary.Folder]
        :type deselectedFolders: list[studiolibrary.Folder]
        :rtype: None
        """
        self.reloadItems()
        path = self.selectedFolderPath()
        self.folderSelectionChanged.emit(path)
        self.globalSignal.folderSelectionChanged.emit(self, path)

    def itemsFromUrls(self, urls):
        """
        :type urls: list[QtGui.QUrl]
        :rtype: list[studiolibrary.LibraryItem]
        """
        items = []
        for url in urls:
            path = url.toLocalFile()

            # Fixes a bug when dragging from windows explorer on windows 10
            if studiolibrary.isWindows():
                if path.startswith("/"):
                    path = path[1:]

            item = studiolibrary.itemFromPath(path)
            items.append(item)

        return items

    # -----------------------------------------------------------------
    # Support for loading and setting items
    # -----------------------------------------------------------------

    def refreshLibraryWidgets(self):
        """
        Reload items for all the library widgets.

        :rtype: None
        """
        for library in self.library().libraries():
            widget = library.libraryWidget()
            if widget:
                widget.reloadItems()

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

    def setItems(self, items, sortEnabled=False):
        """
        Set the items for the library widget.

        :rtype: list[studiolibrary.LibraryItem]
        """
        self.itemsWidget().setItems(items, sortEnabled=sortEnabled)

    def setLoaderEnabled(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self._loaderEnabled = value

    def loaderEnabled(self):
        """
        :rtype: func
        """
        return self._loaderEnabled

    def loader(self):
        """
        :rtype: list[studiolibrary.LibraryItem]
        """
        items = []
        folders = self.foldersWidget().selectedFolders()

        for folder in folders:

            path = folder.path()
            depth = 1

            if self.isRecursiveSearchEnabled():
                depth = 3

            for item in studiolibrary.findItems(path, depth=depth):
                item.setLibrary(self.library())
                items.append(item)

        return items

    def reload(self):
        """Reload the library widget."""
        self.clearItems()
        self.clearPreviewWidget()
        self.updateWindowTitle()
        self.setRootPath(self.library().path())

    @studioqt.showWaitCursor
    def reloadItems(self):
        """Reload the items widget."""
        if not self.loaderEnabled():
            logger.debug("Loader disabled!")
            return

        logger.debug("Loading items for library '%s'" % self.library().name())

        elapsedTime = time.time()

        selectedItems = self.selectedItems()

        items = self.loader()

        self.setItems(items, sortEnabled=False)

        self.loadCustomOrder()
        self.itemsWidget().refreshSortBy()

        if selectedItems:
            self.selectItems(selectedItems)

        self.refreshSearch()

        elapsedTime = time.time() - elapsedTime
        self.setLoadedMessage(elapsedTime)

        logger.debug("Loaded items")

    @studioqt.showWaitCursor
    def reloadFolders(self):
        """Reload the folder widget."""
        ignoreFilter = self.folderIgnoreFilter()

        self.foldersWidget().reload()
        self.foldersWidget().setIgnoreFilter(ignoreFilter)

    # -----------------------------------------------------------------
    # Support for folder and item context menus
    # -----------------------------------------------------------------

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

        icon = studiolibrary.resource().icon("add_library", color=color)
        action = QtWidgets.QAction(icon, "Library", menu)
        action.triggered.connect(self.showNewLibraryDialog)
        menu.addAction(action)

        separator = QtWidgets.QAction("", menu)
        separator.setSeparator(True)
        menu.addAction(separator)

        for itemClass in studiolibrary.itemClasses():

            action = itemClass.createAction(menu, self)
            if action:
                menu.addAction(action)

        return menu

    def createSettingsMenu(self):
        """
        Return the settings menu for changing the library widget.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu("", self)
        menu.setTitle("Settings")

        librariesMenu = studiolibrary.LibrariesMenu(menu)
        menu.addMenu(librariesMenu)
        menu.addSeparator()

        if self.DPI_ENABLED:
            action = studioqt.SliderAction("Dpi", menu)
            dpi = self.dpi() * 100.0
            action.slider().setRange(self.MIN_SLIDER_DPI, self.MAX_SLIDER_DPI)
            action.slider().setValue(dpi)
            action.valueChanged.connect(self._dpiSliderChanged)
            menu.addAction(action)

        action = QtWidgets.QAction("Settings", menu)
        action.triggered[bool].connect(self.showSettingsDialog)
        menu.addAction(action)

        if self.THEMES_MENU_ENABLED:
            themesMenu = studioqt.ThemesMenu(menu)
            themesMenu.themeTriggered.connect(self.library().setTheme)
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

        if studiolibrary.isMaya():
            menu.addSeparator()
            dockMenu = self.dockMenu()
            menu.addMenu(dockMenu)

        menu.addSeparator()

        action = QtWidgets.QAction("Debug mode", menu)
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

    def showFolderContextMenu(self, pos=None):
        """
        Show the folder context menu at the current cursor position.

        :type menu: QtWidgets.QMenu
        :rtype: QtWidgets.QAction
        """
        menu = self.createFolderContextMenu()

        point = QtGui.QCursor.pos()
        point.setX(point.x() + 3)
        point.setY(point.y() + 3)
        action = menu.exec_(point)
        menu.close()

        return action

    def createFolderContextMenu(self):
        """
        Return the folder menu for editing the selected folders.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu(self)

        if self.isLocked():
            action = menu.addAction("Locked")
            action.setEnabled(False)
        else:

            menu.addMenu(self.createNewMenu())

            folders = self.selectedFolders()

            if folders:
                m = self.foldersWidget().createEditMenu(menu)
                menu.addMenu(m)

            menu.addSeparator()
            menu.addMenu(self.createSettingsMenu())

        return menu

    def showItemsContextMenu(self, pos=None):
        """
        Show the item context menu at the current cursor position.

        :type pos: QtGui.QPoint
        :rtype QtWidgets.QAction
        """
        items = self.itemsWidget().selectedItems()

        menu = self.createItemContextMenu(items)

        point = QtGui.QCursor.pos()
        point.setX(point.x()+3)
        point.setY(point.y()+3)
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

        if self.trashEnabled():
            action = QtWidgets.QAction("Move to trash", menu)
            action.setEnabled(self.isTrashEnabled())
            action.triggered.connect(self.trashSelectedItemsDialog)
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
            items = items[-1]
            try:
                items.contextMenu(menu)
            except Exception, msg:
                logger.exception(msg)

        if not self.isLocked():
            menu.addMenu(self.createNewMenu())

            if items:
                menu.addMenu(self.createItemEditMenu())

        menu.addSeparator()
        menu.addMenu(self.createSettingsMenu())

        return menu

    # -------------------------------------------------------------------
    # Support for saving and loading folder data
    # -------------------------------------------------------------------

    def folderDataPath(self):
        """
        Return the disc location of the folder data.

        :rtype: str
        """
        return self.library().folderDataPath()

    def writeFolderData(self, data):
        """
        Save the item data to disc.

        :type data: dict
        :rtype: None
        """
        path = self.folderDataPath()

        _data = self.readFolderData()
        _data.update(data)

        return studiolibrary.saveJson(path, data)

    def readFolderData(self):
        """
        Read the item data from disc.

        :rtype: dict
        """
        path = self.folderDataPath()
        return studiolibrary.readJson(path)

    def loadFolderData(self):
        """
        Load and set the custom sort order from disc.

        :rtype: None
        """
        data = self.readFolderData()
        try:
            self.foldersWidget().setFolderSettings(data)
        except Exception, msg:
            logger.exception(msg)

    def saveFolderData(self):
        """
        Save the custom sort order to disc.

        :rtype: None
        """
        data = self.foldersWidget().folderSettings()
        self.writeFolderData(data)

    # -------------------------------------------------------------------
    # Support loading the custom sort order
    # -------------------------------------------------------------------

    def itemDataPath(self):
        """
        Return the disc location of the item data.

        :rtype: str
        """
        path = self.library().itemDataPath()
        return path

    def writeItemData(self, data):
        """
        Save the item data to disc.

        :type data: dict
        :rtype: None
        """
        path = self.itemDataPath()

        _data = self.readItemData()
        _data.update(data)

        return studiolibrary.saveJson(path, _data)

    def readItemData(self):
        """
        Read the item data from disc.

        :rtype: dict
        """
        path = self.itemDataPath()
        return studiolibrary.readJson(path)

    def loadCustomOrder(self):
        """
        Load and set the custom sort order from disc.

        :rtype: None
        """
        data = self.readItemData()

        try:
            self.itemsWidget().setCustomSortOrder(data)
        except Exception, msg:
            logger.exception(msg)

    def saveCustomOrder(self):
        """
        Save the custom sort order to disc.

        :rtype: None
        """
        data = self.itemsWidget().customSortOrder()
        self.writeItemData(data)

    # -------------------------------------------------------------------
    # Support for moving items with drag and drop
    # -------------------------------------------------------------------

    def _itemMoved(self, item):
        """
        :rtype: None
        """
        self.saveCustomOrder()

    def _folderDropped(self, event):
        """
        :type event: list[studiolibrary.LibraryItem]
        :rtype: None
        """
        mimeData = event.mimeData()

        if mimeData.hasUrls():
            folder = self.selectedFolder()
            items = self.itemsFromUrls(mimeData.urls())

            for item in items:
                # Check if the item is moving to another folder.
                if folder.path() != item.dirname():
                    self.moveItemsToFolder(items, folder=folder)
                    self.refreshLibraryWidgets()
                    break

    def moveItemsDialog(self, parent=None):
        """
        :type parent: QtWidgets.QWidget
        :rtype: QtWidgets.QMessageBox
        """
        parent = parent or self

        msgBox = QtWidgets.QMessageBox(parent)
        msgBox.setWindowTitle("Move or Copy items?")
        msgBox.setText('Would you like to copy or move the selected item/s?')
        msgBox.addButton('Copy', QtWidgets.QMessageBox.AcceptRole)
        msgBox.addButton('Move', QtWidgets.QMessageBox.AcceptRole)
        msgBox.addButton('Cancel', QtWidgets.QMessageBox.RejectRole)

        return msgBox

    def moveItemsToFolder(self, items, folder):
        """
        :type items: list[studiolibrary.LibraryItem]
        :type folder: studiolibrary.Folder
        :rtype: None
        """
        Copy = 0
        Move = 1
        Cancel = 2
        movedItems = []

        dialog = self.moveItemsDialog()
        action = dialog.exec_()
        dialog.close()

        if action == Cancel:
            return

        self.itemsWidget().clearSelection()

        try:
            for item in items:

                path = folder.path() + "/" + item.name()

                if action == Copy:
                    item.copy(path)

                elif action == Move:
                    item.rename(path)

                movedItems.append(item)

        except Exception, e:
            message = str(e)
            logger.exception(message)
            self.criticalDialog(message)
            raise
        finally:
            self.itemsWidget().addItems(movedItems)
            self.selectItems(movedItems)

    def _itemSaved(self, item):
        """
        :type item: studiolibrary.LibraryItem
        :rtype: None
        """
        folder = self.selectedFolder()

        if folder and folder.path() == item.dirname():
            path = item.path()
            self.itemsWidget().clearSelection()
            self.reloadItems()
            self.selectPaths([path])

    def _itemSaving(self, item):
        """
        :type item: studiolibrary.LibraryItem
        :rtype: None
        """
        if self.library().path() in item.path():
            if item.exists():
                self.showItemExistsDialog(item)

    def showItemExistsDialog(self, item):
        """
        :type item: studiolibrary.LibraryItem
        :rtype: None
        """
        path = item.path()
        items = [item]
        title = "Warning"
        message = 'Item already exists! Would you like to move the existing item "{name}" to the trash?'
        message = message.format(name=item.name())

        result = self.trashItemsDialog(items, title=title, message=message)

        if result == QtWidgets.QMessageBox.Cancel:
            item.setErrorString("Item was not saved! Saving was canceled.")
        elif result != QtWidgets.QMessageBox.Yes:
            item.setErrorString("Item was not saved! You cannot save over an existsing item.")

        item.setPath(path)

    def showNewLibraryDialog(self):
        """
        :rtype: None
        """
        studiolibrary.showNewLibraryDialog()

    def folderIgnoreFilter(self):
        """
        Return a list of folder names that should be hidden/ignored.

        :rtype: list[str]
        """
        ignoreFilter = ['.', '.studiolibrary', ".mayaswatches"]

        if not self.isTrashFolderVisible():
            ignoreFilter.append('trash')

        for ext in studiolibrary.itemExtensions():
            ignoreFilter.append(ext)

        return ignoreFilter

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
        ignoreFilter = self.folderIgnoreFilter()

        folderWidget.clearSelection()
        folderWidget.setRootPath(path)
        folderWidget.setIgnoreFilter(ignoreFilter)
        folderWidget.setFolderOrderIndex(trashPath, 0)

    def showSettingsDialog(self):
        """Show the settings dialog for the current library."""
        return self.library().showSettingsDialog()

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

    def filterItems(self, items):
        """
        Filter the given items using the search filter.

        :rtype: list[studiolibrary.LibraryItem]
        """
        searchFilter = self.searchWidget().searchFilter()

        column = self.itemsWidget().treeWidget().columnFromLabel("Search Order")

        for item in items:
            if searchFilter.match(item.searchText()):
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

    def settings(self):
        """
        :rtype: studiolibrary.MetaFile
        """
        geometry = (
            self.parentX().geometry().x(),
            self.parentX().geometry().y(),
            self.parentX().geometry().width(),
            self.parentX().geometry().height()
        )
        settings = {}

        settings['dpi'] = self.dpi()
        settings['geometry'] = geometry
        settings['sizes'] = self._splitter.sizes()

        settings["foldersWidgetVisible"] = self.isFoldersWidgetVisible()
        settings["previewWidgetVisible"] = self.isPreviewWidgetVisible()
        settings["menuBarWidgetVisible"] = self.isMenuBarWidgetVisible()
        settings["statusBarWidgetVisible"] = self.isStatusBarWidgetVisible()
        settings["recursiveSearchEnabled"] = self.isRecursiveSearchEnabled()

        settings["dockWidget"] = self.dockSettings()
        settings['searchWidget'] = self.searchWidget().settings()
        settings['foldersWidget'] = self.foldersWidget().settings()
        settings['itemsWidget'] = self.itemsWidget().settings()

        return settings

    def setSettings(self, settings):
        """
        :type settings: studiolibrary.MetaFile
        """

        self.itemsWidget().setToastEnabled(False)

        dpi = settings.get("dpi", 1.0)
        self.setDpi(dpi)

        sizes = settings.get('sizes', [140, 280, 180])
        if len(sizes) == 3:
            self.setSizes(sizes)

        x, y, width, height = settings.get("geometry", [200, 200, 860, 680])
        self.parentX().setGeometry(x, y, width, height)

        # Make sure the window is on the screen.
        screenGeometry = QtWidgets.QApplication.desktop().screenGeometry()
        if x < 0 or y < 0 or x > screenGeometry.x() or y > screenGeometry.y():
            self.centerWindow()

        # Reload the stylesheet before loading the dock widget settings.
        # Otherwise the widget will show docked without a stylesheet.
        self.reloadStyleSheet()

        dockSettings = settings.get("dockWidget", {})
        self.setDockSettings(dockSettings)

        value = settings.get("foldersWidgetVisible", True)
        self.setFoldersWidgetVisible(value)

        value = settings.get("menuBarWidgetVisible", True)
        self.setMenuBarWidgetVisible(value)

        value = settings.get("previewWidgetVisible", True)
        self.setPreviewWidgetVisible(value)

        value = settings.get("statusBarWidgetVisible", True)
        self.setStatusBarWidgetVisible(value)

        value = settings.get("recursiveSearchEnabled", self.RECURSIVE_SEARCH_ENABLED)
        self.setRecursiveSearchEnabled(value)

        searchWidgetSettings = settings.get('searchWidget', {})
        self.searchWidget().setSettings(searchWidgetSettings)

        foldersWidgetSettings = settings.get('foldersWidget', {})
        self.foldersWidget().setSettings(foldersWidgetSettings)

        itemsWidgetSettings = settings.get('itemsWidget', {})
        self.itemsWidget().setSettings(itemsWidgetSettings)

        self.itemsWidget().setToastEnabled(True)

    def loadSettings(self):
        """
        :rtype: None
        """
        self.setLoaderEnabled(False)

        try:
            settings = self.library().settings().get("libraryWidget", {})
            self.setSettings(settings)
        finally:
            self.reloadStyleSheet()
            self.setLoaderEnabled(True)
            self.reloadItems()

        self.loadFolderData()

        self._isLoaded = True
        self.loaded.emit()

    def saveSettings(self):
        """
        :rtype: None
        """
        settings = self.settings()

        self.library().settings()["libraryWidget"] = settings
        self.library().saveSettings()

        self.saveFolderData()

    def isLoaded(self):
        """
        :rtype: bool
        """
        return self._isLoaded

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
        self.parentX().move(geometry.topLeft())

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
        if not self.isLoaded():
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
        self.statusWidget().setFixedHeight(20*dpi)

        self._splitter.setHandleWidth(2*dpi)

        self.itemsWidget().setToast("DPI: {0}".format(int(dpi * 100)))

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
        return self.library().theme().iconColor()

    def reloadStyleSheet(self):
        """
        Reload the style sheet to the current theme.

        :rtype: None
        """
        theme = self.library().theme()
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

        self.searchWidget().update()
        self.menuBarWidget().update()

    # -----------------------------------------------------------------------
    # Support for the Trash folder.
    # -----------------------------------------------------------------------

    def trashEnabled(self):
        return self._trashEnabled

    def setTrashEnabled(self, value):
        self._trashEnabled = value

    def trashPath(self):
        """
        :rtype: str
        """
        path = self.path()
        return u'{0}/{1}'.format(path, "Trash")

    def trashFolderExists(self):
        """
        :rtype: bool
        """
        return os.path.exists(self.trashPath())

    def createTrashFolder(self):
        """
        :rtype: None
        """
        path = self.trashPath()
        if not os.path.exists(path):
            os.makedirs(path)

    def isTrashFolderVisible(self):
        """
        :rtype: bool
        """
        return self._isTrashFolderVisible

    def setTrashFolderVisible(self, visible):
        """
        :type visible: str
        :rtype: None
        """
        self._isTrashFolderVisible = visible
        self.reloadFolders()

    def isTrashEnabled(self):
        """
        :rtype: bool
        """
        folders = self.selectedFolders()
        for folder in folders:
            if "Trash" in folder.path():
                return False

        items = self.selectedItems()
        for item in items:
            if "Trash" in item.path():
                return False

        return True

    def trashSelectedFoldersDialog(self):
        """
        :rtype: None
        """
        items = self.selectedFolders()

        if items:
            title = "Move selected folders to trash?"
            msg = "Are you sure you want to move the selected folder/s to the trash?"
            result = self.questionDialog(msg, title=title)

            if result == QtWidgets.QMessageBox.Yes:
                self.foldersWidget().clearSelection()
                self.trashItems(items)

    def trashSelectedItemsDialog(self):
        """
        Show the "move to trash" dialog for the selected items.

        :rtype: QtWidgets.QMessageBox.Button
        """
        items = self.selectedItems()

        return self.trashItemsDialog(
            items=items,
            title="Move selected items to trash?",
            message="Are you sure you want to move the selected item/s to the trash?",
        )

    def trashItemsDialog(self, items, title, message):
        """
        Show the "move to trash" dialog.

        :type items: list[studiolibrary.LibraryItem]
        :type title: str
        :type message: str

        :rtype: QtWidgets.QMessageBox.Button
        """
        result = None

        if items:
            title = title
            msg = message
            result = self.questionDialog(msg, title=title)

            if result == QtWidgets.QMessageBox.Yes:
                self.trashItems(items)

        return result

    def trashItems(self, items):
        """
        :items items: list[studiolibrary.LibraryItem]
        :rtype: None
        """
        trashPath = self.trashPath()

        self.createTrashFolder()

        try:
            for item in items:
                item.move(trashPath)

        except Exception, e:
            logger.exception(e.message)
            self.setError(e.message)
            raise

        finally:
            self.reloadItems()

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

    def setLoadedMessage(self, elapsedTime):
        """
        :type elapsedTime: time.time
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
        self.statusWidget().setInfo(msg)

    # -----------------------------------------------------------------------
    # Support for locking
    # -----------------------------------------------------------------------

    def setLocked(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self._isLocked = value

        self.foldersWidget().setLocked(value)
        self.itemsWidget().setLocked(value)

        self.updateNewButton()
        self.updateWindowTitle()

        self.lockChanged.emit(value)

    def isLocked(self):
        """
        :rtype: bool
        """
        return self._isLocked

    def updateNewButton(self):

        action = self.menuBarWidget().findAction("New Item")

        if self.isLocked():
            pixmap = studioqt.pixmap("lock")
            action.setEnabled(False)
            action.setIcon(pixmap)
        else:
            pixmap = studioqt.pixmap("add")
            action.setEnabled(True)
            action.setIcon(pixmap)

        self.menuBarWidget().update()

    def updateLock(self):
        """
        Update the lock state for the library.

        :param libraryWidget: studiolibrary.LibraryWidget
        :rtype: None
        """
        kwargs = self.library().kwargs()

        superusers = kwargs.get("superusers", [])
        reLockedFolders = re.compile(kwargs.get("lockFolder", ""))
        reUnlockedFolders = re.compile(kwargs.get("unlockFolder", ""))

        if studiolibrary.user() in superusers:
            self.setLocked(False)

        elif reLockedFolders.match("") and reUnlockedFolders.match(""):

            if superusers:
                # Lock if only the superusers arg is used
                self.setLocked(True)
            else:
                # Unlock if no keyword arguments are used
                self.setLocked(False)

        else:
            folders = self.selectedFolders()

            # Lock the selected folders that match the reLockedFolders regx
            if not reLockedFolders.match(""):
                for folder in folders:
                    if reLockedFolders.search(folder.path()):
                        self.setLocked(True)
                        return

                self.setLocked(False)

            # Unlock the selected folders that match the reUnlockedFolders regx
            if not reUnlockedFolders.match(""):
                for folder in folders:
                    if reUnlockedFolders.search(folder.path()):
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

    def renameSelectedItem(self):
        """
        Rename the selected item.

        :rtype: None
        """
        try:
            self._renameSelectedItem()
        except Exception, e:
            self.criticalDialog(e.message)
            raise

    def _renameSelectedItem(self):
        """
        :rtype: None
        """
        item = self.itemsWidget().selectedItem()

        if not item:
            raise Exception("Please select an item")

        result = item.showRenameDialog(parent=self)
        if result:
            self.reloadItems()
            self.selectItems([item])

    def kwargs(self):
        """
        :rtype: dict
        """
        return self.library().kwargs()

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

    def showCreateFolderDialog(self):
        """
        :rtype: None
        """
        try:
            self.foldersWidget().showCreateDialog(parent=self)
        except Exception, e:
            self.setError(e.message)
            raise

    def selectPath(self, path):
        self.selectPaths([path])

    def selectPaths(self, paths):
        """
        :type paths: list[str]
        :rtype: None
        """
        selection = self.selectedItems()
        self.itemsWidget().selectPaths(paths)

        if self.selectedItems() != selection:
            self._itemSelectionChanged()

    def selectItems(self, items):
        paths = [item.path() for item in items]
        self.selectPaths(paths)

    def selectFolders(self, folders):
        self._foldersWidget.selectFolders(folders)

    def selectedItems(self):
        return self._itemsWidget.selectedItems()

    def selectedFolderPath(self):
        folder = self.selectedFolder()
        if folder:
            return folder.path()

    def selectedFolder(self):
        """
        :rtype: studiolibrary.Folder
        """
        folders = self.selectedFolders()
        if folders:
            return folders[0]
        return None

    def selectedFolders(self):
        return self._foldersWidget.selectedFolders()

    def isRecursiveSearchEnabled(self):
        """
        :rtype: int
        """
        return self._recursiveSearchEnabled

    def setRecursiveSearchEnabled(self, value):
        """
        :type value: int
        :rtype: None
        """
        self._recursiveSearchEnabled = value
        self.reloadItems()

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

        logger = logging.getLogger("studiolibrary")

        if value:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        self.debugModeChanged.emit(value)
        self.globalSignal.debugModeChanged.emit(self, value)

    def isDebug(self):
        """
        :rtype: bool
        """
        return self._isDebug


