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

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

from studioqt import ImageSequence
import studioqt


__all__ = ['ImageSequenceWidget']


STYLE = """
QToolBar {
    border: 0px solid black; 
    border-radius:2px;
    background-color: rgba(0,0,0,100);
}

QToolButton {
    background-color: transparent;
}
"""


class ImageSequenceWidget(QtWidgets.QToolButton):

    DEFAULT_PLAYHEAD_COLOR = QtGui.QColor(255, 255, 255, 220)

    def __init__(self,  parent=None, theme=None):
        QtWidgets.QToolButton.__init__(self, parent)

        self._theme = theme

        self._imageSequence = ImageSequence("")
        self._imageSequence.frameChanged.connect(self._frameChanged)

        self._toolBar = QtWidgets.QToolBar(self)
        self._toolBar.setStyleSheet(STYLE)

        studioqt.fadeOut(self._toolBar, duration=0)

        spacer = QtWidgets.QWidget()
        spacer.setMaximumWidth(4)
        spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred
        )
        self._toolBar.addWidget(spacer)

        spacer = QtWidgets.QWidget()
        spacer.setMaximumWidth(4)
        spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred
        )
        self._firstSpacer = self._toolBar.addWidget(spacer)

        self.setSize(150, 150)
        self.setMouseTracking(True)

    def hasFrames(self):
        """
        Check if the images sequence has any frames.

        :rtype: bool
        """
        return bool(self.firstFrame())

    def firstFrame(self):
        """
        Get the first frame in the image sequence.

        :rtype: str
        """
        return self._imageSequence.firstFrame()

    def isSequence(self):
        """
        Check if the image sequence has more than one frame.

        :rtype: bool
        """
        return bool(self._imageSequence.frameCount() > 1)

    def dirname(self):
        """
        Get the directory to the image sequence on disk.

        :rtype: str
        """
        return self._imageSequence.dirname()

    def addAction(self, path, text, tip, callback):
        """
        Add an action to the tool bar.
        
        :type path: str 
        :type text: str
        :type tip: str
        :type callback: func
        
        :rtype: QtWidgets.QAction
        """
        icon = studioqt.Icon.fa(
            path,
            color="rgba(250,250,250,160)",
            color_active="rgba(250,250,250,250)",
            color_disabled="rgba(0,0,0,20)"
        )

        action = QtWidgets.QAction(icon, text, self._toolBar)
        action.setToolTip(tip)
        # action.setStatusTip(tip)
        # action.setWhatsThis(tip)

        self._toolBar.insertAction(self._firstSpacer, action)
        action.triggered.connect(callback)

        return action

    def actions(self):
        """
        Get all the actions that are a child of the ToolBar.

        :rtype: list[QtWidgets.QAction] 
        """
        actions = []

        for child in self._toolBar.children():
            if isinstance(child, QtWidgets.QAction):
                actions.append(child)

        return actions

    def resizeEvent(self, event):
        """
        Called when the widget is resized.
        
        :type event: QtWidgets.QResizeEvent 
        """
        self.updateToolBar()

    def updateToolBar(self):
        """Update the tool bar size depending on the number of actions."""
        dpi = 1.0
        if self._theme:
            dpi = self._theme.dpi()

        self._toolBar.setIconSize(QtCore.QSize(16*dpi, 16*dpi))

        count = (len(self.actions())) - 3
        width = ((26*dpi) * count)

        self._toolBar.setGeometry(0, 0, width, 25*dpi)

        x = self.rect().center().x() - (self._toolBar.width()/2)
        y = self.height() - self._toolBar.height() - (12*dpi)
        width = self._toolBar.width()

        self._toolBar.setGeometry(x, y,  width,  self._toolBar.height())

    def isControlModifier(self):
        """
        Check if the control modifier is active.
        
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

    def setPath(self, path):
        """
        Set a single frame image sequence.
        
        :type path: str
        """
        self._imageSequence.setPath(path)
        self.updateIcon()

    def setDirname(self, dirname):
        """
        This method has been deprecated.

        Please use setPath instead.

        :type dirname: str
        """
        self._imageSequence.setPath(dirname)
        self.updateIcon()

    def updateIcon(self):
        """Update the icon for the current frame."""
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
        studioqt.fadeIn(self._toolBar, duration=300)

    def leaveEvent(self, event):
        """
        Stop playing the image sequence when the mouse leaves the widget.

        :type event: QtCore.QEvent
        :rtype: None
        """
        self._imageSequence.pause()
        studioqt.fadeOut(self._toolBar, duration=300)

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