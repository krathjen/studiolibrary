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

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary


__all__ = ["SettingsDialog"]


class SettingsDialogSignal(QtCore.QObject):
    """
    """
    onNameChanged = QtCore.Signal(object)
    onPathChanged = QtCore.Signal(object)
    onColorChanged = QtCore.Signal(object)
    onBackgroundColorChanged = QtCore.Signal(object)


class SettingsDialog(QtWidgets.QDialog):
    """
    """
    signal = SettingsDialogSignal()
    onNameChanged = signal.onNameChanged
    onPathChanged = signal.onPathChanged
    onColorChanged = signal.onColorChanged
    onBackgroundColorChanged = signal.onBackgroundColorChanged

    def __init__(self, parent, library):
        """
        :type parent: QtWidgets.QWidget
        :type library: studiolibrary.Library
        """
        QtWidgets.QDialog.__init__(self, parent)
        studioqt.loadUi(self)

        resource = studiolibrary.resource()
        self.setWindowIcon(resource.icon("icon_black"))

        windowTitle = "Studio Library - {version}"
        windowTitle = windowTitle.format(version=studiolibrary.version())
        self.setWindowTitle(windowTitle)

        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.rejectButton.clicked.connect(self.close)

        self.ui.browseColorButton.clicked.connect(self.browseColor)
        self.ui.browseLocationButton.clicked.connect(self.browseLocation)
        self.ui.browseBackgroundColorButton.clicked.connect(self.browseBackgroundColor)

        self.ui.theme1Button.clicked.connect(self.setTheme1)
        self.ui.theme2Button.clicked.connect(self.setTheme2)
        self.ui.theme3Button.clicked.connect(self.setTheme3)
        self.ui.theme4Button.clicked.connect(self.setTheme4)
        self.ui.theme5Button.clicked.connect(self.setTheme5)
        self.ui.theme6Button.clicked.connect(self.setTheme6)
        self.ui.theme7Button.clicked.connect(self.setTheme7)

        self.ui.background1Button.clicked.connect(self.setBackground1)
        self.ui.background2Button.clicked.connect(self.setBackground2)
        self.ui.background3Button.clicked.connect(self.setBackground3)
        self.ui.background4Button.clicked.connect(self.setBackground4)

        self._library = library
        self.updateStyleSheet()
        self.center()

    def acceptButton(self):
        """
        :rtype: QtWidgets.QPushButton
        """
        return self.ui.acceptButton

    def rejectButton(self):
        """
        :rtype: QtWidgets.QPushButton
        """
        return self.ui.rejectButton

    def accept(self):
        """
        Hides the modal dialog and sets the result code to Accepted.

        :rtype: None
        """
        self.validate()
        QtWidgets.QDialog.accept(self)

    def validate(self):
        """
        :rtype: None
        """
        try:
            library = self.library()
            library.validateName(self.name())
            library.validatePath(self.location())
        except Exception, e:
            QtWidgets.QMessageBox.critical(self, "Validate Error", str(e))
            raise

    def center(self, width=600, height=435):
        """
        :rtype: None
        """
        desktopRect = QtWidgets.QApplication.desktop().availableGeometry()
        center = desktopRect.center()
        self.setGeometry(0, 0, width, height)
        self.move(center.x() - self.width() * 0.5, center.y() - self.height() * 0.5)

    def library(self):
        """
        :rtype: studiolibrary.Library
        """
        return self._library

    def setTitle(self, text):
        """
        :type text: str
        :rtype: None
        """
        self.ui.title.setText(text)

    def setText(self, text):
        """
        :type text: str
        :rtype: None
        """
        self.ui.text.setText(text)

    def setHeader(self, text):
        """
        :type text: str
        :rtype: None
        """
        self.ui.header.setText(text)

    def color(self):
        """
        :rtype: studioqt.Color
        """
        return self.library().accentColor()

    def backgroundColor(self):
        """
        :rtype: studioqt.Color
        """
        return self.library().backgroundColor()

    def name(self):
        """
        :rtype: str
        """
        return str(self.ui.nameEdit.text())

    def setName(self, name):
        """
        :type name: str
        :rtype: None
        """
        self.ui.nameEdit.setText(name)

    def setLocation(self, path):
        """
        :type path: str
        """
        self.ui.locationEdit.setText(path)

    def location(self):
        """
        :rtype: str
        """
        return str(self.ui.locationEdit.text())

    def setUpdateEnabled(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self._update = value

    def setTheme1(self):
        """
        """
        c = studioqt.Color(230, 60, 60, 255)
        self.setColor(c)

    def setTheme2(self):
        """
        """
        c = studioqt.Color(255, 90, 40)
        self.setColor(c)

    def setTheme3(self):
        """
        """
        c = studioqt.Color(255, 125, 100, 255)
        self.setColor(c)

    def setTheme4(self):
        """
        """
        c = studioqt.Color(250, 200, 0, 255)
        self.setColor(c)

    def setTheme5(self):
        """
        """
        c = studioqt.Color(80, 200, 140, 255)
        self.setColor(c)

    def setTheme6(self):
        """
        """
        c = studioqt.Color(50, 180, 240, 255)
        self.setColor(c)

    def setTheme7(self):
        """
        """
        c = studioqt.Color(110, 110, 240, 255)
        self.setColor(c)

    def setBackground1(self):
        """
        """
        c = studioqt.Color(80, 80, 80)
        self.setBackgroundColor(c)

    def setBackground2(self):
        """
        """
        c = studioqt.Color(65, 65, 65)
        self.setBackgroundColor(c)

    def setBackground3(self):
        """
        """
        c = studioqt.Color(50, 50, 52)
        self.setBackgroundColor(c)

    def setBackground4(self):
        """
        """
        c = studioqt.Color(40, 40, 50)
        self.setBackgroundColor(c)

    def setColor(self, color):
        """
        :type color: studioqt.Color
        :rtype: None
        """
        self.library().setAccentColor(color)
        self.updateStyleSheet()
        self.onColorChanged.emit(self)

    def setBackgroundColor(self, color):
        """
        :type color: studioqt.Color
        :rtype: None
        """
        self.library().setBackgroundColor(color)
        self.updateStyleSheet()
        self.onBackgroundColorChanged.emit(self)

    def browseColor(self):
        """
        :rtype: None
        """
        color = self.color()
        d = QtWidgets.QColorDialog(self)
        d.setCurrentColor(color)

        colors = [
            # Top row, Bottom row
            (230, 60, 60), (250, 80, 130),
            (255, 90, 40), (240, 100, 170),
            (255, 125, 100), (240, 200, 150),
            (250, 200, 0), (225, 200, 40),
            (80, 200, 140), (80, 225, 120),
            (50, 180, 240), (100, 200, 245),
            (130, 110, 240), (180, 160, 255),
            (180, 110, 240), (210, 110, 255),
        ]

        index = -1

        for colorR, colorG, colorB in colors:

            for i in range(0, 3):
                index += 1

                if colorR < 0:
                    colorR = 0

                if colorG < 0:
                    colorG = 0

                if colorB < 0:
                    colorB = 0

                try:
                    standardColor = QtGui.QColor(colorR, colorG, colorB)
                    d.setStandardColor(index, standardColor)
                except:
                    standardColor = QtGui.QColor(colorR, colorG, colorB).rgba()
                    d.setStandardColor(index, standardColor)

                colorR -= 20
                colorB -= 20
                colorG -= 20

        d.currentColorChanged.connect(self.setColor)

        # PySide2 doesn't support d.open(), so we need to pass a blank slot.
        d.open(self, QtCore.SLOT("blankSlot()"))

        if d.exec_():
            self.setColor(d.selectedColor())
        else:
            self.setColor(color)

    @QtCore.Slot()
    def blankSlot(self):
        """
        Blank slot to fix an issue with PySide2.QColorDialog.open()
        """
        pass

    def browseBackgroundColor(self):
        """
        :rtype: None
        """
        color = self.backgroundColor()
        d = QtWidgets.QColorDialog(self)
        d.setCurrentColor(color)

        colors = [
            (0, 0, 0),
            (20, 20, 30),
            (0, 30, 60),
            (0, 60, 60),
            (0, 60, 30),
            (60, 0, 10),
            (60, 0, 40),
            (40, 15, 5),
        ]

        index = -1

        for colorR, colorG, colorB in colors:
            for i in range(0, 6):
                index += 1

                try:
                    standardColor = QtGui.QColor(colorR, colorG, colorB)
                    d.setStandardColor(index, standardColor)
                except:
                    standardColor = QtGui.QColor(colorR, colorG, colorB).rgba()
                    d.setStandardColor(index, standardColor)

                colorR += 20
                colorB += 20
                colorG += 20

        d.currentColorChanged.connect(self.setBackgroundColor)

        # PySide2 doesn't support d.open(), so we need to pass a blank slot.
        d.open(self, QtCore.SLOT("blankSlot()"))

        if d.exec_():
            self.setBackgroundColor(d.selectedColor())
        else:
            self.setBackgroundColor(color)

    def updateStyleSheet(self):
        """
        :rtype: None
        """
        self.setStyleSheet(self.library().theme().styleSheet())

    def browseLocation(self):
        """
        :rtype: None
        """
        path = self.location()
        path = self.browse(path, title="Browse Location")
        if path:
            self.setLocation(path)

    @staticmethod
    def browse(path, title="Browse Location"):
        """
        :type path: str
        :type title: str
        :rtype: str
        """
        if not path:
            from os.path import expanduser
            path = expanduser("~")

        path = str(QtWidgets.QFileDialog.getExistingDirectory(None, title, path))
        path = path.replace("\\", "/")
        return path
