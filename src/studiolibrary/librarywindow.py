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

import re
import os
import time
import copy
import logging
import webbrowser
from functools import partial

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt
import studiolibrary
import studiolibrary.widgets


__all__ = ["LibraryWindow"]


logger = logging.getLogger(__name__)


class PreviewFrame(QtWidgets.QFrame):
    pass


class SidebarFrame(QtWidgets.QFrame):
    pass


class GlobalSignal(QtCore.QObject):
    """
    Triggered for all library instance.
    """
    folderSelectionChanged = QtCore.Signal(object, object)


class CheckForUpdate(QtCore.QThread):

    finished = QtCore.Signal(object)

    def __init__(self, url):
        super(CheckForUpdate, self).__init__()
        self.url = url

    def run(self):
        info = studiolibrary.checkForUpdates()
        self.finished.emit(info)


class LibraryWindow(QtWidgets.QWidget):

    _instances = {}

    DEFAULT_NAME = "Default"
    DEFAULT_SETTINGS = {
        "library": {
            "sortBy": ["name:asc"],
            "groupBy": ["category:asc"]
        },
        "paneSizes": [130, 280, 180],
        "geometry": [-1, -1, 820, 780],
        "trashFolderVisible": False,
        "sidebarWidgetVisible": True,
        "previewWidgetVisible": True,
        "menuBarWidgetVisible": True,
        "statusBarWidgetVisible": True,
        "recursiveSearchEnabled": True,
        "itemsWidget": {
            "spacing": 2,
            "padding": 6,
            "zoomAmount": 80,
            "textVisible": True,
        },
        "searchWidget": {
            "text": "",
        },
        "filterByMenu": {
            "Folder": False
        },
        "theme": {
            "accentColor": "rgb(60, 160, 210)",
            "backgroundColor": "rgb(50, 50, 60)",
        }
    }

    TRASH_ENABLED = True
    TEMP_PATH_MENU_ENABLED = False

    DPI_ENABLED = studiolibrary.config.get("scaleFactorEnabled", False)

    ICON_COLOR = QtGui.QColor(255, 255, 255, 200)
    ICON_BADGE_COLOR = QtGui.QColor(230, 230, 0)

    # Customize widget classes
    SORTBY_MENU_CLASS = studiolibrary.widgets.SortByMenu
    GROUPBY_MENU_CLASS = studiolibrary.widgets.GroupByMenu
    FILTERBY_MENU_CLASS = studiolibrary.widgets.FilterByMenu

    ITEMS_WIDGET_CLASS = studiolibrary.widgets.ItemsWidget
    SEARCH_WIDGET_CLASS = studiolibrary.widgets.SearchWidget
    STATUS_WIDGET_CLASS = studiolibrary.widgets.StatusWidget
    MENUBAR_WIDGET_CLASS = studiolibrary.widgets.MenuBarWidget
    SIDEBAR_WIDGET_CLASS = studiolibrary.widgets.SidebarWidget

    # Customize library classe
    LIBRARY_CLASS = studiolibrary.Library

    globalSignal = GlobalSignal()

    # Local signal
    loaded = QtCore.Signal()
    lockChanged = QtCore.Signal(object)

    itemRenamed = QtCore.Signal(str, str)
    itemSelectionChanged = QtCore.Signal(object)

    folderRenamed = QtCore.Signal(str, str)
    folderSelectionChanged = QtCore.Signal(object)

    @staticmethod
    def instances():
        """
        Return all the LibraryWindow instances that have been initialised.

        :rtype: list[LibraryWindow]
        """
        return LibraryWindow._instances.values()

    @staticmethod
    def destroyInstances():
        """Delete all library widget instances."""
        for widget in LibraryWindow.instances():
            widget.destroy()

        LibraryWindow._instances = {}

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
            **kwargs
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
        
        :rtype: LibraryWindow
        """
        name = name or studiolibrary.defaultLibrary()

        libraryWindow = LibraryWindow._instances.get(name)

        if not libraryWindow:
            studioqt.installFonts(studiolibrary.resource.get("fonts"))
            libraryWindow = cls(name=name)
            LibraryWindow._instances[name] = libraryWindow

        kwargs_ = {
            "lock": lock,
            "show": show,
            "superusers": superusers,
            "lockRegExp": lockRegExp,
            "unlockRegExp": unlockRegExp
        }

        libraryWindow.setKwargs(kwargs_)
        libraryWindow.setLocked(lock)
        libraryWindow.setSuperusers(superusers)
        libraryWindow.setLockRegExp(lockRegExp)
        libraryWindow.setUnlockRegExp(unlockRegExp)

        if path:
            libraryWindow.setPath(path)

        if show:
            libraryWindow.show(**kwargs)

        return libraryWindow

    def __init__(self, parent=None, name="", path=""):
        """
        Create a new instance of the Library Widget.

        :type parent: QtWidgets.QWidget or None
        :type name: str
        :type path: str
        """
        QtWidgets.QWidget.__init__(self, parent)

        self.setObjectName("studiolibrary")

        version = studiolibrary.version()

        self.setWindowIcon(studiolibrary.resource.icon("icon_black"))

        self._dpi = 1.0
        self._path = ""
        self._items = []
        self._name = name or self.DEFAULT_NAME
        self._theme = None
        self._kwargs = {}
        self._isDebug = False
        self._isLocked = False
        self._isLoaded = False
        self._previewWidget = None
        self._currentItem = None
        self._library = None
        self._lightbox = None
        self._refreshEnabled = False
        self._progressBar = None
        self._superusers = None
        self._lockRegExp = None
        self._unlockRegExp = None
        self._settingsWidget = None

        self._updateInfo = {}
        self._checkForUpdateThread = CheckForUpdate(self)
        self._checkForUpdateThread.finished.connect(self.checkForUpdateFinished)
        self._checkForUpdateEnabled = True

        self._trashEnabled = self.TRASH_ENABLED

        self._itemsHiddenCount = 0
        self._itemsVisibleCount = 0

        self._isTrashFolderVisible = False
        self._sidebarWidgetVisible = True
        self._previewWidgetVisible = True
        self._statusBarWidgetVisible = True

        # --------------------------------------------------------------------
        # Create Widgets
        # --------------------------------------------------------------------

        library = self.LIBRARY_CLASS(libraryWindow=self)
        library.dataChanged.connect(self.refresh)
        library.searchTimeFinished.connect(self._searchFinished)

        self._sidebarFrame = SidebarFrame(self)
        self._previewFrame = PreviewFrame(self)

        self._itemsWidget = self.ITEMS_WIDGET_CLASS(self)
        self._itemsWidget.installEventFilter(self)
        self._itemsWidget.keyPressed.connect(self._keyPressed)

        tip = "Search all current items."
        self._searchWidget = self.SEARCH_WIDGET_CLASS(self)
        self._searchWidget.setToolTip(tip)
        self._searchWidget.setStatusTip(tip)

        self._filterByMenu = self.FILTERBY_MENU_CLASS(self)
        self._statusWidget = self.STATUS_WIDGET_CLASS(self)

        # Add the update available button to the status widget
        self._updateAvailableButton = QtWidgets.QPushButton(self._statusWidget)
        self._updateAvailableButton.setObjectName("updateAvailableButton")
        self._updateAvailableButton.setText("Update Available")
        self._updateAvailableButton.setCursor(QtCore.Qt.PointingHandCursor)
        self._updateAvailableButton.hide()
        self._updateAvailableButton.clicked.connect(self.openReleasesUrl)

        self.statusWidget().layout().addWidget(self._updateAvailableButton)

        self._menuBarWidget = self.MENUBAR_WIDGET_CLASS(self)
        self._sidebarWidget = self.SIDEBAR_WIDGET_CLASS(self)

        self._filterByMenu.setDataset(library)
        self._itemsWidget.setDataset(library)
        self._searchWidget.setDataset(library)
        self._sidebarWidget.setDataset(library)

        self.setLibrary(library)

        # --------------------------------------------------------------------
        # Setup the menu bar buttons
        # --------------------------------------------------------------------

        iconColor = self.iconColor()

        name = "New Item"
        icon = studiolibrary.resource.icon("plus")
        tip = "Add a new item to the selected folder"
        self.addMenuBarAction(name, icon, tip, callback=self.showNewMenu)
        self._menuBarWidget.addWidget(self._searchWidget)

        name = "Filters"
        icon = studiolibrary.resource.icon("filter")
        tip = "Filter the current results by type.\n" \
              "CTRL + Click will hide the others and show the selected one."
        action = self.addMenuBarAction(name, icon, tip, callback=self.showFilterByMenu)

        name = "Item View"
        icon = studiolibrary.resource.icon("sliders")
        tip = "Change the style of the item view"
        self.addMenuBarAction(name, icon, tip, callback=self.showItemViewMenu)

        name = "View"
        icon = studiolibrary.resource.icon("columns-3")
        tip = "Choose to show/hide both the preview and navigation pane.\n" \
              "CTRL + Click will hide the menu bar as well."
        self.addMenuBarAction(name, icon, tip, callback=self.toggleView)

        name = "Sync items"
        icon = studiolibrary.resource.icon("arrows-rotate")
        tip = "Sync with the filesystem"
        self.addMenuBarAction(name, icon, tip, callback=self.sync)

        name = "Settings"
        icon = studiolibrary.resource.icon("bars")
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

        self._sidebarFrame.setLayout(layout)
        self._sidebarFrame.layout().addWidget(self._sidebarWidget)

        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self._splitter.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                     QtWidgets.QSizePolicy.Expanding)
        self._splitter.setHandleWidth(2)
        self._splitter.setChildrenCollapsible(False)

        self._splitter.insertWidget(0, self._sidebarFrame)
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

        itemsWidget = self.itemsWidget()
        itemsWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        itemsWidget.itemMoved.connect(self._itemMoved)
        itemsWidget.itemDropped.connect(self._itemDropped)
        itemsWidget.itemSelectionChanged.connect(self._itemSelectionChanged)
        itemsWidget.customContextMenuRequested.connect(self.showItemsContextMenu)

        sidebarWidget = self.sidebarWidget()
        sidebarWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        sidebarWidget.itemDropped.connect(self._itemDropped)
        sidebarWidget.itemSelectionChanged.connect(self._folderSelectionChanged)
        sidebarWidget.customContextMenuRequested.connect(self.showFolderMenu)
        sidebarWidget.settingsMenuRequested.connect(self._foldersMenuRequested)

        self.folderSelectionChanged.connect(self.updateLock)

        self.updateMenuBar()
        self.updatePreviewWidget()

        if path:
            self.setPath(path)

    def _keyPressed(self, event):
        """
        Triggered from the items widget on key press event.

        :type event: QKeyEvent
        """
        text = event.text().strip()

        if not text.isalpha() and not text.isdigit():
            return

        if text and not self.searchWidget().hasFocus():
            self.searchWidget().setFocus()
            self.searchWidget().setText(text)

    def _searchFinished(self):
        self.showRefreshMessage()

    def _foldersMenuRequested(self, menu):
        """
        Triggered when the folders settings menu has been requested.

        :type menu: QtWidgets.QMenu
        """
        # Adding a blank icon fixes the text alignment issue when using Qt 5.12.+
        icon = studiolibrary.resource.icon("blank")

        action = QtWidgets.QAction("Change Path", menu)
        action.triggered.connect(self.showChangePathDialog)
        action.setIcon(icon)

        menu.addAction(action)
        menu.addSeparator()

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
        Triggered when items are dropped on the items widget or sidebar widget.

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
        self.folderSelectionChanged.emit(path)
        self.globalSignal.folderSelectionChanged.emit(self, path)

    def isUpdateAvailable(self):
        return self._updateAvailable

    def checkForUpdate(self):
        """Check if there are any new versions available."""
        self._updateAvailableButton.hide()
        if self.isCheckForUpdateEnabled():
            self._checkForUpdateThread.start()

    def checkForUpdateFinished(self, info):
        """Triggered when the check for update thread has finished."""
        self._updateInfo = info or {}
        if self._updateInfo.get("updateFound"):
            self._updateAvailableButton.show()
        else:
            self._updateAvailableButton.hide()

    def destroy(self):
        """Destroy the current library window instance."""
        self.hide()
        self.closePreviewWidget()
        self.close()
        self.itemsWidget().clear()
        self.library().clear()
        super(LibraryWindow, self).destroy()

    def setKwargs(self, kwargs):
        """
        Set the key word arguments used to open the window.
        
        :type kwargs: dict
        """
        self._kwargs.update(kwargs)

    def library(self):
        """
        Return the library model object.

        :rtype: studiolibrary.Library
        """
        return self._library

    def setLibrary(self, library):
        """
        Set the library model.

        :type library: studiolibrary.Library
        :rtype: None
        """
        self._library = library

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

        library = self.library()
        library.setPath(path)

        if not os.path.exists(library.databasePath()):
            self.sync()

        self.refresh()
        self.library().search()
        self.updatePreviewWidget()

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

        dialog = studiolibrary.widgets.createMessageBox(self, title, text)

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

        dialog = studiolibrary.widgets.createMessageBox(self, title, text)
        dialog.show()

        dialog.accepted.connect(self.showChangePathDialog)

    def showChangePathDialog(self):
        """
        Show a file browser dialog for changing the root path.

        :rtype: None
        """
        path = self._showChangePathDialog()
        if path:
            self.setPath(path)
        else:
            self.refresh()

    @studioqt.showArrowCursor
    def _showChangePathDialog(self):
        """
        Open the file dialog for setting a new root path.

        :rtype: str
        """
        path = self.path()

        if not path:
            path = os.path.expanduser("~")

        path = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Choose a root folder location",
            path
        )

        return studiolibrary.normPath(path)

    def isRefreshEnabled(self):
        """
        Return True if the LibraryWindow can be refreshed.
        
        :rtype: bool 
        """
        return self._refreshEnabled

    def setRefreshEnabled(self, enable):
        """
        If enable is False, all updates will be ignored.

        :rtype: bool 
        """
        self.library().setSearchEnabled(enable)
        self._refreshEnabled = enable

    @studioqt.showWaitCursor
    def sync(self):
        """
        Sync any data that might be out of date with the model. 
        
        :rtype: None 
        """
        progressBar = self.statusWidget().progressBar()

        @studioqt.showWaitCursor
        def _sync():
            elapsedTime = time.time()
            self.library().sync(progressCallback=self.setProgressBarValue)

            elapsedTime = time.time() - elapsedTime

            msg = "Synced items in {0:.3f} seconds."
            msg = msg.format(elapsedTime)

            self.statusWidget().showInfoMessage(msg)
            self.setProgressBarValue("Done")

            studioqt.fadeOut(progressBar, duration=500, onFinished=progressBar.close)

        self.setProgressBarValue("Syncing")
        studioqt.fadeIn(progressBar, duration=1, onFinished=_sync)

        progressBar.show()

    def setProgressBarValue(self, label, value=-1):
        """Set the progress bar label and value"""

        progressBar = self.statusWidget().progressBar()

        if value == -1:
            self.statusWidget().progressBar().reset()
            value = 100

        progressBar.setValue(value)
        progressBar.setText(label)

    def refresh(self):
        """
        Refresh all sidebar items and library items.
        
        :rtype: None 
        """
        if self.isRefreshEnabled():
            self.update()

    def update(self):
        """Update the library widget and the data. """
        self.refreshSidebar()
        self.updateWindowTitle()

    # -----------------------------------------------------------------
    # Methods for the sidebar widget
    # -----------------------------------------------------------------

    def sidebarWidget(self):
        """
        Return the sidebar widget.
        
        :rtype: studioqt.SidebarWidget
        """
        return self._sidebarWidget

    def selectedFolderPath(self):
        """
        Return the selected folder items.

        :rtype: str or None
        """
        return self.sidebarWidget().selectedPath()

    def selectedFolderPaths(self):
        """
        Return the selected folder items.

        :rtype: list[str]
        """
        return self.sidebarWidget().selectedPaths()

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
        self.sidebarWidget().selectPaths(paths)

    @studioqt.showWaitCursor
    def refreshSidebar(self):
        """
        Refresh the state of the sidebar widget.
        
        :rtype: None 
        """
        path = self.path()

        if not path:
            return self.showWelcomeDialog()
        elif not os.path.exists(path):
            return self.showPathErrorDialog()

        self.updateSidebar()

    def updateSidebar(self):
        """
        Update the folders to be shown in the folders widget.
        
        :rtype: None 
        """
        data = {}
        root = self.path()

        queries = [{'filters': [('type', 'is', 'Folder')]}]

        items = self.library().findItems(queries)

        for item in items:
            data[item.path()] = item.itemData()

        self.sidebarWidget().setData(data, root=root)

    def setFolderData(self, path, data):
        """
        Convenience method for setting folder data.

        :type path: str
        :type data: dict
        """
        self.sidebarWidget().setItemData(path, data)

    def createFolderContextMenu(self):
        """
        Return the folder menu for the selected folders.

        :rtype: QtWidgets.QMenu
        """

        path = self.selectedFolderPath()

        items = []

        if path:
            queries = [{"filters": [("path", "is", path)]}]

            items = self.library().findItems(queries)

            if items:
                self._items_ = items

        return self.createItemContextMenu(items)

    # -----------------------------------------------------------------
    # Methods for the items widget
    # -----------------------------------------------------------------

    def itemsWidget(self):
        """
        Return the widget the contains all the items.

        :rtype: studiolibrary.widgets.ItemsWidget
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
        return self._items

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
        self._items.extend(items)

        if select:
            self.selectItems(items)
            self.scrollToSelectedItem()

    def createItemsFromUrls(self, urls):
        """
        Return a new list of items from the given urls.

        :rtype: list[studiolibrary.LibraryItem]
        """
        return self.library().itemsFromUrls(urls, libraryWindow=self)

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

    def showFilterByMenu(self):
        """
        Show the filters menu.

        :rtype: None
        """
        widget = self.menuBarWidget().findToolButton("Filters")
        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        self._filterByMenu.show(point)
        self.updateMenuBar()

    def showGroupByMenu(self):
        """
        Show the group by menu at the group button.

        :rtype: None
        """
        widget = self.menuBarWidget().findToolButton("Group By")
        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        self._groupByMenu.show(point)

    def showSortByMenu(self):
        """
        Show the sort by menu at the sort button.

        :rtype: None
        """
        widget = self.menuBarWidget().findToolButton("Sort By")
        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        self._sortByMenu.show(point)

    def showItemViewMenu(self):
        """
        Show the item settings menu.

        :rtype: None
        """
        menu = self.itemsWidget().createSettingsMenu()
        widget = self.menuBarWidget().findToolButton("Item View")

        point = widget.mapToGlobal(QtCore.QPoint(0, widget.height()))
        menu.exec_(point)

    def createNewItemMenu(self):
        """
        Return the create new item menu for adding new folders and items.

        :rtype: QtWidgets.QMenu
        """
        color = self.iconColor()

        icon = studiolibrary.resource.icon("add", color=color)
        menu = QtWidgets.QMenu(self)
        menu.setIcon(icon)
        menu.setTitle("New")

        def _sortKey(item):
            return item.MENU_ORDER

        for cls in sorted(studiolibrary.registeredItems(), key=_sortKey):
            action = cls.createAction(menu, self)

            if action:
                icon = studioqt.Icon(action.icon())
                icon.setColor(self.iconColor())

                action.setIcon(icon)
                menu.addAction(action)

        return menu

    def settingsValidator(self, **kwargs):
        """
        The validator used for the settings dialog.

        :type kwargs: dict
        """
        fields = []

        color = kwargs.get("accentColor")
        if color and self.theme().accentColor().toString() != color:
            self.theme().setAccentColor(color)

        color = kwargs.get("backgroundColor")
        if color and self.theme().backgroundColor().toString() != color:
            self.theme().setBackgroundColor(color)

        path = kwargs.get("path", "")
        if not os.path.exists(path):
            fields.append(
                {
                    "name": "path",
                    "value": path,
                    "error": "Path does not exists!"
                }
            )

        scaleFactor = kwargs.get("scaleFactor")
        scaleFactorMap = {"Small": 1.0, "Large": 1.5}
        value = scaleFactorMap.get(scaleFactor, 1.0)

        if value != self.dpi():
            self.setDpi(value)

        return fields

    def settingsAccepted(self, **kwargs):
        """
        Called when the user has accepted the changes in the settings dialog.

        :type kwargs: dict
        """
        path = kwargs.get("path")
        if path and path != self.path():
            self.setPath(path)

        self.saveSettings()

    def showSettingDialog(self):
        """Show the settings dialog."""
        accentColor = self.theme().accentColor().toString()
        backgroundColor = self.theme().backgroundColor().toString()

        form = {
            "title": "Settings",
            "description": "Your local settings",
            "layout": "vertical",
            "schema": [
                # {"name": "name", "type": "string", "default": self.name()},
                {"name": "path", "type": "path", "value": self.path()},
                {
                    "name": "accentColor",
                    "type": "color",
                    "value": accentColor,
                    "colors": [
                        "rgb(225, 110, 110)",
                        # "rgb(220, 135, 100)",
                        "rgb(225, 150, 70)",
                        "rgb(225, 180, 35)",
                        "rgb(90, 175, 130)",
                        "rgb(100, 175, 160)",
                        "rgb(70, 160, 210)",
                        # "rgb(5, 135, 245)",
                        "rgb(30, 145, 245)",
                        "rgb(110, 125, 220)",
                        "rgb(100, 120, 150)",
                    ]
                },
                {
                    "name": "backgroundColor",
                    "type": "color",
                    "value": backgroundColor,
                    "colors": [
                        "rgb(45, 45, 48)",
                        "rgb(55, 55, 60)",
                        "rgb(68, 68, 70)",
                        "rgb(80, 60, 80)",
                        "rgb(85, 60, 60)",
                        "rgb(60, 75, 75)",
                        "rgb(60, 64, 79)",
                        "rgb(245, 245, 255)",
                    ]
                },
            ],
            "validator": self.settingsValidator,
            "accepted": self.settingsAccepted,
        }

        if self.DPI_ENABLED:
            value = 'Large' if self.dpi() > 1 else "Small"

            form["schema"].append(
                {
                    "name": "scaleFactor",
                    "type": "buttonGroup",
                    "title": "Scale Factor (DPI)",
                    "value": value,
                    "items": [
                        "Small",
                        "Large",
                    ]
                },
            )

        self._settingsWidget = studiolibrary.widgets.FormDialog(form=form)
        self._settingsWidget.setObjectName("settingsDialog")
        self._settingsWidget.acceptButton().setText("Save")

        self._lightbox = studiolibrary.widgets.Lightbox(self)
        self._lightbox.setWidget(self._settingsWidget)
        self._lightbox.show()

    def createSettingsMenu(self):
        """
        Return the settings menu for changing the library widget.

        :rtype: studioqt.Menu
        """
        menu = studioqt.Menu("", self)
        menu.setTitle("Settings")

        # Adding a blank icon fixes the text alignment issue when using Qt 5.12.+
        icon = studiolibrary.resource.icon("blank")

        action = menu.addAction("Sync")
        action.triggered.connect(self.sync)
        action.setIcon(icon)

        menu.addSeparator()
        action = menu.addAction("Settings")
        action.triggered.connect(self.showSettingDialog)

        menu.addSeparator()

        librariesMenu = studiolibrary.widgets.LibrariesMenu(libraryWindow=self)
        menu.addMenu(librariesMenu)
        menu.addSeparator()

        action = QtWidgets.QAction("Show Menu", menu)
        action.setCheckable(True)
        action.setChecked(self.isMenuBarWidgetVisible())
        action.triggered[bool].connect(self.setMenuBarWidgetVisible)
        menu.addAction(action)

        action = QtWidgets.QAction("Show Sidebar", menu)
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

        action = QtWidgets.QAction("Save Settings", menu)
        action.triggered.connect(self.saveSettings)
        menu.addAction(action)

        action = QtWidgets.QAction("Reset Settings", menu)
        action.triggered.connect(self.resetSettings)
        menu.addAction(action)

        action = QtWidgets.QAction("Open Settings", menu)
        action.triggered.connect(self.openSettings)
        menu.addAction(action)

        if self.TEMP_PATH_MENU_ENABLED:
            action = QtWidgets.QAction("Open Temp Path", menu)
            action.triggered.connect(self.openTempPath)
            menu.addAction(action)

        menu.addSeparator()

        if self.trashEnabled():
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

        action = QtWidgets.QAction("Check For Updates", menu)
        action.setCheckable(True)
        action.setChecked(self.isCheckForUpdateEnabled())
        action.triggered[bool].connect(self.setCheckForUpdateEnabled)
        menu.addAction(action)

        action = QtWidgets.QAction("Debug Mode", menu)
        action.setCheckable(True)
        action.setChecked(self.isDebug())
        action.triggered[bool].connect(self.setDebugMode)
        menu.addAction(action)

        menu.addSeparator()

        action = QtWidgets.QAction("Report Issue", menu)
        action.triggered.connect(self.openReportUrl)
        menu.addAction(action)

        action = QtWidgets.QAction("Help", menu)
        action.triggered.connect(self.openHelpUrl)
        menu.addAction(action)

        return menu

    def showNewMenu(self):
        """
        Creates and shows the new menu at the new action button.

        :rtype: QtWidgets.QAction
        """
        menu = self.createNewItemMenu()

        point = self.menuBarWidget().rect().bottomLeft()
        point = self.menuBarWidget().mapToGlobal(point)

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
        menu.move(-1000, -1000)  # Fix display bug on linux
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
        menu = self.createFolderContextMenu()

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
            menu.addMenu(self.createNewItemMenu())

            if item:
                editMenu = studioqt.Menu(menu)
                editMenu.setTitle("Edit")
                menu.addMenu(editMenu)

                item.contextEditMenu(editMenu)

                if self.trashEnabled():
                    editMenu.addSeparator()

                    callback = partial(self.showMoveItemsToTrashDialog, items)

                    action = QtWidgets.QAction("Move to Trash", editMenu)
                    action.setEnabled(not self.isTrashSelected())
                    action.triggered.connect(callback)
                    editMenu.addAction(action)

        menu.addSeparator()

        sortByMenu = self.SORTBY_MENU_CLASS("Sort By", menu, self.library())
        menu.addMenu(sortByMenu)

        groupByMenu = self.GROUPBY_MENU_CLASS("Group By", menu, self.library())
        menu.addMenu(groupByMenu)

        menu.addSeparator()
        menu.addMenu(self.createSettingsMenu())

        return menu

    def saveCustomOrder(self):
        """
        Convenience method for saving the custom order.

        :rtype:  None
        """
        self.library().saveItemData(self.library()._items, emitDataChanged=True)

    # -------------------------------------------------------------------
    # Support for moving items with drag and drop
    # -------------------------------------------------------------------

    def isCustomOrderEnabled(self):
        """
        Return True if sorting by "Custom Order" is enabled.

        :rtype: bool 
        """
        return 'Custom Order' in str(self.library().sortBy())

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
        
        :rtype: studiolibrary.widgets.MessageBox
        """
        text = 'Would you like to copy or move the selected item/s?'

        dialog = studiolibrary.widgets.createMessageBox(self, "Move or Copy items?", text)
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
            if os.path.dirname(item.path()) == dst:
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
            self.library().blockSignals(True)

            for item in items:

                path = dst + "/" + os.path.basename(item.path())

                if force:
                    path = studiolibrary.generateUniquePath(path)

                if copy:
                    item.copy(path)
                else:
                    item.rename(path)

                movedItems.append(item)

        except Exception as error:
            self.showExceptionDialog("Move Error", error)
            raise
        finally:
            self.library().blockSignals(False)

            self.refresh()
            self.selectItems(movedItems)
            self.scrollToSelectedItem()

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
        return self._sidebarWidgetVisible

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

        self.updateMenuBar()

    def setFoldersWidgetVisible(self, value):
        """
        If the value is True then show the FoldersWidget, otherwise hide.
        
        :type value: bool
        """
        value = bool(value)
        self._sidebarWidgetVisible = value

        if value:
            self._sidebarFrame.show()
        else:
            self._sidebarFrame.hide()

        self.updateMenuBar()

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

        # Force the preview pane to expand when creating a new item.
        fsize, rsize, psize = self._splitter.sizes()
        if psize < 150:
            self.setSizes((fsize, rsize, 180))

        self.setPreviewWidget(widget)

    def clearPreviewWidget(self):
        """
        Set the default preview widget.
        """
        self._previewWidget = None
        widget = studiolibrary.widgets.PlaceholderWidget()
        self.setPreviewWidget(widget)

    def updatePreviewWidget(self):
        """Update the current preview widget."""
        self.setPreviewWidgetFromItem(self._currentItem, force=True)

    def setPreviewWidgetFromItem(self, item, force=False):
        """
        :type item: studiolibrary.LibraryItem
        :rtype: None
        """
        if not force and self._currentItem == item:
            logger.debug("The current item preview widget is already set.")
            return

        self._currentItem = item

        if item:
            self.closePreviewWidget()
            try:
                item.showPreviewWidget(self)
            except Exception as error:
                self.showErrorMessage(error)
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
        settings['kwargs'] = self._kwargs
        settings['geometry'] = self.geometrySettings()
        settings['paneSizes'] = self._splitter.sizes()

        if self.theme():
            settings['theme'] = self.theme().settings()

        settings["library"] = self.library().settings()
        settings["trashFolderVisible"] = self.isTrashFolderVisible()
        settings["sidebarWidgetVisible"] = self.isFoldersWidgetVisible()
        settings["previewWidgetVisible"] = self.isPreviewWidgetVisible()
        settings["menuBarWidgetVisible"] = self.isMenuBarWidgetVisible()
        settings["statusBarWidgetVisible"] = self.isStatusBarWidgetVisible()

        settings['itemsWidget'] = self.itemsWidget().settings()
        settings['searchWidget'] = self.searchWidget().settings()
        settings['sidebarWidget'] = self.sidebarWidget().settings()
        settings["recursiveSearchEnabled"] = self.isRecursiveSearchEnabled()
        settings["checkForUpdateEnabled"] = self.isCheckForUpdateEnabled()

        settings['filterByMenu'] = self._filterByMenu.settings()

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

            value = settings.get("sidebarWidgetVisible")
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

            value = settings.get("checkForUpdateEnabled") or studiolibrary.config.get("checkForUpdateEnabled")
            if value is not None:
                self.setCheckForUpdateEnabled(value)

            value = settings.get('filterByMenu')
            if value is not None:
                self._filterByMenu.setSettings(value)

        finally:
            self.reloadStyleSheet()
            self.setRefreshEnabled(isRefreshEnabled)
            self.refresh()

        value = settings.get('library')
        if value is not None:
            self.library().setSettings(value)

        value = settings.get('trashFolderVisible')
        if value is not None:
            self.setTrashFolderVisible(value)

        value = settings.get('sidebarWidget', {})
        self.sidebarWidget().setSettings(value)

        value = settings.get('itemsWidget', {})
        self.itemsWidget().setSettings(value)

        self.itemsWidget().setToastEnabled(True)

        self.updateMenuBar()

    def updateSettings(self, settings):
        """
        Save the given path to the settings on disc.

        :type settings: dict
        :rtype: None 
        """
        data = self.readSettings()
        data.update(settings)
        self.saveSettings(data)

    def openTempPath(self):
        """Launch the system explorer to the temp directory."""
        path = studiolibrary.tempPath()
        studiolibrary.showInFolder(path)

    def openSettings(self):
        """Launch the system explorer to the open directory."""
        path = studiolibrary.settingsPath()
        studiolibrary.showInFolder(path)

    def saveSettings(self, data=None):
        """
        Save the settings to the settings path set in the config.

        :type data: dict or None
        :rtype: None
        """
        settings = studiolibrary.readSettings()

        settings.setdefault(self.name(), {})
        settings[self.name()].update(data or self.settings())

        studiolibrary.saveSettings(settings)

        self.showToastMessage("Saved")

    @studioqt.showWaitCursor
    def loadSettings(self):
        """
        Load the user settings from disc.

        :rtype: None
        """
        self.reloadStyleSheet()
        settings = self.readSettings()
        self.setSettings(settings)

    def readSettings(self):
        """
        Get the user settings from disc.

        :rtype: dict
        """
        key = self.name()
        data = studiolibrary.readSettings()
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

        desktop = QtWidgets.QApplication.desktop()

        pos = desktop.cursor().pos()
        screen = desktop.screenNumber(pos)
        centerPoint = desktop.screenGeometry(screen).center()

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

    def show(self, **kwargs):
        """
        Overriding this method to always raise_ the widget on show.

        Developers can use the kwargs to set platform dependent show options used in subclasses.

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
        if not self.DPI_ENABLED:
            return 1.0

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
        self.sidebarWidget().setDpi(dpi)
        self.statusWidget().setFixedHeight(20 * dpi)

        self._splitter.setHandleWidth(2 * dpi)

        self.showToastMessage("DPI: {0}".format(int(dpi * 100)))

        self.reloadStyleSheet()

    def iconColor(self):
        """
        Return the icon color.

        :rtype: studioqt.Color
        """
        return self.ICON_COLOR

    def setThemeSettings(self, settings):
        """
        Set the theme from the given settings.

        :type settings: dict
        :rtype: None
        """
        theme = studiolibrary.widgets.Theme()
        theme.setSettings(settings)
        self.setTheme(theme)

    def setTheme(self, theme):
        """
        Set the theme.

        :type theme: studioqt.Theme
        :rtype: None
        """
        self._theme = theme
        self._theme.updated.connect(self.reloadStyleSheet)
        self.reloadStyleSheet()

    def theme(self):
        """
        Return the current theme.

        :rtype: studioqt.Theme
        """
        if not self._theme:
            self._theme = studiolibrary.widgets.Theme()

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
        self.itemsWidget().setItemBackgroundColor(color)

        color = studioqt.Color.fromString(options["BACKGROUND_COLOR"])
        self.itemsWidget().setBackgroundColor(color)

        color = studioqt.Color.fromString(
            options["ITEM_BACKGROUND_HOVER_COLOR"])
        self.itemsWidget().setBackgroundHoverColor(color)

        color = studioqt.Color.fromString(
            options["ITEM_BACKGROUND_SELECTED_COLOR"])
        self.itemsWidget().setBackgroundSelectedColor(color)

        self.setStyleSheet(styleSheet)

        # Reloading the style sheets is needed for OSX
        self.itemsWidget().setStyleSheet(self.itemsWidget().styleSheet())
        self.searchWidget().setStyleSheet(self.searchWidget().styleSheet())
        self.menuBarWidget().setStyleSheet(self.menuBarWidget().styleSheet())
        self.sidebarWidget().setStyleSheet(self.sidebarWidget().styleSheet())
        self.previewWidget().setStyleSheet(self.previewWidget().styleSheet())

        if self._settingsWidget:
            self._settingsWidget.setStyleSheet(self._settingsWidget.styleSheet())

        self.searchWidget().update()
        self.menuBarWidget().update()
        self.sidebarWidget().update()

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

        if visible:
            query = {
                'name': 'trash_query',
                'filters': []
            }
        else:
            query = {
                'name': 'trash_query',
                'filters': [('path', 'not_contains', 'Trash')]
            }

        self.library().addGlobalQuery(query)
        self.updateSidebar()
        self.library().search()

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

    def showMoveItemsToTrashDialog(self, items=None):
        """
        Show the "Move to trash" dialog for the selected items.

        :type items: list[studiolibrary.LibraryItem] or None
        :rtype: None
        """
        items = items or self.selectedItems()

        if items:
            title = "Move to trash?"
            text = "Are you sure you want to move the selected" \
                   "item/s to the trash?"

            buttons = [
                ("Move to Trash", QtWidgets.QDialogButtonBox.AcceptRole),
                QtWidgets.QDialogButtonBox.Cancel
            ]

            result = studiolibrary.widgets.MessageBox.question(self, title, text, buttons=buttons)

            if result != QtWidgets.QDialogButtonBox.Cancel:
                self.moveItemsToTrash(items)

    # -----------------------------------------------------------------------
    # Support for message boxes
    # -----------------------------------------------------------------------

    def showToastMessage(self, text, duration=1000):
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

    def showRefreshMessage(self):
        """Show how long the current refresh took."""
        itemCount = len(self.library().results())
        elapsedTime = self.library().searchTime()

        plural = ""
        if itemCount > 1:
            plural = "s"

        msg = "Found {0} item{1} in {2:.3f} seconds."
        msg = msg.format(itemCount, plural, elapsedTime)
        self.statusWidget().showInfoMessage(msg)

        logger.debug(msg)

    def showInfoDialog(self, title, text):
        """
        A convenience method for showing an information dialog to the user.

        :type title: str
        :type text: str
        :rtype: QMessageBox.StandardButton
        """
        buttons = QtWidgets.QDialogButtonBox.Ok

        return studiolibrary.widgets.MessageBox.question(self, title, text, buttons=buttons)

    def showErrorDialog(self, title, text):
        """
        A convenience method for showing an error dialog to the user.

        :type title: str
        :type text: str
        :rtype: QMessageBox.StandardButton
        """
        self.showErrorMessage(text)
        return studiolibrary.widgets.MessageBox.critical(self, title, text)

    def showExceptionDialog(self, title, error):
        """
        A convenience method for showing an error dialog to the user.

        :type title: str
        :type error: Exception
        :rtype: QMessageBox.StandardButton
        """
        logger.exception(error)
        self.showErrorDialog(title, error)

    def showQuestionDialog(self, title, text, buttons=None):
        """
        A convenience method for showing a question dialog to the user.

        :type title: str
        :type text: str
        :type buttons: list[QMessageBox.StandardButton] 
        :rtype: QMessageBox.StandardButton
        """
        buttons = buttons or [
            QtWidgets.QDialogButtonBox.Yes,
            QtWidgets.QDialogButtonBox.No,
            QtWidgets.QDialogButtonBox.Cancel
        ]

        return studiolibrary.widgets.MessageBox.question(self, title, text, buttons=buttons)

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

        self.sidebarWidget().setLocked(value)
        self.itemsWidget().setLocked(value)

        self.updateMenuBar()
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

        This will lock all folders unless the current user is a superuser.

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

    def updateMenuBar(self):

        # Update view icon
        action = self.menuBarWidget().findAction("New Item")

        if self.isLocked():
            icon = studiolibrary.resource.icon("lock")
            action.setEnabled(False)
        else:
            icon = studiolibrary.resource.icon("plus-large")
            action.setEnabled(True)

        action.setIcon(icon)

        # Update view icon
        action = self.menuBarWidget().findAction("View")

        if not self.isCompactView():
            icon = studiolibrary.resource.icon("eye")
        else:
            icon = studiolibrary.resource.icon("eye-slash")

        action.setIcon(icon)

        # Update filters icon
        action = self.menuBarWidget().findAction("Filters")

        if self._filterByMenu.isActive():
            icon = studiolibrary.resource.icon("filter")
            action._badgeColor = self.ICON_BADGE_COLOR
            action._badgeEnabled = True
        else:
            icon = studiolibrary.resource.icon("filter")

        action.setIcon(icon)

        self.menuBarWidget().updateIconColor()

    def isRecursiveSearchEnabled(self):
        """
        Return True if recursive search is enabled.

        :rtype: bool
        """
        return self.sidebarWidget().isRecursive()

    def setRecursiveSearchEnabled(self, value):
        """
        Enable recursive search for searching sub folders.

        :type value: int

        :rtype: None
        """
        self.sidebarWidget().setRecursive(value)

    def openHelpUrl(self):
        """Open the help URL in a web browse."""
        webbrowser.open(self._updateInfo.get("helpUrl", "https://www.studiolibrary.com"))

    def openReportUrl(self):
        """Open the report URL in a web browse."""
        webbrowser.open(self._updateInfo.get("reportUrl", "https://www.studiolibrary.com"))

    def openReleasesUrl(self):
        """Open the releases URL in a web browser."""
        webbrowser.open(self._updateInfo.get("releasesUrl", "https://www.studiolibrary.com"))

    def setDebugMode(self, value):
        """
        :type value: bool
        """
        self._isDebug = value
        studiolibrary.setDebugMode(value)

    def setCheckForUpdateEnabled(self, value):
        self._checkForUpdateEnabled = value
        self.checkForUpdate()

    def isCheckForUpdateEnabled(self):
        return self._checkForUpdateEnabled

    def isDebug(self):
        """
        :rtype: bool
        """
        return self._isDebug
