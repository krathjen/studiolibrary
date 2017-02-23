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
import shutil
import logging

from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary


__all__ = ["Library"]

logger = logging.getLogger(__name__)


class Library(QtCore.QObject):

    _instances = {}

    DEFAULT_NAME = "Default"
    ITEM_DATA_PATH = "{localPath}/item_data.json"
    FOLDER_DATA_PATH = "{localPath}/folder_data.json"

    @classmethod
    def instance(cls, name=None):
        """
        Return the library instance for the given name.

        :type name: str
        :rtype: Library
        """
        if not name:
            name = Library.DEFAULT_NAME

        if name not in Library._instances:
            library = cls(name)
            Library._instances[name] = library

        return Library._instances[name]

    @classmethod
    def default(cls):
        """
        Return the default library instance.

        :rtype: list[Library]
        """

        libraries = cls.libraries()

        for library in libraries:
            if library.isDefault():
                return library

        if libraries:
            return libraries[0]
        else:
            library = cls.instance(Library.DEFAULT_NAME)
            library.setDefault(True)
            return library

    @classmethod
    def libraries(cls):
        """
        Return all library instances.

        :rtype: list[Library]
        """
        cls.initLibraries()
        libraries = Library._instances.values()
        libraries.sort(key=lambda lib: lib.name())
        return libraries

    @classmethod
    def initLibraries(cls):
        """Initialise all library instances."""
        path = unicode(studiolibrary.LIBRARIES_PATH)
        if os.path.exists(path):
            for name in os.listdir(path):
                filename, extension = os.path.splitext(name)
                library_ = cls.instance(filename)

    @staticmethod
    def libraryWidgets():
        """
        Return all library widgets that have been loaded.

        :rtype: list[studiolibrary.LibraryWidget]
        """
        result = []
        for library in Library.libraries():
            if library.libraryWidget() is not None:
                result.append(library.libraryWidget())
        return result

    def __init__(self, name):
        """Create a new library instance."""

        super(Library, self).__init__()

        studiolibrary.validateName(name)

        self._name = name
        self._theme = None
        self._settings = {}
        self._isDefault = False
        self._libraryWidget = None

        self.loadSettings()

    def formatPath(self, value, **kwargs):
        """
        Resolve the given destination path.

        :type value: str
        :rtype: str
        """
        kwargs_ = {
            "name": self.name(),
            "path": self.path(),
            "root": self.path(),
            "localPath": self.localPath(),
        }

        if kwargs:
            kwargs_.update(kwargs)

        return unicode(value).format(**kwargs_)

    def folderDataPath(self):
        """
        Return the resolved path for the folder data.

        :rtype: str
        """
        return self.formatPath(self.FOLDER_DATA_PATH)

    def itemDataPath(self):
        """
        Return the resolved path for the item data.

        :rtype: str
        """
        return self.formatPath(self.ITEM_DATA_PATH)

    def name(self):
        """
        Return the name of the library.

        :rtype: str
        """
        return self._name

    def setName(self, name):
        """
        Set the name of the library.

        :type name: str
        """
        if self.name() == name:
            return

        studiolibrary.validateName(name)

        if self._name in self._instances:
            self._instances[name] = self._instances.pop(self.name())

        oldLocalPath = self.localPath()

        self._name = name

        # Make sure that the local path is renamed to the new name.
        if os.path.exists(oldLocalPath):
            newLocalPath = self.localPath()
            os.rename(oldLocalPath, newLocalPath)

        if self.libraryWidget():
            self.libraryWidget().updateWindowTitle()

    def path(self):
        """
        Return the location path on disc.

        :rtype: str
        """
        return self.settings().get("path", "")

    def setPath(self, path):
        """
        Set the path location on disc.

        :type path: str
        """
        if path.endswith("/"):
            path = path[:-1]

        studiolibrary.validatePath(path)
        self.settings()["path"] = path

        if self.libraryWidget():
            self.libraryWidget().reload()

    def setDefault(self, value):
        """
        Set this library as the default library.

        :type value: bool
        """
        for library in self.libraries():
            library._setDefault(False)
        self._setDefault(value)

    def _setDefault(self, value):
        """
        :type value: bool
        """
        self.settings()["isDefault"] = value

    def isDefault(self):
        """
        Return True if this is the default library.

        :rtype: bool
        """
        return self.settings().get("isDefault", False)

    def setKwargs(self, kwargs):
        """
        :type kwargs: dict
        """
        self.settings()["kwargs"] = kwargs

    def kwargs(self):
        """
        :rtype: dict
        """
        return self.settings().get("kwargs", {})

    # ------------------------------------------------------------------
    # Support for settings
    # ------------------------------------------------------------------

    def localPath(self):
        """
        :rtype: str
        """
        name = self.name()
        return os.path.join(studiolibrary.LIBRARIES_PATH, name)

    def settings(self):
        """
        :rtype: dict
        """
        settings = self._settings

        settings["theme"] = self.theme().settings()

        return settings

    def setSettings(self, settings):
        """
        :type settings: dict
        """
        self._settings = settings

        theme = settings.get("theme", None)
        if theme:
            self.theme().setSettings(theme)

    def settingsPath(self):
        """
        :rtype: str
        """
        return os.path.join(self.localPath(), "library.json")

    def saveSettings(self):
        """
        Save the settings dictionary to a local json location.

        :rtype: None
        """
        data = self.settings()
        path = self.settingsPath()
        studiolibrary.saveJson(path, data)

    def loadSettings(self):
        """
        Read the settings dict from the local json location.

        :rtype: None
        """
        path = self.settingsPath()
        try:
            data = studiolibrary.readJson(path)
            self.setSettings(data)
        except Exception, e:
            logger.exception(e)

    # ------------------------------------------------------------------
    # Support for themes and custom stylesheets
    # ------------------------------------------------------------------

    def theme(self):
        """
        Return the Theme object for the library.

        :rtype: studioqt.Theme
        """
        if not self._theme:
            self._theme = studioqt.Theme()

            # Load legacy theme data.
            settings = self.settings()

            color = settings.get("color")
            if color:
                self._theme.setAccentColor(color)

            color = settings.get("accentColor")
            if color:
                self._theme.setAccentColor(color)

            color = settings.get("backgroundColor")
            if color:
                self._theme.setBackgroundColor(color)

            # Load new theme data.
            themeSettings = settings.get("theme")
            if themeSettings:
                self._theme.setSettings(themeSettings)

        return self._theme

    def setTheme(self, theme):
        """
        Set the Theme object for the library.

        :rtype: studioqt.Theme
        """
        self._theme = theme

        if self.libraryWidget():
            self.libraryWidget().reloadStyleSheet()

    def accentColor(self):
        """
        :rtype: studioqt.Color
        """
        return self.theme().accentColor()

    def setAccentColor(self, color):
        """
        :type color: studioqt.Color
        """
        self.theme().setAccentColor(color)

        if self.libraryWidget():
            self.libraryWidget().reloadStyleSheet()

    def backgroundColor(self):
        """
        :rtype: studioqt.Color
        """
        return self.theme().backgroundColor()

    def setBackgroundColor(self, color):
        """
        :type color: studioqt.Color
        """
        self.theme().setBackgroundColor(color)

        if self.libraryWidget():
            self.libraryWidget().reloadStyleSheet()

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def libraryWidget(self):
        """
        :rtype: studiolibrary.LibraryWidget
        """
        return self._libraryWidget

    def setLibraryWidget(self, libraryWidget):
        """
        :type libraryWidget: studiolibrary.LibraryWidget
        """
        self._libraryWidget = libraryWidget

    def createLibraryWidget(self):
        """
        :rtype: studiolibrary.LibraryWidget
        """
        return studiolibrary.LibraryWidget(library=self)

    def reset(self):
        """
        Reset the library to the default settings.

        :rtype: None
        """
        kwargs = self.kwargs()
        self.delete(deleteInstance=False)
        self.show(**kwargs)

    def delete(self, deleteInstance=True):
        """
        Delete this library from the users local settings.

        :rtype: None
        """
        logger.debug("Deleting library: %s" % self.name())

        if self.libraryWidget():
            self.libraryWidget().close()
            self.setLibraryWidget(None)

        if os.path.exists(self.localPath()):
            shutil.rmtree(self.localPath())

        if deleteInstance:
            if self.name() in Library._instances:
                del Library._instances[self.name()]

        logger.debug("Deleted library: %s" % self.name())

    def showDeleteDialog(self):
        """
        Show the delete dialog for deleting this library.

        :rtype: int
        """
        message = u'''Would you like to remove the "{0}" library from the manager?
This does not modify or delete the contents of the library.'''.format(
            self.name())

        result = studioqt.MessageBox.question(
            None,
            "Remove Library",
            message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result == QtWidgets.QMessageBox.Yes:
            self.delete()

        return result

    def show(self):
        """Show the library widget/window for this library."""

        path = self.path()

        if not os.path.exists(path):

            result = self.showSettingsDialog()

            if result == QtWidgets.QDialog.Rejected:
                logger.debug("Dialog was canceled")
                return

        logger.debug("Showing library '%s'" % path)

        if not self.libraryWidget():
            libraryWidget = self.createLibraryWidget()
            self.setLibraryWidget(libraryWidget)
        else:
            self.libraryWidget().close()

        self.libraryWidget().show()
        self.libraryWidget().raise_()

    def settingsDialog(self):
        """
        Return a new instance of the settings dialog for this library.

        :rtype: studiolibrary.SettingsDialog
        """
        def validator():
            name = settingsDialog.name()
            path = settingsDialog.path()
            valid = [self.name()]

            studiolibrary.validateName(name, valid=valid)
            studiolibrary.validatePath(path)

        title = "Settings"
        header = "Local Library Settings"
        text = "All changes will be saved to your local settings."

        parent = self.libraryWidget()
        settingsDialog = studiolibrary.SettingsDialog(parent)

        settingsDialog.close()
        settingsDialog.setTitle(title)
        settingsDialog.setHeader(header)
        settingsDialog.setText(text)
        settingsDialog.setName(self.name())
        settingsDialog.setPath(self.path())
        settingsDialog.setValidator(validator)
        settingsDialog.setAccentColor(self.accentColor())
        settingsDialog.setBackgroundColor(self.backgroundColor())

        settingsDialog.accentColorChanged.connect(self.setAccentColor)
        settingsDialog.backgroundColorChanged.connect(self.setBackgroundColor)

        return settingsDialog

    def showSettingsDialog(self):
        """
        Show the settings dialog for this library.

        :rtype: int
        """
        path = self.path()
        name = self.name()
        accentColor = self.accentColor()
        backgroundColor = self.backgroundColor()

        dialog = self.settingsDialog()
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:

            if path != dialog.path():
                self.setPath(dialog.path())

            if name != dialog.name():
                self.setName(dialog.name())

            self.saveSettings()

        else:
            self.setAccentColor(accentColor)
            self.setBackgroundColor(backgroundColor)

        return result
