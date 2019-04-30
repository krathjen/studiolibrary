# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
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

from functools import partial

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt


class ColorButton(QtWidgets.QPushButton):

    def __init__(self, *args):
        QtWidgets.QPushButton.__init__(self, *args)


class ColorPickerAction(QtWidgets.QWidgetAction):

    def __init__(self, *args):
        super(ColorPickerAction, self).__init__(*args)

        self._picker = ColorPickerWidget(self.parent())
        self._picker.colorChanged.connect(self._triggered)

    def picker(self):
        """
        Get the picker widget instance.
        
        :rtype: ColorPickerWidget
        """
        return self._picker

    def _triggered(self):
        """Triggered when the checkbox value has changed."""
        self.trigger()
        self.parent().close()

    def createWidget(self, menu):
        """
        This method is called by the QWidgetAction base class.

        :type menu: QtWidgets.QMenu
        """
        widget = QtWidgets.QFrame(self.parent())
        widget.setObjectName("colorPickerAction")

        actionLayout = QtWidgets.QHBoxLayout(widget)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(self.picker(), stretch=1)
        widget.setLayout(actionLayout)

        return widget


class ColorPickerWidget(QtWidgets.QFrame):

    COLOR_BUTTON_CLASS = ColorButton

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
        """
        self._currentColor = color

    def setColors(self, colors):
        """
        Set the colors for the color bar.

        :type colors: list[str] or list[studioqt.Color]
        """
        self.deleteButtons()

        first = True
        last = False

        for i, color in enumerate(colors):

            if i == len(colors)-1:
                last = True

            if not isinstance(color, str):
                color = studioqt.Color(color)
                color = color.toString()

            callback = partial(self._colorChanged, color)
            css = "background-color: " + color

            button = self.COLOR_BUTTON_CLASS(self)
            button.setObjectName('colorButton')
            button.setStyleSheet(css)
            button.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Preferred
            )

            button.setProperty("first", first)
            button.setProperty("last", last)

            button.clicked.connect(callback)
            self.layout().addWidget(button)

            first = False

        button = QtWidgets.QPushButton("...", self)
        button.setObjectName('menuButton')
        button.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred
        )

        button.clicked.connect(self.browseColor)
        self.layout().addWidget(button)

    def setBrowserColors(self, colors):
        """
        :type colors: list((int,int,int))
        """
        self._browserColors = colors

    def browserColors(self):
        """
        Get the colors to be displayed in the browser
    
        :rtype: list[studioqt.Color]
        """
        return self._browserColors

    @QtCore.Slot()
    def blankSlot(self):
        """Blank slot to fix an issue with PySide2.QColorDialog.open()"""
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

        if d.exec_():
            self._colorChanged(d.selectedColor())
        else:
            self._colorChanged(color)


def example():
    """
    Example:

        import studiolibrary.widgets.colorpicker
        reload(studiolibrary.widgets.colorpicker)
        studiolibrary.widgets.colorpicker.example()
    """
    def _colorChanged(color):
        print("colorChanged:", color)

    style = """   
        #colorButton {
            margin: 5px;
            min-width: 100px;
            min-height: 100px;
        }
        
        #browseColorButton {
            margin: 5px;
            font-size: 45px;
            min-width: 100px;
            min-height: 100px;
        }
    """

    colors = [
        "rgb(230, 60, 60, 255)",
        "rgb(255, 90, 40)",
        "rgb(255, 125, 100, 255)",
        "rgb(250, 200, 0, 255)",
        "rgb(80, 200, 140, 255)",
        "rgb(50, 180, 240, 255)",
        "rgb(110, 110, 240, 255)",
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

    picker = ColorPickerWidget()
    picker.setColors(colors)
    picker.setStyleSheet(style)
    picker.setBrowserColors(browserColors)
    picker.colorChanged.connect(_colorChanged)
    picker.show()


def example2():
    """
    Example:

        import studiolibrary.widgets.colorpicker
        reload(studiolibrary.widgets.colorpicker)
        studiolibrary.widgets.colorpicker.example2()
    """
    menu = QtWidgets.QMenu()

    colors = [
        "rgb(230, 60, 60)",
        "rgb(255, 90, 40)",
        "rgb(255, 125, 100)",
        "rgb(250, 200, 0)",
        "rgb(80, 200, 140)",
        "rgb(50, 180, 240)",
        "rgb(110, 110, 240)",
    ]

    action = ColorPickerAction(menu)
    action.picker().setColors(colors)
    menu.addAction(action)

    colors = [
        "rgb(20, 20, 20)",
        "rgb(20, 30, 40)",
        "rgb(40, 40, 40)",
        "rgb(40, 50, 60)",
        "rgb(60, 60, 60)",
        "rgb(60, 70, 80)",
        "rgb(240, 240, 240)",
    ]

    action = ColorPickerAction(menu)
    action.picker().setColors(colors)
    menu.addAction(action)
    menu.addSeparator()

    menu.exec_()


if __name__ == "__main__":
    with studioqt.app():
        example()
