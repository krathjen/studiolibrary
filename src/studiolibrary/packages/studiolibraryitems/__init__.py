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
import logging

import studiolibrary
import studioqt

__encoding__ = sys.getfilesystemencoding()

PATH = unicode(os.path.abspath(__file__), __encoding__)
DIRNAME = os.path.dirname(PATH).replace('\\', '/')
RESOURCE_DIRNAME = DIRNAME + "/resource"


_resource = None


def resource():
    """
    :rtype: studioqt.Resource
    """
    global _resource

    if not _resource:
        _resource = studioqt.Resource(dirname=RESOURCE_DIRNAME)

    return _resource


def setDebugMode(libraryWidget, value):
    """
    Triggered when the user chooses debug mode.

    :type level: int
    :rtype: None
    """
    if value:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger_ = logging.getLogger("mutils")
    logger_.setLevel(level)

    logger_ = logging.getLogger("studiolibraryitems")
    logger_.setLevel(level)


studiolibrary.LibraryWidget.globalSignal.debugModeChanged.connect(setDebugMode)
