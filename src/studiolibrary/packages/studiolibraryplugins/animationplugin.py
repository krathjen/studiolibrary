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

"""
#---------------------------------------------------------------------------
# Saving an animation record
#---------------------------------------------------------------------------

from studiolibraryplugins import animationplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.anim"
objects = maya.cmds.ls(selection=True) or []

record = animationplugin.Record(path)
record.save(objects=objects, startFrame=0, endFrame=200)

#---------------------------------------------------------------------------
# Loading an animation record
#---------------------------------------------------------------------------

from studiolibraryplugins import animationplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.anim"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

record = animationplugin.Record(path)
record.load(
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
import studiolibraryplugins

from studiolibraryplugins import mayabaseplugin

try:
    import mutils
    import mutils.gui
    import maya.cmds
    PasteOption = mutils.PasteOption
except ImportError, msg:
    print msg


logger = logging.getLogger(__name__)


class AnimationPluginError(Exception):

    """Base class for exceptions in this module."""


class ValidateAnimationError(AnimationPluginError):

    """Raised when there is invalid animation"""


class Plugin(mayabaseplugin.Plugin):

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        mayabaseplugin.Plugin.__init__(self, library)

        iconPath = studiolibraryplugins.resource().get("icons", "animation.png")

        self.setName("Animation")
        self.setExtension("anim")
        self.setIconPath(iconPath)

        settings = self.settings()
        settings.setdefault('byFrame', 1)
        settings.setdefault('currentTime', False)
        settings.setdefault('byFrameDialog', True)
        settings.setdefault('connectOption', False)
        settings.setdefault('showHelpImage', False)
        settings.setdefault('pasteOption', "replace")

    def record(self, path=None):
        """
        :type path: str or None
        :rtype: Record
        """
        return Record(path=path, plugin=self)

    def createWidget(self, parent):
        """
        :type parent: QtWidgets.QWidget
        :rtype: AnimationCreateWidget
        """
        record = self.record()
        return AnimationCreateWidget(parent=parent, record=record)

    def previewWidget(self, parent, record):
        """
        :type parent: QtWidgets.QWidget
        :type record: Record
        :rtype: AnimationPreviewWidget
        """
        records = self.libraryWidget().selectedRecords()
        record.setRecords(records)

        return AnimationPreviewWidget(parent=parent, record=record)


class Record(mayabaseplugin.Record):

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        mayabaseplugin.Record.__init__(self, *args, **kwargs)

        self._records = []

        self.setTransferClass(mutils.Animation)
        self.setTransferBasename("")
        self.setImageSequencePath(self.path() + "/sequence")

    def records(self):
        """
        :rtype: list[Record]
        """
        return self._records

    def setRecords(self, records):
        """
        :type records: list[Record]
        """
        self._records = records

    def rename(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        self.resetImageSequence()
        mayabaseplugin.Record.rename(self, *args, **kwargs)

    def startFrame(self):
        """
        :rtype: int
        """
        if self.transferObject().isLegacy():
            return int(self.metaFile().get("start", 0))
        else:
            return self.transferObject().startFrame()

    def endFrame(self):
        """
        :rtype: int
        """
        if self.transferObject().isLegacy():
            return int(self.metaFile().get("end", 0))
        else:
            return self.transferObject().endFrame()

    def doubleClicked(self):
        """
        :return: None
        """
        self.loadFromSettings()

    def loadFromSettings(self, sourceStart=None, sourceEnd=None):
        """
        :rtype: None
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

        except Exception, msg:
            self.showErrorDialog(msg)
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
        :type option: PasteOption
        :type connect: bool
        :type currentTime: bool
        :rtype: None
        """
        logger.info("Loading: %s" % self.path())
        objects = objects or []

        if sourceStart is None:
            sourceStart = self.startFrame()

        if sourceEnd is None:
            sourceEnd = self.endFrame()

        records = self.records()

        if len(records) > 1:

            paths = []
            for record in records:
                path = record.transferObject().path()
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

        logger.info("Loaded: %s" % self.path())

    def save(self, objects, path=None, contents=None, iconPath=None,
             startFrame=None, endFrame=None, bakeConnected=False):
        """
        :type contents: list[str]
        :type iconPath: str
        :type startFrame: int
        :type endFrame: int
        :type bakeConnected: bool
        :rtype: None
        """
        contents = contents or list()

        tempDir = mutils.TempDir("Transfer", clean=True)
        tempPath = tempDir.path() + "/transfer.anim"

        t = self.transferClass().fromObjects(objects)
        t.save(tempPath, time=[startFrame, endFrame], bakeConnected=bakeConnected)

        if iconPath:
            contents.append(iconPath)

        contents.extend(t.paths())

        self.metaFile().set("start", startFrame)
        self.metaFile().set("end", endFrame)
        studiolibrary.Record.save(self, path=path, contents=contents)


class AnimationCreateWidget(mayabaseplugin.CreateWidget):

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        mayabaseplugin.CreateWidget.__init__(self, *args, **kwargs)

        self._sequencePath = None
        start, end = mutils.currentFrameRange()

        self.ui.sequenceWidget = studioqt.ImageSequenceWidget(self)

        icon = studiolibraryplugins.resource().icon("thumbnail")
        self.ui.sequenceWidget.setIcon(icon)

        self.ui.layout().insertWidget(1, self.ui.sequenceWidget)
        self.ui.snapshotButton.parent().hide()
        self.ui.sequenceWidget.setStyleSheet(self.ui.snapshotButton.styleSheet())

        validator = QtGui.QIntValidator(-50000000, 50000000, self)
        self.ui.endFrameEdit.setValidator(validator)
        self.ui.startFrameEdit.setValidator(validator)

        self.ui.endFrameEdit.setText(str(int(end)))
        self.ui.startFrameEdit.setText(str(int(start)))

        self.ui.byFrameEdit.setValidator(QtGui.QIntValidator(1, 1000, self))
        self.ui.byFrameEdit.setText(str(self.settings().get("byFrame")))

        self.ui.sequenceWidget.clicked.connect(self.snapshot)
        self.ui.setEndFrameButton.clicked.connect(self.setEndFrame)
        self.ui.setStartFrameButton.clicked.connect(self.setStartFrame)

    def sequencePath(self):
        """
        :rtype: str
        """
        return self._sequencePath

    def startFrame(self):
        """
        :rtype: int | None
        """
        try:
            return int(float(str(self.ui.startFrameEdit.text()).strip()))
        except ValueError:
            return None

    def endFrame(self):
        """
        :rtype: int | None
        """
        try:
            return int(float(str(self.ui.endFrameEdit.text()).strip()))
        except ValueError:
            return None

    def duration(self):
        """
        :rtype: int
        """
        return self.endFrame() - self.startFrame()

    def byFrame(self):
        """
        :rtype: int
        """
        return int(float(self.ui.byFrameEdit.text()))

    def close(self):
        """
        :rtype: None
        """
        self.settings().set("byFrame", self.byFrame())
        self.settings().save()
        mayabaseplugin.CreateWidget.close(self)

    def setEndFrame(self):
        """
        :rtype: None
        """
        start, end = mutils.selectedFrameRange()
        self.ui.endFrameEdit.setText(str(end))

    def setStartFrame(self):
        """
        :rtype: None
        """
        start, end = mutils.selectedFrameRange()
        self.ui.startFrameEdit.setText(str(start))

    def showByFrameDialog(self):
        """
        :rtype: None
        """
        msg = """To help speed up the playblast you can set the "by frame" to a number greater than 1. \
For example if the "by frame" is set to 2 it will playblast every second frame.

Would you like to show this message again?"""

        if self.settings().get("byFrameDialog") and self.duration() > 100 and self.byFrame() == 1:

            buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel
            result = studioqt.MessageBox.question(self, "Snapshot tip", msg, buttons)

            if result == QtWidgets.QMessageBox.Cancel:
                raise Exception("Cancelled!")
            elif result == QtWidgets.QMessageBox.No:
                self.settings().set("byFrameDialog", False)

    def _captured(self, playblastPath):
        """
        Triggered when the user captures a thumbnail/playblast.

        :type playblastPath: str
        :rtype: None
        """
        thumbnailPath = mutils.gui.tempThumbnailPath()
        shutil.copyfile(playblastPath, thumbnailPath)

        self.setIconPath(thumbnailPath)
        self.setSequencePath(playblastPath)

    def snapshot(self):
        """
        :raise: AnimationPluginError
        """
        startFrame, endFrame = mutils.selectedFrameRange()
        if startFrame == endFrame:
            self.validateFrameRange()
            endFrame = self.endFrame()
            startFrame = self.startFrame()

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
                captured=self._captured,
            )

        except Exception, msg:
            title = "Error while taking snapshot"
            QtWidgets.QMessageBox.critical(None, title, str(msg))
            raise

    def setSequencePath(self, path):
        """
        :type path: str
        :rtype: None
        """
        self._sequencePath = path
        self.ui.sequenceWidget.setDirname(os.path.dirname(path))

    def validateFrameRange(self):
        """
        :raise: ValidateAnimationError
        """
        if self.startFrame() is None or self.endFrame() is None:
            msg = "Please choose a start frame and an end frame."
            raise ValidateAnimationError(msg)

    def save(self, objects, path,  iconPath, description):
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
        bakeConnected = int(self.ui.bakeCheckBox.isChecked())

        record = self.record()
        record.setDescription(description)
        iconPath = self.iconPath()

        sequencePath = self.sequencePath()
        if sequencePath:
            contents = [os.path.dirname(sequencePath)]

        record.save(
            path=path,
            objects=objects,
            contents=contents,
            iconPath=iconPath,
            endFrame=endFrame,
            startFrame=startFrame,
            bakeConnected=bakeConnected
        )


class AnimationPreviewWidget(mayabaseplugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :type record: Record
        :type libraryWidget: studiolibrary.LibraryWidget
        """
        mayabaseplugin.PreviewWidget.__init__(self, *args, **kwargs)

        self._records = []

        self.connect(self.ui.currentTime, QtCore.SIGNAL("stateChanged(int)"), self.updateState)
        self.connect(self.ui.helpCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.showHelpImage)
        self.connect(self.ui.connectCheckBox, QtCore.SIGNAL('stateChanged(int)'), self.connectChanged)
        self.connect(self.ui.option, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.optionChanged)

        self.loadSettings()

    def setRecord(self, record):
        """
        :type record: Record
        :rtype: None
        """
        mayabaseplugin.PreviewWidget.setRecord(self, record)

        startFrame = str(record.startFrame())
        endFrame = str(record.endFrame())

        self.ui.start.setText(startFrame)
        self.ui.end.setText(endFrame)
        self.ui.sourceStartEdit.setText(startFrame)
        self.ui.sourceEndEdit.setText(endFrame)

    def setRecords(self, records):
        """
        :rtype: list[Record]
        """
        self._records = records

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

    def state(self):
        """
        :rtype: dict
        """
        state = super(AnimationPreviewWidget, self).state()

        state["pasteOption"] = str(self.ui.option.currentText())
        state["currentTime"] = bool(self.ui.currentTime.isChecked())
        state["showHelpImage"] = bool(self.ui.helpCheckBox.isChecked())
        state["connectOption"] = float(self.ui.connectCheckBox.isChecked())

        return state

    def setState(self, state):
        """
        :type state: dict
        """
        connect = state.get("connectOption")
        pasteOption = state.get("pasteOption")
        currentTime = state.get("currentTime")
        showHelpImage = state.get("showHelpImage")

        self.ui.currentTime.setChecked(currentTime)
        self.ui.connectCheckBox.setChecked(connect)
        self.ui.helpCheckBox.setChecked(showHelpImage)

        self.optionChanged(pasteOption, save=False)
        self.showHelpImage(showHelpImage, save=False)

        super(AnimationPreviewWidget, self).setState(state)

    def connectChanged(self, value):
        """
        :type value: bool
        """
        self.optionChanged(str(self.ui.option.currentText()))

    def optionChanged(self, text, save=True):
        """
        :type text: str
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
        imageIcon = studiolibraryplugins.resource().icon(basename)

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

        self.record().loadFromSettings(
            sourceStart=sourceStart,
            sourceEnd=sourceEnd
        )
