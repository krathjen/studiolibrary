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
from functools import partial

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt
import studiolibrary

logger = logging.getLogger(__name__)


class SearchWidget(QtWidgets.QLineEdit):

    SPACE_OPERATOR = "and"
    PLACEHOLDER_TEXT = "Search"

    searchChanged = QtCore.Signal()

    def __init__(self, *args):
        QtWidgets.QLineEdit.__init__(self, *args)

        self._dataset = None
        self._spaceOperator = "and"
        self._iconButton = QtWidgets.QPushButton(self)
        self._iconButton.setObjectName("searchIconWidget")
        self._iconButton.clicked.connect(self._iconClicked)

        icon = studiolibrary.resource.icon("magnifying-glass.svg")
        self.setIcon(icon)

        self._clearButton = QtWidgets.QPushButton(self)
        self._clearButton.setCursor(QtCore.Qt.ArrowCursor)
        icon = studiolibrary.resource.icon("xmark")
        self._clearButton.setIcon(icon)
        self._clearButton.setToolTip("Clear all search text")
        self._clearButton.clicked.connect(self._clearClicked)
        self._clearButton.setStyleSheet("QFrame {background-color: transparent;}")

        self.setPlaceholderText(self.PLACEHOLDER_TEXT)
        self.textChanged.connect(self._textChanged)

        self.update()

    def update(self):
        self.updateIconColor()
        self.updateClearButton()

    def setDataset(self, dataset):
        """
        Set the data set for the search widget:
        
        :type dataset: studiolibrary.Dataset
        """
        self._dataset = dataset

    def dataset(self):
        """
        Get the data set for the search widget.
        
        :rtype: studiolibrary.Dataset 
        """
        return self._dataset

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
        self.search()

    def search(self):
        """Run the search query on the data set."""
        if self.dataset():
            self.dataset().addQuery(self.query())
            self.dataset().search()
        else:
            logger.info("No dataset found the the search widget.")

        self.updateClearButton()
        self.searchChanged.emit()

    def query(self):
        """
        Get the query used for the data set.
        
        :rtype: dict 
        """
        text = str(self.text())

        filters = []
        for filter_ in text.split(' '):
            if filter_.split():
                filters.append(('*', 'contains', filter_))

        uniqueName = 'searchwidget' + str(id(self))

        return {
            'name': uniqueName,
            'operator': self.spaceOperator(),
            'filters': filters
        }

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

        self.setProperty('hasText', bool(self.text()))
        self.setStyleSheet(self.styleSheet())

    def contextMenuEvent(self, event):
        """
        Triggered when the user right clicks on the search widget.

        :type event: QtCore.QEvent
        :rtype: None
        """
        self.showContextMenu()

    def spaceOperator(self):
        """
        Get the space operator for the search widget.

        :rtype: str
        """
        return self._spaceOperator

    def setSpaceOperator(self, operator):
        """
        Set the space operator for the search widget.

        :type operator: str
        """
        self._spaceOperator = operator
        self.search()

    def createSpaceOperatorMenu(self, parent=None):
        """
        Return the menu for changing the space operator.

        :type parent: QGui.QMenu
        :rtype: QGui.QMenu
        """
        menu = QtWidgets.QMenu(parent)
        menu.setTitle("Space Operator")

        # Create the space operator for the OR operator
        action = QtWidgets.QAction(menu)
        action.setText("OR")
        action.setCheckable(True)

        callback = partial(self.setSpaceOperator, "or")
        action.triggered.connect(callback)

        if self.spaceOperator() == "or":
            action.setChecked(True)

        menu.addAction(action)

        # Create the space operator for the AND operator
        action = QtWidgets.QAction(menu)
        action.setText("AND")
        action.setCheckable(True)

        callback = partial(self.setSpaceOperator, "and")
        action.triggered.connect(callback)

        if self.spaceOperator() == "and":
            action.setChecked(True)

        menu.addAction(action)

        return menu

    def showContextMenu(self):
        """
        Create and show the context menu for the search widget.

        :rtype QtWidgets.QAction
        """
        menu = QtWidgets.QMenu(self)

        # Adding a blank icon fixes the text alignment issue when using Qt 5.12.+
        icon = studiolibrary.resource.icon("blank")

        subMenu = self.createStandardContextMenu()
        subMenu.setTitle("Edit")
        subMenu.setIcon(icon)

        menu.addMenu(subMenu)

        subMenu = self.createSpaceOperatorMenu(menu)
        menu.addMenu(subMenu)

        point = QtGui.QCursor.pos()
        action = menu.exec_(point)

        return action

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

    def updateIconColor(self):
        """
        Update the icon colors to the current foregroundRole.

        :rtype: None
        """
        color = self.palette().color(self.foregroundRole())
        color = studioqt.Color.fromColor(color)
        self.setIconColor(color)

    def settings(self):
        """
        Return a dictionary of the current widget state.

        :rtype: dict
        """
        settings = {
            "text": self.text(),
            "spaceOperator": self.spaceOperator(),
        }
        return settings

    def setSettings(self, settings):
        """
        Restore the widget state from a settings dictionary.

        :type settings: dict
        :rtype: None
        """
        text = settings.get("text", "")
        self.setText(text)

        spaceOperator = settings.get("spaceOperator")
        if spaceOperator:
            self.setSpaceOperator(spaceOperator)

    def resizeEvent(self, event):
        """
        Reimplemented so the icon maintains the same height as the widget.

        :type event:  QtWidgets.QResizeEvent
        :rtype: None
        """
        QtWidgets.QLineEdit.resizeEvent(self, event)

        self.setTextMargins(self.height(), 0, 0, 0)
        size = QtCore.QSize(self.height(), self.height())

        self._iconButton.setFixedSize(size)

        x = self.width() - self.height()
        self._clearButton.setGeometry(x, 0, self.height(), self.height())


def showExample():
    """
    Run a simple example of the search widget.

    :rtype: SearchWidget
    """

    with studioqt.app():

        def searchFinished():
            print('-' * 25)
            print('Found: {}'.format(len(dataset.results())))

            for data in dataset.results():
                print('Match:', data)

        data = [
            {'text': 'This is a dog'},
            {'text': 'I love cats'},
            {'text': 'How man eggs can you eat?'},
        ]

        dataset = studiolibrary.Dataset()
        dataset.setData(data)
        dataset.searchFinished.connect(searchFinished)

        widget = SearchWidget()
        widget.setDataset(dataset)
        widget.show()

        return widget



if __name__ == '__main__':
    showExample()
