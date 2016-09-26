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

from studioqt import QtWidgets
from studioqt import QtCore


class SliderAction(QtWidgets.QWidgetAction):

    def __init__(self, label="", parent=None, dpi=1):
        """
        :type parent: QtWidgets.QMenu
        """
        QtWidgets.QWidgetAction.__init__(self, parent)

        self.setObjectName("customAction")

        self._frame = QtWidgets.QFrame(parent)

        self._label = QtWidgets.QLabel(label, self._frame)
        self._label.setObjectName("sliderActionLabel")
        self._label.setMinimumWidth(85)

        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self._frame)
        self.valueChanged = self._slider.valueChanged

    def frame(self):
        return self._frame

    def label(self):
        return self._label

    def slider(self):
        return self._slider

    def createWidget(self, parent):
        """
        :type parent: QtWidgets.QMenu
        """
        actionWidget = self.frame()
        actionWidget.setObjectName("sliderActionWidget")

        actionLayout = QtWidgets.QHBoxLayout(actionWidget)
        actionLayout.setSpacing(0)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(self.label())
        actionLayout.addWidget(self.slider())
        actionWidget.setLayout(actionLayout)

        return actionWidget