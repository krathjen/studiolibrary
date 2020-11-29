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

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtWidgets

import mutils


__all__ = ["FrameRangeMenu", "showFrameRangeMenu"]


class FrameRangeAction(QtWidgets.QAction):
    def __init__(self, *args):
        super(FrameRangeAction, self).__init__(*args)

        self._frameRange = (0, 100)

    def frameRange(self):
        return self._frameRange

    def setFrameRange(self, frameRange):
        self._frameRange = frameRange


class FrameRangeMenu(QtWidgets.QMenu):

    def __init__(self, parent=None):
        super(FrameRangeMenu, self).__init__(parent)

        action = FrameRangeAction("From Timeline", self)
        action.setFrameRange(mutils.playbackFrameRange())
        self.addAction(action)

        action = FrameRangeAction("From Selected Timeline", self)
        action.setFrameRange(mutils.selectedFrameRange())
        self.addAction(action)

        action = FrameRangeAction("From Selected Objects", self)
        action.setFrameRange(mutils.selectedObjectsFrameRange())
        self.addAction(action)


def showFrameRangeMenu():
    """
    Show the frame range menu at the current cursor position.

    :rtype: QtWidgets.QAction
    """
    menu = FrameRangeMenu()
    position = QtGui.QCursor().pos()
    action = menu.exec_(position)
    return action


if __name__ == "__main__":
    action = showFrameRangeMenu()
    print(action.frameRange())
