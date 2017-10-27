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

    def insertAction(self, before, *args):
        """
        Add support for finding the before action by the given string.

        :type before: str  or QtWidget.QAction
        :type args: list

        :rtype: QtWidgets.QAction
        """
        if isinstance(before, basestring):
            before = self.findAction(before)

        return QtWidgets.QMenu.insertAction(self, before, *args)

    def insertMenu(self, before, menu):
        """
        Add support for finding the before action by the given string.
        
        :type before: str  or QtWidget.QAction
        :type menu: QtWidgets.QMenu
        
        :rtype: QtWidgets.QAction
        """
        if isinstance(before, basestring):
            before = self.findAction(before)

        QtWidgets.QMenu.insertMenu(self, before, menu)

    def insertSeparator(self, before):
        """
        Add support for finding the before action by the given string.
        
        :type before: str or QtWidget.QAction

        :rtype: QtWidgets.QAction
        """
        if isinstance(before, basestring):
            before = self.findAction(before)

        return QtWidgets.QMenu.insertSeparator(self, before)
