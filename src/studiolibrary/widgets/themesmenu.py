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

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets
from studiovendor import six

import studioqt
import studiolibrary

from .separatoraction import SeparatorAction


__all__ = ["Theme", "ThemeAction", "ThemesMenu"]


THEME_PRESETS = [
    {
        "name": "Blue",
        "accentColor": "rgba(50, 180, 240, 255)",
        "backgroundColor": None,
    },
    {
        "name": "Green",
        "accentColor": "rgba(80, 200, 140, 255)",
        "backgroundColor": None,
    },
    {
        "name": "Yellow",
        "accentColor": "rgb(250, 200, 0)",
        "backgroundColor": None,
    },
    {
        "name": "Orange",
        "accentColor": "rgb(255, 170, 0)",
        "backgroundColor": None,
    },
    {
        "name": "Peach",
        "accentColor": "rgb(255, 125, 100)",
        "backgroundColor": None,
    },
    {
        "name": "Red",
        "accentColor": "rgb(230, 60, 60)",
        "backgroundColor": None,
    },
    {
        "name": "Pink",
        "accentColor": "rgb(255, 87, 123)",
        "backgroundColor": None,
    },
    {
        "name": "Purple",
        "accentColor": "rgb(110, 110, 240)",
        "backgroundColor": None,
    },
    {
        "name": "Dark",
        "accentColor": None,
        "backgroundColor": "rgb(60, 64, 79)",
    },
    {
        "name": "Grey",
        "accentColor": None,
        "backgroundColor": "rgb(60, 60, 60)",
    },
    {
        "name": "Light",
        "accentColor": None,
        "backgroundColor": "rgb(245, 245, 255)",
    },
]


def themePresets():
    """
    Return the default theme presets.

    :rtype list[Theme]
    """
    themes = []

    for data in THEME_PRESETS:
        theme = Theme()

        theme.setName(data.get("name"))
        theme.setAccentColor(data.get("accentColor"))
        theme.setBackgroundColor(data.get("backgroundColor"))

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

        if theme.accentColor():
            color = theme.accentColor()
        elif theme.backgroundColor():
            color = theme.backgroundColor()
        else:
            color = "rgb(255,255,255)"

        icon = studiolibrary.resource.icon(ThemesMenu.THEME_ICON, color=color)
        self.setIcon(icon)

    def theme(self):
        """
        Return the theme object for the action.
        
        :rtype: Theme
        """
        return self._theme


class ThemesMenu(QtWidgets.QMenu):

    THEME_ICON = "radio_button_checked_white"

    ENABLE_CUSTOM_ACTION = True

    def __init__(self, parent, theme, themes=None):
        """
        :type themes: list[Theme]
        :rtype: QtWidgets.QMenu
        """
        QtWidgets.QMenu.__init__(self, "Themes", parent)

        self._theme = theme
        self._themes = themes

        self.createActions()

    def createActions(self):
        """
        Crate the actions to be shown in the menu.
        
        :rtype: None 
        """
        # Create the menu actions for setting the accent color
        action = SeparatorAction("Accent", self)
        self.addAction(action)

        themes = self._themes

        if not themes:
            themes = themePresets()

        for theme in themes:
            if theme.accentColor():
                action = ThemeAction(theme, self)
                self.addAction(action)

        if self.ENABLE_CUSTOM_ACTION:
            action = QtWidgets.QAction("Custom", self)
            action.triggered.connect(self.theme().browseAccentColor)
            color = self.theme().accentColor().toString()
            icon = studiolibrary.resource.icon(ThemesMenu.THEME_ICON, color=color)
            action.setIcon(icon)
            self.addAction(action)

        # Create the menu actions for setting the background color
        action = SeparatorAction("Background", self)
        self.addAction(action)

        for theme in themes:
            if not theme.accentColor() and theme.backgroundColor():
                action = ThemeAction(theme, self)
                self.addAction(action)

        if self.ENABLE_CUSTOM_ACTION:
            action = QtWidgets.QAction("Custom", self)
            action.triggered.connect(self._theme.browseBackgroundColor)
            color = self._theme.backgroundColor().toString()
            icon = studiolibrary.resource.icon(ThemesMenu.THEME_ICON, color=color)
            action.setIcon(icon)
            self.addAction(action)

        self.triggered.connect(self._triggered)

    def theme(self):
        """
        Return the current theme for the menu.

        :rtype: studioqt.Theme
        """
        return self._theme

    def setTheme(self, theme):
        """
        Set the current theme for the menu.
        
        :type theme: studioqt.Theme
        :rtype: None 
        """
        self._theme = theme

    def _triggered(self, action):
        """
        Triggered when a theme has been clicked.

        :type action: Action
        :rtype: None
        """
        theme = self.theme()
        if not theme:
            raise Exception("Please set the current theme for the menu.")

        if not isinstance(action, ThemeAction):
            return

        if action.theme().accentColor():
            theme.setAccentColor(action.theme().accentColor())

        if action.theme().backgroundColor():
            theme.setBackgroundColor(action.theme().backgroundColor())


def showThemesMenu(parent=None, themes=None):
    """
    Show a menu with the given themes.

    :type themes: list[Theme]
    :type parent: QtWidgets.QWidget
    :rtype: QtWidgets.QAction
    """
    theme = Theme()
    menu = ThemesMenu(parent=parent, theme=theme, themes=themes)
    position = QtGui.QCursor().pos()
    action = menu.exec_(position)
    return theme


class Theme(QtCore.QObject):

    updated = QtCore.Signal()

    DEFAULT_DARK_COLOR = QtGui.QColor(60, 60, 60)
    DEFAULT_LIGHT_COLOR = QtGui.QColor(220, 220, 220)

    DEFAULT_ACCENT_COLOR = QtGui.QColor(30, 145, 245)
    DEFAULT_BACKGROUND_COLOR = QtGui.QColor(50, 50, 60)

    def __init__(self):
        QtCore.QObject.__init__(self)

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

        color = settings.get("accentColor")
        if color:
            color = studioqt.Color.fromString(color)
            self.setAccentColor(color)

        color = settings.get("backgroundColor")
        if color:
            color = studioqt.Color.fromString(color)
            self.setBackgroundColor(color)

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

    def isDark(self):
        """
        Return True if the current theme is dark.

        rtype: bool
        """
        # The luminance for digital formats are (0.299, 0.587, 0.114)
        red = self.backgroundColor().redF() * 0.299
        green = self.backgroundColor().greenF() * 0.587
        blue = self.backgroundColor().blueF() * 0.114

        darkness = red + green + blue

        if darkness < 0.6:
            return True

        return False

    def setDark(self):
        """
        Set the current theme to the default dark color.
        
        :rtype: None 
        """
        self.setBackgroundColor(self.DEFAULT_DARK_COLOR)

    def setLight(self):
        """
        Set the current theme to the default light color.

        :rtype: None 
        """
        self.setBackgroundColor(self.DEFAULT_LIGHT_COLOR)

    def iconColor(self):
        """
        Return the icon color for the theme.

        :rtype: studioqt.Color 
        """
        return self.foregroundColor()

    def accentForgroundColor(self):
        """
        Return the foreground color for the accent color.

        :rtype: studioqt.Color 
        """
        return studioqt.Color(255, 255, 255, 255)

    def foregroundColor(self):
        """
        Return the foreground color for the theme.

        :rtype: studioqt.Color 
        """
        if self.isDark():
            return studioqt.Color(250, 250, 250, 225)
        else:
            return studioqt.Color(0, 40, 80, 180)

    def itemBackgroundColor(self):
        """
        Return the item background color.

        :rtype: studioqt.Color 
        """
        if self.isDark():
            return studioqt.Color(255, 255, 255, 20)
        else:
            return studioqt.Color(255, 255, 255, 120)

    def itemBackgroundHoverColor(self):
        """
        Return the item background color when the mouse hovers over the item.

        :rtype: studioqt.Color 
        """
        return studioqt.Color(255, 255, 255, 60)

    def accentColor(self):
        """
        Return the accent color for the theme.

        :rtype: studioqt.Color or None
        """
        return self._accentColor

    def backgroundColor(self):
        """
        Return the background color for the theme.

        :rtype: studioqt.Color or None
        """
        return self._backgroundColor

    def setAccentColor(self, color):
        """
        Set the accent color for the theme.

        :type color: studioqt.Color | QtGui.QColor
        """
        if isinstance(color, six.string_types):
            color = studioqt.Color.fromString(color)

        if isinstance(color, QtGui.QColor):
            color = studioqt.Color.fromColor(color)

        self._accentColor = color

        self.updated.emit()

    def setBackgroundColor(self, color):
        """
        Set the background color for the theme.

        :type color: studioqt.Color | QtGui.QColor
        """
        if isinstance(color, six.string_types):
            color = studioqt.Color.fromString(color)

        if isinstance(color, QtGui.QColor):
            color = studioqt.Color.fromColor(color)

        self._backgroundColor = color

        self.updated.emit()

    def createColorDialog(
            self,
            parent,
            standardColors=None,
            currentColor=None,
    ):
        """
        Create a new instance of the color dialog.

        :type parent: QtWidgets.QWidget
        :type standardColors: list[int]
        :rtype: QtWidgets.QColorDialog
        """
        dialog = QtWidgets.QColorDialog(parent)

        if standardColors:
            index = -1
            for colorR, colorG, colorB in standardColors:
                index += 1

                color = QtGui.QColor(colorR, colorG, colorB).rgba()

                try:
                    # Support for new qt5 signature
                    color = QtGui.QColor(color)
                    dialog.setStandardColor(index, color)
                except:
                    # Support for new qt4 signature
                    color = QtGui.QColor(color).rgba()
                    dialog.setStandardColor(index, color)

        # PySide2 doesn't support d.open(), so we need to pass a blank slot.
        dialog.open(self, QtCore.SLOT("blankSlot()"))

        if currentColor:
            dialog.setCurrentColor(currentColor)

        return dialog

    def browseAccentColor(self, parent=None):
        """
        Show the color dialog for changing the accent color.
        
        :type parent: QtWidgets.QWidget
        :rtype: None
        """
        standardColors = [
            (230, 60, 60), (210, 40, 40), (190, 20, 20), (250, 80, 130),
            (230, 60, 110), (210, 40, 90), (255, 90, 40), (235, 70, 20),
            (215, 50, 0), (240, 100, 170), (220, 80, 150), (200, 60, 130),
            (255, 125, 100), (235, 105, 80), (215, 85, 60), (240, 200, 150),
            (220, 180, 130), (200, 160, 110), (250, 200, 0), (230, 180, 0),
            (210, 160, 0), (225, 200, 40), (205, 180, 20), (185, 160, 0),
            (80, 200, 140), (60, 180, 120), (40, 160, 100), (80, 225, 120),
            (60, 205, 100), (40, 185, 80), (50, 180, 240), (30, 160, 220),
            (10, 140, 200), (100, 200, 245), (80, 180, 225), (60, 160, 205),
            (130, 110, 240), (110, 90, 220), (90, 70, 200), (180, 160, 255),
            (160, 140, 235), (140, 120, 215), (180, 110, 240), (160, 90, 220),
            (140, 70, 200), (210, 110, 255), (190, 90, 235), (170, 70, 215)
        ]

        currentColor = self.accentColor()

        dialog = self.createColorDialog(parent, standardColors, currentColor)
        dialog.currentColorChanged.connect(self.setAccentColor)

        if dialog.exec_():
            self.setAccentColor(dialog.selectedColor())
        else:
            self.setAccentColor(currentColor)

    def browseBackgroundColor(self, parent=None):
        """
        Show the color dialog for changing the background color.

        :type parent: QtWidgets.QWidget
        :rtype: None
        """
        standardColors = [
            (0, 0, 0), (20, 20, 20), (40, 40, 40), (60, 60, 60),
            (80, 80, 80), (100, 100, 100), (20, 20, 30), (40, 40, 50),
            (60, 60, 70), (80, 80, 90), (100, 100, 110), (120, 120, 130),
            (0, 30, 60), (20, 50, 80), (40, 70, 100), (60, 90, 120),
            (80, 110, 140), (100, 130, 160), (0, 60, 60), (20, 80, 80),
            (40, 100, 100), (60, 120, 120), (80, 140, 140), (100, 160, 160),
            (0, 60, 30), (20, 80, 50), (40, 100, 70), (60, 120, 90),
            (80, 140, 110), (100, 160, 130), (60, 0, 10), (80, 20, 30),
            (100, 40, 50), (120, 60, 70), (140, 80, 90), (160, 100, 110),
            (60, 0, 40), (80, 20, 60), (100, 40, 80), (120, 60, 100),
            (140, 80, 120), (160, 100, 140), (40, 15, 5), (60, 35, 25),
            (80, 55, 45), (100, 75, 65), (120, 95, 85), (140, 115, 105)
        ]

        currentColor = self.backgroundColor()

        dialog = self.createColorDialog(parent, standardColors, currentColor)
        dialog.currentColorChanged.connect(self.setBackgroundColor)

        if dialog.exec_():
            self.setBackgroundColor(dialog.selectedColor())
        else:
            self.setBackgroundColor(currentColor)

    def options(self):
        """
        Return the variables used to customise the style sheet.

        :rtype: dict
        """
        accentColor = self.accentColor()
        accentForegroundColor = self.accentForgroundColor()

        foregroundColor = self.foregroundColor()
        backgroundColor = self.backgroundColor()

        itemBackgroundColor = self.itemBackgroundColor()
        itemBackgroundHoverColor = self.itemBackgroundHoverColor()

        if self.isDark():
            darkness = "white"
        else:
            darkness = "black"

        resourceDirname = studiolibrary.resource.RESOURCE_DIRNAME
        resourceDirname = resourceDirname.replace("\\", "/")

        options = {
            "DARKNESS": darkness,
            "RESOURCE_DIRNAME": resourceDirname,

            "ACCENT_COLOR": accentColor.toString(),
            "ACCENT_COLOR_R": str(accentColor.red()),
            "ACCENT_COLOR_G": str(accentColor.green()),
            "ACCENT_COLOR_B": str(accentColor.blue()),

            "ACCENT_FOREGROUND_COLOR": accentForegroundColor.toString(),

            "FOREGROUND_COLOR": foregroundColor.toString(),
            "FOREGROUND_COLOR_R": str(foregroundColor.red()),
            "FOREGROUND_COLOR_G": str(foregroundColor.green()),
            "FOREGROUND_COLOR_B": str(foregroundColor.blue()),

            "BACKGROUND_COLOR": backgroundColor.toString(),
            "BACKGROUND_COLOR_R": str(backgroundColor.red()),
            "BACKGROUND_COLOR_G": str(backgroundColor.green()),
            "BACKGROUND_COLOR_B": str(backgroundColor.blue()),

            "ITEM_TEXT_COLOR": foregroundColor.toString(),
            "ITEM_TEXT_SELECTED_COLOR": accentForegroundColor.toString(),

            "ITEM_BACKGROUND_COLOR": itemBackgroundColor.toString(),
            "ITEM_BACKGROUND_HOVER_COLOR": itemBackgroundHoverColor.toString(),
            "ITEM_BACKGROUND_SELECTED_COLOR": accentColor.toString(),
        }

        return options

    def styleSheet(self):
        """
        Return the style sheet for this theme.

        :rtype: str
        """
        options = self.options()
        path = studiolibrary.resource.get("css", "default.css")
        styleSheet = studioqt.StyleSheet.fromPath(path, options=options, dpi=self.dpi())
        return styleSheet.data()


def example():
    """
    Run a simple example of theme menu.

    :rtype: None
    """
    theme = showThemesMenu()
    print("Accent color:", theme.accentColor())
    print("Background color:", theme.backgroundColor())


if __name__ == "__main__":
    with studioqt.app():
        example()
