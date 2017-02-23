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
import shutil
import logging
import traceback

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary
import studiolibraryitems

try:
    import mutils
    import mutils.gui
    import maya.cmds
except ImportError, e:
    print e


__all__ = [
    "TransferItem",
    "CreateWidget",
    "PreviewWidget",

]

logger = logging.getLogger(__name__)


class TransferItemError(Exception):
    """Base class for exceptions in this module."""
    pass


class ValidateError(TransferItemError):
    """"""
    pass


class NamespaceOption:
    FromFile = "pose"
    FromCustom = "custom"
    FromSelection = "selection"


class TransferItem(studiolibrary.LibraryItem):

    """Base class for anim, pose, mirror and sets transfer items."""

    def __init__(self, *args, **kwargs):
        """
        Initialise a new instance for the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        studiolibrary.LibraryItem.__init__(self, *args, **kwargs)

        self._namespaces = []
        self._namespaceOption = NamespaceOption.FromSelection

        self._transferClass = None
        self._transferObject = None
        self._transferBasename = None

    def setTransferClass(self, classname):
        """
        Set the transfer class used to read and write the data.

        :type classname: mutils.TransferObject
        """
        self._transferClass = classname

    def transferClass(self):
        """
        Return the transfer class used to read and write the data.

        :rtype: mutils.TransferObject
        """
        return self._transferClass

    def transferPath(self):
        """
        Return the disc location to transfer path.

        :rtype: str
        """
        if self.transferBasename():
            return "/".join([self.path(), self.transferBasename()])
        else:
            return self.path()

    def transferBasename(self):
        """
        Return the filename of the transfer path.

        :rtype: str
        """
        return self._transferBasename

    def setTransferBasename(self, transferBasename):
        """
        Set the filename of the transfer path.

        :type: str
        """
        self._transferBasename = transferBasename

    def transferObject(self):
        """
        Return the transfer object used to read and write the data.

        :rtype: mutils.TransferObject
        """
        if not self._transferObject:
            path = self.transferPath()
            if os.path.exists(path):
                self._transferObject = self.transferClass().fromPath(path)
        return self._transferObject

    def thumbnailPath(self):
        """
        Return the thumbnail location on disc to be displayed for the item.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: QtWidgets.QWidget
        """
        iconPath = self.path() + "/thumbnail.jpg"

        if not os.path.exists(iconPath):
            iconPath = studiolibraryitems.resource().get("icons", "thumbnail.png")

        return iconPath

    def settings(self):
        """
        Return a settings object for saving data to the users local disc.

        :rtype: studiolibrary.Settings
        """
        return self.localSettings()

    def owner(self):
        """
        Return the user who created this item.

        :rtype: str
        """
        owner = studiolibrary.LibraryItem.owner(self)
        transferObject = self.transferObject()

        if not owner and transferObject:
            owner = self.transferObject().metadata().get("user")

        return owner

    def ctime(self):
        """
        Return when the item was created.

        :rtype: str
        """
        path = self.path()
        ctime = ""

        if os.path.exists(path):
            ctime = studiolibrary.LibraryItem.ctime(self)

            if not ctime:
                ctime = int(os.path.getctime(path))

        return ctime

    def description(self):
        """
        Return the user description for this item.

        :rtype: str
        """
        description = studiolibrary.LibraryItem.description(self)
        transferObject = self.transferObject()

        if not description and transferObject:
            description = self.transferObject().metadata().get("description")

        return description

    def objectCount(self):
        """
        Return the number of controls this item contains.

        :rtype: int
        """
        if self.transferObject():
            return self.transferObject().count()
        else:
            return 0

    def contextMenu(self, menu, items=None):
        """
        This method is called when the user right clicks on this item.

        :type menu: QtWidgets.QMenu
        :type items: list[TransferItem]
        :rtype: None
        """
        import setsmenu

        action = setsmenu.selectContentAction(self, parent=menu)
        menu.addAction(action)
        menu.addSeparator()

        subMenu = self.createSelectionSetsMenu(menu, enableSelectContent=False)
        menu.addMenu(subMenu)
        menu.addSeparator()

    def showSelectionSetsMenu(self, **kwargs):
        """
        Show the selection sets menu for this item at the cursor position.

        :rtype: QtWidgets.QAction
        """
        menu = self.createSelectionSetsMenu(**kwargs)
        position = QtGui.QCursor().pos()
        action = menu.exec_(position)
        return action

    def createSelectionSetsMenu(self, parent=None, enableSelectContent=True):
        """
        Return a new instance of the selection sets menu.

        :type parent: QtWidgets.QWidget
        :type enableSelectContent: bool
        :rtype: QtWidgets.QMenu
        """
        import setsmenu

        namespaces = self.namespaces()

        menu = setsmenu.SetsMenu(
                item=self,
                parent=parent,
                namespaces=namespaces,
                enableSelectContent=enableSelectContent,
        )
        return menu

    def selectContent(self, namespaces=None, **kwargs):
        """
        Select the contents of this item in the Maya scene.

        :type namespaces: list[str]
        """
        namespaces = namespaces or self.namespaces()
        kwargs = kwargs or mutils.selectionModifiers()

        msg = "Select content: Item.selectContent(namespacea={0}, kwargs={1})"
        msg = msg.format(namespaces, kwargs)
        logger.debug(msg)

        try:
            self.transferObject().select(namespaces=namespaces, **kwargs)
        except Exception, msg:
            title = "Error while selecting content"
            studioqt.MessageBox.critical(None, title, str(msg))
            raise

    def mirrorTable(self):
        """
        Return the mirror table object for this item.

        :rtype: mutils.MirrorTable or None
        """
        mirrorTable = None
        path = self.mirrorTablePath()

        if path:
            mirrorTable = mutils.MirrorTable.fromPath(path)

        return mirrorTable

    def mirrorTablePath(self):
        """
        Return the mirror table path for this item.

        :rtype: str or None
        """
        path = None
        paths = self.mirrorTablePaths()

        if paths:
            path = paths[0]

        return path

    def mirrorTablePaths(self):
        """
        Return all mirror table paths for this item.

        :rtype: list[str]
        """
        paths = list(studiolibrary.findPaths(
                self.path(),
                match=lambda path: path.endswith(".mirror"),
                direction=studiolibrary.Direction.Up,
                depth=10,
            )
        )
        return paths

    def namespaces(self):
        """
        Return the namesapces for this item depending on the namespace option.

        :rtype: list[str]
        """
        namespaces = []
        namespaceOption = self.namespaceOption()

        # When creating a new item we can only get the namespaces from
        # selection because the file (transferObject) doesn't exist yet.
        if not self.transferObject():
            namespaces = self.namespaceFromSelection()

        # If the file (transferObject) exists then we can use the namespace
        # option to determined which namespaces to return.
        elif namespaceOption == NamespaceOption.FromFile:
            namespaces = self.namespaceFromFile()

        elif namespaceOption == NamespaceOption.FromCustom:
            namespaces = self.namespaceFromCustom()

        elif namespaceOption == NamespaceOption.FromSelection:
            namespaces = self.namespaceFromSelection()

        return namespaces

    def setNamespaceOption(self, namespaceOption):
        """
        Set the namespace option for this item.

        :type namespaceOption: NamespaceOption
        :rtype: None
        """
        self.settings().set("namespaceOption", namespaceOption)

    def namespaceOption(self):
        """
        Return the namespace option for this item.

        :rtype: NamespaceOption
        """
        namespaceOption = self.settings().get(
                "namespaceOption",
                NamespaceOption.FromSelection
        )
        return namespaceOption

    def namespaceFromCustom(self):
        """
        Return the namespace the user has set.

        :rtype: list[str]
        """
        return self.settings().get("namespaces", "")

    def setCustomNamespaces(self, namespaces):
        """
        Set the users custom namespace.

        :type namespaces: list[str]
        :rtype: None
        """
        self.settings().set("namespaces", namespaces)

    def namespaceFromFile(self):
        """
        Return the namespaces from the transfer data.

        :rtype: list[str]
        """
        return self.transferObject().namespaces()

    @staticmethod
    def namespaceFromSelection():
        """
        Return the current namespaces from the selected objects in Maya.

        :rtype: list[str]
        """
        return mutils.namespace.getFromSelection() or [""]

    def doubleClicked(self):
        """
        This method is called when the user double clicks the item.

        :rtype: None
        """
        self.load()

    def load(self, objects=None, namespaces=None, **kwargs):
        """
        Load the data from the transfer object.

        :type namespaces: list[str]
        :type objects: list[str]
        :rtype: None
        """
        logger.debug(u'Loading: {0}'.format(self.transferPath()))

        self.transferObject().load(objects=objects, namespaces=namespaces, **kwargs)

        logger.debug(u'Loading: {0}'.format(self.transferPath()))

    def save(self, objects, path=None, iconPath=None, **kwargs):
        """
        Save the data to the transfer path on disc.

        :type path: path
        :type objects: list
        :type iconPath: str
        :raise ValidateError:
        """
        logger.info(u'Saving: {0}'.format(path))

        contents = list()
        tempDir = mutils.TempDir("Transfer", clean=True)

        transferPath = tempDir.path() + "/" + self.transferBasename()
        t = self.transferClass().fromObjects(objects)
        t.save(transferPath, **kwargs)

        if iconPath:
            contents.append(iconPath)

        contents.append(transferPath)
        studiolibrary.LibraryItem.save(self, path=path, contents=contents)

        logger.info(u'Saved: {0}'.format(path))


class BaseWidget(QtWidgets.QWidget):

    """Base widget for creating and previewing transfer items."""

    stateChanged = QtCore.Signal(object)

    def __init__(self, item, parent=None):
        """
        Create a new widget for the given item.

        :type item: BaseItem
        :type parent: studiolibrary.LibraryWidget
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.setObjectName("studioLibraryItemWidget")

        studioqt.loadUi(self)

        self._item = None
        self._iconPath = ""
        self._scriptJob = None

        self.setItem(item)
        self.loadSettings()

        try:
            self.selectionChanged()
            self.enableScriptJob()
        except NameError, msg:
            logger.exception(msg)

        self.updateThumbnailSize()

    def resizeEvent(self, event):
        """
        Overriding to adjust the image size when the widget changes size.

        :type event: QtCore.QSizeEvent
        """
        self.updateThumbnailSize()

    def updateThumbnailSize(self):

        if hasattr(self.ui, "thumbnailButton"):
            width = self.width() - 10
            if width > 250:
                width = 250

            size = QtCore.QSize(width, width)
            self.ui.thumbnailButton.setIconSize(size)
            self.ui.thumbnailButton.setMaximumSize(size)
            self.ui.thumbnailFrame.setMaximumSize(size)

    def enableScriptJob(self):
        """
        :rtype: None
        """
        if not self._scriptJob:
            event = ['SelectionChanged', self.selectionChanged]
            self._scriptJob = mutils.ScriptJob(event=event)

    def setItem(self, item):
        """
        :type item: BaseItem
        """
        self._item = item

        if hasattr(self.ui, 'name'):
            self.ui.name.setText(item.name())

        if hasattr(self.ui, 'owner'):
            self.ui.owner.setText(item.owner())

        if hasattr(self.ui, 'comment'):
            if isinstance(self.ui.comment, QtWidgets.QLabel):
                self.ui.comment.setText(item.description())
            else:
                self.ui.comment.setPlainText(item.description())

        if hasattr(self.ui, "contains"):
            self.updateContains()

        ctime = item.ctime()
        if hasattr(self.ui, 'created') and ctime:
            self.ui.created.setText(studiolibrary.timeAgo(ctime))

    def item(self):
        """
        :rtype: Item
        """
        return self._item

    def setState(self, state):
        """
        :type state: dict
        :rtype: None
        """
        self.stateChanged.emit(self)

    def updateState(self):
        """
        :rtype: None
        """
        self.stateChanged.emit(self)

    def state(self):
        """
        :rtype: dict
        """
        return {}

    def settings(self):
        """
        :rtype: studiolibrary.Settings
        """
        return self.item().settings()

    def iconPath(self):
        """
        :rtype str
        """
        return self._iconPath

    def setIconPath(self, path):
        """
        :type path: str
        :rtype: None
        """
        self._iconPath = path
        icon = QtGui.QIcon(QtGui.QPixmap(path))
        self.setIcon(icon)
        self.updateThumbnailSize()

    def setIcon(self, icon):
        """
        :type icon: QtGui.QIcon
        """
        self.ui.thumbnailButton.setIcon(icon)
        self.ui.thumbnailButton.setIconSize(QtCore.QSize(200, 200))
        self.ui.thumbnailButton.setText("")

    def showSelectionSetsMenu(self):
        """
        :rtype: None
        """
        item = self.item()
        item.showSelectionSetsMenu(parent=self)

    def selectionChanged(self):
        """
        :rtype: None
        """
        pass

    def nameText(self):
        """
        :rtype: str
        """
        return self.ui.name.text().strip()

    def description(self):
        """
        :rtype: str
        """
        return self.ui.comment.toPlainText().strip()

    def loadSettings(self):
        """
        :rtype: None
        """
        pass

    def saveSettings(self):
        """
        :rtype: None
        """
        pass

    def scriptJob(self):
        """
        :rtype: mutils.ScriptJob
        """
        return self._scriptJob

    def close(self):
        """
        :rtype: None
        """
        sj = self.scriptJob()
        if sj:
            sj.kill()
        QtWidgets.QWidget.close(self)

    def objectCount(self):
        """
        :rtype: int
        """
        return 0

    def updateContains(self):
        """
        :rtype: None
        """
        if hasattr(self.ui, "contains"):
            count = self.objectCount()
            plural = "s" if count > 1 else ""
            self.ui.contains.setText(str(count) + " Object" + plural)


class CreateWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        """
        BaseWidget.__init__(self, *args, **kwargs)

        self.setWindowTitle("Create Item")

        self._iconPath = ""
        self._focusWidget = None

        self.ui.thumbnailButton.setToolTip("Click to capture a thumbnail from the current model panel.\nCTRL + Click to show the capture window for better framing.")

        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.thumbnailButton.clicked.connect(self.thumbnailCapture)
        self.ui.browseFolderButton.clicked.connect(self.browseFolder)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

    def objectCount(self):
        """
        Return the number of selected objects in the Maya scene.

        :rtype: int
        """
        selection = []

        try:
            selection = maya.cmds.ls(selection=True) or []
        except NameError, e:
            logger.exception(e)

        return len(selection)

    def folderFrame(self):
        """
        Return the frame that contains the folder edit, label and button.

        :rtype: QtWidgets.QFrame
        """
        return self.ui.folderFrame

    def setFolderPath(self, path):
        """
        Set the destination path

        :type path: str
        :rtype: None
        """
        self.ui.folderEdit.setText(path)

    def folderPath(self):
        """
        Return the folder path

        :rtype: str
        """
        return self.ui.folderEdit.text()

    def browseFolder(self):
        """
        Show the file dialog for choosing the folder location to save the item.

        :rtype: None
        """
        path = self.folderPath()
        path = QtWidgets.QFileDialog.getExistingDirectory(None, "Browse Folder", path)
        if path:
            self.setFolderPath(path)

    def showSelectionSetsMenu(self):
        """
        Show the selection sets menu for the current folder path.

        :rtype: None
        """
        import setsmenu

        path = self.folderPath()
        menu = setsmenu.SetsMenu.fromPath(path, parent=self)
        position = QtGui.QCursor().pos()

        menu.exec_(position)

    def selectionChanged(self):
        """
        Triggered when the Maya selection changes.

        :rtype: None
        """
        self.updateContains()

    def _thumbnailCaptured(self, path):
        """
        Triggered when the user captures a thumbnail/playblast.

        :type path: str
        :rtype: None
        """
        self.setIconPath(path)

    def thumbnailCapture(self):
        """
        Capture a playblast and save it to the temp thumbnail path.

        :rtype: None
        """
        path = mutils.gui.tempThumbnailPath()
        mutils.gui.thumbnailCapture(path=path, captured=self._thumbnailCaptured)

    def thumbnailCaptureQuestion(self):
        """
        Ask the user if they would like to capture a thumbnail.

        :rtype: int
        """
        title = "Create a thumbnail"
        message = "Would you like to capture a thumbanil?"
        options = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Ignore | QtWidgets.QMessageBox.Cancel

        result = studioqt.MessageBox.question(None, title, str(message), options)

        if result == QtWidgets.QMessageBox.Yes:
            self.thumbnailCapture()

        return result

    def accept(self):
        """Triggered when the user clicks the save button."""
        try:
            name = self.nameText()
            path = self.folderPath()

            objects = maya.cmds.ls(selection=True) or []

            if not path:
                raise ValidateError("No folder selected. Please select a destination folder.")

            if not name:
                raise ValidateError("No name specified. Please set a name before saving.")

            if not objects:
                raise ValidateError("No objects selected. Please select at least one object.")

            if not os.path.exists(self.iconPath()):
                result = self.thumbnailCaptureQuestion()
                if result == QtWidgets.QMessageBox.Cancel:
                    return

            path += "/" + name
            description = str(self.ui.comment.toPlainText())

            self.save(
                path=path,
                objects=objects,
                iconPath=self.iconPath(),
                description=description,
            )

        except Exception, msg:
            title = "Error while saving"
            studioqt.MessageBox.critical(self, title, str(msg))
            raise

    def save(self, objects, path, iconPath, description):
        """
        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type description: str
        :rtype: None
        """
        r = self.item()
        r.setDescription(description)
        r.save(objects=objects, path=path, iconPath=iconPath)
        self.close()


class PreviewWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        """
        BaseWidget.__init__(self, *args, **kwargs)

        if hasattr(self.ui, 'thumbnailButton'):
            path = self.item().thumbnailPath()
            if os.path.exists(path):
                self.setIconPath(path)

        try:
            self.updateNamespaceEdit()
        except NameError, msg:
            logger.exception(msg)

        self.setupConnections()

    def updateNamespaceFromScene(self):
        """
        Update the namespaces in the combobox with the ones in the scene.

        :rtype: None
        """
        IGNORE_NAMESPACES = ['UI', 'shared']

        namespaces = maya.cmds.namespaceInfo(listOnlyNamespaces=True)
        namespaces = list(set(namespaces) - set(IGNORE_NAMESPACES))
        namespaces = sorted(namespaces)

        text = self.ui.namespaceComboBox.currentText()

        if namespaces:
            self.ui.namespaceComboBox.setToolTip("")
        else:
            self.ui.namespaceComboBox.setToolTip("No namespaces found in scene.")

        self.ui.namespaceComboBox.clear()
        self.ui.namespaceComboBox.addItems(namespaces)
        self.ui.namespaceComboBox.setEditText(text)

    def setupConnections(self):
        """
        :rtype: None
        """
        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

        self.ui.useFileNamespace.clicked.connect(self.updateState)
        self.ui.useCustomNamespace.clicked.connect(self.updateState)
        self.ui.useSelectionNamespace.clicked.connect(self.updateState)

        self.ui.namespaceComboBox.activated[str].connect(self._namespaceEditChanged)
        self.ui.namespaceComboBox.editTextChanged[str].connect(self._namespaceEditChanged)
        self.ui.namespaceComboBox.currentIndexChanged[str].connect(self._namespaceEditChanged)

        self.ui.iconToggleBoxButton.clicked.connect(self.updateState)
        self.ui.infoToggleBoxButton.clicked.connect(self.updateState)
        self.ui.optionsToggleBoxButton.clicked.connect(self.updateState)
        self.ui.namespaceToggleBoxButton.clicked.connect(self.updateState)

        self.ui.iconToggleBoxButton.toggled[bool].connect(self.ui.iconToggleBoxFrame.setVisible)
        self.ui.infoToggleBoxButton.toggled[bool].connect(self.ui.infoToggleBoxFrame.setVisible)
        self.ui.optionsToggleBoxButton.toggled[bool].connect(self.ui.optionsToggleBoxFrame.setVisible)
        self.ui.namespaceToggleBoxButton.toggled[bool].connect(self.ui.namespaceToggleBoxFrame.setVisible)

    def _namespaceEditChanged(self, text):
        """
        Triggered when the combox box has changed value.

        :type text: str
        :rtype: None
        """
        self.ui.useCustomNamespace.setChecked(True)
        self.ui.namespaceComboBox.setEditText(text)
        self.saveSettings()

    def objectCount(self):
        """
        :rtype: int
        """
        objectCount = 0

        if self.item().exists():
            objectCount = self.item().objectCount()

        return objectCount

    def updateState(self):
        """
        :rtype: None
        """
        logger.debug("Updating widget state")

        self.updateNamespaceEdit()
        self.saveSettings()

        BaseWidget.updateState(self)

    def namespaces(self):
        """
        :rtype: list[str]
        """
        namespaces = str(self.ui.namespaceComboBox.currentText())
        namespaces = studiolibrary.stringToList(namespaces)
        return namespaces

    def setNamespaces(self, namespaces):
        """
        :type namespaces: list
        :rtype: None
        """
        namespaces = studiolibrary.listToString(namespaces)
        self.ui.namespaceComboBox.setEditText(namespaces)

    def namespaceOption(self):
        """
        :rtype: NamespaceOption
        """
        if self.ui.useFileNamespace.isChecked():
            namespaceOption = NamespaceOption.FromFile
        elif self.ui.useCustomNamespace.isChecked():
            namespaceOption = NamespaceOption.FromCustom
        else:
            namespaceOption = NamespaceOption.FromSelection

        return namespaceOption

    def setNamespaceOption(self, namespaceOption):
        """
        :type namespaceOption: NamespaceOption
        """
        if namespaceOption == NamespaceOption.FromFile:
            self.ui.useFileNamespace.setChecked(True)
        elif namespaceOption == NamespaceOption.FromCustom:
            self.ui.useCustomNamespace.setChecked(True)
        else:
            self.ui.useSelectionNamespace.setChecked(True)

    def setState(self, state):
        """
        :type state: dict
        """
        namespaceOption = state.get("namespaceOption", "")
        self.setNamespaceOption(namespaceOption)

        namespaces = state.get("namespaces", "")
        self.setNamespaces(namespaces)

        toggleBoxChecked = state.get("iconToggleBoxChecked", True)
        self.ui.iconToggleBoxFrame.setVisible(toggleBoxChecked)
        self.ui.iconToggleBoxButton.setChecked(toggleBoxChecked)

        toggleBoxChecked = state.get("infoToggleBoxChecked", True)
        self.ui.infoToggleBoxFrame.setVisible(toggleBoxChecked)
        self.ui.infoToggleBoxButton.setChecked(toggleBoxChecked)

        toggleBoxChecked = state.get("optionsToggleBoxChecked", True)
        self.ui.optionsToggleBoxFrame.setVisible(toggleBoxChecked)
        self.ui.optionsToggleBoxButton.setChecked(toggleBoxChecked)

        toggleBoxChecked = state.get("namespaceToggleBoxChecked", True)
        self.ui.namespaceToggleBoxFrame.setVisible(toggleBoxChecked)
        self.ui.namespaceToggleBoxButton.setChecked(toggleBoxChecked)

        super(PreviewWidget, self).setState(state)

    def state(self):
        """
        :rtype: dict
        """
        state = super(PreviewWidget, self).state()

        state["namespaces"] = self.namespaces()
        state["namespaceOption"] = self.namespaceOption()

        state["iconToggleBoxChecked"] = self.ui.iconToggleBoxButton.isChecked()
        state["infoToggleBoxChecked"] = self.ui.infoToggleBoxButton.isChecked()
        state["optionsToggleBoxChecked"] = self.ui.optionsToggleBoxButton.isChecked()
        state["namespaceToggleBoxChecked"] = self.ui.namespaceToggleBoxButton.isChecked()

        return state

    def loadSettings(self):
        """
        :rtype: None
        """
        settings = self.settings()
        self.setState(settings.data())

    def saveSettings(self):
        """
        :rtype: None
        """
        settings = self.settings()
        settings.data().update(self.state())
        settings.save()

    def selectionChanged(self):
        """
        :rtype: None
        """
        self.updateNamespaceEdit()

    def updateNamespaceEdit(self):
        """
        :rtype: None
        """
        logger.debug('Updating namespace edit')

        self.ui.namespaceComboBox.blockSignals(True)

        self.updateNamespaceFromScene()

        namespaces = []

        if self.ui.useSelectionNamespace.isChecked():
            namespaces = mutils.namespace.getFromSelection()
        elif self.ui.useFileNamespace.isChecked():
            namespaces = self.item().transferObject().namespaces()

        if self.ui.useCustomNamespace.isChecked():
            self.ui.namespaceComboBox.setFocus()
        else:
            self.setNamespaces(namespaces)

            # Removes focus from the combobox
            self.ui.namespaceComboBox.setEnabled(False)
            self.ui.namespaceComboBox.setEnabled(True)

        self.ui.namespaceComboBox.blockSignals(False)

    def accept(self):
        """
        :rtype: None
        """
        try:
            self.item().load()
        except Exception, msg:
            title = "Error while loading"
            studioqt.MessageBox.critical(self, title, str(msg))
            raise
