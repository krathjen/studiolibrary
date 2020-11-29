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
import shutil
import logging

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import mutils.gui

import studiolibrary.widgets


__all__ = [
    "ThumbnailCaptureMenu",
    "testThumbnailCaptureMenu"
]


logger = logging.getLogger(__name__)


class ThumbnailCaptureMenu(QtWidgets.QMenu):

    captured = QtCore.Signal(str)

    def __init__(self, path, force=False, parent=None):
        """
        Thumbnail capture menu.

        :type path: str
        :type force: bool
        :type parent: None or QtWidgets.QWidget
        """
        QtWidgets.QMenu.__init__(self, parent)

        self._path = path
        self._force = force

        changeImageAction = QtWidgets.QAction('Capture new image', self)
        changeImageAction.triggered.connect(self.capture)
        self.addAction(changeImageAction)

        changeImageAction = QtWidgets.QAction('Show Capture window', self)
        changeImageAction.triggered.connect(self.showCaptureWindow)
        self.addAction(changeImageAction)

        loadImageAction = QtWidgets.QAction('Load image from disk', self)
        loadImageAction.triggered.connect(self.showLoadImageDialog)
        self.addAction(loadImageAction)

    def path(self):
        """
        Return the thumbnail path on disc.
        
        :rtype: str
        """
        return self._path

    def showWarningDialog(self):
        """Show a warning dialog for overriding the previous thumbnail."""
        title = "Override Thumbnail"

        text = u"This action will delete the previous thumbnail. The " \
               u"previous image cannot be backed up. Do you want to " \
               u"confirm the action to take a new image and delete " \
               u"the previous one?"

        clickedButton = studiolibrary.widgets.MessageBox.warning(
            self.parent(),
            title=title,
            text=text,
            enableDontShowCheckBox=True,
        )

        if clickedButton != QtWidgets.QDialogButtonBox.StandardButton.Yes:
            raise Exception("Dialog was canceled!")

    def showCaptureWindow(self):
        """Show the capture window for framing."""
        self.capture(show=True)

    def capture(self, show=False):
        """
        Capture an image from the Maya viewport.
        
        :type show: bool
        """
        if not self._force and os.path.exists(self.path()):
            self.showWarningDialog()

        mutils.gui.thumbnailCapture(
            show=show,
            path=self.path(),
            captured=self.captured.emit
        )

    def showLoadImageDialog(self):
        """Show a file dialog for choosing an image from disc."""
        if not self._force and os.path.exists(self.path()):
            self.showWarningDialog()

        fileDialog = QtWidgets.QFileDialog(
            self,
            caption="Open Image",
            filter="Image Files (*.png *.jpg *.bmp)"
        )

        fileDialog.fileSelected.connect(self._fileSelected)
        fileDialog.exec_()

    def _fileSelected(self, path):
        """
        Triggered when the file dialog is accepted.
        
        :type path: str
        """
        shutil.copy(path, self.path())
        self.captured.emit(self.path())


def testThumbnailCaptureMenu():
    """A method for testing the thumbnail capture menu in Maya."""

    def capturedCallback(path):
        """
        Triggered when the captured menu has been accepted.
        
        :type path: str
        """
        print("Captured thumbnail to:", path)

    path = "c:/tmp/test.png"

    menu = ThumbnailCaptureMenu(path, True)
    menu.captured.connect(capturedCallback)
    menu.exec_(QtGui.QCursor.pos())
