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

from studioqt import QtGui
from studioqt import QtWidgets

import studioqt


class Resource(object):

    DEFAULT_DIRNAME = ""

    def __init__(self, dirname=None):
        """
        :type dirname: str
        """
        dirname = dirname.replace("\\", "/")
        self._dirname = dirname or self.DEFAULT_DIRNAME

    def dirname(self):
        """
        :rtype: str
        """
        return self._dirname

    def get(self, *token):
        """
        :rtype: str
        """
        return os.path.join(self.dirname(), *token)

    def icon(self, name, extension="png", color=None):
        """
        :type name: str
        :type extension: str
        :rtype: QtGui.QIcon
        """
        pixmap = self.pixmap(name, extension=extension, color=color)
        return QtGui.QIcon(pixmap)

    def pixmap(self, name, scope="icons", extension="png", color=None):
        """
        :type name: str
        :type extension: str
        :rtype: QtWidgets.QPixmap
        """
        path = self.get(scope, name + "." + extension)
        pixmap = studioqt.Pixmap(path)

        if color:
            pixmap.setColor(color)

        return pixmap
