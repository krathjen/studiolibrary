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
import getpass
import tempfile


__all__ = ["TempDir"]


class TempDir(object):

    def __init__(self, *args, **kwargs):
        """
        :type subDirs: list[str]
        """
        user = getpass.getuser().lower()
        tempdir = tempfile.gettempdir().replace("\\", "/")
        self._path = os.path.join(tempdir, "mutils", user, *args)

        if kwargs.get("clean", False):
            self.clean()

        if kwargs.get("makedirs", True):
            self.makedirs()

    def path(self):
        """
        :rtype: str
        """
        return self._path

    def clean(self):
        """
        :rtype: str
        """
        if os.path.exists(self.path()):
            shutil.rmtree(self.path())

    def makedirs(self):
        """
        :rtype: str
        """
        if not os.path.exists(self.path()):
            os.makedirs(self.path())

