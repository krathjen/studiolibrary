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
The capture dialog is used for creating thumbnails and thumbnail playblasts.

import mutils.gui
print mutils.gui.capture("c:/temp/test.jpg", startFrame=1, endFrame=100)
# c:/temp/test.0001.jpg
"""

import os
import shutil

try:
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()

import studioqt

import mutils.gui
import mutils.gui.modelpanelwidget

from studioqt import QtCore
from studioqt import QtWidgets

__all__ = [
    "thumbnailCapture",
    "ThumbnailCaptureDialog",
    "tempPlayblastPath",
    "tempThumbnailPath",
    ]


def tempThumbnailPath(clean=False):
    """
    Return the temp thumbnail location on disc.

    :type clean: bool
    :rtype: str
    """
    tempDir = mutils.TempDir("icon", clean=clean)
    return tempDir.path() + "/thumbnail.jpg"


def tempPlayblastPath(clean=False):
    """
    Return the temp playblast location on disc.

    :type clean: bool
    :rtype: str
    """
    tempDir = mutils.TempDir("sequence", clean=clean)
    return tempDir.path() + "/thumbnail.jpg"


_instance = None


def thumbnailCapture(path, startFrame=None, endFrame=None, step=1, clearCache=False, captured=None):
    """
    Capture a playblast and save it to the given path.

    :type path: str
    :type startFrame: int
    :type endFrame:  int
    :type step: int
    :type clearCache: bool
    :type captured: func
    :rtype: ThumbnailCaptureDialog
    """

    global _instance

    def _clearCache():
        dirname = os.path.dirname(path)
        if os.path.exists(dirname):
            shutil.rmtree(dirname)

    if _instance:
        _instance.close()

    d = mutils.gui.ThumbnailCaptureDialog(
        path=path,
        startFrame=startFrame,
        endFrame=endFrame,
        step=step,
    )

    if captured:
        d.captured.connect(captured)

    if clearCache:
        d.capturing.connect(_clearCache)

    d.show()

    if not studioqt.isControlModifier():
        d.capture()
        d.close()

    _instance = d

    return _instance


class ThumbnailCaptureDialog(QtWidgets.QDialog):

    DEFAULT_WIDTH = 250
    DEFAULT_HEIGHT = 250

    captured = QtCore.Signal(str)
    capturing = QtCore.Signal(str)

    def __init__(self, path="", parent=None, startFrame=None, endFrame=None, step=1):
        """
        :type path: str
        :type parent: QtWidgets.QWidget
        :type startFrame: int
        :type endFrame:  int
        :type step: int
        """
        parent = parent or mutils.gui.mayaWindow()

        QtWidgets.QDialog.__init__(self, parent)

        self._path = path
        self._step = step
        self._endFrame = None
        self._startFrame = None
        self._capturedPath = None

        if endFrame is None:
            endFrame = int(maya.cmds.currentTime(query=True))

        if startFrame is None:
            startFrame = int(maya.cmds.currentTime(query=True))

        self.setEndFrame(endFrame)
        self.setStartFrame(startFrame)

        self.setObjectName("CaptureWindow")
        self.setWindowTitle("Capture Window")

        self._captureButton = QtWidgets.QPushButton("Capture")
        self._captureButton.clicked.connect(self.capture)

        self._modelPanelWidget = mutils.gui.modelpanelwidget.ModelPanelWidget(self)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setObjectName(self.objectName() + "Layout")
        vbox.addWidget(self._modelPanelWidget)
        vbox.addWidget(self._captureButton)

        self.setLayout(vbox)

        width = (self.DEFAULT_WIDTH * 1.5)
        height = (self.DEFAULT_HEIGHT * 1.5) + 50

        self.setWidthHeight(width, height)
        self.centerWindow()

    def path(self):
        """
        Return the destination path.

        :rtype: str
        """
        return self._path

    def setPath(self, path):
        """
        Set the destination path.

        :type path: str
        """
        self._path = path

    def endFrame(self):
        """
        Return the end frame of the playblast.

        :rtype: int
        """
        return self._endFrame

    def setEndFrame(self, endFrame):
        """
        Specify the end frame of the playblast.

        :type endFrame: int
        """
        self._endFrame = int(endFrame)

    def startFrame(self):
        """
        Return the start frame of the playblast.

        :rtype: int
        """
        return self._startFrame

    def setStartFrame(self, startFrame):
        """
        Specify the start frame of the playblast.

        :type startFrame: int
        """
        self._startFrame = int(startFrame)

    def step(self):
        """
        Return the step amount of the playblast.

        Example:
            if step is set to 2 it will playblast every second frame.

        :rtype: int
        """
        return self._step

    def setStep(self, step):
        """
        Set the step amount of the playblast.

        :type step: int
        """
        self._step = step

    def setWidthHeight(self, width, height):
        """
        Set the width and height of the window.

        :type width: int
        :type height: int
        :rtype: None
        """
        x = self.geometry().x()
        y = self.geometry().y()
        self.setGeometry(x, y, width, height)

    def centerWindow(self):
        """
        Center the widget to the center of the desktop.

        :rtype: None
        """
        geometry = self.frameGeometry()
        pos = QtWidgets.QApplication.desktop().cursor().pos()
        screen = QtWidgets.QApplication.desktop().screenNumber(pos)
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(
            screen).center()
        geometry.moveCenter(centerPoint)
        self.move(geometry.topLeft())

    def capturedPath(self):
        """
        Return the location of the captured playblast.

        :rtype:
        """
        return self._capturedPath

    def capture(self):
        """
        Capture a playblast and save it to the given path.

        :rtype: None
        """
        path = self.path()

        self.capturing.emit(path)

        modelPanel = self._modelPanelWidget.name()
        startFrame = self.startFrame()
        endFrame = self.endFrame()
        step = self.step()
        width = self.DEFAULT_WIDTH
        height = self.DEFAULT_HEIGHT

        self._capturedPath = mutils.playblast.playblast(
            path,
            modelPanel,
            startFrame,
            endFrame,
            width,
            height,
            step=step,
        )

        self.accept()

        self.captured.emit(self._capturedPath)
        return self._capturedPath
