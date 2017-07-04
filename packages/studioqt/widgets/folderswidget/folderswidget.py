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

import folderitem


__all__ = ["FoldersWidget"]

logger = logging.getLogger(__name__)


class FoldersWidget(QtWidgets.QTreeView):

    itemDropped = QtCore.Signal(object)
    itemRenamed = QtCore.Signal(str, str)
    itemSelectionChanged = QtCore.Signal()

    def __init__(self, parent=None):
        """
        :type parent: QtWidgets.QWidget
        """
        QtWidgets.QTreeView.__init__(self, parent)

        self._filter = []
        self._folders = {}
        self._isLocked = False
        self._blockSignals = False
        self._enableFolderSettings = True

        self._sourceModel = FileSystemModel(self)

        self.setDpi(1)

        proxyModel = SortFilterProxyModel(self)
        proxyModel.setSourceModel(self._sourceModel)
        proxyModel.sort(0)

        self.setAcceptDrops(True)
        self.setModel(proxyModel)
        self.setHeaderHidden(True)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        signal = "selectionChanged(const QItemSelection&,const QItemSelection&)"

        self.connect(
            self.selectionModel(),
            QtCore.SIGNAL(signal),
            self._selectionChanged,
        )

    def enableFolderSettings(self, value):
        self._enableFolderSettings = value

    def folders(self):
        return self._folders.values()

    def createEditMenu(self, parent=None):
        """
        Return the edit menu for deleting, renaming folders.

        :rtype: QtWidgets.QMenu
        """
        selectedFolders = self.selectedFolders()

        menu = QtWidgets.QMenu(parent)
        menu.setTitle("Edit")

        if len(selectedFolders) == 1:
            action = QtWidgets.QAction("Rename", menu)
            action.triggered.connect(self.showRenameDialog)
            menu.addAction(action)

            action = QtWidgets.QAction("Show in folder", menu)
            action.triggered.connect(self.showInFolder)
            menu.addAction(action)

        separator = QtWidgets.QAction("Separator2", menu)
        separator.setSeparator(True)
        menu.addAction(separator)

        action = QtWidgets.QAction("Show icon", menu)
        action.setCheckable(True)
        action.setChecked(self.isFolderIconVisible())
        action.triggered[bool].connect(self.setFolderIconVisible)
        menu.addAction(action)

        action = QtWidgets.QAction("Show bold", menu)
        action.setCheckable(True)
        action.setChecked(self.isFolderBold())
        action.triggered[bool].connect(self.setFolderBold)

        menu.addAction(action)
        separator = QtWidgets.QAction("Separator2", menu)
        separator.setSeparator(True)
        menu.addAction(separator)

        action = QtWidgets.QAction("Change icon", menu)
        action.triggered.connect(self.browseFolderIcon)
        menu.addAction(action)

        action = QtWidgets.QAction("Change color", menu)
        action.triggered.connect(self.browseFolderColor)
        menu.addAction(action)

        separator = QtWidgets.QAction("Separator3", menu)
        separator.setSeparator(True)
        menu.addAction(separator)

        action = QtWidgets.QAction("Reset settings", menu)
        action.triggered.connect(self.resetFolderSettings)
        menu.addAction(action)

        return menu

    def setDpi(self, dpi):
        size = 24 * dpi
        self.setIndentation(15 * dpi)
        self.setMinimumWidth(35 * dpi)
        self.setIconSize(QtCore.QSize(size, size))
        self.setStyleSheet("height: {size}".format(size=size))

    def showInFolder(self):
        folders = self.selectedFolders()
        for folder in folders:
            folder.showInFolder()

    def reload(self):
        """
        Force the root path and state to be reloaded.

        :rtype: None
        """
        path = self.rootPath()
        settings = self.settings()
        ignoreFilter = self.ignoreFilter()

        self.setRootPath("")
        self.setRootPath(path)
        self.setSettings(settings)
        self.setIgnoreFilter(ignoreFilter)

    def setLocked(self, value):
        """
        :rtype: bool
        """
        self._isLocked = value

    def isLocked(self):
        """
        :rtype: bool
        """
        return self._isLocked

    def folderFromIndex(self, index):
        """
        :type index: QtCore.QModelIndex
        :rtype: Folder
        """
        path = self.pathFromIndex(index)
        return self.folderFromPath(path)

    def folderFromPath(self, path):
        """
        :type path: str
        :rtype: Folder
        """
        folders = self._folders
        if path not in folders:
            folders[path] = folderitem.FolderItem(path, self)
        return folders[path]

    def indexFromFolder(self, folder):
        """
        :type path: FolderItem
        :rtype: QtCore.QModelIndex
        """
        return self.indexFromPath(folder.path())

    def indexFromPath(self, path):
        """
        :type path: str
        :rtype: QtCore.QModelIndex
        """
        index = self.model().sourceModel().index(path)
        return self.model().mapFromSource(index)

    def pathFromIndex(self, index):
        """
        :type index: QtCore.QModelIndex
        :rtype: str
        """
        index = self.model().mapToSource(index)
        return self.model().sourceModel().filePath(index)

    def _selectionChanged(self, selected=None, deselected=None):
        """
        Triggered when the folder item changes selection.

        :type selected: list[Folder] or None
        :type deselected: list[Folder] or None
        :rtype: None
        """
        if not self._blockSignals:
            self.itemSelectionChanged.emit()

    def saveSettings(self, path):
        data = self.settings()
        studioqt.saveJson(path, data)

    def loadSettings(self, path):
        if os.path.exists(path):
            data = studioqt.readJson(path)
            self.setSettings(data)

    def folderSettings(self):
        settings = {}

        for folder in self.folders():
            if folder.settings() and folder.exists():
                settings[folder.path()] = folder.settings()

        return settings

    def setFolderSettings(self, settings):
        for path in settings:
            folder = self.folderFromPath(path)
            folder.setSettings(settings[path])

    def settings(self):
        """
        :rtype: dict
        """
        settings = {
            "selectedPaths": self.selectedPaths(),
            # Saving the state of expanded folders is not supported yet!
            # "expandedPaths": self.expandedPaths(),
            "folderSettings": self.folderSettings(),
        }

        if self._enableFolderSettings:
            settings["folderSettings"] = self.folderSettings()

        return settings

    def setSettings(self, settings):
        """
        :rtype state: list
        """
        # Saving the state of expanded folders is not supported yet!
        # expandedPaths = settings.get("expandedPaths", [])
        # self.expandPaths(expandedPaths)

        selectedPaths = settings.get("selectedPaths", [])
        self.selectPaths(selectedPaths)

        if self._enableFolderSettings:
            folderSettings = settings.get("folderSettings", {})
            self.setFolderSettings(folderSettings)

    def setFolderOrderIndex(self, path, orderIndex):
        """
        :type path:
        :type: position:
        :rtype: None
        """
        folder = self.folderFromPath(path)
        folder.setOrderIndex(orderIndex)

    def setIgnoreFilter(self, ignoreFilter):
        """
        :type ignoreFilter: list[str]
        """
        self.model().sourceModel().setIgnoreFilter(ignoreFilter)

    def ignoreFilter(self):
        return self.model().sourceModel().ignoreFilter()

    def setRootPath(self, path):
        """
        :type path: str
        """
        self.model().sourceModel().setRootPath(path)
        index = self.indexFromPath(path)
        self.setRootIndex(index)

    def rootPath(self):
        """
        :rtype: str
        """
        return self.model().sourceModel().rootPath()

    def selectFolders(self, folders):
        """
        :type folders: list[Folder]
        :rtype: None
        """
        paths = [folder.path() for folder in folders]
        self.selectPaths(paths)

    def selectPaths(self, paths):
        """
        :type paths: list[str]
        :rtype: None
        """
        if not paths:
            return

        self._blockSignals = True
        for path in paths[:-1]:
            self.selectPath(path)
        self._blockSignals = False
        self.selectPath(paths[-1])

    def selectFolder(self, folder, mode=QtCore.QItemSelectionModel.Select):
        """
        :type folder: Folder
        :rtype: None
        """
        self.selectPath(folder.path(), mode=mode)

    def expandedPaths(self):
        """
        Return the expanded folder paths.

        :rtype: list[str]
        """
        return [folder.path() for folder in self.expandedFolders()]

    def expandedFolders(self):
        """
        Return the expanded folder paths.

        :rtype: list[studioqt.FolderItem]
        """
        folders = []

        for folder in self.folders():
            index = self.indexFromPath(folder.path())
            if self.isExpanded(index):
                folders.append(folder)

        return folders

    def expandPaths(self, paths):
        self._blockSignals = True
        for path in paths:
            self.expandParentsFromPath(path)
        self._blockSignals = False

    def expandParentsFromPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        for i in range(0, 4):
            path = os.path.dirname(path)
            index = self.indexFromPath(path)
            if index and not self.isExpanded(index):
                self.setExpanded(index, True)

    def selectPath(self, path, mode=QtCore.QItemSelectionModel.Select):
        """
        Select the given folders.

        :type path: str
        :rtype: Nones
        """
        isSelected = path in self.selectedPaths()

        if not isSelected:
            self.expandParentsFromPath(path)
            index = self.indexFromPath(path)
            self.selectionModel().select(index, mode)

    def showCreateDialog(self, parent=None):
        """
        :rtype: None
        """
        name, accepted = QtWidgets.QInputDialog.getText(
            parent,
            "Create Folder",
            "Folder name",
            QtWidgets.QLineEdit.Normal
        )
        name = name.strip()

        if accepted and name:
            folders = self.selectedFolders()

            if len(folders) == 1:
                folder = folders[-1]
                path = folder.path() + "/" + name
            else:
                path = self.rootPath() + "/" + name

            if not os.path.exists(path):
                os.makedirs(path)

            folder = self.folderFromPath(path)

            self.reload()
            self.clearSelection()
            self.selectFolder(folder)

    def showRenameDialog(self, parent=None):
        """
        :rtype: None
        """
        parent = parent or self.parent()

        folder = self.selectedFolder()
        if folder:
            name, accept = QtWidgets.QInputDialog.getText(
                parent,
                "Rename Folder",
                "New Name",
                QtWidgets.QLineEdit.Normal,
                folder.name()
            )

            if accept:
                self.renameFolder(folder, unicode(name))

    def renameFolder(self, folder, name):
        """
        Rename the folder item to the give name.

        :type folder: Folder
        :type name: str
        """
        self.blockSignals(True)
        self.clearSelection()

        oldPath = folder.path()
        folder.rename(unicode(name))
        newPath = folder.path()

        del self._folders[oldPath]
        self._folders[newPath] = folder

        self.reload()
        self.blockSignals(False)

        self.selectPath(newPath)

        self.itemRenamed.emit(oldPath, newPath)

    def selectedFolder(self):
        """
        :rtype: None | Folder
        """
        folders = self.selectedFolders()
        if folders:
            return folders[-1]
        return None

    def selectedPaths(self):
        return [folder.path() for folder in self.selectedFolders()]

    def selectedFolders(self):
        """
        :rtype: list[Folder]
        """

        folders = []

        for index in self.selectionModel().selectedIndexes():
            path = self.pathFromIndex(index)
            folder = self.folderFromPath(path)
            folders.append(folder)

        return folders

    def dragEnterEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        event.accept()

    def clearSelection(self):
        """
        :rtype: None
        """
        self.selectionModel().clearSelection()

    def dragMoveEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        mimeData = event.mimeData()

        if mimeData.hasUrls() and not self.isLocked():
            event.accept()
        else:
            event.ignore()

        folder = self.folderAt(event.pos())
        if folder:
            self.selectFolder(folder, QtCore.QItemSelectionModel.ClearAndSelect)

    def dropEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        if self.isLocked():
            logger.debug("Folder is locked! Cannot accept drop!")
            return

        self.itemDropped.emit(event)

    def mouseMoveEvent(self, event):

        if studioqt.isControlModifier():
            return

        folder = self.folderAt(event.pos())
        selectedFolders = self.selectedFolders()
        isSelected = folder in selectedFolders

        if folder:
            self.clearSelection()
            self.selectFolder(folder)

    def mousePressEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        folder = self.folderAt(event.pos())
        selectedFolders = self.selectedFolders()
        isSelected = folder in selectedFolders

        if event.button() == QtCore.Qt.RightButton:
            QtWidgets.QTreeView.mousePressEvent(self, event)
        else:
            QtWidgets.QTreeView.mousePressEvent(self, event)

        if not folder:
            self.clearSelection()

        elif event.button() == QtCore.Qt.LeftButton and studioqt.isControlModifier():

            if folder and isSelected:
                self.clearSelection()
                selectedFolders.remove(folder)
                self.selectFolders(selectedFolders)

            if folder and not isSelected:
                selectedFolders.append(folder)
                self.selectFolders(selectedFolders)

        self.repaint()

    def mouseReleaseEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        if event.button() == QtCore.Qt.MidButton:
            event.ignore()
        else:
            QtWidgets.QTreeView.mouseReleaseEvent(self, event)

    def showContextMenu(self):
        """
        :rtype: None
        """
        menu = QtWidgets.QMenu(self)

        if self.isLocked():
            self.lockedMenu(menu)
        else:
            self.createContextMenu(menu)

        action = menu.exec_(QtGui.QCursor.pos())
        menu.close()

        return action

    def lockedMenu(self, menu):
        """
        :type menu: QtWidgets.QMenu
        :rtype: None
        """
        action = QtWidgets.QAction("Locked", menu)
        action.setEnabled(False)
        menu.addAction(action)

    def createContextMenu(self, menu):
        """
        :type menu: QtWidgets.QMenu
        :rtype: None
        """
        folders = self.selectedFolders()

        if not folders:
            action = menu.addAction("No folder selected")
            action.setEnabled(False)
            return

        editMenu = self.createEditMenu(menu)
        menu.addMenu(editMenu)

        return menu

    def folderAt(self, pos):
        """
        :type pos: QtGui.QPoint
        :rtype: None or Folder
        """
        index = self.indexAt(pos)
        if not index.isValid():
            return

        path = self.pathFromIndex(index)
        folder = self.folderFromPath(path)
        return folder

    def setFolderIconVisible(self, value):
        """
        :type value: Bool
        """
        for folder in self.selectedFolders():
            folder.setIconVisible(value)

    def isFolderIconVisible(self):
        """
        :rtype: bool
        """
        for folder in self.selectedFolders():
            if not folder.isIconVisible():
                return False
        return True

    def setFolderBold(self, value):
        """
        :type value: Bool
        """
        for folder in self.selectedFolders():
            folder.setBold(value)

    def isFolderBold(self):
        """
        :rtype: bool
        """
        for folder in self.selectedFolders():
            if not folder.isBold():
                return False
        return True

    def setFolderColor(self, color):
        """
        :type color:
        :return:
        """
        for folder in self.selectedFolders():
            folder.setColor(color)

    def resetFolderSettings(self):
        """
        :rtype:
        """
        for folder in self.selectedFolders():
            folder.reset()

    def browseFolderIcon(self):
        """
        :rtype: None
        """
        path, ext = QtWidgets.QFileDialog.getOpenFileName(
            self.parent(),
            "Select an image",
            "",
            "*.png"
        )

        path = unicode(path).replace("\\", "/")
        if path:
            for folder in self.selectedFolders():
                folder.setIconPath(path)

    def browseFolderColor(self):
        """
        :rtype: None
        """
        dialog = QtWidgets.QColorDialog(self.parent())
        dialog.currentColorChanged.connect(self.setFolderColor)

        # PySide2 doesn't support d.open(), so we need to pass a blank slot.
        dialog.open(self, QtCore.SLOT("blankSlot()"))

        if dialog.exec_():
            self.setFolderColor(dialog.selectedColor())

    @QtCore.Slot()
    def blankSlot(self):
        """
        Blank slot to fix an issue with PySide2.QColorDialog.open()
        """
        pass


class FileSystemModel(QtWidgets.QFileSystemModel):

    def __init__(self, foldersWidget):
        """
        :type foldersWidget: FileSystemWidget
        """
        QtWidgets.QFileSystemModel.__init__(self, foldersWidget)

        self._ignoreFilter = []
        self._foldersWidget = foldersWidget
        self.setFilter(QtCore.QDir.AllDirs)

    def foldersWidget(self):
        """
        :rtype: FileSystemWidget
        """
        return self._foldersWidget

    def columnCount(self, *args):
        """
        :type args: list
        :rtype: int
        """
        return 1

    def ignoreFilter(self):
        """
        :rtype: list or None
        """
        return self._ignoreFilter

    def setIgnoreFilter(self, ignoreFilter):
        """
        :type ignoreFilter: list or None
        """
        self._ignoreFilter = ignoreFilter or []

    def isPathValid(self, path):
        """
        :type path: str
        :rtype: bool
        """
        if os.path.isdir(path):
            path = path.lower()
            valid = [item for item in self._ignoreFilter if path.endswith(item)]
            if not valid:
                return True
        return False

    def hasChildren(self, index):
        """
        :type index: QtCore.QModelIndex
        :rtype: bool
        """
        path = self.filePath(index)
        if os.path.isdir(path):
            for name in os.listdir(path):
                if self.isPathValid(path + "/" + name):
                    return True
        return False

    def data(self, index, role):
        """
        :type index: QtCore.QModelIndex
        :type role:
        :rtype: QtWidgets.QVariant
        """
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                dirname = self.filePath(index)
                folder = self.foldersWidget().folderFromPath(dirname)
                pixmap = QtGui.QIcon(folder.pixmap())

                if pixmap:
                    pixmap = pixmap.pixmap(self.foldersWidget().iconSize(),
                                  transformMode=QtCore.Qt.SmoothTransformation)

                    return QtGui.QIcon(pixmap)
                else:
                    return None

        if role == QtCore.Qt.FontRole:
            if index.column() == 0:
                dirname = self.filePath(index)
                folder = self.foldersWidget().folderFromPath(dirname)
                if folder.exists():
                    if folder.isBold():
                        font = QtGui.QFont()
                        font.setBold(True)
                        return font

        if role == QtCore.Qt.DisplayRole:
            text = QtWidgets.QFileSystemModel.data(self, index, role)
            return text

        return QtWidgets.QFileSystemModel.data(self, index, role)


class SortFilterProxyModel(QtCore.QSortFilterProxyModel):

    def __init__(self, folderWidget):
        """
        :type folderWidget: FileSystemWidget
        """
        self._folderWidget = folderWidget
        QtCore.QSortFilterProxyModel.__init__(self, folderWidget)

    def folderWidget(self):
        """
        :rtype: FileSystemWidget
        """
        return self._folderWidget

    def lessThan(self, leftIndex, rightIndex):
        """
        :type leftIndex: QtWidgets.QModelIndex
        :type rightIndex: QtWidgets.QModelIndex
        :rtype: bool
        """
        path1 = self.sourceModel().filePath(leftIndex)
        path2 = self.sourceModel().filePath(rightIndex)

        folder1 = self.folderWidget().folderFromPath(path1)
        folder2 = self.folderWidget().folderFromPath(path2)

        orderIndex1 = folder1.orderIndex()
        orderIndex2 = folder2.orderIndex()

        if orderIndex1 >= 0 and orderIndex2 >= 0:

            if orderIndex1 < orderIndex2:
                return True
            else:
                return False

        elif orderIndex1 >= 0:
            return True

        else:
            return False

    def filterAcceptsRow(self, sourceRow, sourceParent):
        """
        :type sourceRow:
        :type sourceParent:
        :rtype: bool
        """
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        path = self.sourceModel().filePath(index)
        return self.sourceModel().isPathValid(path)


def example():
    path = r'C:/Users/Hovel/Dropbox/libraries/animation'
    trashPath = path + r'/Trash'

    ignoreFilter = ['.', '.studiolibrary', '.pose', '.anim', '.set']

    with studioqt.app():

        def itemSelectionChanged():
            print w.selectedFolders()
            print w.settings()

        w = FoldersWidget()
        w.enableFolderSettings(True)

        w.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        w.customContextMenuRequested.connect(w.showContextMenu)

        theme = studioqt.Theme()
        w.setStyleSheet(theme.styleSheet())

        w.setRootPath(path)
        w.reload()

        w.show()
        w.setIgnoreFilter(ignoreFilter)
        w.setFolderOrderIndex(trashPath, 0)

        w.itemSelectionChanged.connect(itemSelectionChanged)

    return w


if __name__ == "__main__":
    w = example()
