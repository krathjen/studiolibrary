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

from studiovendor import six
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studiolibrary


class ProgressBar(QtWidgets.QFrame):

    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QtWidgets.QLabel("", self)
        self._label.setAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignVCenter
        )
        self._label.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )

        layout.addWidget(self._label)

        self._progressBar = QtWidgets.QProgressBar(self)
        self._progressBar.setFormat("")
        self._progressBar.setRange(0, 100)
        self._progressBar.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred
        )

        layout.addWidget(self._progressBar)

        self.setLayout(layout)

    def reset(self):
        """Reimplementing for convenience"""
        self._progressBar.reset()

    def setText(self, text):
        """
        Reimplementing for convenience

        :type text: str
        """
        self._label.setText(text)

    def setValue(self, value):
        """
        Reimplementing for convenience

        :type value: float or int
        """
        self._progressBar.setValue(value)

    def setRange(self, min_, max_):
        """
        Reimplementing for convenience

        :type min_: int
        :type max_: int
        """
        self._progressBar.setRange(min_, max_)


class StatusWidget(QtWidgets.QFrame):

    DEFAULT_DISPLAY_TIME = 10000  # Milliseconds, 15 secs

    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)

        self.setObjectName("statusWidget")
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self._blocking = False
        self._timer = QtCore.QTimer(self)

        self._label = QtWidgets.QLabel("", self)
        self._label.setCursor(QtCore.Qt.IBeamCursor)
        self._label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._label.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Preferred)

        self._button = QtWidgets.QPushButton(self)
        self._button.setMaximumSize(QtCore.QSize(17, 17))
        self._button.setIconSize(QtCore.QSize(17, 17))

        self._progressBar = ProgressBar(self)
        self._progressBar.hide()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(1, 0, 0, 0)

        layout.addWidget(self._button)
        layout.addWidget(self._label)
        layout.addWidget(self._progressBar)

        self.setLayout(layout)
        self.setFixedHeight(19)
        self.setMinimumWidth(5)

        self._timer.timeout.connect(self.reset)

    def progressBar(self):
        """
        Get the progress widget

        rtype: QtWidgets.QProgressBar
        """
        return self._progressBar

    def isBlocking(self):
        """
        Return true if the status widget is blocking, otherwise return false.
        :rtype: bool 
        """
        return self._blocking

    def showInfoMessage(self, message, msecs=None):
        """
        Set an info message to be displayed in the status widget.
        
        :type message: str
        :type msecs: int
        
        :rtype: None 
        """
        if self.isBlocking():
            return

        self.setProperty("status", "info")

        icon = studiolibrary.resource.icon("info")
        self.showMessage(message, icon, msecs)

    def setProperty(self, *args):
        """
        Overriding this method to force the style sheet to reload.

        :type args: list
        """
        super(StatusWidget, self).setProperty(*args)
        self.setStyleSheet(self.styleSheet())

    def showErrorMessage(self, message, msecs=None):
        """
        Set an error to be displayed in the status widget.

        :type message: str
        :type msecs: int
        
        :rtype: None 
        """
        self.setProperty("status", "error")

        icon = studiolibrary.resource.icon("error")
        self.showMessage(message, icon, msecs, blocking=True)

    def showWarningMessage(self, message, msecs=None):
        """
        Set a warning to be displayed in the status widget.
        
        :type message: str
        :type msecs: int
        
        :rtype: None 
        """
        if self.isBlocking():
            return

        self.setProperty("status", "warning")

        icon = studiolibrary.resource.icon("warning")
        self.showMessage(message, icon, msecs)

    def showMessage(self, message, icon, msecs=None, blocking=False):
        """
        Set the given text to be displayed in the status widget.
        
        :type message: str
        :type icon: icon
        :type msecs: int
        
        :rtype: None 
        """
        msecs = msecs or self.DEFAULT_DISPLAY_TIME

        self._blocking = blocking

        if icon:
            self._button.setIcon(icon)
            self._button.show()
        else:
            self._button.hide()

        if message:
            self._label.setText(six.text_type(message))
            self._timer.stop()
            self._timer.start(msecs)
        else:
            self.reset()

        self.update()

    def reset(self):
        """
        Called when the current animation has finished.
        
        :rtype: None 
        """
        self._timer.stop()
        self._button.hide()
        self._label.setText("")
        icon = studiolibrary.resource.icon("blank")
        self._button.setIcon(icon)
        self.setProperty("status", "")
        self._blocking = False
