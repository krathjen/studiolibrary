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

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

from studioqt import ImageSequence


__all__ = ['ImageSequenceWidget']


class ImageSequenceWidget(QtWidgets.QToolButton):

    DEFAULT_PLAYHEAD_COLOR = QtGui.QColor(255, 255, 255, 220)

    def __init__(self,  *args):
        QtWidgets.QToolButton.__init__(self, *args)
        self.setStyleSheet('border: 0px solid rgb(0, 0, 0, 20);')

        self._imageSequence = ImageSequence("")
        self._imageSequence.frameChanged.connect(self._frameChanged)

        self.setSize(150, 150)
        self.setMouseTracking(True)

    def isControlModifier(self):
        """
        :rtype: bool
        """
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        return modifiers == QtCore.Qt.ControlModifier

    def setSize(self, w, h):
        """
        Reimplemented so that the icon size is set at the same time.

        :type w: int
        :type h: int
        :rtype: None
        """
        self._size = QtCore.QSize(w, h)
        self.setIconSize(self._size)
        self.setFixedSize(self._size)

    def setDirname(self, dirname):
        """
        Set the location to the image sequence.

        :type dirname: str
        :rtype: None
        """
        self._imageSequence.setDirname(dirname)
        if self._imageSequence.frames():
            icon = self._imageSequence.currentIcon()
            self.setIcon(icon)

    def enterEvent(self, event):
        """
        Start playing the image sequence when the mouse enters the widget.

        :type event: QtCore.QEvent
        :rtype: None
        """
        self._imageSequence.start()

    def leaveEvent(self, event):
        """
        Stop playing the image sequence when the mouse leaves the widget.

        :type event: QtCore.QEvent
        :rtype: None
        """
        self._imageSequence.pause()

    def mouseMoveEvent(self, event):
        """
        Reimplemented to add support for scrubbing.

        :type event: QtCore.QEvent
        :rtype: None
        """
        if self.isControlModifier() and self._imageSequence.frameCount() > 1:
            percent = 1.0 - (float(self.width() - event.pos().x()) / float(self.width()))
            frame = int(self._imageSequence.frameCount() * percent)
            self._imageSequence.jumpToFrame(frame)
            icon = self._imageSequence.currentIcon()
            self.setIcon(icon)

    def _frameChanged(self, frame=None):
        """
        Triggered when the image sequence changes frame.

        :type frame: int or None
        :rtype: None
        """
        if not self.isControlModifier():
            icon = self._imageSequence.currentIcon()
            self.setIcon(icon)

    def currentFilename(self):
        """
        Return the current image location.

        :rtype: str
        """
        return self._imageSequence.currentFilename()

    def playheadHeight(self):
        """
        Return the height of the playhead.

        :rtype: int
        """
        return 4

    def paintEvent(self, event):
        """
        Triggered on frame changed.

        :type event: QtCore.QEvent
        :rtype: None
        """
        QtWidgets.QToolButton.paintEvent(self, event)

        painter = QtGui.QPainter()
        painter.begin(self)

        if self.currentFilename() and self._imageSequence.frameCount() > 1:

            r = event.rect()

            playheadHeight = self.playheadHeight()
            playheadPosition = self._imageSequence.percent() * r.width()-1

            x = r.x()
            y = self.height() - playheadHeight

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(self.DEFAULT_PLAYHEAD_COLOR))
            painter.drawRect(x, y, playheadPosition, playheadHeight)

        painter.end()