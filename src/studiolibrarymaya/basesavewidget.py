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
import shutil
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrarymaya
import studiolibrary.widgets

try:
    import mutils
    import mutils.gui
    import maya.cmds
except ImportError as error:
    print(error)

__all__ = [
    "BaseSaveWidget",
]

logger = logging.getLogger(__name__)


class BaseSaveWidget(QtWidgets.QWidget):

    """Base create widget for creating new maya items."""

    def __init__(self, item, parent=None):
        """
        :type item: studiolibrarymaya.BaseItem
        :type parent: QtWidgets.QWidget
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.setObjectName("studioLibraryMayaCreateWidget")

        self.setWindowTitle("Create Item")

        studioqt.loadUi(self)

        self._item = None
        self._iconPath = ""
        self._scriptJob = None
        self._formWidget = None
        self._focusWidget = None
        self._libraryWindow = None
        self._sequencePath = None

        text = "Click to capture a thumbnail from the current model panel.\n" \
               "CTRL + Click to show the capture window for better framing."

        self.ui.thumbnailButton.setToolTip(text)

        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.thumbnailButton.clicked.connect(self.thumbnailCapture)
        self.ui.browseFolderButton.clicked.connect(self.browseFolder)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

        try:
            self.selectionChanged()
            self.setScriptJobEnabled(True)
        except NameError as error:
            logger.exception(error)

        self.createSequenceWidget()
        self.setItem(item)
        self.updateThumbnailSize()

    def createSequenceWidget(self):
        """
        Create a sequence widget to replace the static thumbnail widget.

        :rtype: None
        """
        sequenceWidget = studiolibrary.widgets.ImageSequenceWidget(self)
        sequenceWidget.setObjectName("thumbnailButton")
        sequenceWidget.setStyleSheet(self.ui.thumbnailButton.styleSheet())
        sequenceWidget.setToolTip(self.ui.thumbnailButton.toolTip())

        path = studiolibrary.resource().get('icons/fa/camera.svg')
        sequenceWidget.addAction(
            path,
            "Capture new image",
            "Capture new image",
            self.thumbnailCapture
        )

        path = studiolibrary.resource().get('icons/fa/expand.svg')
        sequenceWidget.addAction(
            path,
            "Show Capture window",
            "Show Capture window",
            self.showCaptureWindow
        )

        path = studiolibrary.resource().get('icons/fa/folder.svg')
        sequenceWidget.addAction(
            path,
            "Load image from disk",
            "Load image from disk",
            self.showBrowseImageDialog
        )

        icon = studiolibrarymaya.resource().icon("thumbnail2")
        sequenceWidget.setIcon(icon)

        self.ui.thumbnailFrame.layout().insertWidget(0, sequenceWidget)
        self.ui.thumbnailButton.hide()
        self.ui.thumbnailButton = sequenceWidget
        self.ui.thumbnailButton.clicked.connect(self.thumbnailCapture)

    def setLibraryWindow(self, libraryWindow):
        """
        Set the library widget for the item.
        
        :type libraryWindow: studiolibrary.LibraryWindow
        :rtype: None
        """
        self.item().setLibraryWindow(libraryWindow)

    def libraryWindow(self):
        """
        Return the library widget for the item.

        :rtype: libraryWindow: studiolibrary.LibraryWindow
        """
        return self.item().libraryWindow()

    def formWidget(self):
        """
        Get the form widget instance.

        :rtype: studiolibrary.widgets.formwidget.FormWidget
        """
        return self._formWidget

    def item(self):
        """
        Return the library item to be created.

        :rtype: studiolibrarymaya.BaseItem
        """
        return self._item

    def setItem(self, item):
        """
        Set the base item to be created.

        :type item: studiolibrarymaya.BaseItem
        """
        self._item = item

        self.ui.titleLabel.setText(item.MenuName)
        self.ui.iconLabel.setPixmap(QtGui.QPixmap(item.TypeIconPath))

        schema = item.saveSchema()

        if not item.isDefaultThumbnailPath():
            self.setThumbnail(item.thumbnailPath())

        if schema:
            formWidget = studiolibrary.widgets.FormWidget(self)
            formWidget.setSchema(schema)
            formWidget.setValidator(item.saveValidator)

            formWidget.setValues({"name": item.name()})

            self.ui.optionsFrame.layout().addWidget(formWidget)
            self._formWidget = formWidget
            self.loadSettings()

            formWidget.stateChanged.connect(self._optionsChanged)
            formWidget.validate()
        else:
            self.ui.optionsFrame.setVisible(False)

    def _optionsChanged(self):
        """
        Get the options from the user settings.
        
        :rtype: dict 
        """
        self.saveSettings()

    def defaultValues(self):
        """
        Get all the default values for the save fields.
        
        :rtype: dict
        """
        values = {}

        for option in self.item().saveSchema():
            values[option.get('name')] = option.get('default')

        return values

    def loadSettings(self):
        """
        Return the settings object for saving the state of the widget.

        :rtype: studiolibrary.Settings
        """
        settings = studiolibrarymaya.settings()
        settings = settings.get(self.item().__class__.__name__, {})

        options = settings.get("saveOptions", {})
        values = self.defaultValues()

        # Only include the persistent fields
        if options:
            for option in self.item().saveSchema():
                name = option.get("name")
                persistent = option.get("persistent")
                if not persistent and name in options:
                    options[name] = values[name]

            self._formWidget.setValues(options)

    def saveSettings(self):
        """
        Save the current state of the widget to disc.

        :rtype: None
        """
        state = self._formWidget.persistentValues()
        settings = studiolibrarymaya.settings()
        settings[self.item().__class__.__name__] = {"saveOptions": state}
        studiolibrarymaya.saveSettings(settings)

    def iconPath(self):
        """
        Return the icon path to be used for the thumbnail.

        :rtype str
        """
        return self._iconPath

    def setIcon(self, icon):
        """
        Set the icon for the create widget thumbnail.

        :type icon: QtGui.QIcon
        """
        self.ui.thumbnailButton.setIcon(icon)
        self.ui.thumbnailButton.setIconSize(QtCore.QSize(200, 200))
        self.ui.thumbnailButton.setText("")

    def showSelectionSetsMenu(self):
        """
        Show the selection sets menu for the current folder path.

        :rtype: None
        """
        import setsmenu

        path = self.folderPath()
        position = QtGui.QCursor().pos()
        libraryWindow = self.libraryWindow()

        menu = setsmenu.SetsMenu.fromPath(path, libraryWindow=libraryWindow)
        menu.exec_(position)

    def close(self):
        """
        Overriding the close method so that we can disable the script job.

        :rtype: None
        """
        self.saveSettings()
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

    def name(self):
        """
        Return the str from the name field.

        :rtype: str
        """
        return self.ui.name.text().strip()

    def description(self):
        """
         Return the str from the comment field.

        :rtype: str
        """
        return self.ui.comment.toPlainText().strip()

    def folderFrame(self):
        """
        Return the frame that contains the folder edit, label and button.

        :rtype: QtWidgets.QFrame
        """
        return self.ui.folderFrame

    def setFolderPath(self, path):
        """
        Set the destination folder path.

        :type path: str
        :rtype: None
        """
        self.ui.folderEdit.setText(path)

    def folderPath(self):
        """
        Return the folder path.

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

    def selectionChanged(self):
        """
        Triggered when the Maya selection changes.

        :rtype: None
        """
        if self._formWidget:
            self._formWidget.validate()

    def sequencePath(self):
        """
        Return the playblast path.

        :rtype: str
        """
        return self._sequencePath

    def setSequencePath(self, path):
        """
        Set the disk location for the image sequence to be saved.

        :type path: str
        :rtype: None
        """
        self._sequencePath = path
        self.ui.thumbnailButton.setDirname(os.path.dirname(path))

    def showByFrameDialog(self):
        """
        Show the by frame dialog.

        :rtype: None
        """
        text = 'To help speed up the playblast you can set the "by frame" ' \
               'to a number greater than 1. For example if the "by frame" ' \
               'is set to 2 it will playblast every second frame.'

        options = self._formWidget.values()
        byFrame = options.get("byFrame", 1)
        startFrame, endFrame = options.get("frameRange", [None, None])

        duration = 1
        if startFrame is not None and endFrame is not None:
            duration = endFrame - startFrame

        if duration > 100 and byFrame == 1:

            buttons = QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel

            result = studiolibrary.widgets.MessageBox.question(
                self.libraryWindow(),
                title="Anim Item Tip",
                text=text,
                buttons=buttons,
                enableDontShowCheckBox=True,
            )

            if result != QtWidgets.QMessageBox.Ok:
                raise Exception("Canceled!")

    def showBrowseImageDialog(self):
        """Show a file dialog for choosing an image from disc."""
        fileDialog = QtWidgets.QFileDialog(
            self,
            caption="Open Image",
            filter="Image Files (*.png *.jpg)"
        )

        fileDialog.fileSelected.connect(self.setThumbnail)
        fileDialog.exec_()

    def showCaptureWindow(self):
        """Show the capture window for framing."""
        self.thumbnailCapture(show=True)

    def setSequence(self, src):
        """
        Set the sequence path for the thumbnail widget.
        
        :type src: str 
        """
        self.setThumbnail(src, sequence=True)

    def setThumbnail(self, src, sequence=False):
        """
        Triggered when the user captures a thumbnail/playblast.

        :rtype: None
        """
        filename, extension = os.path.splitext(src)

        dst = studiolibrary.tempPath("thumbnail" + extension)

        studiolibrary.copyPath(src, dst, force=True)

        self._iconPath = dst
        self.ui.thumbnailButton.setPath(dst)

        if sequence:
            self.setSequencePath(src)

    def thumbnailCapture(self, show=False):
        """Capture a playblast and save it to the temp thumbnail path."""
        options = self._formWidget.values()
        startFrame, endFrame = options.get("frameRange", [None, None])
        step = options.get("byFrame", 1)

        # Ignore the by frame dialog when the control modifier is pressed.
        if not studioqt.isControlModifier():
            self.showByFrameDialog()

        try:
            path = studiolibrary.tempPath("sequence", "thumbnail.jpg")
            mutils.gui.thumbnailCapture(
                show=show,
                path=path,
                startFrame=startFrame,
                endFrame=endFrame,
                step=step,
                clearCache=True,
                captured=self.setSequence,
            )

        except Exception as e:
            title = "Error while capturing thumbnail"
            studiolibrary.widgets.MessageBox.critical(self.libraryWindow(), title, str(e))
            raise

    def showThumbnailCaptureDialog(self):
        """
        Ask the user if they would like to capture a thumbnail.

        :rtype: int
        """
        title = "Create a thumbnail"
        text = "Would you like to capture a thumbnail?"

        buttons = QtWidgets.QMessageBox.Yes | \
                  QtWidgets.QMessageBox.Ignore | \
                  QtWidgets.QMessageBox.Cancel

        parent = self.item().libraryWindow()
        button = studiolibrary.widgets.MessageBox.question(
            parent,
            title,
            text,
            buttons=buttons
        )

        if button == QtWidgets.QMessageBox.Yes:
            self.thumbnailCapture()

        return button

    def accept(self):
        """Triggered when the user clicks the save button."""
        try:
            path = self.folderPath()

            options = self._formWidget.values()
            name = options.get("name")

            objects = maya.cmds.ls(selection=True) or []

            if not path:
                raise Exception("No folder selected. Please select a destination folder.")

            if not name:
                raise Exception("No name specified. Please set a name before saving.")

            if not objects:
                raise Exception("No objects selected. Please select at least one object.")

            if not os.path.exists(self.iconPath()):
                button = self.showThumbnailCaptureDialog()
                if button == QtWidgets.QMessageBox.Cancel:
                    return

            path += "/" + name
            iconPath = self.iconPath()

            self.save(
                objects,
                path=path,
                iconPath=iconPath,
            )

        except Exception as e:
            title = "Error while saving"
            studiolibrary.widgets.MessageBox.critical(self.libraryWindow(), title, str(e))
            raise

    def save(self, objects, path, iconPath):
        """
        Save the item with the given objects to the given disc location path.

        :type objects: list[str]
        :type path: str
        :type iconPath: str

        :rtype: None
        """
        item = self.item()

        options = self._formWidget.values()

        sequencePath = self.sequencePath()
        if sequencePath:
            sequencePath = os.path.dirname(sequencePath)

        item.save(
            path,
            objects,
            iconPath=iconPath,
            sequencePath=sequencePath,
            **options
        )
        self.close()
