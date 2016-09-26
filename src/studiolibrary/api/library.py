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

import os
import shutil
import logging

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary


__all__ = ["Library", "LibraryError"]

logger = logging.getLogger(__name__)


class LibraryError(Exception):
    """"""
    pass


class LibraryValidateError(LibraryError):
    """"""
    pass


class Library(QtCore.QObject):

    _instances = {}

    DEFAULT_NAME = "Default"
    DEFAULT_PLUGINS = []

    ITEM_DATA_PATH = "{localPath}/item_data.json"
    FOLDER_DATA_PATH = "{localPath}/folder_data.json"

    @classmethod
    def instance(cls, name=None):
        """
        Return the library instance by name.

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
        for library in cls.libraries():
            if library.isDefault():
                return library

        return cls.instance(Library.DEFAULT_NAME)

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
        """
        Initialise all library instances.

        :rtype: None
        """
        path = studiolibrary.LIBRARIES_PATH
        if os.path.exists(path):
            for name in os.listdir(path):

                filename, extension = os.path.splitext(name)

                try:
                    studiolibrary.validateString(filename)
                    library_ = cls.instance(filename)
                except studiolibrary.ValidateStringError, e:
                    logger.debug(e)

    @staticmethod
    def windows():
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
        super(Library, self).__init__()

        self.validateName(name)

        self._name = name
        self._debug = False
        self._theme = None
        self._settings = {}
        self._isDefault = False
        self._libraryWidget = None
        self._settingsDialog = None
        self._pluginManager = studiolibrary.PluginManager()

        self.loadSettings()

    def format(self, value, **kwargs):
        """
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

        return value.format(**kwargs_)

    def folderDataPath(self):
        """
        Return the formatted path for the folder data.

        :rtype: str
        """
        return self.format(self.FOLDER_DATA_PATH)

    def itemDataPath(self):
        """
        Return the formatted path for the item data.

        :rtype: str
        """
        return self.format(self.ITEM_DATA_PATH)

    def isDebug(self):
        """
        Return True if debug mode is enabled.

        :rtype: bool
        """
        return self._debug

    def setLoggerLevel(self, level):
        """
        Set the logging level for the studiolibrary and plugins.

        :type level: int
        """
        logger = logging.getLogger("studiolibrary")
        logger.setLevel(level)
        for plugin in self.pluginManager().plugins().values():
            plugin.setLoggerLevel(level)

    def recordFromPath(self, path):
        """
        Return the record for the given path.

        :type path: str
        :rtype: studiolibrary.Record
        """
        plugin = self.pluginFromPath(path)
        if plugin:
            return plugin.record(path)
        logger.debug('Cannot find plugin for path extension "%s"' % path)

    def recordsFromPaths(self, paths):
        """
        Return the records for the given paths.

        :type paths: list[str]
        :rtype: list[studiolibrary.Record]
        """
        records = []
        for path in paths:
            record = self.recordFromPath(path)
            if record:
                records.append(record)
        return records

    def loadRecords(self, path, direction=studiolibrary.Direction.Down, depth=3):
        """
        Load the records for the given path by walking the tree.

        :type path: str
        :type direction: studiolibrary.Direction
        :rtype: list[studiolibrary.Record]
        """
        match = lambda path: self.pluginFromPath(path)

        paths = studiolibrary.findPaths(
            path,
            match=match,
            ignore=[".studioLibrary"],
            direction=direction,
            depth=depth
        )

        return self.recordsFromPaths(paths)

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
        :rtype: None
        """
        if self.name() == name:
            return

        self.validateName(name)

        if self._name in self._instances:
            self._instances[name] = self._instances.pop(self.name())

        oldLocalPath = self.localPath()

        self._name = name

        # Make sure that the local path is renamed to the new name.
        if os.path.exists(oldLocalPath):
            newLocalPath = self.localPath()
            os.rename(oldLocalPath, newLocalPath)

    def validateName(self, name, caseSensitive=True):
        """
        :type name: str
        """
        libraries = {}

        if not name or not name.strip():
            raise LibraryValidateError('Cannot use an empty name!')

        try:
            name.decode('ascii')
        except UnicodeDecodeError:
            raise LibraryValidateError('The name "%s" is not an ascii-encoded string!' % name)

        studiolibrary.validateString(name)

        if name in Library._instances:
            if self != Library._instances[name]:
                raise LibraryValidateError('The Library "%s" already exists!' % name)

        if caseSensitive:
            for n in Library._instances:
                libraries[n.lower()] = Library._instances[n]

            if name.lower() in libraries:
                if self != libraries[name.lower()]:
                    raise LibraryValidateError('The Library "%s" already exists. It is case sensitive!' % name)

    @staticmethod
    def validatePath(path):
        """
        :type path: str
        """
        if "\\" in path:
            raise LibraryValidateError("Please use '/' instead of '\\'. Invalid token found for path '%s'!" % path)

        if not path or not path.strip():
            raise LibraryValidateError("Cannot set an empty path '%s'!" % path)

        if not os.path.exists(path):
            raise LibraryValidateError("Cannot find folder path '%s'!" % path)

    def path(self):
        """
        :rtype: str
        """
        return self.settings().get("path", "")

    def setPath(self, path):
        """
        :type path: str
        """
        if path.endswith("/"):
            path = path[:-1]

        self.validatePath(path)
        self.settings()["path"] = path

    def setDefault(self, value):
        """
        :type value: bool
        :rtype: None
        """
        for library in self.libraries():
            library._setDefault(False)
        self._setDefault(value)

    def _setDefault(self, value):
        """
        :type value: bool
        :rtype: None
        """
        self.settings()["isDefault"] = value

    def isDefault(self):
        """
        :rtype: bool
        """
        return self.settings().get("isDefault", False)

    def setKwargs(self, kwargs):
        """
        :type kwargs: dict
        :rtype: None
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
        except:
            pass

    # ------------------------------------------------------------------
    # Support for plugin framework
    # ------------------------------------------------------------------

    def pluginFromPath(self, path):
        """
        :type path: str
        :rtype: studiolibrary.Plugin
        """
        plugins = self.pluginManager().plugins().values()
        for plugin in plugins:
            if plugin.match(path):
                return plugin
        return None

    def pluginManager(self):
        """
        :rtype: studiolibrary.PluginManager
        """
        return self._pluginManager

    def plugins(self):
        """
        :rtype: list[str]
        """
        return self.settings().get("plugins", Library.DEFAULT_PLUGINS)

    def setPlugins(self, plugins):
        """
        :type plugins: list[str]
        :rtype: None
        """
        self.settings()["plugins"] = plugins

    def loadPlugin(self, name):

        """
        :type name: str
        :rtype: None
        """
        return self.pluginManager().loadPlugin(name, library=self)

    def loadPlugins(self):
        """
        :rtype: None
        """
        for name in self.plugins():
            self.loadPlugin(name)

    def loadedPlugins(self):
        """
        :rtype: dict[studiolibrary.Plugin]
        """
        return self.pluginManager().plugins()

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

            color = settings.get("color", None)
            if color:
                self._theme.setAccentColor(color)

            color = settings.get("accentColor", None)
            if color:
                self._theme.setAccentColor(color)

            color = settings.get("backgroundColor", None)
            if color:
                self._theme.setBackgroundColor(color)

            # Load new theme data.
            themeSettings = settings.get("theme", None)
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

    def showDeleteDialog(self):
        """
        :rtype: None
        """
        message = """Would you like to remove the "%s" library from the manager?
This does not modify or delete the contents of the library.""" % self.name()

        result = studioqt.MessageBox.question(
            None,
            "Remove Library",
            message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result == QtWidgets.QMessageBox.Yes:
            self.delete()

        return result

    def delete(self, deleteInstance=True):
        """
        :rtype: None
        """
        logger.debug("Deleting library: %s" % self.name())

        if self.libraryWidget():
            self.libraryWidget().close()
            self.setLibraryWidget(None)

        if self.settingsDialog():
            self.settingsDialog().close()
            self.setSettingsDialog(None)

        if os.path.exists(self.localPath()):
            shutil.rmtree(self.localPath())

        if deleteInstance:
            del Library._instances[self.name()]

        logger.debug("Deleted library: %s" % self.name())

    def reset(self):
        """
        Reset the library to the default settings.

        :rtype: None
        """
        kwargs = self.kwargs()

        self.delete(deleteInstance=False)

        self.show(**kwargs)

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

    def load(self):
        """
        :rtype: None
        """
        self.show(**self.kwargs())

    def createLibraryWidget(self):
        """
        :rtype: studiolibrary.LibraryWidget
        """
        return studiolibrary.LibraryWidget(library=self)

    def show(self, **kwargs):
        """
        :rtype: None
        """
        if not self.path():
            result = self.execWelcomeDialog()
            if result == QtWidgets.QDialog.Rejected:
                logger.debug("Dialog was canceled")
                return

        elif not os.path.exists(self.path()):
            result = self.execSettingsDialog()
            if result == QtWidgets.QDialog.Rejected:
                logger.debug("Dialog was canceled")
                return

        logger.debug("Showing library '%s'" % self.path())
        self.setKwargs(kwargs)

        # Create a new window
        if not self.libraryWidget():
            libraryWidget = self.createLibraryWidget()
            self.setLibraryWidget(libraryWidget)
        else:
            self.libraryWidget().close()

        self.libraryWidget().show()
        self.libraryWidget().raise_()

    def settingsDialog(self):
        """
        :rtype: studiolibrary.SettingsDialog
        """
        if not self._settingsDialog:
            self._settingsDialog = studiolibrary.SettingsDialog(None, library=self)
        return self._settingsDialog

    def setSettingsDialog(self, dialog):
        """
        :type dialog: studiolibrary.SettingsDialog
        """
        self._settingsDialog = dialog

    def execSettingsDialog(self):
        """
        :rtype: bool
        """
        self.showSettingsDialog()
        return self._execSettingsDialog()

    def execWelcomeDialog(self):
        """
        :rtype: bool
        """
        self.showWelcomeDialog()
        return self._execSettingsDialog()

    def _execSettingsDialog(self):
        """
        :rtype: bool
        """
        color = self.accentColor()
        backgroundColor = self.backgroundColor()
        result = self.settingsDialog().exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.saveSettingsDialog()
        else:
            self.setAccentColor(color)
            self.setBackgroundColor(backgroundColor)

        return result

    @staticmethod
    def showNewLibraryDialog():
        """
        :rtype: None
        """
        library = Library("None")

        settingsDialog = studiolibrary.SettingsDialog(None, library=library)
        settingsDialog.setTitle("New Library!")
        settingsDialog.setHeader("Create a new library")
        settingsDialog.setText(
            "Create a new library with a different folder location and switch between them. "
            "For example; This could be useful when working on different film productions, "
            "or for having a shared library and a local library."
        )

        result = settingsDialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            name = settingsDialog.name()
            path = settingsDialog.location()

            library.validateName(name)
            library.validatePath(path)

            library = Library.instance(name)

            library.setPath(path)
            library.setAccentColor(settingsDialog.color())
            library.setBackgroundColor(settingsDialog.backgroundColor())

            library.show()

            return library
        else:
            logger.info("New library dialog was canceled!")

    def showWelcomeDialog(self):
        """
        :rtype: studiolibrary.SettingsDialog
        """
        self.showSettingsDialog()
        self.settingsDialog().setTitle("Hello!")
        self.settingsDialog().setHeader("Welcome to the Studio Library")
        self.settingsDialog().setText("""Before you get started please choose a folder location for storing the data. \
A network folder is recommended for sharing within a studio.""")
        return self.settingsDialog()

    def showSettingsDialog(self):
        """
        :rtype: studiolibrary.SettingsDialog
        """
        self.settingsDialog().close()

        self.settingsDialog().setTitle("Settings")
        self.settingsDialog().setHeader("Local Library Settings")
        self.settingsDialog().setText("All changes will be saved to your local settings.")

        self.settingsDialog().setName(self.name())
        self.settingsDialog().setLocation(self.path())
        self.settingsDialog().updateStyleSheet()

        self.settingsDialog().showNormal()
        return self.settingsDialog()

    def saveSettingsDialog(self):
        """
        :rtype: None
        """
        if len(Library.libraries()) == 1:
            self.setDefault(True)

        self.setName(self.settingsDialog().name())
        self.setAccentColor(self.settingsDialog().color())
        self.setPath(self.settingsDialog().location())
        self.setBackgroundColor(self.settingsDialog().backgroundColor())
        self.settingsDialog().close()
        self.saveSettings()
