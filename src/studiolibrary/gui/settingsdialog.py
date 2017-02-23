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

from functools import partial

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary


__all__ = ["SettingsDialog"]


class SettingsDialog(QtWidgets.QDialog):

    DEFAULT_ACCENT_COLOR = QtGui.QColor(20, 175, 250)
    DEFAULT_BACKGROUND_COLOR = QtGui.QColor(70, 70, 80)

    DEFAULT_ACCENT_COLORS = [
        QtGui.QColor(230, 75, 75),
        QtGui.QColor(235, 100, 70),
        QtGui.QColor(240, 125, 100),
        QtGui.QColor(240, 190, 40),
        QtGui.QColor(80, 200, 140),
        QtGui.QColor(20, 175, 250),
        QtGui.QColor(110, 110, 240),
    ]

    DEFAULT_BACKGROUND_COLORS = [
        QtGui.QColor(70, 70, 80),
        QtGui.QColor(65, 65, 75),
        QtGui.QColor(55, 55, 65),
        QtGui.QColor(50, 50, 57),
        QtGui.QColor(40, 40, 47),
    ]

    accentColorChanged = QtCore.Signal(object)
    backgroundColorChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        """
        :type parent: QtWidgets.QWidget
        :type library: studiolibrary.Library
        """
        QtWidgets.QDialog.__init__(self, parent)
        studioqt.loadUi(self)

        self._validator = None
        self._accentColor = self.DEFAULT_ACCENT_COLOR
        self._backgroundColor = self.DEFAULT_BACKGROUND_COLOR

        resource = studiolibrary.resource()
        self.setWindowIcon(resource.icon("icon_black"))

        windowTitle = "Studio Library - {version}"
        windowTitle = windowTitle.format(version=studiolibrary.version())
        self.setWindowTitle(windowTitle)

        self.createAccentColorBar()
        self.createBackgroundColorBar()

        self.ui.acceptButton.clicked.connect(self.accept)
        self.ui.rejectButton.clicked.connect(self.close)
        self.ui.browsePathButton.clicked.connect(self.browsePath)

        self.updateStyleSheet()
        self.center()

    def resizeEvent(self, event):
        """
        Reimplemented to support the logo scaling on DPI screens.

        :type event: QtGui.QEvent
        :rtype: None
        """
        scaleFactor = 1.4
        height = self.ui.headerFrame.height()
        self.ui.logo.setFixedWidth(height / scaleFactor)
        self.ui.logo.setFixedHeight(height / scaleFactor)

    def _accentColorChanged(self, color):
        """
        Triggered when the user clicks/changes the accent color.

        :type color: studioqt.Color
        :rtype: None
        """
        self.setAccentColor(color)

    def _backgroundColorClicked(self, color):
        """
        Triggered when the user clicks/changes the background color.

        :type color: studioqt.Color
        :rtype: None
        """
        self.setBackgroundColor(color)

    def createAccentColorBar(self):
        """
        Create and setup the accent color bar.

        :rtype: None
        """
        browserColors_ = [
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

        browserColors = []
        for colorR, colorG, colorB in browserColors_:
            for i in range(0, 3):

                colorR = colorR if colorR > 0 else 0
                colorG = colorG if colorG > 0 else 0
                colorB = colorB if colorB > 0 else 0

                color = QtGui.QColor(colorR, colorG, colorB).rgba()
                browserColors.append(color)

                colorR -= 20
                colorB -= 20
                colorG -= 20

        hColorBar = studioqt.HColorBar()
        hColorBar.setColors(self.DEFAULT_ACCENT_COLORS)
        hColorBar.setCurrentColor(self.DEFAULT_ACCENT_COLOR)
        hColorBar.setBrowserColors(browserColors)
        hColorBar.colorChanged.connect(self._accentColorChanged)

        self.ui.accentColorBarFrame.layout().addWidget(hColorBar)

    def createBackgroundColorBar(self):
        """
        Create and setup the background color bar.

        :rtype: None
        """
        browserColors_ = [
            (0, 0, 0),
            (20, 20, 30),
            (0, 30, 60),
            (0, 60, 60),
            (0, 60, 30),
            (60, 0, 10),
            (60, 0, 40),
            (40, 15, 5),
        ]

        browserColors = []
        for colorR, colorG, colorB in browserColors_:
            for i in range(0, 6):

                color = QtGui.QColor(colorR, colorG, colorB).rgba()
                browserColors.append(color)

                colorR += 20
                colorB += 20
                colorG += 20

        hColorBar = studioqt.HColorBar()
        hColorBar.setColors(self.DEFAULT_BACKGROUND_COLORS)
        hColorBar.setCurrentColor(self.DEFAULT_BACKGROUND_COLOR)
        hColorBar.setBrowserColors(browserColors)
        hColorBar.colorChanged.connect(self._backgroundColorClicked)

        self.ui.backgroundColorBarFrame.layout().addWidget(hColorBar)

    def accept(self):
        """
        Hides the modal dialog and sets the result code to Accepted.

        :rtype: None
        """
        self.validate()
        QtWidgets.QDialog.accept(self)

    def setValidator(self, validator):
        """
        Set the validator for the dialog.

        :type validator: func
        :rtype: None
        """
        self._validator = validator

    def validator(self):
        """
        Return the validator for the dialog.

        :rtype: func
        """
        return self._validator

    def validate(self):
        """
        Run the validate.

        :rtype: None
        """
        try:
            validator = self.validator()
            if validator:
                validator()
        except Exception, e:
            QtWidgets.QMessageBox.critical(self, "Validate Error", str(e))
            raise

    def setTitle(self, text):
        """
        Set the title for the dialog.

        :type text: str
        :rtype: None
        """
        self.ui.title.setText(text)

    def setText(self, text):
        """
        Set the message for the dialog.

        :type text: str
        :rtype: None
        """
        self.ui.text.setText(text)

    def setHeader(self, text):
        """
        Set the header for the dialog.

        :type text: str
        :rtype: None
        """
        self.ui.header.setText(text)

    def name(self):
        """
        Return the text in the name field.

        :rtype: str
        """
        return self.ui.nameEdit.text()

    def setName(self, name):
        """
        Set the text in the name field.

        :type name: str
        :rtype: None
        """
        self.ui.nameEdit.setText(name)

    def path(self):
        """
        Return the text in the path field.

        :rtype: str
        """
        return self.ui.pathEdit.text()

    def setPath(self, path):
        """
        Set the text in the name field.

        :type path: str
        :rtype: None
        """
        self.ui.pathEdit.setText(path)

    def setAccentColor(self, color):
        """
        Set the current accent color.

        :type color: studioqt.Color
        :rtype: None
        """
        self._accentColor = color
        self.updateStyleSheet()
        self.accentColorChanged.emit(color)

    def setBackgroundColor(self, color):
        """
        Set the current background color.

        :type color: studioqt.Color
        :rtype: None
        """
        self._backgroundColor = color
        self.updateStyleSheet()
        self.backgroundColorChanged.emit(color)

    def accentColor(self):
        """
        Return the current accent color.

        :rtype: studioqt.Color
        """
        return self._accentColor

    def backgroundColor(self):
        """
        Return the current background color.

        :rtype: studioqt.Color
        """
        return self._backgroundColor

    def updateStyleSheet(self):
        """
        Update the style sheet with the current accent and background colors.

        :rtype: None
        """
        theme = studioqt.Theme()
        theme.setAccentColor(self.accentColor())
        theme.setBackgroundColor(self.backgroundColor())
        self.setStyleSheet(theme.styleSheet())

        # Update the font size to use "pt" for higher dpi screens.
        self.ui.text.setStyleSheet("font:11pt;")
        self.ui.title.setStyleSheet("font:22pt;")
        self.ui.header.setStyleSheet("font:15pt;")
        self.ui.nameEdit.setStyleSheet("font:12pt;")
        self.ui.pathEdit.setStyleSheet("font:12pt;")
        self.ui.nameLabel.setStyleSheet("font:14pt;")
        self.ui.themeLabel.setStyleSheet("font:14pt;")
        self.ui.locationLabel.setStyleSheet("font:14pt;")

    def browsePath(self):
        """
        Open the file dialog for setting a new path.

        :rtype: str
        """
        path = self.path()
        title = "Browse Location"

        if not path:
            from os.path import expanduser
            path = expanduser("~")

        path = QtWidgets.QFileDialog.getExistingDirectory(None, title, path)
        path = path.replace("\\", "/")

        if path:
            self.setPath(path)

        return path

    def center(self, width=600, height=435):
        """
        Center the dialog in the center of the active screen.

        :type width: int
        :type height: int
        :rtype: None
        """
        self.setGeometry(0, 0, width, height)
        geometry = self.frameGeometry()
        pos = QtWidgets.QApplication.desktop().cursor().pos()
        screen = QtWidgets.QApplication.desktop().screenNumber(pos)
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        centerPoint.setY(centerPoint.y() / 1.2)
        geometry.moveCenter(centerPoint)
        self.move(geometry.topLeft())


def example():
    """
    Example to show/test the SettingsDialog.

    :rtype: None
    """
    def _accentColorChanged(color):
        print "accent", color

    def _backgroundColorChanged(color):
        print "background:", color

    theme = studioqt.Theme()

    dialog = SettingsDialog()
    dialog.accentColorChanged.connect(_accentColorChanged)
    dialog.backgroundColorChanged.connect(_backgroundColorChanged)
    dialog.exec_()

    print dialog.name()
    print dialog.path()
    print dialog.accentColor()
    print dialog.backgroundColor()


if __name__ == "__main__":
    with studioqt.app():
        example()
