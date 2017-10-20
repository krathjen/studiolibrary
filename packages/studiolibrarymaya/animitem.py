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
"""
#---------------------------------------------------------------------------
# Saving an anim item
#---------------------------------------------------------------------------

from studiolibrarymaya import animitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.anim"
objects = maya.cmds.ls(selection=True) or []

item = animitem.AnimItem(path)
item.save(objects=objects, startFrame=0, endFrame=200)

#---------------------------------------------------------------------------
# Loading an anim item
#---------------------------------------------------------------------------

from studiolibrarymaya import animitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.anim"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

item = animitem.AnimItem(path)
item.load(
    objects=objects,
    namespaces=namespaces,
    option="replaceCompletely",
    connect=False,
    currentTime=False,
)
"""

import os
import shutil
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary
import studiolibrarymaya

from studiolibrarymaya import baseitem
from studiolibrarymaya import basecreatewidget
from studiolibrarymaya import basepreviewwidget

try:
    import mutils
    import mutils.gui
    import maya.cmds
    PasteOption = mutils.PasteOption
except ImportError, e:
    print e


__all__ = [
    "AnimItem",
    "AnimItemError",
    "AnimCreateWidget",
    "AnimPreviewWidget",
]

logger = logging.getLogger(__name__)


class AnimItemError(Exception):

    """Base class for exceptions in this module."""


class ValidateAnimError(AnimItemError):

    """Raised when there is an invalid animation option"""


class AnimItem(baseitem.BaseItem):

    def __init__(self, *args, **kwargs):
        """
        Create a new instance of the anim item from the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        baseitem.BaseItem.__init__(self, *args, **kwargs)

        self._items = []

        self.setTransferClass(mutils.Animation)
        self.setTransferBasename("")

    def previewWidget(self, libraryWidget):
        """
        Return the widget to be shown when the user clicks on the item.

        Overriding this method to add support for loading many animations.

        :type libraryWidget: studiolibrary.LibraryWidget
        :rtype: AnimationPreviewWidget
        """
        items = libraryWidget.selectedItems()
        self.setItems(items)
        return AnimPreviewWidget(parent=None, item=self)

    def imageSequencePath(self):
        """
        Return the image sequence location for playing the animation preview.

        :rtype: str
        """
        return self.path() + "/sequence"

    def items(self):
        """
        :rtype: list[AnimItem]
        """
        return self._items

    def setItems(self, items):
        """
        :type items: list[AnimItem]
        """
        self._items = items

    def startFrame(self):
        """Return the start frame for the animation."""
        return self.transferObject().startFrame()

    def endFrame(self):
        """Return the end frame for the animation."""
        return self.transferObject().endFrame()

    def doubleClicked(self):
        """Overriding this method to load the animation on double click."""
        self.loadFromSettings()

    def loadFromSettings(self, sourceStart=None, sourceEnd=None):
        """
        Load the animation using the settings for this item.

        :type sourceStart: int
        :type sourceEnd: int
        """
        objects = maya.cmds.ls(selection=True) or []
        namespaces = self.namespaces()

        settings = self.settings()
        option = str(settings.get("pasteOption"))
        connect = bool(settings.get("connectOption"))
        currentTime = bool(settings.get("currentTime"))

        try:
            self.load(
                objects=objects,
                option=option,
                connect=connect,
                namespaces=namespaces,
                currentTime=currentTime,
                sourceStart=sourceStart,
                sourceEnd=sourceEnd,
            )

        except Exception, e:
            self.showErrorDialog("Item Error", str(e))
            raise

    def load(
        self,
        objects=None,
        namespaces=None,
        startFrame=None,
        sourceStart=None,
        sourceEnd=None,
        option=None,
        connect=None,
        currentTime=False,
    ):
        """
        :type objects: list[str]
        :type namespaces: list[str]
        :type startFrame: bool
        :type sourceStart: int
        :type sourceEnd: int
        :type option: PasteOption or str
        :type connect: bool
        :type currentTime: bool
        :rtype: None
        """
        logger.info(u'Loading: {0}'.format(self.path()))

        objects = objects or []

        if sourceStart is None:
            sourceStart = self.startFrame()

        if sourceEnd is None:
            sourceEnd = self.endFrame()

        items = self.items()

        if len(items) > 1:

            paths = []
            for item in items:
                path = item.transferObject().path()
                paths.append(path)

            mutils.loadAnims(
                paths=paths,
                spacing=5,
                objects=objects,
                namespaces=namespaces,
                currentTime=currentTime,
                option=option,
                connect=connect,
                startFrame=startFrame,
                showDialog=True,
            )
        else:
            self.transferObject().load(
                objects=objects,
                namespaces=namespaces,
                currentTime=currentTime,
                connect=connect,
                option=option,
                startFrame=startFrame,
                sourceTime=(sourceStart, sourceEnd)
            )

        logger.info(u'Loaded: {0}'.format(self.path()))

    def save(
        self,
        objects,
        path="",
        contents=None,
        iconPath="",
        fileType="",
        startFrame=None,
        endFrame=None,
        bakeConnected=False,
        description="",
    ):
        """
        :type path: str
        :type objects: list[str] or None
        :type contents: list[str] or None
        :type iconPath: str
        :type startFrame: int or None
        :type endFrame: int or None
        :type fileType: str
        :type bakeConnected: bool
        :type description: str

        :rtype: None
        """
        if path and not path.endswith(".anim"):
            path += ".anim"

        contents = contents or list()

        tempDir = mutils.TempDir("Transfer", clean=True)
        tempPath = tempDir.path() + "/transfer.anim"

        t = self.transferClass().fromObjects(objects)
        t.setMetadata("description", description)
        t.save(
            tempPath,
            fileType=fileType,
            time=[startFrame, endFrame],
            bakeConnected=bakeConnected,
        )

        if iconPath:
            contents.append(iconPath)

        contents.extend(t.paths())

        studiolibrary.LibraryItem.save(self, path=path, contents=contents)


class AnimCreateWidget(basecreatewidget.BaseCreateWidget):

    def __init__(self, item=None, parent=None):
        """
        :type item: studiolibrary.LibraryItem
        :type parent: QtWidgets.QWidget
        """
        item = item or AnimItem()
        super(AnimCreateWidget, self).__init__(item, parent=parent)

        self._sequencePath = None

        start, end = (1, 100)

        try:
            start, end = mutils.currentFrameRange()
        except NameError, e:
            logger.exception(e)

        self.createSequenceWidget()

        validator = QtGui.QIntValidator(-50000000, 50000000, self)
        self.ui.endFrameEdit.setValidator(validator)
        self.ui.startFrameEdit.setValidator(validator)

        self.ui.endFrameEdit.setText(str(int(end)))
        self.ui.startFrameEdit.setText(str(int(start)))

        self.ui.byFrameEdit.setValidator(QtGui.QIntValidator(1, 1000, self))
        self.ui.frameRangeButton.clicked.connect(self.showFrameRangeMenu)

        settings = studiolibrarymaya.settings()

        byFrame = settings.get("byFrame")
        self.setByFrame(byFrame)

        fileType = settings.get("fileType")
        self.setFileType(fileType)

        self.ui.byFrameEdit.textChanged.connect(self.saveSettings)
        self.ui.fileTypeComboBox.currentIndexChanged.connect(self.saveSettings)

    def createSequenceWidget(self):
        """
        Create a sequence widget to replace the static thumbnail widget.

        :rtype: None
        """
        self.ui.sequenceWidget = studioqt.ImageSequenceWidget(self)
        self.ui.sequenceWidget.setStyleSheet(self.ui.thumbnailButton.styleSheet())
        self.ui.sequenceWidget.setToolTip(self.ui.thumbnailButton.toolTip())

        icon = studiolibrarymaya.resource().icon("thumbnail2")
        self.ui.sequenceWidget.setIcon(icon)

        self.ui.thumbnailFrame.layout().insertWidget(0, self.ui.sequenceWidget)
        self.ui.thumbnailButton.hide()
        self.ui.thumbnailButton = self.ui.sequenceWidget

        self.ui.sequenceWidget.clicked.connect(self.thumbnailCapture)

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
        self.ui.sequenceWidget.setDirname(os.path.dirname(path))

    def startFrame(self):
        """
        Return the start frame that will be exported.

        :rtype: int | None
        """
        try:
            return int(float(str(self.ui.startFrameEdit.text()).strip()))
        except ValueError:
            return None

    def endFrame(self):
        """
        Return the end frame that will be exported.

        :rtype: int | None
        """
        try:
            return int(float(str(self.ui.endFrameEdit.text()).strip()))
        except ValueError:
            return None

    def duration(self):
        """
        Return the duration of the animation that will be exported.

        :rtype: int
        """
        return self.endFrame() - self.startFrame()

    def byFrame(self):
        """
        Return the by frame for the playblast.

        :rtype: int
        """
        return int(float(self.ui.byFrameEdit.text()))

    def setByFrame(self, byFrame):
        """
        Set the by frame for the playblast.

        :type byFrame: int or str
        :rtype: None
        """
        self.ui.byFrameEdit.setText(str(byFrame))

    def fileType(self):
        """
        Return the file type for the animation.

        :rtype: str
        """
        return self.ui.fileTypeComboBox.currentText()

    def setFileType(self, fileType):
        """
        Set the file type for the animation.

        :type fileType: str
        """
        fileTypeIndex = self.ui.fileTypeComboBox.findText(fileType)
        if fileTypeIndex:
            self.ui.fileTypeComboBox.setCurrentIndex(fileTypeIndex)

    def settings(self):
        """
        Overriding this method to add support for saving the byFrame and type.
        
        :rtype: dict 
        """
        settings = super(AnimCreateWidget, self).settings()

        settings["byFrame"] = self.byFrame()
        settings["fileType"] = self.fileType()

        return settings

    def showFrameRangeMenu(self):
        """
        Show the frame range menu at the current cursor location.

        :rtype: None
        """
        action = mutils.gui.showFrameRangeMenu()
        if action:
            self.setFrameRange(action.frameRange())

    def setFrameRange(self, frameRange):
        """
        Set the frame range for the animation to be exported.

        :type frameRange: (int, int)
        """
        start, end = frameRange

        if start == end:
            end += 1

        self.setStartFrame(start)
        self.setEndFrame(end)

    def setEndFrame(self, frame):
        """
        Set the end frame range for the animation to be exported.

        :type frame: int or str
        """
        self.ui.endFrameEdit.setText(str(int(frame)))

    def setStartFrame(self, frame):
        """
        Set the start frame range for the animation to be exported.

        :type frame: int or str
        """
        self.ui.startFrameEdit.setText(str(int(frame)))

    def showByFrameDialog(self):
        """
        Show the by frame dialog.

        :rtype: None
        """
        text = 'To help speed up the playblast you can set the "by frame" ' \
               'to a number greater than 1. For example if the "by frame" ' \
               'is set to 2 it will playblast every second frame.'

        if self.duration() > 100 and self.byFrame() == 1:

            buttons = QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel

            result = studioqt.MessageBox.question(
                self.libraryWidget(),
                title="Anim Item Tip",
                text=text,
                buttons=buttons,
                enableDontShowCheckBox=True,
            )

            if result != QtWidgets.QMessageBox.Ok:
                raise Exception("Canceled!")

    def _thumbnailCaptured(self, playblastPath):
        """
        Triggered when the user captures a thumbnail/playblast.

        :type playblastPath: str
        :rtype: None
        """
        thumbnailPath = mutils.gui.tempThumbnailPath()
        shutil.copyfile(playblastPath, thumbnailPath)

        self.setIconPath(thumbnailPath)
        self.setSequencePath(playblastPath)

    def thumbnailCapture(self):
        """
        :raise: AnimItemError
        """
        startFrame, endFrame = mutils.selectedFrameRange()
        if startFrame == endFrame:
            self.validateFrameRange()
            endFrame = self.endFrame()
            startFrame = self.startFrame()

        # Ignore the by frame dialog when the control modifier is pressed.
        if not studioqt.isControlModifier():
            self.showByFrameDialog()

        try:
            step = self.byFrame()
            playblastPath = mutils.gui.tempPlayblastPath()

            mutils.gui.thumbnailCapture(
                path=playblastPath,
                startFrame=startFrame,
                endFrame=endFrame,
                step=step,
                clearCache=True,
                captured=self._thumbnailCaptured,
            )

        except Exception, e:
            title = "Error while capturing thumbnail"
            QtWidgets.QMessageBox.critical(self.libraryWidget(), title, str(e))
            raise

    def validateFrameRange(self):
        """
        :raise: ValidateAnimationError
        """
        if self.startFrame() is None or self.endFrame() is None:
            msg = "Please choose a start frame and an end frame."
            raise ValidateAnimError(msg)

    def save(self, objects, path, iconPath, description):
        """
        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type description: str
        :rtype: None
        """
        contents = None
        endFrame = self.endFrame()
        startFrame = self.startFrame()
        fileType = self.ui.fileTypeComboBox.currentText()
        bakeConnected = int(self.ui.bakeCheckBox.isChecked())

        item = self.item()
        iconPath = self.iconPath()

        sequencePath = self.sequencePath()
        if sequencePath:
            contents = [os.path.dirname(sequencePath)]

        item.save(
            path=path,
            objects=objects,
            contents=contents,
            iconPath=iconPath,
            fileType=fileType,
            endFrame=endFrame,
            startFrame=startFrame,
            description=description,
            bakeConnected=bakeConnected
        )


class AnimPreviewWidget(basepreviewwidget.BasePreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :type item: AnimItem
        :type libraryWidget: studiolibrary.LibraryWidget
        """
        super(AnimPreviewWidget, self).__init__(*args, **kwargs)

        self._items = []

        self.createSequenceWidget()

        self.connect(self.ui.currentTime, QtCore.SIGNAL("stateChanged(int)"), self.saveSettings)
        self.connect(self.ui.helpCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.showHelpImage)
        self.connect(self.ui.connectCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.connectChanged)
        self.connect(self.ui.option, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.optionChanged)

    def createSequenceWidget(self):
        """
        Create a sequence widget to replace the static thumbnail widget.

        :rtype: None
        """
        self.ui.sequenceWidget = studioqt.ImageSequenceWidget(self)
        self.ui.sequenceWidget.setStyleSheet(self.ui.thumbnailButton.styleSheet())
        self.ui.sequenceWidget.setToolTip(self.ui.thumbnailButton.toolTip())
        self.ui.sequenceWidget.setDirname(self.item().imageSequencePath())

        self.ui.thumbnailFrame.layout().insertWidget(0, self.ui.sequenceWidget)
        self.ui.thumbnailButton.hide()
        self.ui.thumbnailButton = self.ui.sequenceWidget

    def setItem(self, item):
        """
        :type item: AnimItem
        :rtype: None
        """
        super(AnimPreviewWidget, self).setItem(item)

        startFrame = str(item.startFrame())
        endFrame = str(item.endFrame())

        self.ui.start.setText(startFrame)
        self.ui.end.setText(endFrame)
        self.ui.sourceStartEdit.setText(startFrame)
        self.ui.sourceEndEdit.setText(endFrame)

    def setItems(self, items):
        """
        :rtype: list[AnimItem]
        """
        self._items = items

    def sourceStart(self):
        """
        :rtype int
        """
        return int(self.ui.sourceStartEdit.text())

    def sourceEnd(self):
        """
        :rtype int
        """
        return int(self.ui.sourceEndEdit.text())

    def showHelpImage(self, value, save=True):
        """
        :type value:
        :type save:
        """
        if value:
            self.ui.helpImage.show()
        else:
            self.ui.helpImage.hide()

        if save:
            self.saveSettings()

    def settings(self):
        """
        :rtype: dict
        """
        settings = super(AnimPreviewWidget, self).settings()

        settings["pasteOption"] = str(self.ui.option.currentText())
        settings["currentTime"] = bool(self.ui.currentTime.isChecked())
        settings["showHelpImage"] = bool(self.ui.helpCheckBox.isChecked())
        settings["connectOption"] = float(self.ui.connectCheckBox.isChecked())

        return settings

    def setSettings(self, settings):
        """
        :type settings: dict
        """
        connect = settings.get("connectOption")
        pasteOption = settings.get("pasteOption")
        currentTime = settings.get("currentTime")
        showHelpImage = settings.get("showHelpImage")

        self.ui.currentTime.setChecked(currentTime)
        self.ui.connectCheckBox.setChecked(bool(connect))
        self.ui.helpCheckBox.setChecked(showHelpImage)

        self.optionChanged(pasteOption, save=False)
        self.showHelpImage(showHelpImage, save=False)

        super(AnimPreviewWidget, self).setSettings(settings)

    def connectChanged(self, value):
        """
        :type value: bool
        """
        self.optionChanged(str(self.ui.option.currentText()))

    def optionChanged(self, text, save=True):
        """
        :type text: str
        :type save: bool
        """
        imageText = text

        if text == "replace all":
            imageText = "replaceCompletely"
            self.ui.connectCheckBox.setEnabled(False)
        else:
            self.ui.connectCheckBox.setEnabled(True)

        connect = ""
        if self.ui.connectCheckBox.isChecked() and text != "replace all":
            connect = "Connect"

        basename = "{0}{1}".format(imageText, connect)
        imageIcon = studiolibrarymaya.resource().icon(basename)

        self.ui.helpImage.setIcon(imageIcon)
        index = self.ui.option.findText(text)
        if index:
            self.ui.option.setCurrentIndex(index)
        if save:
            self.saveSettings()

    def accept(self):
        """
        :rtype: None
        """
        sourceStart = self.sourceStart()
        sourceEnd = self.sourceEnd()

        self.item().loadFromSettings(
            sourceStart=sourceStart,
            sourceEnd=sourceEnd
        )


# Register the anim item to the Studio Library
iconPath = studiolibrarymaya.resource().get("icons", "animation.png")

AnimItem.Extensions = [".anim"]
AnimItem.MenuName = "Animation"
AnimItem.MenuIconPath = iconPath
AnimItem.TypeIconPath = iconPath
AnimItem.CreateWidgetClass = AnimCreateWidget

studiolibrary.registerItem(AnimItem)
