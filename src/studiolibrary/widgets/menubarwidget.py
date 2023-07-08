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

import logging

from studiovendor import six
from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt
import studiolibrary


logger = logging.getLogger(__name__)


class MenuBarWidget(QtWidgets.QToolBar):

    DEFAULT_EXPANDED_HEIGHT = 32
    DEFAULT_COLLAPSED_HEIGHT = 10
    ICON_SIZE = 28

    def __init__(self, parent=None):
        QtWidgets.QToolBar.__init__(self, parent)

        self._dpi = 1
        self._isExpanded = True
        self._expandHeight = self.DEFAULT_EXPANDED_HEIGHT
        self._collapseHeight = self.DEFAULT_COLLAPSED_HEIGHT

    def dpi(self):
        """
        Return the zoom multiplier.
        
        :rtype: float 
        """
        return self._dpi

    def setDpi(self, dpi):
        """
        Set the zoom multiplier.

        Used for high resolution devices.
        
        :type dpi: float 
        :rtype: None 
        """
        self._dpi = dpi
        if self.isExpanded():
            self.expand()
        else:
            self.collapse()

    def mousePressEvent(self, *args):
        if not self.isExpanded():
            self.expand()

    def isExpanded(self):
        """
        Return True if the menuBarWidget is expanded.
        
        :rtype: bool 
        """
        return self._isExpanded

    def expandHeight(self):
        """
        Return the height of widget when expanded.
        
        :rtype: int 
        """
        return int(self._expandHeight * self.dpi())

    def collapseHeight(self):
        """
        Return the height of widget when collapsed.

        :rtype: int 
        """
        return int(self._collapseHeight * self.dpi())

    def setFixedHeight(self, value):
        """
        Overriding this method to also set the height for all child widgets.

        :type value: bool
        :rtype: None 
        """
        self.setChildrenHeight(value)
        QtWidgets.QToolBar.setFixedHeight(self, value)

    def setChildrenHidden(self, value):
        """
        Set all child widgets to hidden.

        :type value: bool
        :rtype: None 
        """
        for w in self.widgets():
            w.setHidden(value)

    def setChildrenHeight(self, height):
        """
        Set the height of all the child widgets to the given height.
        
        :type height: int
        :rtype: None 
        """
        for w in self.widgets():
            w.setFixedHeight(height)

    def expand(self):
        """
        Expand the MenuBar to the expandHeight. 
        
        :rtype: None
        """
        self._isExpanded = True
        height = self.expandHeight()
        self.setFixedHeight(height)
        self.setChildrenHidden(False)

    def collapse(self):
        """
        Collapse the MenuBar to the collapseHeight. 

        :rtype: None
        """
        self._isExpanded = False
        height = self.collapseHeight()
        self.setFixedHeight(height)
        self.setChildrenHeight(0)
        self.setChildrenHidden(True)

    def updateIconColor(self):
        color = self.palette().color(self.foregroundRole())
        color = studioqt.Color.fromColor(color)

        for action in self.actions():

            icon = studioqt.Icon(action.icon())

            try:
                icon.setBadgeColor(action._badgeColor)
                icon.setBadgeEnabled(action._badgeEnabled)
            except AttributeError as error:
                pass

            icon.setColor(color)
            action.setIcon(icon)

    def widgets(self):
        """
        Return all the widget that are a child of the MenuBarWidget.
        
        :rtype: list[QtWidgets.QWidget] 
        """
        widgets = []

        for i in range(0, self.layout().count()):
            w = self.layout().itemAt(i).widget()
            if isinstance(w, QtWidgets.QWidget):
                widgets.append(w)

        return widgets

    def actions(self):
        """
        Return all the actions that are a child of the MenuBarWidget.

        :rtype: list[QtWidgets.QAction] 
        """
        actions = []

        for child in self.children():
            if isinstance(child, QtWidgets.QAction):
                actions.append(child)

        return actions

    def findAction(self, text):
        """
        Find the action with the given text.

        :rtype: QtWidgets.QAction or None
        """
        for child in self.children():
            if isinstance(child, QtWidgets.QAction):
                if child.text() == text:
                    return child

    def findToolButton(self, text):
        """
        Find the QToolButton with the given text.

        :rtype: QtWidgets.QToolButton or None
        """
        for child in self.children():
            if isinstance(child, QtWidgets.QAction):
                if child.text() == text:
                    return self.widgetForAction(child)

    def insertAction(self, before, action):
        """
        Overriding this method to support the before argument as string.
        
        :type before: QtWidgets.QAction or str
        :type action: QtWidgets.QAction 
        :rtype: QtWidgets.QAction 
        """
        action.setParent(self)

        if isinstance(before, six.string_types):
            before = self.findAction(before)

        action = QtWidgets.QToolBar.insertAction(self, before, action)

        return action


def showExample():
    """
    Run a simple example of the widget.

    :rtype: QtWidgets.QWidget
    """

    with studioqt.app():

        menuBarWidget = MenuBarWidget(None)

        def setIconColor():
            menuBarWidget.setIconColor(QtGui.QColor(255, 255, 0))

        def collapse():
            menuBarWidget.collapse()

        menuBarWidget.show()

        action = menuBarWidget.addAction("Collapse")
        action.triggered.connect(collapse)

        w = QtWidgets.QLineEdit()
        menuBarWidget.addWidget(w)

        icon = studiolibrary.resource.icon("add")
        menuBarWidget.addAction(icon, "Plus")
        menuBarWidget.setStyleSheet("""
background-color: rgb(0,200,100);
spacing:5px;
        """)

        menuBarWidget.setChildrenHeight(50)

        action = QtWidgets.QAction("Yellow", None)
        action.triggered.connect(setIconColor)
        menuBarWidget.insertAction("Plus", action)
        menuBarWidget.setGeometry(400, 400, 400, 100)

        menuBarWidget.expand()


if __name__ == "__main__":
    showExample()
