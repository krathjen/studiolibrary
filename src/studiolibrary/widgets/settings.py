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

import studiolibrary

_settings = None


def path():
    """
    Get the settings path.

    :rtype: str
    """
    return studiolibrary.localPath("widgets2.json")


def get(key, default=None):
    """
    Convenience function for getting the a value from disc.

    :type key: str
    :type default: object
    :rtype: object
    """
    return read().get(key, default)


def set(key, value):
    """
    Convenience function for setting key values to disc.

    :type key: str
    :type value: object
    """
    save({key: value})


def read():
    """
    Return the local settings from the location of the SETTING_PATH.

    :rtype: dict
    """
    global _settings

    if not _settings:
        _settings = studiolibrary.readJson(path())

    return _settings


def save(data):
    """
    Save the given dict to the local location of the SETTING_PATH.

    :type data: dict
    :rtype: None
    """
    global _settings
    _settings = None
    studiolibrary.updateJson(path(), data)


def reset():
    """Remove and reset the item settings."""
    global _settings
    _settings = None
    studiolibrary.removePath(path())
