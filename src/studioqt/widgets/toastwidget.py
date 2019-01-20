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

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt


class ToastWidget(QtWidgets.QLabel):
    """
    A toast is a widget containing a quick little message for the user. 
    
    The toast class helps you create and show those.

    Example:
        toast = studioqt.ToastWidget(parent)
        toast.setDuration(1000)  # Show for 1 second
        toast.setText("Hello world")
        toast.show()
    """

    DEFAULT_DURATION = 500  # 0.5 seconds

    def __init__(self, *args):
        QtWidgets.QLabel.__init__(self, *args)

        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.fadeOut)

        self._duration = self.DEFAULT_DURATION

        self.setMouseTracking(True)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        if self.parent():
            self.parent().installEventFilter(self)

    def eventFilter(self, obj, event):
        """
        Update the geometry when the parent widget changes size.

        :type obj: QWidgets.QWidget
        :type event: QtCore.QEvent 
        
        :rtype: bool 
        """
        if event.type() == QtCore.QEvent.Resize:
            self.updateGeometry()
        return QtWidgets.QLabel.eventFilter(self, obj, event)

    def updateGeometry(self):
        """
        Update and align the geometry to the parent widget.
        
        :rtype: None 
        """
        padding = 30
        widget = self.parent()

        width = self.textWidth() + padding
        height = self.textHeight() + padding

        x = widget.width() / 2 - width / 2
        y = (widget.height() - height) / 1.2

        self.setGeometry(x, y, width, height)

    def duration(self):
        """
        Return the duration.
        
        :rtype: int 
        """
        return self._duration

    def setDuration(self, duration):
        """
        Set how long to show the toast for in milliseconds.
        
        :type duration: int
        :rtype: None 
        """
        self._duration = duration

    def fadeOut(self, duration=250):
        """
        Fade out the toast message.
        
        :type duration: int 
        :rtype: None 
        """
        studioqt.fadeOut(self, duration=duration, onFinished=self.hide)

    def textRect(self):
        """
        Return the bounding box rect for the text.
        
        :rtype: QtCore.QRect 
        """
        text = self.text()
        font = self.font()
        metrics = QtGui.QFontMetricsF(font)
        return metrics.boundingRect(text)

    def textWidth(self):
        """
        Return the width of the text.
        
        :rtype: int 
        """
        textWidth = self.textRect().width()
        return max(0, textWidth)

    def textHeight(self):
        """
        Return the height of the text.
        
        :rtype: int 
        """
        textHeight = self.textRect().height()
        return max(0, textHeight)

    def setText(self, text):
        """
        Overriding this method to update the size depending on the text width.
        
        :type text: str 
        :rtype: None 
        """
        QtWidgets.QLabel.setText(self, text)
        self.updateGeometry()

    def show(self):
        """
        Overriding this method to start the timer to hide the toast.

        :rtype: None
        """
        duration = self.duration()

        self._timer.stop()
        self._timer.start(duration)

        if not self.isVisible():
            # Fade in will reset the alpha effect back to 1.
            studioqt.fadeIn(self, duration=0)
            QtWidgets.QLabel.show(self)
