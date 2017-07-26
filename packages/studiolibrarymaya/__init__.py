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

import mutils
import studioqt

from mayalibrarywidget import MayaLibraryWidget


__encoding__ = sys.getfilesystemencoding()

PATH = unicode(os.path.abspath(__file__), __encoding__)
DIRNAME = os.path.dirname(PATH).replace('\\', '/')
RESOURCE_DIRNAME = DIRNAME + "/resource"

DEFAULT_FILE_TYPE = "mayaBinary"

_resource = None


def settings():
    """
    Return the local settings for importing and exporting an animation.

    :rtype: studiolibrary.Settings
    """
    settings = studiolibrary.Settings.instance("StudioLibrary", "ItemSettings")

    # Shared options
    settings.setdefault("namespaces", [])
    settings.setdefault("namespaceOption", "file")

    settings.setdefault("iconToggleBoxChecked", True)
    settings.setdefault("infoToggleBoxChecked", True)
    settings.setdefault("optionsToggleBoxChecked", True)
    settings.setdefault("namespaceToggleBoxChecked", True)

    # Anim options
    settings.setdefault('byFrame', 1)
    settings.setdefault('fileType', DEFAULT_FILE_TYPE)
    settings.setdefault('currentTime', False)
    settings.setdefault('connectOption', False)
    settings.setdefault('showHelpImage', False)
    settings.setdefault('pasteOption', "replace")

    # Pose options
    settings.setdefault("keyEnabled", False)
    settings.setdefault("mirrorEnabled", False)

    # Mirror options
    settings.setdefault("mirrorOption", mutils.MirrorOption.Swap)
    settings.setdefault("mirrorAnimation", True)

    return settings


def resource():
    """
    :rtype: studioqt.Resource
    """
    global _resource

    if not _resource:
        _resource = studioqt.Resource(RESOURCE_DIRNAME)

    return _resource


def registerItems():
    """
    Called by the studiolibrary config file to register the items.

    :rtype: None
    """
    # The following items are registered on import.
    from studiolibrarymaya import animitem
    from studiolibrarymaya import poseitem
    from studiolibrarymaya import mirroritem
    from studiolibrarymaya import setsitem


def setDebugMode(libraryWidget, value):
    """
    Triggered when the user chooses debug mode.

    :type libraryWidget: studiolibrary.LibraryWidget
    :type value: int
    :rtype: None
    """
    if value:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger_ = logging.getLogger("mutils")
    logger_.setLevel(level)

    logger_ = logging.getLogger("studiolibrarymaya")
    logger_.setLevel(level)


studiolibrary.LibraryWidget.globalSignal.debugModeChanged.connect(setDebugMode)
