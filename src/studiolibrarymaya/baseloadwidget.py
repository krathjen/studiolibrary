# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
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

import os
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary
import studiolibrarymaya
import studiolibrary.widgets

try:
    import mutils
    import mutils.gui
    import maya.cmds
except ImportError as error:
    print(error)

__all__ = [
    "BaseLoadWidget",
]

logger = logging.getLogger(__name__)


class NamespaceOption:
    FromFile = "file"
    FromCustom = "custom"
    FromSelection = "selection"


class TitleWidget(QtWidgets.QPushButton):

    def __init__(self, title, widget, *args, **kwargs):
        super(TitleWidget, self).__init__(*args, **kwargs)

        self._widget = None

        self.setText(title)
        self.setWidget(widget)
        self.setCheckable(True)

        self.toggled.connect(self._toggle)
        self.loadSettings()

    def _toggle(self, visible):
        """
        Triggered when the user clicks the title.

        :type visible: bool
        """
        self.saveSettings()
        self.setChecked(visible)

    def setWidget(self, widget):
        """
        Set the widget to hide when the user clicks the title.

        :type widget: QWidgets.QWidget
        """
        self._widget = widget

    def setChecked(self, checked):
        """
        Overriding this method to hide the widget when the state changes.

        :type checked: bool
        """
        super(TitleWidget, self).setChecked(checked)
        if self._widget:
            self._widget.setVisible(checked)

    def saveSettings(self):
        """Save the state to disc."""
        data = {
            self.text().lower() + "ToggleBoxChecked": self.isChecked(),
        }
        studiolibrarymaya.saveSettings(data)

    def loadSettings(self):
        """Load the state to disc."""
        data = studiolibrarymaya.settings()
        checked = data.get(self.text().lower() + "ToggleBoxChecked", True)
        self.setChecked(checked)


class BaseLoadWidget(QtWidgets.QWidget):
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
        self._optionsWidget = None

        self.setItem(item)
        self.loadSettings()

        try:
            self.selectionChanged()
            self.setScriptJobEnabled(True)
            self.updateNamespaceEdit()
        except NameError as error:
            logger.exception(error)

        self.createSequenceWidget()
        self.updateThumbnailSize()
        self.setupConnections()

    def setupConnections(self):
        """Setup the connections for all the widgets."""
        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

        self.ui.useFileNamespace.clicked.connect(self._namespaceOptionClicked)
        self.ui.useCustomNamespace.clicked.connect(self._useCustomNamespaceClicked)
        self.ui.useSelectionNamespace.clicked.connect(self._namespaceOptionClicked)

        self.ui.namespaceComboBox.activated[str].connect(self._namespaceEditChanged)
        self.ui.namespaceComboBox.editTextChanged[str].connect(self._namespaceEditChanged)
        self.ui.namespaceComboBox.currentIndexChanged[str].connect(self._namespaceEditChanged)

    def createSequenceWidget(self):
        """
        Create a sequence widget to replace the static thumbnail widget.

        :rtype: None
        """
        self.ui.sequenceWidget = studiolibrary.widgets.ImageSequenceWidget(self)
        self.ui.sequenceWidget.setStyleSheet(self.ui.thumbnailButton.styleSheet())
        self.ui.sequenceWidget.setToolTip(self.ui.thumbnailButton.toolTip())

        self.ui.thumbnailFrame.layout().insertWidget(0, self.ui.sequenceWidget)
        self.ui.thumbnailButton.hide()
        self.ui.thumbnailButton = self.ui.sequenceWidget

        path = self.item().thumbnailPath()
        if os.path.exists(path):
            self.setIconPath(path)

        if self.item().imageSequencePath():
            self.ui.sequenceWidget.setDirname(self.item().imageSequencePath())

    def isEditable(self):
        """
        Return True if the user can edit the item.

        :rtype: bool 
        """
        item = self.item()
        editable = True

        if item and item.libraryWindow():
            editable = not item.libraryWindow().isLocked()

        return editable

    def setCaptureMenuEnabled(self, enable):
        """
        Enable the capture menu for editing the thumbnail.

        :rtype: None 
        """
        if enable:
            parent = self.item().libraryWindow()

            iconPath = self.iconPath()
            if iconPath == "":
                iconPath = self.item().thumbnailPath()

            menu = mutils.gui.ThumbnailCaptureMenu(iconPath, parent=parent)
            menu.captured.connect(self.setIconPath)
            self.ui.thumbnailButton.setMenu(menu)
        else:
            self.ui.thumbnailButton.setMenu(QtWidgets.QMenu(self))

    def item(self):
        """
        Return the library item to be created.

        :rtype: studiolibrarymaya.BaseItem
        """
        return self._item

    def _itemValueChanged(self, field, value):
        """
        :type field: str
        :type value: object
        """
        self._optionsWidget.setValue(field, value)

    def setItem(self, item):
        """
        Set the item for the preview widget.

        :type item: BaseItem
        """
        self._item = item

        if hasattr(self.ui, "titleLabel"):
            self.ui.titleLabel.setText(item.MenuName)

        if hasattr(self.ui, "iconLabel"):
            self.ui.iconLabel.setPixmap(QtGui.QPixmap(item.TypeIconPath))

        if hasattr(self.ui, "infoFrame"):
            infoWidget = studiolibrary.widgets.FormWidget(self)
            infoWidget.setSchema(item.info())
            self.ui.infoFrame.layout().addWidget(infoWidget)

        if hasattr(self.ui, "optionsFrame"):

            options = item.loadSchema()
            if options:
                item.loadValueChanged.connect(self._itemValueChanged)

                optionsWidget = studiolibrary.widgets.FormWidget(self)
                optionsWidget.setSchema(item.loadSchema())
                optionsWidget.setValidator(item.loadValidator)
                optionsWidget.setValues(self.item().optionsFromSettings())
                self.ui.optionsFrame.layout().addWidget(optionsWidget)
                self._optionsWidget = optionsWidget
                optionsWidget.validate()
            else:
                self.ui.optionsToggleBox.setVisible(False)

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
        """Show the selection sets menu."""
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

        if self._optionsWidget:
            self.item().saveOptions(**self._optionsWidget.values())

        QtWidgets.QWidget.close(self)

    def scriptJob(self):
        """
        Get the script job object used when the users selection changes.

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
        Get the current namespace option.

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
        Set the current namespace option.

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
        Set the state of the widget.

        :type settings: dict
        """
        namespaces = settings.get("namespaces", [])
        self.setNamespaces(namespaces)

        namespaceOption = settings.get("namespaceOption", NamespaceOption.FromFile)
        self.setNamespaceOption(namespaceOption)

        infoTitleWidget = TitleWidget("Info", self.ui.infoFrame)
        self.ui.infoTitleFrame.layout().addWidget(infoTitleWidget)

        iconTitleWidget = TitleWidget("Icon", self.ui.iconFrame)
        self.ui.iconTitleFrame.layout().addWidget(iconTitleWidget)

        optionsTitleWidget = TitleWidget("Options", self.ui.optionsFrame)
        self.ui.optionsTitleFrame.layout().addWidget(optionsTitleWidget)

        namespaceTitleWidget = TitleWidget("Namespace", self.ui.namespaceFrame)
        self.ui.namespaceTitleFrame.layout().addWidget(namespaceTitleWidget)

    def settings(self):
        """
        Get the current state of the widget.

        :rtype: dict
        """
        settings = {}

        settings["namespaces"] = self.namespaces()
        settings["namespaceOption"] = self.namespaceOption()

        return settings

    def loadSettings(self):
        """
        Load the user settings from disc.

        :rtype: None
        """
        data = studiolibrarymaya.settings()
        self.setSettings(data)

    def saveSettings(self):
        """
        Save the user settings to disc.

        :rtype: None
        """
        data = self.settings()
        studiolibrarymaya.saveSettings(data)

    def selectionChanged(self):
        """
        Triggered when the users Maya selection has changed.

        :rtype: None
        """
        self.updateNamespaceEdit()

    def updateNamespaceFromScene(self):
        """
        Update the namespaces in the combobox with the ones in the scene.

        :rtype: None
        """
        namespaces = mutils.namespace.getAll()

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
        Update the namespace edit.

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
        Called when the user clicks the apply button.

        :rtype: None
        """
        self.item().loadFromCurrentOptions()
