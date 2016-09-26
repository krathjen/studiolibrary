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
from functools import partial

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


class LibraryWidget(studiolibrary.MayaDockWidgetMixin, QtWidgets.QWidget):

    DPI_ENABLED = False
    TRASH_ENABLED = True

    MIN_SLIDER_DPI = 80
    MAX_SLIDER_DPI = 250

    folderPathSelected = QtCore.Signal(str)

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        QtWidgets.QWidget.__init__(self, None)
        studiolibrary.MayaDockWidgetMixin.__init__(self, None)

        logger.info("Loading library window '{0}'".format(library.name()))

        self.setObjectName("studiolibrary")
        studiolibrary.analytics().logScreen("MainWindow")

        resource = studiolibrary.resource()
        self.setWindowIcon(resource.icon("icon_black"))

        self._dpi = 1.0

        self._pSize = None
        self._pShow = None
        self._library = None
        self._isDebug = False
        self._isLocked = False
        self._isLoaded = False
        self._showFolders = False
        self._updateThread = None
        self._previewWidget = None
        self._loaderEnabled = True
        self._recursiveSearchEnabled = True

        self._trashEnabled = self.TRASH_ENABLED

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

        self._itemsWidget = self.createItemsWidget()

        tip = "Search all current items."
        self._searchWidget = studioqt.SearchWidget(self)
        self._searchWidget.setToolTip(tip)
        self._searchWidget.setStatusTip(tip)

        self._statusWidget = studioqt.StatusWidget(self)
        self._menuBarWidget = studioqt.MenuBarWidget()

        self._foldersWidget = self.createFoldersWidget()

        self.setMinimumWidth(5)
        self.setMinimumHeight(5)

        # The methods below are needed to fix an issue with PySide2.
        def showNewMenu():
            self.showNewMenu()

        def showSettingsMenu():
            self.showSettingsMenu()

        def showSortByMenu():
            self.showSortByMenu()

        def showGroupByMenu():
            self.showGroupByMenu()

        def showItemViewMenu():
            self.showItemViewMenu()

        def toggleView():
            self.toggleView()

        tip = "Add a new item to the selected folder."
        icon = studioqt.icon("add")
        self._newAction = self._menuBarWidget.addLeftAction("New Item")
        self._newAction.setIcon(icon)
        self._newAction.setToolTip(tip)
        self._newAction.setStatusTip(tip)
        self._newAction.triggered.connect(showNewMenu)

        tip = "Change the style of the item view."
        icon = studioqt.icon("settings2")
        self._itemSettingsAction = self._menuBarWidget.addRightAction("Item View")
        self._itemSettingsAction.setIcon(icon)
        self._itemSettingsAction.setToolTip(tip)
        self._itemSettingsAction.setStatusTip(tip)
        self._itemSettingsAction.triggered.connect(showItemViewMenu)

        tip = "Group the items in the view by a column."
        icon = studioqt.icon("groupby")
        self._groupbyAction = self._menuBarWidget.addRightAction("Group By")
        self._groupbyAction.setIcon(icon)
        self._groupbyAction.setToolTip(tip)
        self._groupbyAction.setStatusTip(tip)
        self._groupbyAction.triggered.connect(showGroupByMenu)

        tip = "Sort the items in the view by a column."
        icon = studioqt.icon("sortby")
        self._sortbyAction = self._menuBarWidget.addRightAction("Sort By")
        self._sortbyAction.setIcon(icon)
        self._sortbyAction.setToolTip(tip)
        self._sortbyAction.setStatusTip(tip)
        self._sortbyAction.triggered.connect(showSortByMenu)

        tip = "Choose to show/hide both the preview and navigation pane."
        icon = studioqt.icon("view")
        self._viewAction = self._menuBarWidget.addRightAction("View")
        self._viewAction.setIcon(icon)
        self._viewAction.setToolTip(tip)
        self._viewAction.setStatusTip(tip)
        self._viewAction.triggered.connect(toggleView)

        icon = studioqt.icon("settings")
        self._settingsAction = self._menuBarWidget.addRightAction("Settings")
        self._settingsAction.setIcon(icon)
        self._settingsAction.triggered.connect(showSettingsMenu)

        self._updateButton = QtWidgets.QPushButton(None)
        self._updateButton.setText("Update Available")
        self._updateButton.setObjectName("updateButton")
        self._updateButton.clicked.connect(self.help)
        self._updateButton.hide()

        self._menuBarWidget.layout().insertWidget(1, self._updateButton)
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

        studiolibrary.Record.onSaved.connect(self._recordSaved)
        studiolibrary.Record.onSaving.connect(self._recordSaving)

        itemsWidget = self.itemsWidget()
        itemsWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        itemsWidget.itemMoved.connect(self._itemMoved)
        itemsWidget.itemDropped.connect(self._itemDropped)
        itemsWidget.itemSelectionChanged.connect(self._itemSelectionChanged)
        itemsWidget.customContextMenuRequested.connect(self.showItemsContextMenu)

        folderWidget = self.foldersWidget()
        folderWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        folderWidget.itemDropped.connect(self._folderDropped)
        folderWidget.itemSelectionChanged.connect(self._folderSelectionChanged)
        folderWidget.customContextMenuRequested.connect(self.showFolderContextMenu)

        self.checkForUpdates()
        self.setLibrary(library)

        self._compactView = False

        self.updateViewButton()

        validGroupByColumns = ["Category", "Modified", "Type"]
        self.recordsWidget().treeWidget().setValidGroupByColumns(validGroupByColumns)

    def createItemsWidget(self):

        itemsWidget = studioqt.CombinedWidget(self)
        # itemsWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # itemsWidget.itemMoved.connect(self._itemMoved)
        # itemsWidget.itemDropped.connect(self._itemDropped)
        # itemsWidget.itemSelectionChanged.connect(self._itemSelectionChanged)
        # itemsWidget.customContextMenuRequested.connect(self.showItemsContextMenu)

        return itemsWidget

    def createFoldersWidget(self):

        folderWidget = studioqt.FoldersWidget(self)
        # folderWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # folderWidget.itemDropped.connect(self._folderDropped)
        # folderWidget.itemSelectionChanged.connect(self._folderSelectionChanged)
        # folderWidget.customContextMenuRequested.connect(self.showFolderContextMenu)

        return folderWidget

    def foldersWidget(self):
        """
        :rtype: studiolibrary.FoldersWidget
        """
        return self._foldersWidget

    def isCompactView(self):
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

        if not compact:
            icon = studioqt.icon("view_all")
        else:
            icon = studioqt.icon("view_compact")

        self._viewAction.setIcon(icon)

        self.menuBarWidget().update()

    def showGroupByMenu(self):
        """
        Show the group by menu at the group button.

        :rtype: None
        """
        menu = self.recordsWidget().createGroupByMenu()
        widget = self.menuBarWidget().findToolButton("Group By")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        action = menu.exec_(point)

    def showSortByMenu(self):
        """
        Show the sort by menu at the sort button.

        :rtype: None
        """
        menu = self.recordsWidget().createSortByMenu()
        widget = self.menuBarWidget().findToolButton("Sort By")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        action = menu.exec_(point)

    def showItemViewMenu(self):
        """
        Show the item settings menu.

        :rtype: None
        """
        menu = self.recordsWidget().createItemSettingsMenu()
        widget = self.menuBarWidget().findToolButton("Item View")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        action = menu.exec_(point)

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

    def recordsWidget(self):
        """
        :rtype: studioqt.CombinedWidget
        """
        return self._itemsWidget

    def menuBarWidget(self):
        """
        :rtype: MenuBarWidget
        """
        return self._menuBarWidget

    def items(self):
        """
        Return all the loaded items.

        :rtype: list[studiolibrary.LibraryItem]
        """
        return self.itemsWidget().items()

    def itemsWidget(self):
        """
        Return the widget the contains all the items.

        :rtype: studioqt.CombinedWidget
        """
        return self._itemsWidget

    def refresh(self):
        """
        Refresh/Reload the records.

        :rtype: None
        """
        self.loadRecords()

    def refreshAll(self):
        """
        Refresh all library widgets.

        :rtype: None
        """
        for library in self.library().libraries():
            widget = library.libraryWidget()
            if widget:
                widget.refresh()

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
        self.reloadLibrary()

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
        :rtype: list[studiolibrary.Record]
        """
        records = []
        folders = self.foldersWidget().selectedFolders()

        for folder in folders:

            path = folder.path()
            depth = 1

            if self.isRecursiveSearchEnabled():
                depth = 3

            records.extend(self.library().loadRecords(path, depth=depth))

        return records

    @studioqt.showWaitCursor
    def loadRecords(self):
        """
        :rtype: None
        """
        if not self.loaderEnabled():
            logger.debug("Loader disabled!")
            return

        logger.debug("Loading records for library '%s'" % self.library().name())

        elapsedTime = time.time()

        selectedRecords = self.selectedRecords()

        records = self.loader()

        self.itemsWidget().setItems(records, sortEnabled=False)

        self.loadCustomOrder()
        self.itemsWidget().refreshSortBy()

        if selectedRecords:
            self.selectRecords(selectedRecords)

        self.refreshSearch()

        elapsedTime = time.time() - elapsedTime
        self.setLoadedMessage(elapsedTime)

        logger.debug("Loaded records")

    def reloadLibrary(self):
        """
        :rtype: None
        """
        self.clearRecords()
        self.clearPreviewWidget()
        self.loadPlugins()
        self.updateWindowTitle()
        self.setRootPath(self.library().path())

    def reloadFolders(self):
        """
        :rtype: None
        """
        ignoreFilter = self.folderIgnoreFilter()

        self.foldersWidget().reload()
        self.foldersWidget().setIgnoreFilter(ignoreFilter)

    def checkForUpdates(self):
        """
        :rtype: None
        """
        if studiolibrary.CHECK_FOR_UPDATES_ENABLED:
            if not self._updateThread:
                self._updateThread = studiolibrary.CheckForUpdatesThread(self)
                self.connect(
                    self._updateThread,
                    QtCore.SIGNAL("updateAvailable()"),
                    self.setUpdateAvailable
                )
            self._updateThread.start()
        else:
            logger.debug("Check for updates has been disabled!")

    def _itemSelectionChanged(self):
        """
        Triggered when an item is selected or deselected.

        :rtype: None
        """
        record = self.recordsWidget().selectedItem()
        self.setPreviewWidgetFromRecord(record)

    def _folderSelectionChanged(self):
        """
        Triggered when an item is selected or deselected.

        :type selectedFolders: list[studiolibrary.Folder]
        :type deselectedFolders: list[studiolibrary.Folder]
        :rtype: None
        """
        for plugin in self.plugins().values():
            plugin.folderSelectionChanged()

        self.loadRecords()

        folderPath = self.selectedFolderPath()
        self.folderPathSelected.emit(folderPath)

    def recordsFromUrls(self, urls):
        """
        :type urls: list[QtGui.QUrl]
        :rtype: list[studiolibrary.Records]
        """
        records = []
        for url in urls:
            path = url.toLocalFile()

            # Fixes a bug when dragging from windows explorer on windows 10
            if studiolibrary.isWindows():
                if path.startswith("/"):
                    path = path[1:]

            record = self.library().recordFromPath(path)
            records.append(record)

        return records

    # -----------------------------------------------------------------
    # Support for folder and item context menus
    # -----------------------------------------------------------------

    def createNewMenu(self):
        """
        Return the new menu for adding new folders and records.

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

        for name in self.library().plugins():
            plugin = self.plugin(name)
            action = plugin.newAction(parent=menu)

            if action:
                callback = partial(self.showCreateWidget, plugin=plugin)
                action.triggered.connect(callback)
                menu.addAction(action)

        return menu

    def createRecordEditMenu(self):
        """
        Return the edit menu for deleting, renaming records.

        :rtype: QtWidgets.QMenu
        """
        menu = QtWidgets.QMenu(self)
        menu.setTitle("Edit")

        action = QtWidgets.QAction("Rename", menu)
        action.triggered.connect(self.renameSelectedRecord)
        menu.addAction(action)

        if self.trashEnabled():
            action = QtWidgets.QAction("Move to trash", menu)
            action.setEnabled(self.isTrashEnabled())
            action.triggered.connect(self.trashSelectedRecordsDialog)
            menu.addAction(action)

        action = QtWidgets.QAction("Show in folder", menu)
        action.triggered.connect(self.openSelectedRecords)
        menu.addAction(action)

        return menu

    def createSettingsMenu(self):
        """
        Return the settings menu for changing the library widget.

        :rtype: QtWidgets.QMenu
        """

        icon = studioqt.icon("settings", color=self.iconColor())
        menu = QtWidgets.QMenu("", self)
        menu.setTitle("Settings")
        menu.setIcon(icon)

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

        # themesMenu = studioqt.ThemesMenu(menu)
        # themesMenu.themeTriggered.connect(self.library().setTheme)
        # menu.addMenu(themesMenu)

        separator = QtWidgets.QAction("", menu)
        separator.setSeparator(True)
        menu.addAction(separator)

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

        viewMenu = self.recordsWidget().createSettingsMenu()
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
        :type menu: QtWidgets.QMenu
        :rtype: None
        """
        menu = self.createFolderContextMenu()

        point = QtGui.QCursor.pos()
        point.setX(point.x() + 3)
        point.setY(point.y() + 3)
        action = menu.exec_(point)
        menu.close()

        return action

    def createFolderContextMenu(self):

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

    def createItemContextMenu(self, items):
        """
        :type items: list[studiolibrary.LibraryItem]
        :rtype: studiolibrary.ContextMenu
        """
        menu = studioqt.ContextMenu(self)

        for plugin in self.plugins().values():
            try:
                plugin.recordContextMenu(menu, items)
            except Exception, msg:
                logger.exception(msg)

        if not self.isLocked():
            menu.addMenu(self.createNewMenu())

            if items:
                menu.addMenu(self.createRecordEditMenu())

        menu.addSeparator()
        menu.addMenu(self.itemsWidget().createSettingsMenu())

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

        return studiolibrary.saveJson(path, data)

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
    # Support for moving records with drag and drop
    # -------------------------------------------------------------------

    def _itemMoved(self, item):
        """
        :rtype: None
        """
        self.saveCustomOrder()

    def _itemDropped(self, event):
        """
        :rtype: None
        """
        pass

    def _folderDropped(self, event):
        """
        :type event: list[studiolibrary.Record]
        :rtype: None
        """
        mimeData = event.mimeData()

        if mimeData.hasUrls():
            folder = self.selectedFolder()
            records = self.recordsFromUrls(mimeData.urls())

            for record in records:
                # Check if the record is moving to another folder.
                if folder.path() != record.dirname():
                    self.moveRecordsToFolder(records, folder=folder)
                    self.refreshAll()
                    break

    def moveRecordsDialog(self, parent=None):
        """
        :type parent: QtWidgets.QWidget
        :rtype: QtWidgets.QMessageBox
        """
        parent = parent or self

        msgBox = QtWidgets.QMessageBox(parent)
        msgBox.setWindowTitle("Move or Copy records?")
        msgBox.setText('Would you like to copy or move the selected record/s?')
        msgBox.addButton('Copy', QtWidgets.QMessageBox.AcceptRole)
        msgBox.addButton('Move', QtWidgets.QMessageBox.AcceptRole)
        msgBox.addButton('Cancel', QtWidgets.QMessageBox.RejectRole)

        return msgBox

    def moveRecordsToFolder(self, records, folder):
        """
        :type records: list[studiolibrary.Record]
        :type folder: studiolibrary.Folder
        :rtype: None
        """
        Copy = 0
        Move = 1
        Cancel = 2
        movedRecords = []

        dialog = self.moveRecordsDialog()
        action = dialog.exec_()
        dialog.close()

        if action == Cancel:
            return

        self.recordsWidget().clearSelection()

        try:
            for record in records:

                path = folder.path() + "/" + record.name()

                if action == Copy:
                    record.copy(path)

                elif action == Move:
                    record.rename(path)

                movedRecords.append(record)

        except Exception, msg:
            logger.exception(msg)
            self.criticalDialog(msg)
        finally:
            self.recordsWidget().addItems(movedRecords)
            self.selectRecords(movedRecords)

    def _recordSaved(self, record):
        """
        :type record: studiolibrary.Record
        :rtype: None
        """
        folder = self.selectedFolder()

        if folder and folder.path() == record.dirname():
            path = record.path()
            self.recordsWidget().clearSelection()
            self.loadRecords()
            self.selectPaths([path])

    def _recordSaving(self, record):
        """
        :type record: studiolibrary.Record
        :rtype: None
        """
        if self.library().path() in record.path():
            if record.exists():
                self.showRecordExistsDialog(record)

    def showRecordExistsDialog(self, record):
        """
        :type record: studiolibrary.Record
        :rtype: None
        """
        path = record.path()
        records = [record]
        title = "Warning"
        message = 'Record already exists! Would you like to move the existing record "{name}" to the trash?'
        message = message.format(name=record.name())

        result = self.trashRecordsDialog(records, title=title, message=message)

        if result != QtWidgets.QMessageBox.Yes:
            record.setErrorString("Record was not saved! You cannot save over an existsing record.")

        record.setPath(path)

    def showNewLibraryDialog(self):
        """
        :rtype: None
        """
        studiolibrary.Library.showNewLibraryDialog()

    def folderIgnoreFilter(self):
        """
        Return a list of folder names that should be hidden/ignored.

        :rtype: list[str]
        """
        ignoreFilter = ['.', '.studiolibrary', ".mayaswatches"]

        if not self.isTrashFolderVisible():
            ignoreFilter.append('trash')

        for name, plugin in self.plugins().items():
            ignoreFilter.append(plugin.extension())

        return ignoreFilter

    def setRootPath(self, path):
        """
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
        """
        """
        library = self.library()

        name = library.name()
        path = library.path()
        result = library.execSettingsDialog()

        if result == QtWidgets.QDialog.Accepted:
            self.saveSettings()

            if path != library.path():
                self.reloadLibrary()

            if name != library.name():
                self.updateWindowTitle()

        self.reloadStyleSheet()

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

    def itemsHiddenCount(self):
        """
        Return the number of items hidden.

        :rtype:  int
        """
        return self._itemsHiddenCount

    def itemsVisibleCount(self):
        """
        Return the number of items visible.

        :rtype:  int
        """
        return self._itemsVisibleCount

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

    def showCreateWidget(self, plugin):
        """
        Show the record create widget for a given plugin.

        :type plugin: studiolibrary.Plugin
        :rtype: None
        """
        widget = plugin.createWidget(parent=self._previewFrame)
        self.setCreateWidget(widget)

    def setCreateWidget(self, widget):
        """
        :type widget: QtWidgets.QWidget
        :rtype: None
        """
        self.setPreviewWidgetVisible(True)
        self.recordsWidget().clearSelection()
        self.setPreviewWidget(widget)

    def clearPreviewWidget(self):
        """
        Set the default preview widget.
        """
        widget = studiolibrary.PreviewWidget(None)
        self.setPreviewWidget(widget)

    def setPreviewWidgetFromRecord(self, record):
        """
        :type record: studiolibrary.Record
        :rtype: None
        """
        if record:
            plugin = record.plugin()

            try:
                previewWidget = plugin.previewWidget(None, record)
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
        settings['recordsWidget'] = self.recordsWidget().settings()

        return settings

    def setSettings(self, settings):
        """
        :type settings: studiolibrary.MetaFile
        """

        self.itemsWidget().setToastEnabled(False)

        dpi = settings.get("dpi", 1.0)
        self.setDpi(dpi)

        sizes = settings.get('sizes', [140, 280, 160])
        if len(sizes) == 3:
            self.setSizes(sizes)

        x, y, width, height = settings.get("geometry", [200, 200, 800, 680])
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

        value = settings.get("recursiveSearchEnabled", False)
        self.setRecursiveSearchEnabled(value)

        searchWidgetSettings = settings.get('searchWidget', {})
        self.searchWidget().setSettings(searchWidgetSettings)

        foldersWidgetSettings = settings.get('foldersWidget', {})
        self.foldersWidget().setSettings(foldersWidgetSettings)

        recordsWidgetSettings = settings.get('recordsWidget', {})
        self.recordsWidget().setSettings(recordsWidgetSettings)

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
            self.loadRecords()

        self.loadFolderData()

        self._isLoaded = True

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
        for record in self.selectedRecords():
            record.keyReleaseEvent(event)
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
        self.recordsWidget().setTextColor(color)

        color = studioqt.Color.fromString(options["ITEM_TEXT_SELECTED_COLOR"])
        self.recordsWidget().setTextSelectedColor(color)

        color = studioqt.Color.fromString(options["ITEM_BACKGROUND_COLOR"])
        self.recordsWidget().setBackgroundColor(color)

        color = studioqt.Color.fromString(options["ITEM_BACKGROUND_SELECTED_COLOR"])
        self.recordsWidget().setBackgroundSelectedColor(color)

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
        return self.library().path() + "/Trash"

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

        records = self.selectedRecords()
        for record in records:
            if "Trash" in record.path():
                return False

        return True

    def trashSelectedFoldersDialog(self):
        """
        :rtype: None
        """
        records = self.selectedFolders()

        if records:
            title = "Move selected folders to trash?"
            msg = "Are you sure you want to move the selected folder/s to the trash?"
            result = self.window().questionDialog(msg, title=title)

            if result == QtWidgets.QMessageBox.Yes:
                self.foldersWidget().clearSelection()
                self.trashRecords(records)

    def trashSelectedRecordsDialog(self):
        """
        Show the "move to trash" dialog for the selected records.

        :rtype: QtWidgets.QMessageBox.Button
        """
        records = self.selectedRecords()

        return self.trashRecordsDialog(
            records=records,
            title="Move selected records to trash?",
            message="Are you sure you want to move the selected record/s to the trash?",
        )

    def trashRecordsDialog(self, records, title, message):
        """
        Show the "move to trash" dialog.

        :type records: list[studiolibrary.Record]
        :type title: str
        :type message: str

        :rtype: QtWidgets.QMessageBox.Button
        """
        result = None

        if records:
            title = title
            msg = message
            result = self.window().questionDialog(msg, title=title)

            if result == QtWidgets.QMessageBox.Yes:
                self.trashRecords(records)

        return result

    def trashRecords(self, records):
        """
        :items records: list[studiolibrary.Record]
        :rtype: None
        """
        trashPath = self.trashPath()

        self.createTrashFolder()

        try:
            for record in records:
                record.move(trashPath)

        except Exception, msg:
            logger.exception(msg)
            self.setError(msg)

        finally:
            self.loadRecords()

    # -----------------------------------------------------------------------
    # Support for message boxes
    # -----------------------------------------------------------------------

    def setInfo(self, text):
        self.statusWidget().setInfo(text)

    def setToast(self, text, duration=500):
        self.itemsWidget().setToast(text, duration)

    def setUpdateAvailable(self):
        self._updateButton.show()

    def criticalDialog(self, message, title="Error"):
        self.setError(message)
        return studioqt.MessageBox.critical(self, title, str(message))

    def questionDialog(self, message, title="Question"):
        buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel
        return studioqt.MessageBox.question(self, title, str(message), buttons)

    def setError(self, text):
        text = str(text)
        self.statusWidget().setError(text)
        self.setStatusBarWidgetVisible(True)

    def setWarning(self, text):
        text = str(text)
        self.statusWidget().setWarning(text)
        self.setStatusBarWidgetVisible(True)

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
        recordCount = len(self._itemsWidget.items())
        hiddenCount = self.itemsHiddenCount()

        plural = ""
        if recordCount != 1:
            plural = "s"

        hiddenText = ""
        if hiddenCount > 0:
            hiddenText = ("{0} items hidden.".format(hiddenCount))

        msg = "Loaded {0} item{1} in {2:.3f} seconds. {3}"
        msg = msg.format(recordCount, plural, elapsedTime, hiddenText)
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
        self.recordsWidget().setLocked(value)

        self.updateNewButton()
        self.updateWindowTitle()

    def isLocked(self):
        """
        :rtype: bool
        """
        return self._isLocked

    def updateNewButton(self):
        if self.isLocked():
            pixmap = studioqt.pixmap("lock")
            self._newAction.setEnabled(False)
            self._newAction.setIcon(pixmap)
        else:
            pixmap = studioqt.pixmap("add")
            self._newAction.setEnabled(True)
            self._newAction.setIcon(pixmap)
        self.menuBarWidget().update()

    # -----------------------------------------------------------------------
    # Misc
    # -----------------------------------------------------------------------

    def resetLibrary(self):
        self.library().reset()

    def kwargs(self):
        """
        :rtype: dict
        """
        return self.library().kwargs()

    def window(self):
        """
        :rtype: QtWidgets.QWidget
        """
        return self

    def openSelectedFolders(self):
        folders = self.selectedFolders()
        for folder in folders:
            folder.openLocation()

    def openSelectedRecords(self):
        records = self.selectedRecords()

        for record in records:
            record.openLocation()

        if not records:
            for folder in self.selectedFolders():
                folder.openLocation()

    def renameSelectedRecord(self):
        try:
            self._renameSelectedRecord()
        except Exception, msg:
            self.criticalDialog(msg)
            raise

    def _renameSelectedRecord(self):
        """
        :rtype: None
        """
        record = self.recordsWidget().selectedItem()

        if not record:
            raise Exception("Please select a record")

        result = record.showRenameDialog(parent=self)
        if result:
            self.loadRecords()
            self.selectRecords([record])

    def showCreateFolderDialog(self):
        """
        :rtype: None
        """
        try:
            self.foldersWidget().showCreateDialog(parent=self)
        except Exception, msg:
            self.setError(msg)
            raise

    def selectPath(self, path):
        self.selectPaths([path])

    def selectPaths(self, paths):
        """
        :type paths: list[str]
        :rtype: None
        """
        selection = self.selectedRecords()
        self.recordsWidget().selectPaths(paths)

        if self.selectedRecords() != selection:
            self._itemSelectionChanged()

    def selectRecords(self, records):
        paths = [r.path() for r in records]
        self.selectPaths(paths)

    def selectFolders(self, folders):
        self._foldersWidget.selectFolders(folders)

    def selectedRecords(self):
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

    def plugins(self):
        """
        :rtype: list[studiolibrary.Plugin]
        """
        return self.library().loadedPlugins()

    def plugin(self, name):
        """
        :type name: str
        :rtype: studiolibrary.Plugin
        """
        return self.library().loadedPlugins().get(name, None)

    def loadPlugin(self, name):
        self.library().loadPlugin(name)

    def loadPlugins(self):
        self.library().loadPlugins()

    def clearRecords(self):
        self.recordsWidget().clear()

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
        self.loadRecords()

    @staticmethod
    def help():
        """
        :rtype: None
        """
        studiolibrary.package().openHelp()

    def setDebugMode(self, value):
        """
        :type value: bool
        """
        self._isDebug = value

        if value:
            self.library().setLoggerLevel(logging.DEBUG)
        else:
            self.library().setLoggerLevel(logging.INFO)

    def isDebug(self):
        """
        :rtype: bool
        """
        return self._isDebug

