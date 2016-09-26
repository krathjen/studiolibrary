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


class ThemesWidget(QtWidgets.QWidget):

    themeClicked = QtCore.Signal(object)

    def __init__(self, parent=None, themes=None):
        """
        :type parent: QtWidgets.QWidget
        :type themes: list[Theme]
        """
        QtWidgets.QWidget.__init__(self, parent)

        if not themes:
            themes = themePresets()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        for theme in themes:

            color = theme.accentColor().toString()

            themeWidget = QtWidgets.QPushButton(self)
            themeWidget.setStyleSheet("background-color: " + color)

            callback = partial(self.themeClicked.emit, theme)
            themeWidget.clicked.connect(callback)
            layout.addWidget(themeWidget)


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
    position = QGui.QCursor().pos()
    action = menu.exec_(position)
    return action


class Theme(object):

    DEFAULT_ACCENT_COLOR = QtGui.QColor(0, 175, 255)
    DEFAULT_BACKGROUND_COLOR = QtGui.QColor(70, 70, 70)

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
        :rtype: studioqt.Color
        """
        return self._accentColor

    def backgroundColor(self):
        """
        :rtype: studioqt.Color
        """
        return self._backgroundColor

    def setAccentColor(self, color):
        """
        :type color: studioqt.Color | QtGui.QColor
        """
        if isinstance(color, basestring):
            color = studioqt.Color.fromString(color)

        if isinstance(color, QtGui.QColor):
            color = studioqt.Color.fromColor(color)

        self._accentColor = color

    def setBackgroundColor(self, color):
        """
        :type color: studioqt.Color | QtGui.QColor
        """
        if isinstance(color, basestring):
            color = studioqt.Color.fromString(color)

        if isinstance(color, QtGui.QColor):
            color = studioqt.Color.fromColor(color)

        self._backgroundColor = color

    def browseAccentColor(self, parent=None):
        """
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

        textWhite = studioqt.Color(255, 255, 255, 255)
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


def showExample():
    """
    Run a simple example of the widget.

    :rtype: QtWidgets.QWidget
    """
    def themeClicked(theme):
        print theme

    themesWidget = ThemesWidget()
    themesWidget.themeClicked.connect(themeClicked)

    themesWidget.show()
    return themesWidget


if __name__ == "__main__":
    with studioqt.app():
        w = showExample()