# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
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

from studioqt import QtCore
from studioqt import QtWidgets

import studioqt
import studiolibrary

logger = logging.getLogger(__name__)


class SearchWidget(QtWidgets.QLineEdit):

    DEFAULT_PLACEHOLDER_TEXT = "Search"

    searchChanged = QtCore.Signal()

    def __init__(self, *args):
        QtWidgets.QLineEdit.__init__(self, *args)

        self._iconPadding = 6
        self._iconButton = QtWidgets.QPushButton(self)
        self._iconButton.clicked.connect(self._iconClicked)

        icon = studiolibrary.resource().icon("search")
        self.setIcon(icon)

        self._clearButton = QtWidgets.QPushButton(self)
        self._clearButton.setCursor(QtCore.Qt.ArrowCursor)
        icon = studiolibrary.resource().icon("cross")
        self._clearButton.setIcon(icon)
        self._clearButton.setToolTip("Clear all search text")
        self._clearButton.clicked.connect(self._clearClicked)

        self.setPlaceholderText(self.DEFAULT_PLACEHOLDER_TEXT)

        self.textChanged.connect(self._textChanged)

        self.update()

    def update(self):
        self.updateIconColor()
        self.updateClearButton()

    def updateIconColor(self):
        """
        Update the color of the icons from the current palette.

        :rtype: None
        """
        color = self.palette().color(self.foregroundRole())
        color = studioqt.Color.fromColor(color)
        self.setIconColor(color)

    def _clearClicked(self):
        """
        Triggered when the user clicks the cross icon.

        :rtype: None
        """
        self.setText("")
        self.setFocus()

    def _iconClicked(self):
        """
        Triggered when the user clicks on the icon.

        :rtype: None
        """
        if not self.hasFocus():
            self.setFocus()

    def _textChanged(self, text):
        """
        Triggered when the text changes.

        :type text: str
        :rtype: None
        """
        self.updateClearButton()
        self.searchChanged.emit()

    def updateClearButton(self):
        """
        Update the clear button depending on the current text.

        :rtype: None
        """
        text = self.text()
        if text:
            self._clearButton.show()
        else:
            self._clearButton.hide()

    def contextMenuEvent(self, event):
        """
        Triggered when the user right clicks on the search widget.

        :type event: QtCore.QEvent
        :rtype: None
        """
        pass

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

        icon = self._clearButton.icon()
        icon = studioqt.Icon(icon)
        icon.setColor(color)
        self._clearButton.setIcon(icon)

    def settings(self):
        """
        Return a dictionary of the current widget state.

        :rtype: dict
        """
        settings = {"text": self.text()}
        return settings

    def setSettings(self, settings):
        """
        Restore the widget state from a settings dictionary.

        :type settings: dict
        :rtype: None
        """
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

        self._clearButton.setIconSize(size)

        x = self.width() - self.height()
        self._clearButton.setGeometry(x, 0, self.height(), self.height())


def showExample():
    """
    Run a simple example of the search widget.

    :rtype: SearchWidget
    """

    with studioqt.app():
        searchWidget = studioqt.SearchWidget()

        def searchChanged():
            print("--- Search changed! ---")
            print(searchWidget.text())

        searchWidget.searchChanged.connect(searchChanged)
        searchWidget.show()

        return searchWidget



if __name__ == "__main__":
    showExample()
