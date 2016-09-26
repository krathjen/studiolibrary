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

from studioqt import QtWidgets


__all__ = [
    "ContextMenu",
]


class ContextMenu(QtWidgets.QMenu):

    def __init__(self, *args):
        QtWidgets.QMenu.__init__(self, *args)
        self._menus = []
        self._actions = []

    def actions(self):
        return self._actions

    def insertAction(self, actionBefore, action):
        if str(action.text()) not in self._actions:
            self._actions.append(str(action.text()))
            QtWidgets.QMenu.insertAction(self, actionBefore, action)

    def addAction(self, action):
        if str(action.text()) not in self._actions:
            self._actions.append(str(action.text()))
            QtWidgets.QMenu.addAction(self, action)

    def addMenu(self, menu):
        if str(menu.title()) not in self._menus:
            self._menus.append(str(menu.title()))
            QtWidgets.QMenu.addMenu(self, menu)
