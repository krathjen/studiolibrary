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
