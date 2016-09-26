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

import os
import shutil
import logging
import traceback

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary

try:
    import mutils
    import mutils.gui
    import maya.cmds
except ImportError, msg:
    print msg


__all__ = ["Plugin", "PreviewWidget", "CreateWidget"]

logger = logging.getLogger(__name__)


class PluginError(Exception):
    """Base class for exceptions in this module."""
    pass


class ValidateError(PluginError):
    """"""
    pass


class NamespaceOption:
    FromFile = "pose"
    FromCustom = "custom"
    FromSelection = "selection"


class Plugin(studiolibrary.Plugin):

    def setLoggerLevel(self, level):
        """
        Triggered when the user chooses debug mode.

        :type level: int
        :rtype: None
        """
        logger_ = logging.getLogger("mutils")
        logger_.setLevel(level)

        logger_ = logging.getLogger("studiolibraryplugins")
        logger_.setLevel(level)


class Record(studiolibrary.Record):

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        studiolibrary.Record.__init__(self, *args, **kwargs)

        self._namespaces = []
        self._namespaceOption = NamespaceOption.FromSelection

        self._transferClass = None
        self._transferObject = None
        self._transferBasename = None

    def settings(self):
        """
        :rtype: studiolibrary.Settings
        """
        return self.plugin().settings()

    def showErrorDialog(self, message, title="Record Error"):
        """
        :type title: str
        :type message: str
        :rtype: int
        """
        return studioqt.MessageBox.critical(None, title, str(message))

    def owner(self):
        """
        :rtype: str
        """
        user = studiolibrary.Record.owner(self)
        transferObject = self.transferObject()

        if not user and transferObject:
            user = self.transferObject().metadata().get("user")
        return user

    def ctime(self):
        """
        :rtype: str
        """
        path = self.path()
        ctime = ""

        if os.path.exists(path):
            ctime = studiolibrary.Record.ctime(self)

            if not ctime:
                ctime = int(os.path.getctime(path))

        return ctime

    def description(self):
        """
        :rtype: str
        """
        description = studiolibrary.Record.description(self)
        transferObject = self.transferObject()

        if not description and transferObject:
            description = self.transferObject().metadata().get("description")
        return description

    def contextMenu(self, menu, records=None):
        """
        :type menu: QtWidgets.QMenu
        :type records: list[Record]
        :rtype: None
        """
        import selectionsetmenu

        action = selectionsetmenu.selectContentAction(self, parent=menu)
        menu.addAction(action)
        menu.addSeparator()

        subMenu = self.selectionSetsMenu(parent=menu, enableSelectContent=False)
        menu.addMenu(subMenu)
        menu.addSeparator()

    def showSelectionSetsMenu(self, **kwargs):
        """
        :rtype: QtWidgets.QAction
        """
        menu = self.selectionSetsMenu(**kwargs)
        position = QtGui.QCursor().pos()
        action = menu.exec_(position)
        return action

    def selectionSetsMenu(self, parent=None, enableSelectContent=True):
        """
        :type parent: QtWidgets.QWidget
        :type enableSelectContent: bool
        :rtype: QtWidgets.QMenu
        """
        import selectionsetmenu

        namespaces = self.namespaces()

        menu = selectionsetmenu.SelectionSetMenu(
                record=self,
                parent=parent,
                namespaces=namespaces,
                enableSelectContent=enableSelectContent,
        )
        return menu

    def mirrorTable(self):
        """
        Return the mirror table object for this record.

        :rtype: mutils.MirrorTable or None
        """
        mirrorTable = None
        path = self.mirrorTablePath()

        if path:
            mirrorTable = mutils.MirrorTable.fromPath(path)

        return mirrorTable

    def mirrorTablePath(self):
        """
        Return the mirror table path for this record.

        :rtype: str or None
        """
        path = None
        paths = self.mirrorTablePaths()

        if paths:
            path = paths[0]

        return path

    def mirrorTablePaths(self):
        """
        Return all the mirror table paths for this record.

        :rtype: list[str]
        """
        paths = list(studiolibrary.findPaths(
                self.path(),
                match=lambda path: path.endswith(".mirror"),
                direction=studiolibrary.Direction.Up
            )
        )
        return paths

    def selectContent(self, namespaces=None, **kwargs):
        """
        :type namespaces: list[str]
        """
        namespaces = namespaces or self.namespaces()
        kwargs = kwargs or mutils.selectionModifiers()

        msg = "Select content: Record.selectContent(namespacea={0}, kwargs={1})"
        msg = msg.format(namespaces, kwargs)
        logger.debug(msg)

        try:
            self.transferObject().select(namespaces=namespaces, **kwargs)
        except Exception, msg:
            title = "Error while selecting content"
            studioqt.MessageBox.critical(None, title, str(msg))
            raise

    def setTransferClass(self, classname):
        """
        :type classname: mutils.TransferObject
        """
        self._transferClass = classname

    def transferClass(self):
        """
        :rtype:
        """
        return self._transferClass

    def transferPath(self):
        """
        :rtype: str
        """
        if self.transferBasename():
            return "/".join([self.path(), self.transferBasename()])
        else:
            return self.path()

    def transferBasename(self):
        """
        :rtype: str
        """
        return self._transferBasename

    def setTransferBasename(self, transferBasename):
        """
        :rtype: str
        """
        self._transferBasename = transferBasename

    def transferObject(self):
        """
        :rtype: mutils.TransferObject
        """
        if not self._transferObject:
            path = self.transferPath()
            if os.path.exists(path):
                self._transferObject = self.transferClass().fromPath(path)
        return self._transferObject

    def namespaces(self):
        """
        :rtype: list[str]
        """
        namespaces = []
        namespaceOption = self.namespaceOption()

        # When creating a new record we can only get the namespaces from
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
        :type namespaceOption: NamespaceOption
        :rtype: None
        """
        self.settings().set("namespaceOption", namespaceOption)

    def namespaceOption(self):
        """
        :rtype: NamespaceOption
        """
        namespaceOption = self.settings().get(
                "namespaceOption",
                NamespaceOption.FromSelection
        )
        return namespaceOption

    def setCustomNamespaces(self, namespaces):
        """
        :type namespaces: list[str]
        :rtype: None
        """
        self.settings().set("namespaces", namespaces)

    def namespaceFromFile(self):
        """
        :rtype: list[str]
        """
        return self.transferObject().namespaces()

    def namespaceFromCustom(self):
        """
        :rtype: list[str]
        """
        return self.settings().get("namespaces", "")

    @staticmethod
    def namespaceFromSelection():
        """
        :rtype: list[str]
        """
        return mutils.namespace.getFromSelection() or [""]

    def objectCount(self):
        """
        :rtype: int
        """
        if self.transferObject():
            return self.transferObject().count()
        else:
            return 0

    def doubleClicked(self):
        """
        :rtype: None
        """
        self.load()

    def load(self, objects=None, namespaces=None, **kwargs):
        """
        :type namespaces: list[str]
        :type objects: list[str]
        :rtype: None
        """
        logger.debug("Loading: %s" % self.transferPath())

        self.transferObject().load(objects=objects, namespaces=namespaces, **kwargs)

        logger.debug("Loaded: %s" % self.transferPath())

    def save(self, objects, path=None, iconPath=None, **kwargs):
        """
        :type path: path
        :type objects: list
        :type iconPath: str
        :raise ValidateError:
        """
        logger.info("Saving: {0}".format(path))

        contents = list()
        tempDir = mutils.TempDir("Transfer", clean=True)

        transferPath = tempDir.path() + "/" + self.transferBasename()
        t = self.transferClass().fromObjects(objects)
        t.save(transferPath, **kwargs)

        if iconPath:
            contents.append(iconPath)

        contents.append(transferPath)
        studiolibrary.Record.save(self, path=path, contents=contents)

        logger.info("Saved: {0}".format(path))


class BaseWidget(QtWidgets.QWidget):

    stateChanged = QtCore.Signal(object)

    def __init__(self, record, parent=None):
        """
        :type record: Record
        :type parent: studiolibrary.LibraryWidget
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.setObjectName("studioLibraryPluginsWidget")

        studioqt.loadUi(self)

        self._record = None
        self._iconPath = ""
        self._scriptJob = None

        self.setRecord(record)
        self.loadSettings()

        try:
            self.selectionChanged()
            self.enableScriptJob()
        except NameError, msg:
            logger.exception(msg)

    def enableScriptJob(self):
        """
        :rtype: None
        """
        if not self._scriptJob:
            event = ['SelectionChanged', self.selectionChanged]
            self._scriptJob = mutils.ScriptJob(event=event)

    def setRecord(self, record):
        """
        :type record: Record
        """
        self._record = record

        if hasattr(self.ui, 'name'):
            self.ui.name.setText(record.name())

        if hasattr(self.ui, 'owner'):
            self.ui.owner.setText(str(record.owner()))

        if hasattr(self.ui, 'comment'):
            if isinstance(self.ui.comment, QtWidgets.QLabel):
                self.ui.comment.setText(record.description())
            else:
                self.ui.comment.setPlainText(record.description())

        if hasattr(self.ui, "contains"):
            self.updateContains()

        if hasattr(self.ui, 'snapshotButton'):
            path = record.iconPath()
            if os.path.exists(path):
                self.setIconPath(record.iconPath())

        ctime = record.ctime()
        if hasattr(self.ui, 'created') and ctime:
            self.ui.created.setText(studiolibrary.timeAgo(ctime))

    def record(self):
        """
        :rtype: Record
        """
        return self._record

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
        return self.record().settings()

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

    def setIcon(self, icon):
        """
        :type icon: QtGui.QIcon
        """
        self.ui.snapshotButton.setIcon(icon)
        self.ui.snapshotButton.setIconSize(QtCore.QSize(200, 200))
        self.ui.snapshotButton.setText("")

    def libraryWidget(self):
        """
        :rtype: studiolibrary.LibraryWidget
        """
        return self.record().plugin().libraryWidget()

    def showSelectionSetsMenu(self):
        """
        :rtype: None
        """
        record = self.record()
        record.showSelectionSetsMenu(parent=self)

    def selectionChanged(self):
        """
        :rtype: None
        """
        pass

    def nameText(self):
        """
        :rtype: str
        """
        return str(self.ui.name.text()).strip()

    def description(self):
        """
        :rtype: str
        """
        return str(self.ui.comment.toPlainText()).strip()

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


class PreviewWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        """
        BaseWidget.__init__(self, *args, **kwargs)

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

        if self.record().exists():
            objectCount = self.record().objectCount()

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

        super(PreviewWidget, self).setState(state)

    def state(self):
        """
        :rtype: dict
        """
        state = super(PreviewWidget, self).state()

        state["namespaces"] = self.namespaces()
        state["namespaceOption"] = self.namespaceOption()

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
            namespaces = self.record().transferObject().namespaces()

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
            self.record().load()
        except Exception, msg:
            title = "Error while loading"
            studioqt.MessageBox.critical(self, title, str(msg))
            raise


class CreateWidget(BaseWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        """
        BaseWidget.__init__(self, *args, **kwargs)

        self._iconPath = ""
        self._focusWidget = None

        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.snapshotButton.clicked.connect(self.snapshot)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

        # import mutils.modelpanelwidget
        # self._modelPanel = mutils.modelpanelwidget.ModelPanelWidget(self.ui.modelPanelFrame)
        # self.ui.modelPanelFrame.layout().insertWidget(0, self._modelPanel)
        # self.ui.snapshotButton.hide()

    def objectCount(self):
        """
        :rtype: int
        """
        selection = []
        try:
            selection = maya.cmds.ls(selection=True) or []
        except NameError, e:
            traceback.print_exc()

        return len(selection)

    def dirname(self):
        """
        :rtype: str or None
        """
        dirname = self.record().dirname()

        if not dirname:
            dirname = self.selectedFolderPath()

        return dirname

    def selectedFolderPath(self):
        """
        :rtype: str or None
        """
        dirname = None
        folder = self.libraryWidget().selectedFolder()

        if folder:
            dirname = folder.path()

        return dirname

    def showSelectionSetsMenu(self):
        """
        :rtype: None
        """
        import selectionsetmenu

        dirname = self.dirname()
        menu = selectionsetmenu.SelectionSetMenu.fromPath(dirname, parent=self)
        position = QtGui.QCursor().pos()

        menu.exec_(position)

    def selectionChanged(self):
        """
        :rtype: None
        """
        self.updateContains()

    def modelPanel(self):
        """
        :rtype: mutils.ModelPanelWidget
        """
        return self._modelPanel

    def _captured(self, path):
        """
        Triggered when the user captures a thumbnail/playblast.

        :type path: str
        :rtype: None
        """
        self.setIconPath(path)

    def snapshot(self):
        """
        :rtype: None
        """
        path = mutils.gui.tempThumbnailPath()
        mutils.gui.thumbnailCapture(path=path, captured=self._captured)

    def snapshotQuestion(self):
        """
        :rtype: int
        """
        title = "Create a snapshot icon"
        message = "Would you like to create a snapshot icon?"
        options = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Ignore | QtWidgets.QMessageBox.Cancel

        result = studioqt.MessageBox.question(None, title, str(message), options)

        if result == QtWidgets.QMessageBox.Yes:
            self.snapshot()

        return result

    def accept(self):
        """
        :rtype: None
        """
        try:
            name = self.nameText()
            objects = maya.cmds.ls(selection=True) or []
            dirname = self.dirname()

            if not dirname:
                raise ValidateError("No folder selected. Please select a destination folder.")

            if not name:
                raise ValidateError("No name specified. Please set a name before saving.")

            if not objects:
                raise ValidateError("No objects selected. Please select at least one object.")

            if not os.path.exists(self.iconPath()):
                result = self.snapshotQuestion()
                if result == QtWidgets.QMessageBox.Cancel:
                    return

            path = dirname + "/" + name
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
        r = self.record()
        r.setDescription(description)
        r.save(objects=objects, path=path, iconPath=iconPath)
