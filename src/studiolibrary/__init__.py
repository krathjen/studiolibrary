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
import sys


__version__ = "1.24.3"
__encoding__ = sys.getfilesystemencoding()

_package = None
_resource = None
_analytics = None
_scriptJob = None

PATH = unicode(os.path.abspath(__file__), __encoding__)
DIRNAME = os.path.dirname(PATH).replace('\\', '/')
PACKAGES_PATH = DIRNAME + "/packages"
RESOURCE_PATH = DIRNAME + "/gui/resource"
PACKAGE_HELP_URL = "http://www.studiolibrary.com"
PACKAGE_JSON_URL = "http://dl.dropbox.com/u/28655980/studiolibrary/studiolibrary.json"
CHECK_FOR_UPDATES_ENABLED = True

HOME_PATH = os.getenv('APPDATA') or os.getenv('HOME')
LIBRARIES_PATH = HOME_PATH + "/StudioLibrary/Libraries"


def setup(path):
    """
    Setup the packages that have been decoupled from the Studio Library.

    :param path: The folder location that contains all the packages.
    :type path: str

    :rtype: None
    """
    if os.path.exists(path) and path not in sys.path:
        print "Adding '{path}' to the sys.path".format(path=path)
        sys.path.append(path)


setup(PACKAGES_PATH)


import studioqt

from studiolibrary.main import main

from studiolibrary.core.utils import *
from studiolibrary.core.package import Package
from studiolibrary.core.basepath import BasePath
from studiolibrary.core.metafile import MetaFile
from studiolibrary.core.settings import Settings
from studiolibrary.core.analytics import Analytics
from studiolibrary.core.baseplugin import BasePlugin
from studiolibrary.core.pluginmanager import PluginManager

from studiolibrary.gui.mayadockwidgetmixin import MayaDockWidgetMixin
from studiolibrary.gui.libraryitem import LibraryItem
from studiolibrary.gui.librarywidget import LibraryWidget
from studiolibrary.gui.previewwidget import PreviewWidget
from studiolibrary.gui.librariesmenu import LibrariesMenu
from studiolibrary.gui.settingsdialog import SettingsDialog
from studiolibrary.gui.checkforupdatesthread import CheckForUpdatesThread

from studiolibrary.api.record import Record
from studiolibrary.api.plugin import Plugin
from studiolibrary.api.library import Library


def enableMayaClosedEvent():
    """
    Create a Maya script job to trigger on the event "quitApplication".

    :rtype: None
    """
    global _scriptJob

    if isMaya():
        import maya.cmds
        if not _scriptJob:
            _scriptJob = maya.cmds.scriptJob(
                event=[
                    "quitApplication",
                    "import studiolibrary;studiolibrary.mayaClosedEvent()"
                ]
            )


def mayaClosedEvent():
    """
    This functions is triggered when the user closes Maya.

    :rtype: None
    """
    for window in windows():
        window.saveSettings()


def resource():
    """
    Return a resource object for getting content from the resource folder.

    :rtype: studioqt.Resource
    """
    global _resource

    if not _resource:
        _resource = studioqt.Resource(dirname=RESOURCE_PATH)

    return _resource


def package():
    """
    Return a Package object for getting info about the Studio Library.

    :rtype: studiolibrary.package.Package
    """
    global _package

    if not _package:
        _package = Package()

    _package.setJsonUrl(PACKAGE_JSON_URL)
    _package.setHelpUrl(PACKAGE_HELP_URL)
    _package.setVersion(__version__)
    return _package


def version():
    """
    Return the current version of the Studio Library

    :rtype: str
    """
    return package().version()


def analytics():
    """
    :rtype: studiolibrary.analytics.Analytics
    """
    global _analytics

    if not _analytics:

        _analytics = Analytics(
            tid=Analytics.DEFAULT_ID,
            name="StudioLibrary",
            version=package().version()
        )

    _analytics.setEnabled(Analytics.ENABLED)
    return _analytics


def windows():
    """
    Return a list of all the loaded library windows.

    :rtype: list[MainWindow]
    """
    return Library.windows()


def library(name=None):
    """
    Return a library by name.

    :type name: str
    :rtype: studiolibrary.Library
    """
    return Library.instance(name)


def libraries():
    """
    Return a list of the loaded libraries.

    :rtype: list[studiolibrary.Library]
    """
    return Library.libraries()


def loadFromCommand():
    """
    Triggered when the Studio Library is loaded from the command line.

    :rtype: None
    """
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-p", "--plugins", dest="plugins",
                      help="", metavar="PLUGINS", default="None")
    parser.add_option("-r", "--root", dest="root",
                      help="", metavar="ROOT")
    parser.add_option("-n", "--name", dest="name",
                      help="", metavar="NAME")
    parser.add_option("-v", "--version", dest="version",
                      help="", metavar="VERSION")
    (options, args) = parser.parse_args()

    name = options.name
    plugins = eval(options.plugins)

    main(name=name, plugins=plugins)


def about():
    """
    Return a small description about the Studio Library.

    :rtype str
    """
    msg = """
-------------------------------
Studio Library is a free python script for managing poses and animation in Maya.
Comments, suggestions and bug reports are welcome.

Version: {version}
Package: {package}

www.studiolibrary.com
kurt.rathjen@gmail.com
--------------------------------
"""
    msg = msg.format(version=package().version(), package=PATH)
    return msg


from studiolibrary import config

from studiolibrary import migrate
migrate.migrate()

if __name__ == "__main__":
    loadFromCommand()
else:
    print(about())

