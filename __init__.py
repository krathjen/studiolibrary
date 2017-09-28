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


__version__ = "2.0.0b2"
__encoding__ = sys.getfilesystemencoding()

_resource = None

PATH = unicode(os.path.abspath(__file__), __encoding__)
DIRNAME = os.path.dirname(PATH)
PACKAGES_PATH = os.path.join(DIRNAME, "packages")
RESOURCE_PATH = os.path.join(DIRNAME, "resource")
HELP_URL = "http://www.studiolibrary.com"


LIBRARY_WIDGET_CLASS = None


def setup(path):
    """
    Setup the packages that have been decoupled from the Studio Library.

    :param path: The folder location that contains all the packages.
    :type path: str

    :rtype: None
    """
    if os.path.exists(path) and path not in sys.path:
        sys.path.append(path)


setup(PACKAGES_PATH)


import studioqt

from studiolibrary.cmds import *
from studiolibrary.database import Database
from studiolibrary.libraryitem import LibraryItem
from studiolibrary.librarywidget import LibraryWidget

from studiolibrary.main import main


def resource():
    """
    Return a resource object for getting content from the resource folder.

    :rtype: studioqt.Resource
    """
    global _resource

    if not _resource:
        _resource = studioqt.Resource(RESOURCE_PATH)

    return _resource


def version():
    """
    Return the current version of the Studio Library

    :rtype: str
    """
    return __version__


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


from studiolibrary import config


if __name__ == "__main__":
    loadFromCommand()
