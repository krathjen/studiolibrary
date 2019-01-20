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

from studioqt import QtWidgets
from studioqt import QtCore

import studioqt


class StatusWidget(QtWidgets.QFrame):

    DEFAULT_DISPLAY_TIME = 10000  # Milliseconds, 15 secs

    INFO_CSS = """"""

    ERROR_CSS = """
        color: rgb(240, 240, 240);
        background-color: rgb(220, 40, 40);
        selection-color: rgb(220, 40, 40);
        selection-background-color: rgb(240, 240, 240);
    """

    WARNING_CSS = """
        color: rgb(240, 240, 240);
        background-color: rgb(240, 170, 0);
    """

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

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(1, 0, 0, 0)

        layout.addWidget(self._button)
        layout.addWidget(self._label)

        self.setLayout(layout)
        self.setFixedHeight(19)
        self.setMinimumWidth(5)

        QtCore.QObject.connect(
            self._timer,
            QtCore.SIGNAL("timeout()"),
            self.reset
        )

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

        icon = studioqt.resource.icon("info")
        self.setStyleSheet(self.INFO_CSS)
        self.showMessage(message, icon, msecs)

    def showErrorMessage(self, message, msecs=None):
        """
        Set an error to be displayed in the status widget.

        :type message: str
        :type msecs: int
        
        :rtype: None 
        """
        icon = studioqt.resource.icon("error")
        self.setStyleSheet(self.ERROR_CSS)
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

        icon = studioqt.resource.icon("warning")
        self.setStyleSheet(self.WARNING_CSS)
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
            self._label.setText(unicode(message))
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
        icon = studioqt.resource.icon("blank")
        self._button.setIcon(icon)
        self.setStyleSheet("")
        self._blocking = False
