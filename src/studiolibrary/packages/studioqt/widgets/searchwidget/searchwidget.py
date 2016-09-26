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

import logging
from functools import partial

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


import studioqt


logger = logging.getLogger(__name__)


class SearchWidget(QtWidgets.QLineEdit):

    DEFAULT_PLACEHOLDER_TEXT = "Search"

    searchChanged = QtCore.Signal()

    def __init__(self, *args):
        QtWidgets.QLineEdit.__init__(self, *args)

        self._iconPadding = 4
        self._iconButton = QtWidgets.QPushButton(self)
        self._iconButton.clicked.connect(self._iconClicked)
        self._searchFilter = studioqt.SearchFilter("")

        icon = studioqt.icon("search")
        self.setIcon(icon)

        self.setPlaceholderText(self.DEFAULT_PLACEHOLDER_TEXT)

        self.textChanged.connect(self._textChanged)
        self.searchChanged = self.searchFilter().searchChanged

        self.update()

    def update(self):
        self.updateIconColor()

    def updateIconColor(self):
        color = self.palette().color(self.foregroundRole())
        color = studioqt.Color.fromColor(color)
        self.setIconColor(color)

    def _textChanged(self, text):
        """
        Triggered when the text changes.

        :type text: str
        :rtype: None
        """
        self.searchFilter().setPattern(text)

    def contextMenuEvent(self, event):
        """
        Triggered when the user right clicks on the search widget.

        :type event: QtCore.QEvent
        :rtype: None
        """
        self.showContextMenu()

    def setSpaceOperator(self, operator):
        """
        Set the space operator for the search filter.

        :type operator: studioqt.SearchFilter.Operator
        :rtype: None
        """
        self._searchFilter.setSpaceOperator(operator)

    def createSpaceOperatorMenu(self, parent=None):
        """
        Return the menu for changing the space operator.

        :type parent: QGui.QMenu
        :rtype: QGui.QMenu
        """
        searchFilter = self.searchFilter()

        menu = QtWidgets.QMenu(parent)
        menu.setTitle("Space Operator")

        # Create the space operator for the OR operator
        action = QtWidgets.QAction(menu)
        action.setText("OR")
        action.setCheckable(True)

        callback = partial(self.setSpaceOperator, searchFilter.Operator.OR)
        action.triggered.connect(callback)

        if searchFilter.spaceOperator() == searchFilter.Operator.OR:
            action.setChecked(True)

        menu.addAction(action)

        # Create the space operator for the AND operator
        action = QtWidgets.QAction(menu)
        action.setText("AND")
        action.setCheckable(True)

        callback = partial(self.setSpaceOperator, searchFilter.Operator.AND)
        action.triggered.connect(callback)

        if searchFilter.spaceOperator() == searchFilter.Operator.AND:
            action.setChecked(True)

        menu.addAction(action)

        return menu

    def showContextMenu(self):
        """
        Create and show the context menu for the search widget.

        :rtype QtWidgets.QAction
        """
        menu = QtWidgets.QMenu(self)

        subMenu = self.createStandardContextMenu()
        subMenu.setTitle("Edit")
        menu.addMenu(subMenu)

        subMenu = self.createSpaceOperatorMenu(menu)
        menu.addMenu(subMenu)

        point = QtGui.QCursor.pos()
        action = menu.exec_(point)

        return action

    def searchFilter(self):
        """
        Return the search filter for the widget.

        :rtype: studioqt.SearchFilter
        """
        return self._searchFilter

    def _iconClicked(self):
        """
        Triggered when the user clicks on the icon.

        :rtype: None
        """
        if not self.hasFocus():
            self.setFocus()

    def setIcon(self, icon):
        """
        Set the icon for the search widget.

        :type icon: QtWidgets.QIcon
        :rtype: None
        """
        self._iconButton.setIcon(icon)

    def setIconColor(self, color):
        """
        Set the icon color for the search widget icon.

        :type color: QtGui.QColor
        :rtype: None
        """
        icon = self._iconButton.icon()
        icon = studioqt.Icon(icon)
        icon.setColor(color)
        self._iconButton.setIcon(icon)

    def settings(self):
        """
        Return a dictionary of the current widget state.

        :rtype: dict
        """
        settings = {"text": self.text()}
        settings["searchFilter"] = self.searchFilter().settings()
        return settings

    def setSettings(self, settings):
        """
        Restore the widget state from a settings dictionary.

        :type settings: dict
        :rtype: None
        """
        searchFilterSettings = settings.get("searchFilter", None)
        if searchFilterSettings is not None:
            self.searchFilter().setSettings(searchFilterSettings)

        text = settings.get("text", "")
        self.setText(text)

    def resizeEvent(self, event):
        """
        Reimplemented so the icon maintains the same height as the widget.

        :type event:  QtWidgets.QResizeEvent
        :rtype: None
        """
        QtWidgets.QLineEdit.resizeEvent(self, event)

        self.setTextMargins(self.height(), 0, 0, 0)
        size = QtCore.QSize(self.height(), self.height())

        self._iconButton.setIconSize(size)
        self._iconButton.setFixedSize(size)


def showExample():
    """
    Run a simple example of the search widget.

    :rtype: SearchWidget
    """

    with studioqt.app():
        searchWidget = studioqt.SearchWidget()

        items = [
            "This is a dog",
            "I love cats",
            "how man eggs can you eat?"
        ]

        def searchChanged():
            print "--- Search changed! ---"

            searchFilter = searchWidget.searchFilter()
            for item in items:
                print "Match:", searchFilter.match(item), searchFilter.matches(), item


        searchWidget.searchChanged.connect(searchChanged)
        searchWidget.show()

        return searchWidget


if __name__ == "__main__":
    showExample()
