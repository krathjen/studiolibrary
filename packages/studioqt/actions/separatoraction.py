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

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets


__all__ = ["SeparatorAction"]


class Line(QtWidgets.QFrame):
    pass


class SeparatorWidgetAction(QtWidgets.QFrame):
    pass


class SeparatorAction(QtWidgets.QWidgetAction):

    def __init__(self, label="", parent=None):
        """
        :type parent: QtWidgets.QMenu
        """
        QtWidgets.QWidgetAction.__init__(self, parent)

        self._widget = SeparatorWidgetAction(parent)

        self._label = QtWidgets.QLabel(self._widget)
        self._label.setText(label)

        self._line = Line(self._widget)
        self._line.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

    def setText(self, text):
        """
        Set the text of the separator.

        :type text: str
        :rtype: None
        """
        self.label().setText(text)

    def widget(self):
        """
        Return the QFrame object.

        :rtype: Frame
        """
        return self._widget

    def label(self):
        """
        Return the QLabel object.

        :rtype: QtWidgets.QLabel
        """
        return self._label

    def line(self):
        """
        Return the line widget.

        :rtype: Line
        """
        return self._line

    def createWidget(self, menu):
        """
        This method is called by the QWidgetAction base class.

        :type menu: QtWidgets.QMenu
        """
        actionWidget = self.widget()

        actionLayout = QtWidgets.QHBoxLayout(actionWidget)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(self.label())
        actionLayout.addWidget(self.line())
        actionWidget.setLayout(actionLayout)

        return actionWidget
