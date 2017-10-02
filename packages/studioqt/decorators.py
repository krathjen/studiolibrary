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

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


def showWaitCursor(fn):

    def wrapped(*args, **kwargs):
        cursor = QtGui.QCursor(QtCore.Qt.WaitCursor)
        QtWidgets.QApplication.setOverrideCursor(cursor)
        try:
            return fn(*args, **kwargs)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__

    return wrapped


def showArrowCursor(fn):

    def wrapped(*args, **kwargs):
        cursor = QtGui.QCursor(QtCore.Qt.ArrowCursor)
        QtWidgets.QApplication.setOverrideCursor(cursor)
        try:
            return fn(*args, **kwargs)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    wrapped.__name__ = fn.__name__
    wrapped.__doc__ = fn.__doc__

    return wrapped
