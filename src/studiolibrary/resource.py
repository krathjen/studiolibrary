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

import os

from studioqt import Icon
from studioqt import Pixmap

from . import utils


PATH = os.path.abspath(__file__)
DIRNAME = os.path.dirname(PATH)
RESOURCE_DIRNAME = os.path.join(DIRNAME, "resource")


def get(*args):
    """
    This is a convenience function for returning the resource path.

    :rtype: str 
    """
    path = os.path.join(RESOURCE_DIRNAME, *args)
    return utils.normPath(path)


def icon(*args, **kwargs):
    """
    Return an Icon object from the given resource name.

    :rtype: str
    """
    path = get("icons", *args)
    return Icon(pixmap(path, **kwargs))


def pixmap(name, scope="icons", extension="png", color=None):
    """
    Return a Pixmap object from the given resource name.

    :type name: str
    :type scope: str
    :type extension: str
    :type color: str
    :rtype: QtWidgets.QPixmap
    """
    if name.endswith(".svg"):
        extension = ""

    path = ""

    if os.path.exists(name):
        path = name

    elif extension:
        path = get(scope, name + "." + extension)
        if not os.path.exists(path):
            path = get(scope, name + ".svg")

    p = Pixmap(path)

    if color:
        p.setColor(color)

    return p
