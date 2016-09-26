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

import math
import logging

import studioqt

from studioqt import QtGui
from studioqt import QtCore


logger = logging.getLogger(__name__)


class ListWidgetItemSignal(QtCore.QObject):
    """"""
    blendChanged = QtCore.Signal(float)


class LibraryItem(studioqt.CombinedWidgetItem):

    DEFAULT_PLAYHEAD_COLOR = QtGui.QColor(255, 255, 255, 220)

    itemSignal = ListWidgetItemSignal()

    def __init__(self):
        studioqt.CombinedWidgetItem.__init__(self)

        self._typePixmap = None
        self._typeIconPath = None

        self._imageSequence = None
        self._imageSequencePath = None

        self._blendValue = 0.0
        self._blendPreviousValue = 0.0

        self._blendPosition = None
        self._blendingEnabled = False

        self.blendChanged = self.itemSignal.blendChanged

    def __del__(self):
        self.stop()

    def setTypeIconPath(self, path):
        self._typeIconPath = path

    def typeIconPath(self):
        return self._typeIconPath

    # ------------------------------------------------------------------------
    # Support for middle mouse blending (slider)
    # ------------------------------------------------------------------------

    def setBlendingEnabled(self, enabled):
        self._blendingEnabled = enabled

    def isBlendingEnabled(self):
        return self._blendingEnabled

    def blendingEvent(self, event):

        if self.isBlending():
            value = (event.pos().x() - self.blendPosition().x()) / 1.5
            value = math.ceil(value) + self.blendPreviousValue()
            try:
                self.setBlendValue(value)
            except Exception, msg:
                self.stopBlending()

    def startBlendingEvent(self, event):
        if self.isBlendingEnabled():
            if event.button() == QtCore.Qt.MidButton:
                self._blendPosition = event.pos()

    def stopBlending(self):
        self._blendPosition = None
        self._blendPreviousValue = self.blendValue()

    def resetBlending(self):
        """
        :rtype: None
        """
        self._blendValue = 0.0
        self._blendPreviousValue = 0.0

    def isBlending(self):
        """
        :rtype: bool | None
        """
        return self.blendPosition() is not None

    def setBlendValue(self, value):
        """
        :type value: float
        :rtype: bool
        """
        if self.isBlendingEnabled():
            self._blendValue = value
            self.blendChanged.emit(value)
            logger.debug("BLENDING:" + str(value))

    def blendValue(self):
        """
        :rtype: float
        """
        return self._blendValue

    def blendPreviousValue(self):
        """
        :rtype: float
        """
        return self._blendPreviousValue

    def blendPosition(self):
        """
        :rtype: QtGui.QPoint
        """
        return self._blendPosition

    def selectionChanged(self):
        """
        :rtype: QtGui.QPoint
        """
        self.resetBlending()

    # ------------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------------

    def mouseEnterEvent(self, event):
        """
        :type event: QtGui.QEvent
        """
        studioqt.CombinedWidgetItem.mouseEnterEvent(self, event)
        self._imageSequence = None
        self.play()

    def mouseLeaveEvent(self, event):
        """
        :type event: QtGui.QEvent
        """
        studioqt.CombinedWidgetItem.mouseLeaveEvent(self, event)
        self.stop()

    def mousePressEvent(self, event):
        """
        :type event: QtCore.QEvent
        """
        studioqt.CombinedWidgetItem.mousePressEvent(self, event)
        if event.button() == QtCore.Qt.MidButton:
            self._blendPosition = event.pos()

    def mouseReleaseEvent(self, event):
        """
        :type event: QtCore.QEvent
        """
        if self.isBlending():
            self._blendPosition = None
            self._blendPreviousValue = self.blendValue()
            studioqt.CombinedWidgetItem.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        :type event: QtCore.QEvent
        """
        studioqt.CombinedWidgetItem.mouseMoveEvent(self, event)

        self.blendingEvent(event)

        if self.imageSequence():
            if studioqt.isControlModifier():
                if self.rect():
                    x = event.pos().x() - self.rect().x()
                    width = self.rect().width()
                    percent = 1.0 - (float(width - x) / float(width))
                    frame = int(self.imageSequence().duration() * percent)
                    self.imageSequence().setCurrentFrame(frame)
                    self.updateFrame()

    # ------------------------------------------------------------------------
    # Support animated image sequence
    # ------------------------------------------------------------------------

    def resetImageSequence(self):
        self._imageSequence = None

    def imageSequence(self):
        """
        :rtype: studioqt.ImageSequence
        """
        return self._imageSequence

    def setImageSequence(self, value):
        """
        :type value: studioqt.ImageSequence
        """
        self._imageSequence = value

    def setImageSequencePath(self, path):
        """
        :type path: str
        :rtype: None
        """
        self._imageSequencePath = path

    def imageSequencePath(self):
        """
        :rtype: str
        """
        return self._imageSequencePath

    def stop(self):
        """
        :rtype: None
        """
        if self.imageSequence():
            self.imageSequence().stop()

    def play(self):
        """
        :rtype: None
        """
        if self.imageSequencePath():
            if not self.imageSequence():
                imageSequence = studioqt.ImageSequence()
                imageSequence.setDirname(self.imageSequencePath())
                imageSequence.frameChanged.connect(self._frameChanged)

                self.setImageSequence(imageSequence)

            self.imageSequence().start()

    def _frameChanged(self):
        """
        :rtype: None
        """
        if not studioqt.isControlModifier():
            self.updateFrame()

    def updateFrame(self):
        """
        :rtype: None
        """
        filename = self.imageSequence().currentFilename()

        icon = QtGui.QIcon(filename)
        self.setIcon(0, icon)

    def playheadColor(self):
        """
        :rtype: str
        """
        return self.DEFAULT_PLAYHEAD_COLOR

    def paintPlayhead(self, painter, option):
        """
        :type painter: QtGui.QPainter
        :param option:
        """
        if self.imageSequence().currentFilename():

            r = self.iconRect(option)
            c = self.playheadColor()
            imageSequence = self.imageSequence()

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(c))

            if imageSequence.percent() <= 0:
                width = 0
            elif imageSequence.percent() >= 1:
                width = r.width()
            else:
                width = (imageSequence.percent() * r.width()) - 1

            height = 3 * self.dpi()
            y = r.y() + r.height() - (height - 1)

            painter.drawRect(r.x(), y, width, height)

    def typeIconRect(self, option):
        """
        :rtype: QtGui.QRect
        """
        padding = 2 * self.dpi()
        r = self.iconRect(option)

        x = r.x() + padding
        y = r.y() + padding
        rect = QtCore.QRect(x, y, 13 * self.dpi(), 13 * self.dpi())

        return rect

    def paintTypeIcon(self, painter, option):
        """
        :type painter: QtGui.QPainter
        :type option:
        """
        rect = self.typeIconRect(option)

        if not self._typePixmap:
            path = self.typeIconPath()
            if path:
                self._typePixmap = QtGui.QPixmap(path)

        if self._typePixmap:
            painter.setOpacity(0.5)
            painter.drawPixmap(rect, self._typePixmap)
            painter.setOpacity(1)

    def paint(self, painter, option, index):
        """
        :type painter: QtGui.QPainter
        :type option:
        """
        studioqt.CombinedWidgetItem.paint(self, painter, option, index)

        painter.save()
        try:
            if index.column() == 0:
                self.paintTypeIcon(painter, option)

                if self.imageSequence():
                    self.paintPlayhead(painter, option)
        finally:
            painter.restore()
