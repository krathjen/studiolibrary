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

from . import metafile


__all__ = ["Settings"]


class Settings(metafile.MetaFile):

    _instances = {}

    DEFAULT_PATH = os.getenv('APPDATA') or os.getenv('HOME')

    @classmethod
    def instance(cls, *args):
        """
        Return the settings instance for the given scope.

        :type args: list[str]
        :rtype: Settings
        """
        key = "/".join(args)

        if key not in cls._instances:
            cls._instances[key] = cls(*args)

        return cls._instances[key]

    def __init__(self, *args):
        """
        :type args: list[str]
        """
        self._path = None
        self._args = args
        metafile.MetaFile.__init__(self, "")

    def path(self):
        """
        Return the path.

        :rtype: str
        """
        if not self._path:
            scope = os.path.join(*self._args)
            self._path = os.path.join(Settings.DEFAULT_PATH, scope + ".json")
        return self._path
