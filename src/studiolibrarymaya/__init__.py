# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
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

import os
import sys
import logging

import studiolibrary

import mutils
import studioqt

from studiolibrarymaya.main import main


__encoding__ = sys.getfilesystemencoding()

PATH = unicode(os.path.abspath(__file__), __encoding__)
DIRNAME = os.path.dirname(PATH).replace('\\', '/')
RESOURCE_DIRNAME = DIRNAME + "/resource"
SETTINGS_PATH = studiolibrary.localPath("LibraryItem.json")


_resource = None
_settings = None
_mayaCloseScriptJob = None


def readSettings():
    """
    Return the local settings from the location of the SETTING_PATH.

    :rtype: dict
    """
    return studiolibrary.readJson(SETTINGS_PATH)


def saveSettings(data):
    """
    Save the given dict to the local location of the SETTING_PATH.

    :type data: dict
    :rtype: None
    """
    global _settings
    _settings = None

    studiolibrary.updateJson(SETTINGS_PATH, data)


def resetSettings():
    """Remove and reset the item settings."""
    global _settings
    _settings = None
    studiolibrary.removePath(SETTINGS_PATH)


def settings():
    """
    Return the local settings for importing and exporting an animation.

    :rtype: studiolibrary.Settings
    """
    global _settings

    if not _settings:
        _settings = readSettings()

    # Shared options
    _settings.setdefault("namespaces", [])
    _settings.setdefault("namespaceOption", "file")

    return _settings


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
    The following items are registered on import at the bottom of each file.
    
    :rtype: None 
    """
    from studiolibrarymaya import animitem
    from studiolibrarymaya import poseitem
    from studiolibrarymaya import mirroritem
    from studiolibrarymaya import setsitem


def enableMayaClosedEvent():
    """
    Create a Maya script job to trigger on the event "quitApplication".

    Enable the Maya closed event to save the library settings on close

    :rtype: None
    """
    global _mayaCloseScriptJob

    if not _mayaCloseScriptJob:
        event = ['quitApplication', mayaClosedEvent]
        try:
            _mayaCloseScriptJob = mutils.ScriptJob(event=event)
        except NameError as error:
            logging.exception(error)


def mayaClosedEvent():
    """
    Create a Maya script job to trigger on the event "quitApplication".

    :rtype: None
    """
    for libraryWindow in studiolibrary.LibraryWindow.instances():
        libraryWindow.saveSettings()


def setDebugMode(libraryWindow, value):
    """
    Triggered when the user chooses debug mode.

    :type libraryWindow: studiolibrary.LibraryWindow
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


studiolibrary.LibraryWindow.globalSignal.debugModeChanged.connect(setDebugMode)
