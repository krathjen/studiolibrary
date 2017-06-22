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

    DISPLAY_TIME = 15000

    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)

        self.setObjectName("statusWidget")
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self._label = QtWidgets.QLabel("Hello :)", self)

        policy = QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        self._label.setSizePolicy(*policy)

        self._timer = QtCore.QTimer(self)

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
            self.clear
        )

    def setError(self, text, msec=DISPLAY_TIME):
        icon = studioqt.resource().icon("error")
        self._button.setIcon(icon)
        self._button.show()

        self._label.setStyleSheet("color: rgb(222, 0, 0);background-color: rgb(0, 0, 0, 0);")
        self.setText(text, msec)

    def setWarning(self, text, msec=DISPLAY_TIME):
        icon = studioqt.resource().icon("warning")

        self._button.setIcon(icon)
        self._button.show()

        self._label.setStyleSheet("color: rgb(222, 180, 0);background-color: rgb(0, 0, 0, 0);")
        self.setText(text, msec)

    def setInfo(self, text, msec=DISPLAY_TIME):
        icon = studioqt.resource().icon("info")

        self._button.setIcon(icon)
        self._button.show()

        self._label.setStyleSheet("background-color: rgb(0, 0, 0, 0);")
        self.setText(text, msec)

    def setText(self, text, msec=DISPLAY_TIME):
        if not text:
            self.clear()
        else:
            self._label.setText(text)
            self._timer.stop()
            self._timer.start(msec)

        self.update()

    def clear(self):
        self._timer.stop()
        self._button.hide()
        self._label.setText("")
        self._label.setStyleSheet("")
        icon = studioqt.resource().icon("blank")
        self._button.setIcon(icon)
