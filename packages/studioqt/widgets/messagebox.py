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


class MessageBox(QtWidgets.QDialog):

    @staticmethod
    def question(parent, title, message, options):

        mb = MessageBox(parent)
        mb.setText(message)
        mb.setOptions(options)
        mb.header().setStyleSheet("background-color: rgb(50,150,200);")

        p = studioqt.pixmap("question")
        mb.setPixmap(p)

        mb.setWindowTitle(title)
        mb.setTitleText(title)

        a = mb.exec_()
        mb.close()

        return mb._standardButtonClicked

    @staticmethod
    def critical(parent, title, message):

        mb = MessageBox(parent)
        mb.setText(message)
        mb.setOptions(QtWidgets.QDialogButtonBox.Ok)
        mb.header().setStyleSheet("background-color: rgb(200,50,50);")

        p = studioqt.pixmap("critical")
        mb.setPixmap(p)

        mb.setWindowTitle(title)
        mb.setTitleText(title)

        a = mb.exec_()
        mb.close()

        return mb._standardButtonClicked

    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent)

        self.setMinimumWidth(300)
        self.setMaximumWidth(400)

        self._standardButtonClicked = None

        self._header = QtWidgets.QFrame(self)
        self._header.setStyleSheet("background-color: rgb(50,150,200,0);")
        self._header.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self._header.setFixedHeight(46)

        self._icon = QtWidgets.QLabel(self._header)
        self._icon.setAlignment(QtCore.Qt.AlignTop)
        self._icon.setScaledContents(True)
        self._icon.setFixedWidth(28)
        self._icon.setFixedHeight(28)
        self._icon.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self._title = QtWidgets.QLabel(self._header)
        self._title.setStyleSheet("font: 14pt bold; color:rgb(255,255,255);")
        self._title.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        hlayout = QtWidgets.QHBoxLayout(self._header)
        hlayout.setSpacing(10)
        hlayout.addWidget(self._icon)
        hlayout.addWidget(self._title)

        self._header.setLayout(hlayout)

        self._message = QtWidgets.QLabel()
        self._message.setMinimumHeight(50)
        self._message.setWordWrap(True)
        self._message.setAlignment(QtCore.Qt.AlignLeft)
        self._message.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._message.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        options = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self._buttonBox = QtWidgets.QDialogButtonBox(None, QtCore.Qt.Horizontal, self)
        self._buttonBox.clicked.connect(self._clicked)
        self._buttonBox.accepted.connect(self.accept)
        self._buttonBox.rejected.connect(self.reject)

        vlayout1 = QtWidgets.QVBoxLayout(self)
        vlayout1.setContentsMargins(0, 0, 0, 0)

        vlayout1.addWidget(self._header)

        vlayout2 = QtWidgets.QVBoxLayout(self)
        vlayout2.setSpacing(25)
        vlayout2.setContentsMargins(15, 5, 15, 5)

        vlayout2.addWidget(self._message)
        vlayout2.addWidget(self._buttonBox)

        vlayout1.addLayout(vlayout2)

        self.setLayout(vlayout1)

    def header(self):
        return self._header

    def setTitleText(self, text):
        self._title.setText(text)

    def setText(self, message):
        self._message.setText(message)

    def setOptions(self, options):
        self._buttonBox.setStandardButtons(options)

    def setPixmap(self, pixmap):
        self._icon.setPixmap(pixmap)

    def _clicked(self, button):
        self._standardButtonClicked = self._buttonBox.standardButton(button)


def showExample():

    with studioqt.app():

        title = "Create a snapshot icon"
        message = "Would you like to create a snapshot icon?"
        options = QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.Ignore | QtWidgets.QDialogButtonBox.Cancel
        result = MessageBox.question(None, title, message, options)

        title = "Create a snapshot icon"
        message = "This is to test a very long message. This is to test a very long message. This is to test a very long message. This is to test a very long message. This is to test a very long message. "
        options = QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.Ignore | QtWidgets.QDialogButtonBox.Cancel
        result = MessageBox.question(None, title, message, options)

        if result == QtWidgets.QDialogButtonBox.Yes:
            title = "Error while saving!"
            message = "There was an error while saving"
            result = MessageBox.critical(None, title, message)

if __name__ == "__main__":
    showExample()