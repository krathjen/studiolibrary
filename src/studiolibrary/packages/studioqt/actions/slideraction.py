# Copyright 2015 by Kurt Rathjen. All Rights Reserved.
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

from studioqt import QtCore
from studioqt import QtWidgets


__all__ = ["SliderAction"]


class SliderWidgetAction(QtWidgets.QFrame):
    pass


class SliderAction(QtWidgets.QWidgetAction):

    def __init__(self, label="", parent=None):
        """
        :type parent: QtWidgets.QMenu
        """
        QtWidgets.QWidgetAction.__init__(self, parent)

        self._widget = SliderWidgetAction(parent)
        self._label = QtWidgets.QLabel(label, self._widget)

        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self._widget)
        self._slider.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        self.valueChanged = self._slider.valueChanged

    def widget(self):
        """
        Return the widget for this action.

        :rtype: QtWidgets.QWidget
        """
        return self._widget

    def label(self):
        """
        Return the QLabel object.

        :rtype: QtWidgets.QLabel
        """
        return self._label

    def slider(self):
        """
        Return the QLabel object.

        :rtype: QtWidgets.QSlider
        """
        return self._slider

    def createWidget(self, menu):
        """
        This method is called by the QWidgetAction base class.

        :type parent: QtWidgets.QMenu
        """
        actionWidget = self.widget()

        actionLayout = QtWidgets.QHBoxLayout(actionWidget)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(self.label())
        actionLayout.addWidget(self.slider())
        actionWidget.setLayout(actionLayout)

        return actionWidget