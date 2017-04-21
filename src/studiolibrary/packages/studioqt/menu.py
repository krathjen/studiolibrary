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


class Menu(QtWidgets.QMenu):

    def __init__(self, *args):
        QtWidgets.QMenu.__init__(self, *args)

    def findAction(self, text):
        """
        Return the action that contains the given text.
        
        :type text: str

        :rtype: QtWidgets.QAction
        """
        for child in self.children():

            action = None

            if isinstance(child, QtWidgets.QMenu):
                action = child.menuAction()
            elif isinstance(child, QtWidgets.QAction):
                action = child

            if action and action.text().lower() == text.lower():
                return action

    def insertMenuBefore(self, text, menu):
        """
        Add the given menu before the action with the given text.
        
        :type text: str
        :type menu: QtWidgets.QMenu
        
        :rtype: QtWidgets.QAction
        """
        action = self.findAction(text)
        self.insertMenu(action, menu)

    def insertSeparatorBefore(self, text):
        """
        Add separator before the action with the given text.
        
        :type text: str

        :rtype: QtWidgets.QAction
        """
        action = self.findAction(text)
        return self.insertSeparator(action)