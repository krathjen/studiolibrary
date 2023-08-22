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

import os
import logging

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt
import studiolibrary.widgets

try:
    import mutils
    import mutils.gui
    import maya.cmds
except ImportError as error:
    print(error)


logger = logging.getLogger(__name__)


class BaseSaveWidget(QtWidgets.QWidget):

    """Base widget for saving new items."""

    def __init__(self, item, parent=None):
        """
        :type item: studiolibrarymaya.BaseItem
        :type parent: QtWidgets.QWidget or None
        """
        QtWidgets.QWidget.__init__(self, parent)

        self.setObjectName("studioLibraryBaseSaveWidget")
        self.setWindowTitle("Save Item")

        studioqt.loadUi(self)

        self._item = item
        self._scriptJob = None
        self._formWidget = None

        widget = self.createTitleWidget()
        widget.ui.menuButton.hide()
        self.ui.titleFrame.layout().addWidget(widget)

        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.selectionSetButton.clicked.connect(self.showSelectionSetsMenu)

        try:
            self.setScriptJobEnabled(True)
        except NameError as error:
            logger.exception(error)

        self.createSequenceWidget()
        self.updateThumbnailSize()
        self.setItem(item)

    def showMenu(self):
        """
        Show the edit menu at the current cursor position.

        :rtype: QtWidgets.QAction
        """
        raise NotImplementedError("The title menu is not implemented")

    def createTitleWidget(self):
        """
        Create a new instance of the title bar widget.

        :rtype: QtWidgets.QFrame
        """

        class UI(object):
            """Proxy class for attaching ui widgets as properties."""
            pass

        titleWidget = QtWidgets.QFrame(self)
        titleWidget.setObjectName("titleWidget")
        titleWidget.ui = UI()

        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.setSpacing(0)
        vlayout.setContentsMargins(0, 0, 0, 0)

        hlayout = QtWidgets.QHBoxLayout(self)
        hlayout.setSpacing(0)
        hlayout.setContentsMargins(0, 0, 0, 0)

        vlayout.addLayout(hlayout)

        titleButton = QtWidgets.QLabel(self)
        titleButton.setText(self.item().NAME)
        titleButton.setObjectName("titleButton")
        titleWidget.ui.titleButton = titleButton

        hlayout.addWidget(titleButton)

        menuButton = QtWidgets.QPushButton(self)
        menuButton.setText("...")
        menuButton.setObjectName("menuButton")
        titleWidget.ui.menuButton = menuButton

        hlayout.addWidget(menuButton)

        titleWidget.setLayout(vlayout)

        return titleWidget

    def createSequenceWidget(self):
        """Create a sequence widget to replace the static thumbnail widget."""
        theme = None
        if self.parent():
            try:
                theme = self.parent().theme()
            except AttributeError as error:
                logger.debug("Cannot find theme for parent.")

        self.ui.thumbnailButton = studiolibrary.widgets.ImageSequenceWidget(self, theme=theme)
        self.ui.thumbnailButton.setObjectName("thumbnailButton")
        self.ui.thumbnailFrame.layout().insertWidget(0, self.ui.thumbnailButton)
        self.ui.thumbnailButton.clicked.connect(self.thumbnailCapture)

        text = "Click to capture a thumbnail from the current model panel.\n" \
               "CTRL + Click to show the capture window for better framing."

        self.ui.thumbnailButton.setToolTip(text)

        path = studiolibrary.resource.get("icons", "camera.svg")
        self.ui.thumbnailButton.addAction(
            path,
            "Capture new image",
            "Capture new image",
            self.thumbnailCapture
        )

        path = studiolibrary.resource.get("icons", "expand.svg")
        self.ui.thumbnailButton.addAction(
            path,
            "Show Capture window",
            "Show Capture window",
            self.showCaptureWindow
        )

        path = studiolibrary.resource.get("icons", "folder.svg")
        self.ui.thumbnailButton.addAction(
            path,
            "Load image from disk",
            "Load image from disk",
            self.showBrowseImageDialog
        )

        icon = studiolibrary.resource.icon("thumbnail_solid.png")
        self.ui.thumbnailButton.setIcon(icon)

    def setLibraryWindow(self, libraryWindow):
        """
        Set the library widget for the item.
        
        :type libraryWindow: studiolibrary.LibraryWindow
        :rtype: None
        """
        self.item().setLibraryWindow(libraryWindow)

    def libraryWindow(self):
        """
        Get the library widget for the item.

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
        Get the library item to be created.

        :rtype: studiolibrarymaya.BaseItem
        """
        return self._item

    def setItem(self, item):
        """
        Set the item to be created.

        :type item: studiolibrarymaya.BaseItem
        """
        self._item = item

        if os.path.exists(item.imageSequencePath()):
            self.setThumbnailPath(item.imageSequencePath())
        elif not item.isTHUMBNAIL_PATH():
            self.setThumbnailPath(item.thumbnailPath())

        schema = item.saveSchema()
        if schema:
            formWidget = studiolibrary.widgets.FormWidget(self)
            formWidget.setSchema(schema)
            formWidget.setValidator(item.saveValidator)

            # Used when overriding the item
            name = os.path.basename(item.path())
            formWidget.setValues({"name": name})

            self.ui.optionsFrame.layout().addWidget(formWidget)
            self._formWidget = formWidget

            formWidget.validate()
        else:
            self.ui.optionsFrame.setVisible(False)

    def showSelectionSetsMenu(self):
        """
        Show the selection sets menu for the current folder path.

        :rtype: None
        """
        from studiolibrarymaya import setsmenu

        path = self.folderPath()
        position = QtGui.QCursor().pos()
        libraryWindow = self.libraryWindow()

        menu = setsmenu.SetsMenu.fromPath(path, libraryWindow=libraryWindow)
        menu.exec_(position)

    def close(self):
        """Overriding the close method to disable the script job on close."""
        self._formWidget.savePersistentValues()
        self.setScriptJobEnabled(False)
        QtWidgets.QWidget.close(self)

    def scriptJob(self):
        """
        Get the script job object used when the users selection changes.

        :rtype: mutils.ScriptJob
        """
        return self._scriptJob

    def setScriptJobEnabled(self, enabled):
        """Set the script job used when the users selection changes."""
        if enabled:
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
        """Update the thumbnail button to the size of the widget."""
        width = self.width() - 10
        if width > 250:
            width = 250

        size = QtCore.QSize(width, width)
        self.ui.thumbnailButton.setIconSize(size)
        self.ui.thumbnailButton.setMaximumSize(size)
        self.ui.thumbnailFrame.setMaximumSize(size)

    def setFolderPath(self, path):
        """
        Set the destination folder path.

        :type path: str
        """
        self.formWidget().setValue("folder", path)

    def folderPath(self):
        """
        Return the folder path.

        :rtype: str
        """
        return self.formWidget().value("folder")

    def selectionChanged(self):
        """Triggered when the Maya selection changes."""
        if self.formWidget():
            self.formWidget().validate()

    def showByFrameDialog(self):
        """
        Show the by frame dialog.

        :rtype: None or QtWidgets.QDialogButtonBox.StandardButton
        """
        result = None
        text = 'To help speed up the playblast you can set the "by frame" ' \
               'to a number greater than 1. For example if the "by frame" ' \
               'is set to 2 it will playblast every second frame.'

        options = self.formWidget().values()
        byFrame = options.get("byFrame", 1)
        startFrame, endFrame = options.get("frameRange", [None, None])

        duration = 1
        if startFrame is not None and endFrame is not None:
            duration = endFrame - startFrame

        if duration > 100 and byFrame == 1:

            buttons = [
                QtWidgets.QDialogButtonBox.Ok,
                QtWidgets.QDialogButtonBox.Cancel
            ]

            result = studiolibrary.widgets.MessageBox.question(
                self.libraryWindow(),
                title="Playblast Tip",
                text=text,
                buttons=buttons,
                enableDontShowCheckBox=True,
            )

        return result

    def showBrowseImageDialog(self):
        """Show a file dialog for choosing an image from disc."""
        fileDialog = QtWidgets.QFileDialog(
            self,
            caption="Open Image",
            filter="Image Files (*.png *.jpg)"
        )

        fileDialog.fileSelected.connect(self.setThumbnailPath)
        fileDialog.exec_()

    def showCaptureWindow(self):
        """Show the capture window for framing."""
        self.thumbnailCapture(show=True)

    def setThumbnailPath(self, path):
        """
        Set the path to the thumbnail image or the image sequence directory.

        :type path: str
        """
        filename, extension = os.path.splitext(path)
        dst = studiolibrary.tempPath("thumbnail" + extension)

        studiolibrary.copyPath(path, dst, force=True)

        self.ui.thumbnailButton.setPath(dst)

    def _capturedCallback(self, src):
        """
        Triggered when capturing a thumbnail snapshot.

        :type src: str
        """
        path = os.path.dirname(src)
        self.setThumbnailPath(path)

    def thumbnailCapture(self, show=False):
        """Capture a playblast and save it to the temp thumbnail path."""
        options = self.formWidget().values()
        startFrame, endFrame = options.get("frameRange", [None, None])
        step = options.get("byFrame", 1)

        # Ignore the by frame dialog when the control modifier is pressed.
        if not studioqt.isControlModifier():
            result = self.showByFrameDialog()
            if result == QtWidgets.QDialogButtonBox.Cancel:
                return

        try:
            path = studiolibrary.tempPath("sequence", "thumbnail.jpg")
            mutils.gui.thumbnailCapture(
                show=show,
                path=path,
                startFrame=startFrame,
                endFrame=endFrame,
                step=step,
                clearCache=True,
                captured=self._capturedCallback,
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

        buttons = [
            QtWidgets.QDialogButtonBox.Yes,
            QtWidgets.QDialogButtonBox.Ignore,
            QtWidgets.QDialogButtonBox.Cancel
        ]


        parent = self.item().libraryWindow()
        button = studiolibrary.widgets.MessageBox.question(
            parent,
            title,
            text,
            buttons=buttons
        )

        if button == QtWidgets.QDialogButtonBox.Yes:
            self.thumbnailCapture()

        return button

    def accept(self):
        """Triggered when the user clicks the save button."""
        try:
            self.formWidget().validate()

            if self.formWidget().hasErrors():
                raise Exception("\n".join(self.formWidget().errors()))

            hasFrames = self.ui.thumbnailButton.hasFrames()
            if not hasFrames:
                button = self.showThumbnailCaptureDialog()
                if button == QtWidgets.QDialogButtonBox.Cancel:
                    return

            name = self.formWidget().value("name")
            folder = self.formWidget().value("folder")
            path = folder + "/" + name
            thumbnail = self.ui.thumbnailButton.firstFrame()

            self.save(path=path, thumbnail=thumbnail)

        except Exception as e:
            studiolibrary.widgets.MessageBox.critical(
                self.libraryWindow(),
                "Error while saving",
                str(e),
            )
            raise

    def save(self, path, thumbnail):
        """
        Save the item with the given objects to the given disc location path.

        :type path: str
        :type thumbnail: str
        """
        kwargs = self.formWidget().values()
        sequencePath = self.ui.thumbnailButton.dirname()

        item = self.item()
        item.setPath(path)
        item.safeSave(
            thumbnail=thumbnail,
            sequencePath=sequencePath,
            **kwargs
        )
        self.close()
