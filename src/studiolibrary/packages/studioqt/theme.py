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


__all__ = ["Theme", "ThemeAction", "ThemesMenu"]


THEME_PRESETS = [
    {
        "name": "Blue",
        "accentColor": "rgb(50, 180, 240, 255)",
        "backgroundColor": "rgb(30, 30, 40, 255)",
    },
    {
        "name": "Green",
        "accentColor": "rgb(80, 200, 140, 255)",
        "backgroundColor": "rgb(30, 30, 40, 255)",
    },
    {
        "name": "Yellow",
        "accentColor": "rgb(250, 200, 0, 255)",
        "backgroundColor": "rgb(30, 30, 40, 255)",
    },
    {
        "name": "Orange",
        "accentColor": "rgb(255, 170, 0, 255)",
        "backgroundColor": "rgb(30, 30, 40, 255)",
    },
    {
        "name": "Peach",
        "accentColor": "rgb(255, 125, 100, 255)",
        "backgroundColor": "rgb(30, 30, 40, 255)",
    },
    {
        "name": "Red",
        "accentColor": "rgb(230, 60, 60, 255)",
        "backgroundColor": "rgb(30, 30, 40, 255)",
    },
    {
        "name": "Pink",
        "accentColor": "rgb(255, 87, 123, 255)",
        "backgroundColor": "rgb(30, 30, 40, 255)",
    },
    {
        "name": "Purple",
        "accentColor": "rgb(110, 110, 240, 255)",
        "backgroundColor": "rgb(30, 30, 40, 255)",
    },
]


def themePresets():
    """
    Return the default theme presets.

    :rtype list[Theme]
    """
    themes = []

    for preset in THEME_PRESETS:
        theme = Theme()
        theme.setSettings(preset)
        themes.append(theme)

    return themes


class ThemeAction(QtWidgets.QAction):

    def __init__(self, theme, *args):
        """
        :type theme: Theme
        :type menu: QtWidgets.QMenu
        :rtype: QtWidgets.QAction
        """
        QtWidgets.QAction.__init__(self, theme.name(), *args)
        self._theme = theme

        color = theme.accentColor()
        icon = studioqt.icon("radio_button_checked", color=color)
        self.setIcon(icon)

    def theme(self):
        """
        :rtype: Theme
        """
        return self._theme


class ThemesMenu(QtWidgets.QMenu):

    themeTriggered = QtCore.Signal(object)

    def __init__(self, parent=None, themes=None):
        """
        :type themes: list[Theme]
        :rtype: QtWidgets.QMenu
        """
        QtWidgets.QMenu.__init__(self, "Themes", parent)

        if not themes:
            themes = themePresets()

        for theme in themes:
            action = ThemeAction(theme, self)
            self.addAction(action)

        self.triggered.connect(self._themeTriggered)

    def _themeTriggered(self, action):
        """
        Triggered when a theme has been clicked.

        :type action: Action
        :rtype: None
        """
        if isinstance(action, ThemeAction):
            self.themeTriggered.emit(action.theme())


def showThemesMenu(parent=None, themes=None):
    """
    Show a menu with the given themes.

    :type themes: list[Theme]
    :type parent: QtWidgets.QWidget
    :rtype: QtWidgets.QAction
    """
    menu = ThemesMenu(themes=themes, parent=parent)
    position = QtWidgets.QCursor().pos()
    action = menu.exec_(position)
    return action


class Theme(object):

    DEFAULT_ACCENT_COLOR = QtGui.QColor(0, 175, 255)
    DEFAULT_BACKGROUND_COLOR = QtGui.QColor(70, 70, 80)

    def __init__(self):

        self._dpi = 1

        self._name = "Default"
        self._accentColor = None
        self._backgroundColor = None

        self.setAccentColor(self.DEFAULT_ACCENT_COLOR)
        self.setBackgroundColor(self.DEFAULT_BACKGROUND_COLOR)

    def settings(self):
        """
        Return a dictionary of settings for the current Theme.

        :rtype: dict
        """
        settings = {}

        settings["name"] = self.name()

        accentColor = self.accentColor()
        settings["accentColor"] = accentColor.toString()

        backgroundColor = self.backgroundColor()
        settings["backgroundColor"] = backgroundColor.toString()

        return settings

    def setSettings(self, settings):
        """
        Set a dictionary of settings for the current Theme.

        :type settings: dict
        :rtype: None
        """
        name = settings.get("name")
        self.setName(name)

        accentColor = settings.get("accentColor", self.accentColor().toString())
        accentColor = studioqt.Color.fromString(accentColor)
        self.setAccentColor(accentColor)

        backgroundColor = settings.get("backgroundColor", self.backgroundColor().toString())
        backgroundColor = studioqt.Color.fromString(backgroundColor)
        self.setBackgroundColor(backgroundColor)

    def dpi(self):
        """
        Return the dpi for the Theme

        :rtype: float
        """
        return self._dpi

    def setDpi(self, dpi):
        """
        Set the dpi for the Theme

        :type dpi: float
        :rtype: None
        """
        self._dpi = dpi

    def name(self):
        """
        Return the name for the Theme

        :rtype: str
        """
        return self._name

    def setName(self, name):
        """
        Set the name for the Theme

        :type name: str
        :rtype: None
        """
        self._name = name

    def iconColor(self):
        return studioqt.Color(250, 250, 250)

    def accentForgroundColor(self):
        return studioqt.Color(255, 255, 255, 225)

    def forgroundColor(self):
        return studioqt.Color(250, 250, 250, 225)

    def accentColor(self):
        """
        Return the accent color for the theme.

        :rtype: studioqt.Color
        """
        return self._accentColor

    def backgroundColor(self):
        """
        Return the background color for the theme.

        :rtype: studioqt.Color
        """
        return self._backgroundColor

    def setAccentColor(self, color):
        """
        Set the accent color for the theme.

        :type color: studioqt.Color | QtGui.QColor
        """
        if isinstance(color, basestring):
            color = studioqt.Color.fromString(color)

        if isinstance(color, QtGui.QColor):
            color = studioqt.Color.fromColor(color)

        self._accentColor = color

    def setBackgroundColor(self, color):
        """
        Set the background color for the theme.

        :type color: studioqt.Color | QtGui.QColor
        """
        if isinstance(color, basestring):
            color = studioqt.Color.fromString(color)

        if isinstance(color, QtGui.QColor):
            color = studioqt.Color.fromColor(color)

        self._backgroundColor = color

    def browseAccentColor(self, parent=None):
        """
        Show the color dialog to browser for a accent color.

        :type parent: QtWidgets.QWidget
        :rtype: None
        """
        color = self.accentColor()
        dialog = QtWidgets.QColorDialog(parent)
        dialog.setCurrentColor(color)
        dialog.connect(
            dialog,
            QtCore.SIGNAL("setAccentColor(const QColor&)"),
            self.setAccentColor
        )
        dialog.open()
        if dialog.exec_():
            self.setAccentColor(dialog.selectedColor())
        else:
            self.setAccentColor(color)

    def browseBackgroundColor(self, parent=None):
        """
        Show the color dialog to browser for a background color.

        :type parent: QtWidgets.QWidget
        :rtype: None
        """
        color = self.backgroundColor()
        dialog = QtWidgets.QColorDialog(parent)
        dialog.setCurrentColor(color)
        dialog.connect(
            dialog,
            QtCore.SIGNAL("setBackgroundColor(const QColor&)"),
            self.setBackgroundColor
        )
        dialog.open()
        if dialog.exec_():
            self.setBackgroundColor(dialog.selectedColor())
        else:
            self.setBackgroundColor(color)

    def options(self):
        """
        Return the variables used to customise the style sheet.

        :rtype: dict
        """
        accentColor = self.accentColor()
        backgroundColor = self.backgroundColor()

        textWhite = studioqt.Color(255, 255, 255, 200)
        backgroundWhite = studioqt.Color(255, 255, 255, 20)

        options = {
            "RESOURCE_DIRNAME": studioqt.RESOURCE_DIRNAME,

            "ACCENT_COLOR": accentColor.toString(),
            "ACCENT_COLOR_R": str(accentColor.red()),
            "ACCENT_COLOR_G": str(accentColor.green()),
            "ACCENT_COLOR_B": str(accentColor.blue()),

            "BACKGROUND_COLOR": backgroundColor.toString(),
            "BACKGROUND_COLOR_R": str(backgroundColor.red()),
            "BACKGROUND_COLOR_G": str(backgroundColor.green()),
            "BACKGROUND_COLOR_B": str(backgroundColor.blue()),

            # Item theme colors will be depricated soon.
            "ITEM_TEXT_COLOR": textWhite.toString(),
            "ITEM_TEXT_SELECTED_COLOR": textWhite.toString(),

            "ITEM_BACKGROUND_COLOR": backgroundWhite.toString(),
            "ITEM_BACKGROUND_SELECTED_COLOR":  accentColor.toString(),
        }

        return options

    def styleSheet(self):
        """
        Return the style sheet for this theme.

        :rtype: str
        """
        options = self.options()
        path = studioqt.resource().get("css", "default.css")
        styleSheet = studioqt.StyleSheet.fromPath(path, options=options, dpi=self.dpi())
        return styleSheet.data()


def example():
    """
    Run a simple example of theme menu.

    :rtype: None
    """
    themeAction = showThemesMenu()
    print "Accent color:", themeAction.theme().accentColor()
    print "Background color:", themeAction.theme().backgroundColor()


if __name__ == "__main__":
    with studioqt.app():
        example()