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

import os

from studioqt import QtCore
from studioqt import QtWidgets

import studioqt

HOME_PATH = os.getenv('APPDATA') or os.getenv('HOME')
SETTINGS_PATH = os.path.join(HOME_PATH, 'studioqt.ini')


def createMessageBox(
        parent,
        title,
        message,
        buttons=None,
        headerIcon=None,
        headerColor=None,
        enableDontShowCheckBox=False
):
    """
    Open a question message box with the given options.

    :type parent: QWidget
    :type title: str
    :type message: str
    :type buttons: list[QMessageBox.StandardButton]
    :type headerIcon: str
    :type headerColor: str
    :type enableDontShowCheckBox: bool

    :rtype: MessageBox
    """
    mb = MessageBox(parent, enableDontShowCheckBox=enableDontShowCheckBox)

    mb.setText(message)

    buttons = buttons or QtWidgets.QDialogButtonBox.Ok
    mb.setButtons(buttons)

    if headerIcon:
        p = studioqt.resource.pixmap(headerIcon)
        mb.setPixmap(p)

    headerColor = headerColor or "rgb(50, 150, 200)"
    mb.setHeaderColor(headerColor)

    mb.setWindowTitle(title)
    mb.setTitleText(title)

    return mb


def showMessageBox(
        parent,
        title,
        message,
        buttons=None,
        headerIcon=None,
        headerColor=None,
        enableDontShowCheckBox=False,
        force=False
):
    """
    Open a question message box with the given options.

    :type parent: QWidget
    :type title: str
    :type message: str
    :type buttons: list[QMessageBox.StandardButton]
    :type headerIcon: str
    :type headerColor: str
    :type enableDontShowCheckBox: bool
    :type force: bool

    :rtype: MessageBox
    """
    settings = QtCore.QSettings(SETTINGS_PATH, QtCore.QSettings.IniFormat)

    key = 'MessageBox/{}/'.format(title.replace(" ", "_"))

    clickedButton = int(settings.value(key + "clickedButton") or -1)
    dontShowAgain = settings.value(key + "dontShowAgain") == "true"

    # Force show the dialog if the user is holding the ctrl key down
    if studioqt.isControlModifier() or studioqt.isAltModifier():
        force = True

    if force or not dontShowAgain or not enableDontShowCheckBox:

        mb = createMessageBox(
            parent,
            title,
            message,
            buttons=buttons,
            headerIcon=headerIcon,
            headerColor=headerColor,
            enableDontShowCheckBox=enableDontShowCheckBox
        )

        mb.exec_()
        mb.close()

        # Save the button that was clicked by the user
        clickedButton = mb.clickedStandardButton()
        settings.setValue(key + "clickedButton", clickedButton)

        # Save the dont show again checked state
        dontShowAgain = mb.isDontShowCheckboxChecked()
        settings.setValue(key + "dontShowAgain", dontShowAgain)

    return clickedButton


class MessageBox(QtWidgets.QDialog):

    @staticmethod
    def question(
        parent,
        title,
        message,
        buttons=None,
        headerIcon="question",
        headerColor="rgb(50, 150, 200)",
        enableDontShowCheckBox=False
    ):
        """
        Open a question message box with the given options.

        :type parent: QWidget
        :type title: str
        :type message: str
        :type headerIcon: str
        :type headerColor: str
        :type buttons: list[QMessageBox.StandardButton]

        :rtype: QMessageBox.StandardButton
        """
        clickedButton = showMessageBox(
            parent,
            title,
            message,
            buttons=buttons,
            headerIcon=headerIcon,
            headerColor=headerColor,
            enableDontShowCheckBox=enableDontShowCheckBox,
        )

        return clickedButton

    @staticmethod
    def warning(
        parent,
        title,
        message,
        buttons=None,
        headerIcon="warning2",
        headerColor="rgb(200, 128, 0)",
        enableDontShowCheckBox=False,
        force=False,
    ):
        """
        Open a warning message box with the given options.

        :type parent: QWidget
        :type title: str
        :type message: str
        :type buttons: list[QMessageBox.StandardButton]
        :type headerIcon: str
        :type headerColor: str
        :type enableDontShowCheckBox: bool
        :type force: bool

        :rtype: (QMessageBox.StandardButton, bool)
        """
        buttons = buttons or (QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.No)

        clickedButton = showMessageBox(
            parent,
            title,
            message,
            buttons=buttons,
            headerIcon=headerIcon,
            headerColor=headerColor,
            enableDontShowCheckBox=enableDontShowCheckBox,
            force=force
        )

        return clickedButton

    @staticmethod
    def critical(
        parent,
        title,
        message,
        buttons=None,
        headerIcon="critical",
        headerColor="rgb(200, 50, 50)"
    ):
        """
        Open a critical message box with the given options.

        :type parent: QWidget
        :type title: str
        :type message: str
        :type headerIcon: str
        :type headerColor: str
        :type buttons: list[QMessageBox.StandardButton]

        :rtype: QMessageBox.StandardButton
        """
        clickedButton = showMessageBox(
            parent,
            title,
            message,
            buttons=buttons,
            headerIcon=headerIcon,
            headerColor=headerColor
        )

        return clickedButton

    def __init__(self, parent=None, enableDontShowCheckBox=False):

        super(MessageBox, self).__init__(parent)

        self.setMinimumWidth(300)
        self.setMaximumWidth(400)

        self._dontShowCheckbox = False
        self._clickedStandardButton = None

        self._header = QtWidgets.QFrame(self)
        self._header.setStyleSheet("background-color: rgb(0,0,0,0);")
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

        vlayout1.addLayout(vlayout2)

        if enableDontShowCheckBox:

            msg = "Don't show this message again"
            self._dontShowCheckbox = QtWidgets.QCheckBox(msg, self)

            vlayout2.addWidget(self._dontShowCheckbox)

        vlayout2.addWidget(self._buttonBox)

        self.setLayout(vlayout1)

    def header(self):
        """
        Return the header frame.

        :rtype: QtWidgets.QFrame
        """
        return self._header

    def setTitleText(self, text):
        """
        Set the title text to be displayed.

        :type text: str
        :rtype: None 
        """
        self._title.setText(text)

    def setText(self, text):
        """
        Set the text message to be displayed.
        
        :type text: str
        :rtype: None 
        """
        self._message.setText(text)

    def setButtons(self, buttons):
        """
        Set the buttons to be displayed in message box.

        :type buttons: QMessageBox.StandardButton
        :rtype: None 
        """
        self._buttonBox.setStandardButtons(buttons)

    def setHeaderColor(self, color):
        """
        Set the header color for the message box.

        :type color: str
        :rtype: None 
        """
        self.header().setStyleSheet("background-color:" + color)

    def setPixmap(self, pixmap):
        """
        Set the pixmap for the message box.

        :type pixmap: QWidgets.QPixmap
        :rtype: None 
        """
        self._icon.setPixmap(pixmap)

    def _clicked(self, button):
        """
        Triggered when the user clicks a button.
        
        :type button: QMessageBox.StandardButton
        :rtype: None 
        """
        self._clickedStandardButton = self._buttonBox.standardButton(button)

    def clickedStandardButton(self):
        """
        Return the button that was clicked by the user.

        :rtype: QMessageBox.StandardButton
        """
        return self._clickedStandardButton

    def isDontShowCheckboxChecked(self):
        """
        Return the checked state of the Dont show again checkbox.
        
        :rtype: bool 
        """
        if self._dontShowCheckbox:
            return self._dontShowCheckbox.isChecked()
        else:
            return False


def showExample():

    with studioqt.app():

        title = "Create a snapshot icon"
        message = "Would you like to create a snapshot icon?"
        buttons = QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.Ignore | QtWidgets.QDialogButtonBox.Cancel
        result = MessageBox.question(None, title, message, buttons)
        print result

        title = "Create a snapshot icon"
        message = "This is to test a very long message. This is to test a very long message. This is to test a very long message. This is to test a very long message. This is to test a very long message. "
        buttons = QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.Ignore | QtWidgets.QDialogButtonBox.Cancel
        result = MessageBox.question(None, title, message, buttons)
        print result

        title = "By Frame Tip"
        message = "Testing the don't show check box. "
        buttons = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        result = MessageBox.question(None, title, message, buttons, enableDontShowCheckBox=True)
        print result

        title = "Create a new thumbnail icon"
        message = "This will override the existing thumbnail. Are you sure you would like to continue?"
        buttons = QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.No
        result = MessageBox.warning(None, title, message, buttons, enableDontShowCheckBox=True)
        print result

        title = "Error saving item!"
        message = "An error has occurred while saving an item."
        result = MessageBox.critical(None, title, message)
        print result

        if result == QtWidgets.QDialogButtonBox.Yes:
            title = "Error while saving!"
            message = "There was an error while saving"
            MessageBox.critical(None, title, message)


if __name__ == "__main__":
    showExample()
