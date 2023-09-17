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

import re
import os

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore


__all__ = ['ImageSequence', 'ImageSequenceWidget']


class ImageSequence(QtCore.QObject):

    DEFAULT_FPS = 24

    frameChanged = QtCore.Signal(int)

    def __init__(self, path, *args):
        QtCore.QObject.__init__(self, *args)

        self._timer = None
        self._frame = 0
        self._frames = []
        self._dirname = None
        self._paused = False

        if path:
            self.setPath(path)

    def firstFrame(self):
        """
        Get the path to the first frame.

        :rtype: str
        """
        if self._frames:
            return self._frames[0]
        return ""

    def setPath(self, path):
        """
        Set a single frame or a directory to an image sequence.
        
        :type path: str
        """
        if os.path.isfile(path):
            self._frame = 0
            self._frames = [path]
        elif os.path.isdir(path):
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
            self._timer.timeout.connect(self._frameChanged)

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
            import studiolibrary
            fps = studiolibrary.config.get("playbackFrameRate", self.DEFAULT_FPS)
            self._timer.start(1000.0 / fps)

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
