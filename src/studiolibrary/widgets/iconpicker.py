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

from functools import partial

from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt

from studiolibrary import resource


class IconButton(QtWidgets.QToolButton):

    def __init__(self, *args):
        super(IconButton, self).__init__(*args)

        self.setObjectName('iconButton')

        self._iconPath = None

        self.setCheckable(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def setIconPath(self, path):
        """
        Set the path for the button.

        :type path: str
        """
        self._iconPath = path
        self.updateIcon()

    def updateIcon(self):

        self.setToolTip(self._iconPath)
        self.setStatusTip(self._iconPath)

        color = self.palette().color(self.foregroundRole())
        color = studioqt.Color.fromColor(color)

        icon = resource.icon(self._iconPath, color=color)
        self.setIcon(icon)

    def iconPath(self):
        """
        Get the color for the button.

        :rtype: str
        """
        return self._iconPath


class IconPickerAction(QtWidgets.QWidgetAction):

    def __init__(self, *args):
        super(IconPickerAction, self).__init__(*args)

        self._picker = IconPickerWidget()
        self._picker.setMouseTracking(True)
        self._picker.setObjectName("iconPickerAction")
        self._picker.iconChanged.connect(self._triggered)

    def picker(self):
        """
        Get the picker widget instance.

        :rtype: IconPickerWidget
        """
        return self._picker

    def _triggered(self):
        """Triggered when the checkbox value has changed."""
        self.trigger()

        if isinstance(self.parent().parent(), QtWidgets.QMenu):
            self.parent().parent().close()

        elif isinstance(self.parent(), QtWidgets.QMenu):
            self.parent().close()

    def createWidget(self, menu):
        """
        This method is called by the QWidgetAction base class.

        :type menu: QtWidgets.QMenu
        """
        widget = QtWidgets.QFrame(menu)
        widget.setObjectName("iconPickerAction")

        self.picker().setParent(widget)

        actionLayout = QtWidgets.QHBoxLayout(widget)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(self.picker(), stretch=1)
        widget.setLayout(actionLayout)

        return widget


class IconPickerWidget(QtWidgets.QFrame):

    BUTTON_CLASS = IconButton

    iconChanged = QtCore.Signal(object)

    def __init__(self, *args):
        QtWidgets.QFrame.__init__(self, *args)

        self._buttons = []
        self._currentIcon = None
        self._menuButton = None

        layout = QtWidgets.QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def enterEvent(self, event):
        """
        Overriding this method to fix a bug with custom actions.

        :type event: QtCore.QEvent
        """
        if self.parent():
            menu = self.parent().parent()
            if isinstance(menu, QtWidgets.QMenu):
                menu.setActiveAction(None)

    def _iconChanged(self, iconPath):
        """
        Triggered when the user clicks or browses for a color.

        :type iconPath: str
        :rtype: None
        """
        self.setCurrentIcon(iconPath)
        self.iconChanged.emit(iconPath)

    def menuButton(self):
        """
        Get the menu button used for browsing for custom colors.

        :rtype: QtGui.QWidget
        """
        return self._menuButton

    def deleteButtons(self):
        """
        Delete all the color buttons.

        :rtype: None
        """
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            item.widget().deleteLater()

    def currentIcon(self):
        """
        Return the current color.

        :rtype: studioqt.Color
        """
        return self._currentIcon

    def setCurrentIcon(self, color):
        """
        Set the current color.

        :type color: studioqt.Color
        """
        self._currentIcon = color
        self.refresh()

    def refresh(self):
        """Update the current state of the selected color."""
        for button in self._buttons:
            button.setChecked(button.iconPath() == self.currentIcon())

    def updateTheme(self):
        for button in self._buttons:
            button.updateIcon()

    def setIcons(self, icons):
        """
        Set the colors for the color bar.

        :type icons: list[str] or list[studioqt.Icon]
        """
        self.deleteButtons()

        i = 0
        first = True
        last = False

        positions = [(i, j) for i in range(5) for j in range(5)]
        for position, iconPath in zip(positions, icons):
            i += 1

            if i == len(icons) - 1:
                last = True

            callback = partial(self._iconChanged, iconPath)

            button = self.BUTTON_CLASS(self)
            button.setIconPath(iconPath)
            # button.setIconSize(QtCore.QSize(16, 16))

            button.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Preferred
            )

            button.setProperty("first", first)
            button.setProperty("last", last)

            button.clicked.connect(callback)

            self.layout().addWidget(button, *position)

            self._buttons.append(button)

            first = False

        self._menuButton = QtWidgets.QPushButton("...", self)
        self._menuButton.setObjectName('menuButton')
        self._menuButton.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred
        )

        self._menuButton.clicked.connect(self.browseColor)
        self.layout().addWidget(self._menuButton)

        self.refresh()
        self.updateTheme()

    @QtCore.Slot()
    def blankSlot(self):
        """Blank slot to fix an issue with PySide2.QColorDialog.open()"""
        pass

    def browseColor(self):
        """
        Show the color dialog.

        :rtype: None
        """
        pass
        # color = self.currentColor()
        # if color:
        #     color = studioqt.Color.fromString(color)
        #
        # d = QtWidgets.QColorDialog(self)
        # d.setCurrentColor(color)
        #
        # d.currentColorChanged.connect(self._colorChanged)
        #
        # if d.exec_():
        #     self._colorChanged(d.selectedColor())
        # else:
        #     self._colorChanged(color)


def example():
    """
    Example:

        import studiolibrary.widgets.colorpicker
        reload(studiolibrary.widgets.colorpicker)
        studiolibrary.widgets.colorpicker.example()
    """

    def _iconChanged(icon):
        print("iconChanged:", icon)

    style = """   
    #iconButton {
        margin: 2px;
        min-width: 18px;
        min-height: 18px;
        background-color: rgba(0,0,0,0);
    }
    """

    from studiolibrary import resource

    icons = []
    names = [
        "folder.svg",
        "user.svg",
        "character.svg",
        "users.svg",
        "inbox.svg",
        "favorite.svg",
        "shot.svg",
        "asset.svg",
        "assets.svg",
    ]

    for name in names:
        icons.append(resource.icon(name, color="rgb(255,255,255)"))

    picker = IconPickerWidget()
    picker.setStyleSheet(style)
    picker.setIcons(icons)
    picker.iconChanged.connect(_iconChanged)
    picker.show()


if __name__ == "__main__":
    with studioqt.app():
        example()
