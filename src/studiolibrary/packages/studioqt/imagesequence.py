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

import re
import os

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


__all__ = ['ImageSequence', 'ImageSequenceWidget']


class ImageSequence(QtCore.QObject):

    DEFAULT_FPS = 24

    frameChanged = QtCore.Signal()

    def __init__(self,  *args):
        QtCore.QObject.__init__(self, *args)

        self._fps = self.DEFAULT_FPS
        self._timer = None
        self._frame = 0
        self._frames = []
        self._dirname = None
        self._paused = False

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
        self._frame = 0
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
        self.setCurrentFrame(frame)

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

    def duration(self):
        """
        Return the number of frames.

        :rtype: int
        """
        return len(self._frames)

    def currentFilename(self):
        """
        Return the current file name.

        :rtype: str or None
        """
        try:
            return self._frames[self.currentFrame()]
        except IndexError:
            pass

    def currentFrame(self):
        """
        Return the current frame.

        :rtype: int or None
        """
        return self._frame

    def setCurrentFrame(self, frame):
        """
        Set the current frame.

        :rtype: int or None
        """
        if frame >= self.duration():
            frame = 0
        self._frame = frame
        self.frameChanged.emit()


class ImageSequenceWidget(QtWidgets.QToolButton):

    DEFAULT_PLAYHEAD_COLOR = QtGui.QColor(255, 255, 255, 220)

    def __init__(self,  *args):
        QtWidgets.QToolButton.__init__(self, *args)
        self.setStyleSheet('border: 0px solid rgb(0, 0, 0, 20);')

        self._filename = None
        self._imageSequence = ImageSequence(self)
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

    def currentIcon(self):
        """
        Return a icon object from the current icon path.

        :rtype: QtGui.QIcon
        """
        return QtGui.QIcon(self._imageSequence.currentFilename())

    def setDirname(self, dirname):
        """
        Set the location to the image sequence.

        :type dirname: str
        :rtype: None
        """
        self._imageSequence.setDirname(dirname)
        if self._imageSequence.frames():
            icon = self.currentIcon()
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
            frame = int(self._imageSequence.duration() * percent)
            self._imageSequence.setCurrentFrame(frame)
            icon = self.currentIcon()
            self.setIcon(icon)

    def _frameChanged(self, filename=None):
        """
        Triggered when the image sequence changes frame.

        :type filename: str or None
        :rtype: None
        """
        if not self.isControlModifier():
            self._filename = filename
            icon = self.currentIcon()
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
        w.setDirname("C:/temp/")
        w.show()