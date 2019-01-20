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
        text,
        width=None,
        height=None,
        buttons=None,
        headerIcon=None,
        headerColor=None,
        enableInputEdit=False,
        enableDontShowCheckBox=False
):
    """
    Open a question message box with the given options.

    :type parent: QWidget
    :type title: str
    :type text: str
    :type buttons: list[QMessageBox.StandardButton]
    :type headerIcon: str
    :type headerColor: str
    :type enableDontShowCheckBox: bool

    :rtype: MessageBox
    """
    mb = MessageBox(
        parent,
        width=width,
        height=height,
        enableInputEdit=enableInputEdit,
        enableDontShowCheckBox=enableDontShowCheckBox
    )

    mb.setText(text)

    buttons = buttons or QtWidgets.QDialogButtonBox.Ok
    mb.setButtons(buttons)

    if headerIcon:
        p = studioqt.resource.pixmap(headerIcon)
        mb.setPixmap(p)

    try:
        theme = parent.theme()
    except AttributeError:
        theme = studioqt.Theme()

    mb.setStyleSheet(theme.styleSheet())

    headerColor = headerColor or theme.accentColor().toString()
    headerColor = headerColor or "rgb(50, 150, 200)"

    mb.setHeaderColor(headerColor)

    mb.setWindowTitle(title)
    mb.setTitleText(title)

    return mb


def showMessageBox(
        parent,
        title,
        text,
        width=None,
        height=None,
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
    :type text: str
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
    dontShowAgain = settings.value(key + "dontShowAgain")

    if isinstance(dontShowAgain, basestring):
        dontShowAgain = dontShowAgain == "true"

    # Force show the dialog if the user is holding the ctrl key down
    if studioqt.isControlModifier() or studioqt.isAltModifier():
        force = True

    if force or not dontShowAgain or not enableDontShowCheckBox:

        mb = createMessageBox(
            parent,
            title,
            text,
            width=width,
            height=height,
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

        settings.sync()

    return clickedButton


class MessageBox(QtWidgets.QDialog):

    @staticmethod
    def input(
        parent,
        title,
        text,
        inputText="",
        width=None,
        height=None,
        buttons=None,
        headerIcon=None,
        headerColor=None,
    ):
        """
        Convenience dialog to get a single text value from the user.
        
        :type parent: QWidget
        :type title: str
        :type text: str
        :type width: int
        :type height: int
        :type buttons: list[QMessageBox.StandardButton]
        :type headerIcon: str
        :type headerColor: str
        :rtype: QMessageBox.StandardButton
        """
        buttons = buttons or \
                  QtWidgets.QDialogButtonBox.Ok | \
                  QtWidgets.QDialogButtonBox.Cancel

        dialog = createMessageBox(
            parent,
            title,
            text,
            width=width,
            height=height,
            buttons=buttons,
            headerIcon=headerIcon,
            headerColor=headerColor,
            enableInputEdit=True,
        )

        dialog.setInputText(inputText)
        dialog.exec_()

        clickedButton = dialog.clickedStandardButton()

        return dialog.inputText(), clickedButton

    @staticmethod
    def question(
        parent,
        title,
        text,
        width=None,
        height=None,
        buttons=None,
        headerIcon=None,
        headerColor=None,
        enableDontShowCheckBox=False
    ):
        """
        Open a question message box with the given options.

        :type parent: QWidget
        :type title: str
        :type text: str
        :type headerIcon: str
        :type headerColor: str
        :type buttons: list[QMessageBox.StandardButton]

        :rtype: QMessageBox.StandardButton
        """
        buttons = buttons or \
            QtWidgets.QDialogButtonBox.Yes | \
            QtWidgets.QDialogButtonBox.No | \
            QtWidgets.QDialogButtonBox.Cancel

        clickedButton = showMessageBox(
            parent,
            title,
            text,
            width=width,
            height=height,
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
        text,
        width=None,
        height=None,
        buttons=None,
        headerIcon=None,
        headerColor="rgb(250, 160, 0)",
        enableDontShowCheckBox=False,
        force=False,
    ):
        """
        Open a warning message box with the given options.

        :type parent: QWidget
        :type title: str
        :type text: str
        :type buttons: list[QMessageBox.StandardButton]
        :type headerIcon: str
        :type headerColor: str
        :type enableDontShowCheckBox: bool
        :type force: bool

        :rtype: (QMessageBox.StandardButton, bool)
        """
        buttons = buttons or \
                  QtWidgets.QDialogButtonBox.Yes | \
                  QtWidgets.QDialogButtonBox.No

        clickedButton = showMessageBox(
            parent,
            title,
            text,
            width=width,
            height=height,
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
        text,
        width=None,
        height=None,
        buttons=None,
        headerIcon=None,
        headerColor="rgb(230, 80, 80)"
    ):
        """
        Open a critical message box with the given options.

        :type parent: QWidget
        :type title: str
        :type text: str
        :type headerIcon: str
        :type headerColor: str
        :type buttons: list[QMessageBox.StandardButton]

        :rtype: QMessageBox.StandardButton
        """
        buttons = buttons or QtWidgets.QDialogButtonBox.Ok

        clickedButton = showMessageBox(
            parent,
            title,
            text,
            width=width,
            height=height,
            buttons=buttons,
            headerIcon=headerIcon,
            headerColor=headerColor
        )

        return clickedButton

    def __init__(
            self,
            parent=None,
            width=None,
            height=None,
            enableInputEdit=False,
            enableDontShowCheckBox=False
    ):
        super(MessageBox, self).__init__(parent)
        self.setObjectName("messageBox")

        self._frame = None
        self._animation = None
        self._dontShowCheckbox = False
        self._clickedButton = None
        self._clickedStandardButton = None

        self.setMinimumWidth(width or 320)
        self.setMinimumHeight(height or 220)

        parent = self.parent()

        if parent:
            parent.installEventFilter(self)
            self._frame = QtWidgets.QFrame(parent)
            self._frame.setObjectName("messageBoxFrame")
            self._frame.show()
            self.setParent(self._frame)

        self._header = QtWidgets.QFrame(self)
        self._header.setFixedHeight(46)
        self._header.setObjectName("messageBoxHeaderFrame")
        self._header.setStyleSheet("background-color: rgb(0,0,0,0);")
        self._header.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Fixed)

        self._icon = QtWidgets.QLabel(self._header)
        self._icon.hide()
        self._icon.setFixedWidth(32)
        self._icon.setFixedHeight(32)
        self._icon.setScaledContents(True)
        self._icon.setAlignment(QtCore.Qt.AlignTop)
        self._icon.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                 QtWidgets.QSizePolicy.Preferred)

        self._title = QtWidgets.QLabel(self._header)
        self._title.setObjectName("messageBoxHeaderLabel")
        self._title.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)

        hlayout = QtWidgets.QHBoxLayout(self._header)
        hlayout.setContentsMargins(15, 7, 15, 10)
        hlayout.setSpacing(10)
        hlayout.addWidget(self._icon)
        hlayout.addWidget(self._title)

        self._header.setLayout(hlayout)

        bodyLayout = QtWidgets.QVBoxLayout(self)

        self._body = QtWidgets.QFrame(self)
        self._body.setObjectName("messageBoxBody")
        self._body.setLayout(bodyLayout)

        self._message = QtWidgets.QLabel(self._body)
        self._message.setWordWrap(True)
        self._message.setMinimumHeight(15)
        self._message.setAlignment(QtCore.Qt.AlignLeft)
        self._message.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._message.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Expanding)

        bodyLayout.addWidget(self._message)
        bodyLayout.setContentsMargins(15, 15, 15, 15)

        if enableInputEdit:
            self._inputEdit = QtWidgets.QLineEdit(self._body)
            self._inputEdit.setObjectName("messageBoxInputEdit")
            self._inputEdit.setMinimumHeight(32)
            self._inputEdit.setFocus()

            bodyLayout.addStretch(1)
            bodyLayout.addWidget(self._inputEdit)
            bodyLayout.addStretch(10)

        if enableDontShowCheckBox:
            msg = "Don't show this message again"
            self._dontShowCheckbox = QtWidgets.QCheckBox(msg, self._body)

            bodyLayout.addStretch(10)
            bodyLayout.addWidget(self._dontShowCheckbox)
            bodyLayout.addStretch(2)

        self._buttonBox = QtWidgets.QDialogButtonBox(None, QtCore.Qt.Horizontal, self)
        self._buttonBox.clicked.connect(self._clicked)
        self._buttonBox.accepted.connect(self._accept)
        self._buttonBox.rejected.connect(self._reject)

        vlayout1 = QtWidgets.QVBoxLayout(self)
        vlayout1.setContentsMargins(0, 0, 0, 0)

        vlayout1.addWidget(self._header)
        vlayout1.addWidget(self._body)
        bodyLayout.addWidget(self._buttonBox)

        self.setLayout(vlayout1)
        self.updateGeometry()

    def buttonBox(self):
        """
        Return the button box widget for the dialog.
        
        :rtype: QtGui.QDialogButtonBox 
        """
        return self._buttonBox

    def addButton(self, *args):
        """Create a push button with the given text and role"""
        self.buttonBox().addButton(*args)

    def eventFilter(self, object, event):
        """
        Update the geometry when the parent widget changes size.
        
        :type object: QtWidget.QWidget
        :type event: QtCore.QEvent 
        :rtype: bool 
        """
        if event.type() == QtCore.QEvent.Resize:
            self.updateGeometry()
        return super(MessageBox, self).eventFilter(object, event)

    def showEvent(self, event):
        """
        Fade in the dialog on show.

        :type event: QtCore.QEvent 
        :rtype: None 
        """
        self.updateGeometry()
        self.fadeIn()

    def updateGeometry(self):
        """
        Update the geometry to be in the center of it's parent.

        :rtype: None
        """
        frame = self._frame

        if frame:
            frame.setGeometry(self._frame.parent().geometry())
            frame.move(0, 0)

            geometry = self.geometry()
            centerPoint = frame.geometry().center()
            geometry.moveCenter(centerPoint)
            geometry.setY(geometry.y() - 50)
            self.move(geometry.topLeft())

    def fadeIn(self, duration=200):
        """
        Fade in the dialog using the opacity effect.

        :type duration: int 
        :rtype: QtCore.QPropertyAnimation 
        """
        if self._frame:
            self._animation = studioqt.fadeIn(self._frame, duration=duration)
        return self._animation

    def fadeOut(self, duration=200):
        """
        Fade out the dialog using the opacity effect.
        
        :type duration: int 
        :rtype: QtCore.QPropertyAnimation 
        """
        if self._frame:
            self._animation = studioqt.fadeOut(self._frame, duration=duration)
        return self._animation

    def _accept(self):
        """
        Triggered when the DialogButtonBox has been accepted.
        
        :rtype: None 
        """
        animation = self.fadeOut()

        if animation:
            animation.finished.connect(self._acceptAnimationFinished)
        else:
            self._acceptAnimationFinished()

    def _reject(self):
        """
        Triggered when the DialogButtonBox has been rejected.

        :rtype: None 
        """
        animation = self.fadeOut()

        if animation:
            animation.finished.connect(self._rejectAnimationFinished)
        else:
            self._rejectAnimationFinished()

    def _acceptAnimationFinished(self):
        """
        Triggered when the animation has finished on accepted.

        :rtype: None 
        """
        parent = self._frame or self
        parent.close()
        self.accept()

    def _rejectAnimationFinished(self):
        """
        Triggered when the animation has finished on rejected.

        :rtype: None 
        """
        parent = self._frame or self
        parent.close()
        self.reject()

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
        text = unicode(text)
        self._message.setText(text)

    def inputText(self):
        """
        Return the text that the user has given the input edit.

        :rtype: str 
        """
        return self._inputEdit.text()

    def setInputText(self, text):
        """
        Set the input text.

        :type text: str 
        """
        self._inputEdit.setText(text)

    def setButtons(self, buttons):
        """
        Set the buttons to be displayed in message box.

        :type buttons: QMessageBox.StandardButton
        :rtype: None 
        """
        self.buttonBox().setStandardButtons(buttons)

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
        self._icon.show()

    def _clicked(self, button):
        """
        Triggered when the user clicks a button.
        
        :type button: QWidgets.QPushButton
        :rtype: None 
        """
        self._clickedButton = button
        self._clickedStandardButton = self.buttonBox().standardButton(button)

    def clickedIndex(self):
        """
        Return the button that was clicked by its index.
        
        :rtype: int or None
        """
        for i, button in enumerate(self.buttonBox().buttons()):
            if button == self.clickedButton():
                return i

    def clickedButton(self):
        """
        Return the button that was clicked.
        
        :rtype: QtWidgets.QPushButton or None 
        """
        return self._clickedButton

    def clickedStandardButton(self):
        """
        Return the button that was clicked by the user.

        :rtype: QMessageBox.StandardButton or None
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

    def exec_(self):
        """
        Shows the dialog as a modal dialog
        
        :rtype: int or None
        """
        QtWidgets.QDialog.exec_(self)
        return self.clickedIndex()


def testMessageBox():

    with studioqt.app():

        title = "Test question dialog"
        text = "Would you like to create a snapshot icon?"

        buttons = QtWidgets.QDialogButtonBox.Yes | \
                  QtWidgets.QDialogButtonBox.Ignore | \
                  QtWidgets.QDialogButtonBox.Cancel

        result = MessageBox.question(None, title, text, buttons=buttons)
        print result

        title = "Test long text message"
        text = "This is to test a very long message. " \
               "This is to test a very long message. " \
               "This is to test a very long message. " \
               "This is to test a very long message. " \
               "This is to test a very long message. "

        buttons = QtWidgets.QDialogButtonBox.Yes | \
                  QtWidgets.QDialogButtonBox.Ignore | \
                  QtWidgets.QDialogButtonBox.Cancel

        result = MessageBox.question(None, title, text, buttons=buttons)
        print result

        title = "Test checkbox"
        text = "Testing the don't show check box. "

        buttons = QtWidgets.QDialogButtonBox.Ok | \
                  QtWidgets.QDialogButtonBox.Cancel

        print studioqt.MessageBox.input(
            None,
            "Rename",
            "Rename the selected item?",
            inputText="face.anim",
        )

        result = MessageBox.question(
            None,
            title,
            text,
            buttons=buttons,
            enableDontShowCheckBox=True
        )
        print result

        title = "Create a new thumbnail icon"
        text = "This will override the existing thumbnail. " \
               "Are you sure you would like to continue?"

        buttons = QtWidgets.QDialogButtonBox.Yes | \
                  QtWidgets.QDialogButtonBox.No

        result = MessageBox.warning(
            None,
            title,
            text,
            buttons=buttons,
            enableDontShowCheckBox=True
        )
        print result

        title = "Error saving item!"
        text = "An error has occurred while saving an item."
        result = MessageBox.critical(None, title, text)
        print result

        if result == QtWidgets.QDialogButtonBox.Yes:
            title = "Error while saving!"
            text = "There was an error while saving"
            MessageBox.critical(None, title, text)


if __name__ == "__main__":
    testMessageBox()
