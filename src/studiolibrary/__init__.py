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
import sys


__version__ = "1.30.0"
__encoding__ = sys.getfilesystemencoding()

_resource = None
_analytics = None
_scriptJob = None

PATH = unicode(os.path.abspath(__file__), __encoding__)
DIRNAME = os.path.dirname(PATH).replace('\\', '/')
PACKAGES_PATH = DIRNAME + "/packages"
RESOURCE_PATH = DIRNAME + "/gui/resource"
HELP_URL = "http://www.studiolibrary.com"

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
        print 'Adding "{path}" to the sys.path'.format(path=path)
        sys.path.append(path)


setup(PACKAGES_PATH)


import studioqt

from studiolibrary.main import main

from studiolibrary.core.utils import *
from studiolibrary.core.metafile import MetaFile
from studiolibrary.core.settings import Settings
from studiolibrary.core.database import Database
from studiolibrary.core.analytics import Analytics

from studiolibrary.gui.mayadockwidgetmixin import MayaDockWidgetMixin
from studiolibrary.gui.librarywidget import LibraryWidget
from studiolibrary.gui.previewwidget import PreviewWidget
from studiolibrary.gui.librariesmenu import LibrariesMenu
from studiolibrary.gui.settingsdialog import SettingsDialog

from studiolibrary.api.cmds import *
from studiolibrary.api.library import Library
from studiolibrary.api.libraryitem import LibraryItem


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


def version():
    """
    Return the current version of the Studio Library

    :rtype: str
    """
    return __version__


def analytics():
    """
    :rtype: studiolibrary.analytics.Analytics
    """
    global _analytics

    if not _analytics:

        _analytics = Analytics(
            tid=Analytics.DEFAULT_ID,
            name="StudioLibrary",
            version=__version__
        )

    _analytics.setEnabled(Analytics.ENABLED)
    return _analytics


def windows():
    """
    Return a list of all the loaded library windows.

    :rtype: list[MainWindow]
    """
    return Library.libraryWidgets()


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
    parser.add_option("-r", "--root", dest="root",
                      help="", metavar="ROOT")
    parser.add_option("-n", "--name", dest="name",
                      help="", metavar="NAME")
    parser.add_option("-v", "--version", dest="version",
                      help="", metavar="VERSION")
    (options, args) = parser.parse_args()

    name = options.name
    main(name=name)


def about():
    """
    Return a small description about the Studio Library.

    :rtype str
    """
    msg = u"""
-------------------------------
Studio Library is a free python script for managing poses and animation in Maya.
Comments, suggestions and bug reports are welcome.

Version: {version}
Package: {package}

www.studiolibrary.com
kurt.rathjen@gmail.com
--------------------------------
"""
    msg = msg.format(version=__version__, package=PATH)
    return msg


from studiolibrary import config

from studiolibrary import migrate
migrate.migrate()

if __name__ == "__main__":
    loadFromCommand()

