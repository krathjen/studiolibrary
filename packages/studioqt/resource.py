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
from studioqt import Pixmap


PATH = os.path.abspath(__file__)
DIRNAME = os.path.dirname(PATH)
RESOURCE_DIRNAME = os.path.join(DIRNAME, "resource")


def get(*args):
    """
    This is a convenience function for returning the resource path.

    :rtype: str 
    """
    return Resource().get(*args)


def icon(*args, **kwargs):
    """
    Return an Icon object from the given resource name.
    :rtype: str 
    """
    return Resource().icon(*args, **kwargs)


def pixmap(*args, **kwargs):
    """
    Return a Pixmap object from the given resource name.
    :rtype: str 
    """
    return Resource().pixmap(*args, **kwargs)


class Resource(object):
    DEFAULT_DIRNAME = RESOURCE_DIRNAME

    def __init__(self, *args):
        """"""
        dirname = ""

        if args:
            dirname = os.path.join(*args)

        if os.path.isfile(dirname):
            dirname = os.path.dirname(dirname)

        self._dirname = dirname or self.DEFAULT_DIRNAME

    def dirname(self):
        """
        :rtype: str
        """
        return self._dirname

    def get(self, *args):
        """
        Return the resource path for the given args.

        :rtype: str
        """
        return os.path.join(self.dirname(), *args)

    def icon(self, name, extension="png", color=None):
        """
        Return an Icon object from the given resource name.

        :type name: str
        :type extension: str
        :rtype: QtGui.QIcon
        """
        p = self.pixmap(name, extension=extension, color=color)

        return QtGui.QIcon(p)

    def pixmap(self, name, scope="icons", extension="png", color=None):
        """
        Return a Pixmap object from the given resource name.

        :type name: str
        :type scope: str
        :type extension: str
        :rtype: QtWidgets.QPixmap
        """
        path = self.get(scope, name + "." + extension)
        p = Pixmap(path)

        if color:
            p.setColor(color)

        return p
