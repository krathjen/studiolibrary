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


__all__ = ["HColorBar"]


class HColorBar(QtWidgets.QFrame):

    colorChanged = QtCore.Signal(object)

    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)

        self._buttons = []
        self._currentColor = None
        self._browserColors = None

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _colorChanged(self, color):
        """
        Triggered when the user clicks or browses for a color.

        :type color: studioqt.Color
        :rtype: None
        """
        self._currentColor = color
        self.colorChanged.emit(color)

    def deleteButtons(self):
        """
        Delete all the color buttons.

        :rtype: None
        """
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            item.widget().deleteLater()

    def currentColor(self):
        """
        Return the current color.

        :rtype: studioqt.Color
        """
        return self._currentColor

    def setCurrentColor(self, color):
        """
        Set the current color.

        :type color: studioqt.Color
        :rtype: None
        """
        self._currentColor = color

    def setColors(self, colors, width=24):
        """
        Set the colors for the color bar.

        :type colors: list[studioqt.Color]
        :type width: int
        :rtype: None
        """
        self.deleteButtons()

        for color in colors:

            if not isinstance(color, studioqt.Color):
                color = studioqt.Color(color)

            callback = partial(self._colorChanged, color)
            css = "background-color: " + color.toString()

            button = QtWidgets.QPushButton()
            button.setStyleSheet(css)
            button.setMinimumWidth(width)
            button.setSizePolicy(
                QtWidgets.QSizePolicy.Preferred,
                QtWidgets.QSizePolicy.Preferred
            )
            button.clicked.connect(callback)
            self.layout().addWidget(button)

        button = QtWidgets.QPushButton("...")
        button.setMinimumWidth(width*2)
        button.setMaximumWidth(width*2)
        button.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Preferred
        )

        button.clicked.connect(self.browseColor)
        self.layout().addWidget(button)

    def setBrowserColors(self, colors):
        """
        :type colors: list((int,int,int))
        :rtype: None
        """
        self._browserColors = colors

    def browserColors(self):
        """

        :type colors:
        :rtype: None
        """
        return self._browserColors

    @QtCore.Slot()
    def blankSlot(self):
        """
        Blank slot to fix an issue with PySide2.QColorDialog.open()

        :rtype: None
        """
        pass

    def browseColor(self):
        """
        Show the color dialog.

        :rtype: None
        """
        color = self.currentColor()

        d = QtWidgets.QColorDialog(self)
        d.setCurrentColor(color)

        standardColors = self.browserColors()

        if standardColors:
            index = -1
            for standardColor in standardColors:
                index += 1

                try:
                    # Support for new qt5 signature
                    standardColor = QtGui.QColor(standardColor)
                    d.setStandardColor(index, standardColor)
                except:
                    # Support for new qt4 signature
                    standardColor = QtGui.QColor(standardColor).rgba()
                    d.setStandardColor(index, standardColor)

        d.currentColorChanged.connect(self._colorChanged)

        # PySide2 doesn't support d.open(), so we need to pass a blank slot.
        d.open(self, QtCore.SLOT("blankSlot()"))

        if d.exec_():
            self._colorChanged(d.selectedColor())
        else:
            self._colorChanged(color)


def example():
    """
    Example to show/test the HColorBar.

    :rtype: None
    """

    def _colorChanged(color):
        print "colorChanged:", color

    theme = studioqt.Theme()

    colors = [
        studioqt.Color(230, 60, 60, 255),
        studioqt.Color(255, 90, 40),
        studioqt.Color(255, 125, 100, 255),
        studioqt.Color(250, 200, 0, 255),
        studioqt.Color(80, 200, 140, 255),
        studioqt.Color(50, 180, 240, 255),
        studioqt.Color(110, 110, 240, 255),
    ]

    browserColors = []
    browserColors_ = [
        # Top row, Bottom row
        (230, 60, 60), (250, 80, 130),
        (255, 90, 40), (240, 100, 170),
        (255, 125, 100), (240, 200, 150),
        (250, 200, 0), (225, 200, 40),
        (80, 200, 140), (80, 225, 120),
        (50, 180, 240), (100, 200, 245),
        (130, 110, 240), (180, 160, 255),
        (180, 110, 240), (210, 110, 255)
    ]

    for colorR, colorG, colorB in browserColors_:
        for i in range(0, 3):
            color = QtGui.QColor(colorR, colorG, colorB)
            browserColors.append(color)

    colorBar = HColorBar()
    colorBar.setColors(colors)
    colorBar.setBrowserColors(browserColors)
    colorBar.colorChanged.connect(_colorChanged)
    colorBar.show()


if __name__ == "__main__":
    with studioqt.app():
        example()