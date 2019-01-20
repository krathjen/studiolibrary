# Copyright 2016 by Kurt Rathjen. All Rights Reserved.
#
# Permission to use, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Kurt Rathjen
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# KURT RATHJEN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# KURT RATHJEN BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import mutils

from studioqt import QtGui
from studioqt import QtWidgets


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
    print action.frameRange()
