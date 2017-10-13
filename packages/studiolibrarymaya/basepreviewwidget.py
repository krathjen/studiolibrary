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
import studiolibrary
import studiolibrarymaya

try:
    import mutils
    import mutils.gui
    import maya.cmds
except ImportError, e:
    print e


__all__ = [
    "BasePreviewWidget",
]

logger = logging.getLogger(__name__)


class NamespaceOption:
    FromFile = "file"
    FromCustom = "custom"
    FromSelection = "selection"


class BasePreviewWidget(QtWidgets.QWidget):

    """Base widget for creating and previewing transfer items."""

    stateChanged = QtCore.Signal(object)

    def __init__(self, item, parent=None):
        """
        :type parent: QtWidgets.QWidget
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.setObjectName("studioLibraryMayaPreviewWidget")
        self.setWindowTitle("Preview Item")

        studioqt.loadUi(self)

        self._item = None
        self._iconPath = ""
        self._scriptJob = None

        self.setItem(item)
        self.loadSettings()

        try:
            self.selectionChanged()
            self.setScriptJobEnabled(True)
            self.updateNamespaceEdit()
        except NameError, msg:
            logger.exception(msg)

        path = self.item().thumbnailPath()
        if os.path.exists(path):
            self.setIconPath(path)

        self.updateThumbnailSize()
        self.setupConnections()

    def setupConnections(self):
        """
        :rtype: None
        """
        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

        self.ui.useFileNamespace.clicked.connect(self._namespaceOptionClicked)
        self.ui.useCustomNamespace.clicked.connect(self._useCustomNamespaceClicked)
        self.ui.useSelectionNamespace.clicked.connect(self._namespaceOptionClicked)

        self.ui.namespaceComboBox.activated[str].connect(self._namespaceEditChanged)
        self.ui.namespaceComboBox.editTextChanged[str].connect(self._namespaceEditChanged)
        self.ui.namespaceComboBox.currentIndexChanged[str].connect(self._namespaceEditChanged)

        self.ui.iconToggleBoxButton.clicked.connect(self.saveSettings)
        self.ui.infoToggleBoxButton.clicked.connect(self.saveSettings)
        self.ui.optionsToggleBoxButton.clicked.connect(self.saveSettings)
        self.ui.namespaceToggleBoxButton.clicked.connect(self.saveSettings)

        self.ui.iconToggleBoxButton.toggled[bool].connect(self.ui.iconToggleBoxFrame.setVisible)
        self.ui.infoToggleBoxButton.toggled[bool].connect(self.ui.infoToggleBoxFrame.setVisible)
        self.ui.optionsToggleBoxButton.toggled[bool].connect(self.ui.optionsToggleBoxFrame.setVisible)
        self.ui.namespaceToggleBoxButton.toggled[bool].connect(self.ui.namespaceToggleBoxFrame.setVisible)

    def item(self):
        """
        Return the library item to be created.

        :rtype: studiolibrarymaya.BaseItem
        """
        return self._item

    def setItem(self, item):
        """
        Set the item for the preview widget.

        :type item: BaseItem
        """
        self._item = item

        self.ui.name.setText(item.name())
        self.ui.owner.setText(item.owner())
        self.ui.comment.setText(item.description())

        self.updateContains()

        ctime = item.ctime()
        if ctime:
            self.ui.created.setText(studiolibrary.timeAgo(ctime))

    def iconPath(self):
        """
        Return the icon path to be used for the thumbnail.

        :rtype str
        """
        return self._iconPath

    def setIconPath(self, path):
        """
        Set the icon path to be used for the thumbnail.

        :type path: str
        :rtype: None
        """
        self._iconPath = path
        icon = QtGui.QIcon(QtGui.QPixmap(path))
        self.setIcon(icon)
        self.updateThumbnailSize()
        self.item().update()

    def setIcon(self, icon):
        """
        Set the icon to be shown for the preview.

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
        item.showSelectionSetsMenu()

    def resizeEvent(self, event):
        """
        Overriding to adjust the image size when the widget changes size.

        :type event: QtCore.QSizeEvent
        """
        self.updateThumbnailSize()

    def updateThumbnailSize(self):
        """
        Update the thumbnail button to the size of the widget.

        :rtype: None
        """
        if hasattr(self.ui, "thumbnailButton"):
            width = self.width() - 10
            if width > 250:
                width = 250

            size = QtCore.QSize(width, width)
            self.ui.thumbnailButton.setIconSize(size)
            self.ui.thumbnailButton.setMaximumSize(size)
            self.ui.thumbnailFrame.setMaximumSize(size)

    def close(self):
        """
        Overriding the close method so that we can disable the script job.

        :rtype: None
        """
        self.setScriptJobEnabled(False)
        QtWidgets.QWidget.close(self)

    def scriptJob(self):
        """
        Return the script job object used when the users selection changes.

        :rtype: mutils.ScriptJob
        """
        return self._scriptJob

    def setScriptJobEnabled(self, enable):
        """
        Enable the script job used when the users selection changes.

        :rtype: None
        """
        if enable:
            if not self._scriptJob:
                event = ['SelectionChanged', self.selectionChanged]
                self._scriptJob = mutils.ScriptJob(event=event)
        else:
            sj = self.scriptJob()
            if sj:
                sj.kill()
            self._scriptJob = None

    def objectCount(self):
        """
        Return the number of controls contained in the item.

        :rtype: int
        """
        return self.item().objectCount()

    def updateContains(self):
        """
        Refresh the contains information.

        :rtype: None
        """
        count = self.objectCount()
        plural = "s" if count > 1 else ""
        self.ui.contains.setText(str(count) + " Object" + plural)

    def _namespaceEditChanged(self, text):
        """
        Triggered when the combox box has changed value.

        :type text: str
        :rtype: None
        """
        self.ui.useCustomNamespace.setChecked(True)
        self.ui.namespaceComboBox.setEditText(text)
        self.saveSettings()

    def _namespaceOptionClicked(self):
        self.updateNamespaceEdit()
        self.saveSettings()

    def _useCustomNamespaceClicked(self):
        """
        Triggered when the custom namespace radio button is clicked.

        :rtype: None
        """
        self.ui.namespaceComboBox.setFocus()
        self.updateNamespaceEdit()
        self.saveSettings()

    def namespaces(self):
        """
        Return the namespace names from the namespace edit widget.

        :rtype: list[str]
        """
        namespaces = str(self.ui.namespaceComboBox.currentText())
        namespaces = studiolibrary.stringToList(namespaces)
        return namespaces

    def setNamespaces(self, namespaces):
        """
        Set the namespace names for the namespace edit.

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

    def setSettings(self, settings):
        """
        :type settings: dict
        """
        namespaces = settings.get("namespaces", [])
        self.setNamespaces(namespaces)

        namespaceOption = settings.get("namespaceOption", NamespaceOption.FromFile)
        self.setNamespaceOption(namespaceOption)

        toggleBoxChecked = settings.get("iconToggleBoxChecked", True)
        self.ui.iconToggleBoxFrame.setVisible(toggleBoxChecked)
        self.ui.iconToggleBoxButton.setChecked(toggleBoxChecked)

        toggleBoxChecked = settings.get("infoToggleBoxChecked", True)
        self.ui.infoToggleBoxFrame.setVisible(toggleBoxChecked)
        self.ui.infoToggleBoxButton.setChecked(toggleBoxChecked)

        toggleBoxChecked = settings.get("optionsToggleBoxChecked", True)
        self.ui.optionsToggleBoxFrame.setVisible(toggleBoxChecked)
        self.ui.optionsToggleBoxButton.setChecked(toggleBoxChecked)

        toggleBoxChecked = settings.get("namespaceToggleBoxChecked", True)
        self.ui.namespaceToggleBoxFrame.setVisible(toggleBoxChecked)
        self.ui.namespaceToggleBoxButton.setChecked(toggleBoxChecked)

    def settings(self):
        """
        :rtype: dict
        """
        settings = {}

        settings["namespaces"] = self.namespaces()
        settings["namespaceOption"] = self.namespaceOption()

        settings["iconToggleBoxChecked"] = self.ui.iconToggleBoxButton.isChecked()
        settings["infoToggleBoxChecked"] = self.ui.infoToggleBoxButton.isChecked()
        settings["optionsToggleBoxChecked"] = self.ui.optionsToggleBoxButton.isChecked()
        settings["namespaceToggleBoxChecked"] = self.ui.namespaceToggleBoxButton.isChecked()

        return settings

    def loadSettings(self):
        """
        :rtype: None
        """
        data = studiolibrarymaya.settings()
        self.setSettings(data)

    def saveSettings(self):
        """
        :rtype: None
        """
        data = self.settings()
        studiolibrarymaya.saveSettings(data)

    def selectionChanged(self):
        """
        :rtype: None
        """
        self.updateNamespaceEdit()

    def updateNamespaceFromScene(self):
        """
        Update the namespaces in the combobox with the ones in the scene.

        :rtype: None
        """
        IGNORE_NAMESPACES = ['UI', 'shared']

        if studiolibrary.isMaya():
            namespaces = maya.cmds.namespaceInfo(listOnlyNamespaces=True)
        else:
            namespaces = []

        namespaces = list(set(namespaces) - set(IGNORE_NAMESPACES))
        namespaces = sorted(namespaces)

        text = self.ui.namespaceComboBox.currentText()

        if namespaces:
            self.ui.namespaceComboBox.setToolTip("")
        else:
            toolTip = "No namespaces found in scene."
            self.ui.namespaceComboBox.setToolTip(toolTip)

        self.ui.namespaceComboBox.clear()
        self.ui.namespaceComboBox.addItems(namespaces)
        self.ui.namespaceComboBox.setEditText(text)

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

        if not self.ui.useCustomNamespace.isChecked():
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
        except Exception, e:
            title = "Error while loading"
            self.item().showErrorDialog(title, str(e))
            raise
