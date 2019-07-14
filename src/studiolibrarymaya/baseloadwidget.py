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

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt
import studiolibrary
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


class BaseLoadWidget(QtWidgets.QWidget):
    """Base widget for creating and previewing transfer items."""

    stateChanged = QtCore.Signal(object)

    def __init__(self, item, parent=None):
        """
        :type item: studiolibrarymaya.BaseItem
        :type parent: QtWidgets.QWidget or None
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.setObjectName("studioLibraryMayaPreviewWidget")
        self.setWindowTitle("Preview Item")

        self.loadUi()

        self._item = None
        self._iconPath = ""
        self._scriptJob = None
        self._formWidget = None
        self._infoFormWidget = None

        self.setItem(item)

        iconGroupBoxWidget = studiolibrary.widgets.GroupBoxWidget("Icon", self.ui.iconFrame)
        iconGroupBoxWidget.setObjectName("iconGroupBoxWidget")
        iconGroupBoxWidget.setPersistent(True)
        self.ui.iconTitleFrame.layout().addWidget(iconGroupBoxWidget)

        try:
            self.selectionChanged()
            self.setScriptJobEnabled(True)
        except NameError as error:
            logger.exception(error)

        self.createSequenceWidget()
        self.updateThumbnailSize()
        self.setupConnections()

    def loadUi(self):
        """Convenience method for loading the .ui file."""
        studioqt.loadUi(self, cls=BaseLoadWidget)

    def setCustomWidget(self, widget):
        """Convenience method for adding a custom widget when loading."""
        self.ui.customWidgetFrame.layout().addWidget(widget)

    def setupConnections(self):
        """Setup the connections for all the widgets."""
        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

    def createSequenceWidget(self):
        """
        Create a sequence widget to replace the static thumbnail widget.

        :rtype: None
        """
        self.ui.thumbnailButton = studiolibrary.widgets.ImageSequenceWidget(self)
        self.ui.thumbnailButton.setObjectName("thumbnailButton")
        self.ui.thumbnailFrame.layout().insertWidget(0, self.ui.thumbnailButton)

        path = self.item().thumbnailPath()
        if os.path.exists(path):
            self.setIconPath(path)

        if self.item().imageSequencePath():
            self.ui.thumbnailButton.setDirname(self.item().imageSequencePath())

    def setCaptureMenuEnabled(self, enable):
        """
        Set the capture menu for editing the thumbnail.

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
        Get the library item to be created.

        :rtype: studiolibrarymaya.BaseItem
        """
        return self._item

    def _itemValueChanged(self, field, value):
        """
        Triggered when the a field value has changed.

        :type field: str
        :type value: object
        """
        self._formWidget.setValue(field, value)

    def setItem(self, item):
        """
        Set the item for the preview widget.

        :type item: studiolibrarymaya.BaseItem
        """
        self._item = item

        self.ui.titleLabel.setText(item.MenuName)
        self.ui.titleIcon.setPixmap(QtGui.QPixmap(item.TypeIconPath))

        self._infoFormWidget = studiolibrary.widgets.FormWidget(self)
        self._infoFormWidget.setSchema(item.info())
        self.ui.infoFrame.layout().addWidget(self._infoFormWidget)

        options = item.loadSchema()
        if options:
            item.loadValueChanged.connect(self._itemValueChanged)

            formWidget = studiolibrary.widgets.FormWidget(self)
            formWidget.setObjectName(item.__class__.__name__ + "Form")
            formWidget.setSchema(item.loadSchema())
            formWidget.setValidator(item.loadValidator)

            self.ui.optionsFrame.layout().addWidget(formWidget)
            self._formWidget = formWidget
            formWidget.validate()

    def iconPath(self):
        """
        Get the icon path to be used for the thumbnail.

        :rtype str
        """
        return self._iconPath

    def setIconPath(self, path):
        """
        Set the icon path to be used for the thumbnail.

        :type path: str
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

        if self._formWidget:
            self._formWidget.savePersistentValues()

        if self._infoFormWidget:
            self._infoFormWidget.savePersistentValues()

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

    def selectionChanged(self):
        """
        Triggered when the users Maya selection has changed.

        :rtype: None
        """
        self._formWidget.validate()

    def accept(self):
        """
        Called when the user clicks the apply button.

        :rtype: None
        """
        self.item().loadFromCurrentOptions()
