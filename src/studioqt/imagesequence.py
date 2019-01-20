# Copyright 2017 by Kurt Rathjen. All Rights Reserved.
#
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

import re
import os

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


__all__ = ['ImageSequence', 'ImageSequenceWidget']


class ImageSequence(QtCore.QObject):

    DEFAULT_FPS = 24

    frameChanged = QtCore.Signal(int)

    def __init__(self, path, *args):
        QtCore.QObject.__init__(self, *args)

        self._fps = self.DEFAULT_FPS
        self._timer = None
        self._frame = 0
        self._frames = []
        self._dirname = None
        self._paused = False

        if path:
            self.setDirname(path)

    def setDirname(self, dirname):
        """
        Set the location to the image sequence.

        :type dirname: str
        :rtype: None
        """
        def naturalSortItems(items):
            """
            Sort the given list in the way that humans expect.
            """
            convert = lambda text: int(text) if text.isdigit() else text
            alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
            items.sort(key=alphanum_key)

        self._dirname = dirname
        if os.path.isdir(dirname):
            self._frames = [dirname + "/" + filename for filename in os.listdir(dirname)]
            naturalSortItems(self._frames)

    def dirname(self):
        """
        Return the location to the image sequence.

        :rtype: str
        """
        return self._dirname

    def reset(self):
        """
        Stop and reset the current frame to 0.

        :rtype: None
        """
        if not self._timer:
            self._timer = QtCore.QTimer(self.parent())
            self._timer.setSingleShot(False)
            self.connect(self._timer, QtCore.SIGNAL('timeout()'), self._frameChanged)

        if not self._paused:
            self._frame = 0
        self._timer.stop()

    def pause(self):
        """
        ImageSequence will enter Paused state.

        :rtype: None
        """
        self._paused = True
        self._timer.stop()

    def resume(self):
        """
        ImageSequence will enter Playing state.

        :rtype: None
        """
        if self._paused:
            self._paused = False
            self._timer.start()

    def stop(self):
        """
        Stops the movie. ImageSequence enters NotRunning state.

        :rtype: None
        """
        self._timer.stop()

    def start(self):
        """
        Starts the movie. ImageSequence will enter Running state

        :rtype: None
        """
        self.reset()
        if self._timer:
            self._timer.start(1000.0 / self._fps)

    def frames(self):
        """
        Return all the filenames in the image sequence.

        :rtype: list[str]
        """
        return self._frames

    def _frameChanged(self):
        """
        Triggered when the current frame changes.

        :rtype: None
        """
        if not self._frames:
            return

        frame = self._frame
        frame += 1
        self.jumpToFrame(frame)

    def percent(self):
        """
        Return the current frame position as a percentage.

        :rtype: None
        """
        if len(self._frames) == self._frame + 1:
            _percent = 1
        else:
            _percent = float((len(self._frames) + self._frame)) / len(self._frames) - 1
        return _percent

    def frameCount(self):
        """
        Return the number of frames.

        :rtype: int
        """
        return len(self._frames)

    def currentIcon(self):
        """
        Returns the current frame as a QIcon.

        :rtype: QtGui.QIcon
        """
        return QtGui.QIcon(self.currentFilename())

    def currentPixmap(self):
        """
        Return the current frame as a QPixmap.

        :rtype: QtGui.QPixmap
        """
        return QtGui.QPixmap(self.currentFilename())

    def currentFilename(self):
        """
        Return the current file name.

        :rtype: str or None
        """
        try:
            return self._frames[self.currentFrameNumber()]
        except IndexError:
            pass

    def currentFrameNumber(self):
        """
        Return the current frame.

        :rtype: int or None
        """
        return self._frame

    def jumpToFrame(self, frame):
        """
        Set the current frame.

        :rtype: int or None
        """
        if frame >= self.frameCount():
            frame = 0
        self._frame = frame
        self.frameChanged.emit(frame)


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
        if self.isControlModifier():
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

        if self.currentFilename():

            r = event.rect()

            playheadHeight = self.playheadHeight()
            playheadPosition = self._imageSequence.percent() * r.width()-1

            x = r.x()
            y = self.height() - playheadHeight

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(self.DEFAULT_PLAYHEAD_COLOR))
            painter.drawRect(x, y, playheadPosition, playheadHeight)

        painter.end()


if __name__ == "__main__":

    import studioqt
    with studioqt.app():
        w = ImageSequenceWidget(None)
        w.setDirname("C:/temp/sequence")
        w.show()
