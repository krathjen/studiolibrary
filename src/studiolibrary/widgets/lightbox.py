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

from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt


class Lightbox(QtWidgets.QFrame):

    DEFAULT_DURATION = 400

    def __init__(
            self,
            parent,
            widget=None,
            duration=DEFAULT_DURATION,
    ):

        super(Lightbox, self).__init__(parent)
        self.setObjectName("lightbox")

        self._widget = None
        self._accepted = False
        self._rejected = False
        self._animation = None
        self._duration = duration

        layout = QtWidgets.QGridLayout(self)
        self.setLayout(layout)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 5)
        layout.setRowStretch(2, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 5)
        layout.setColumnStretch(2, 1)

        layout.addWidget(QtWidgets.QWidget(), 0, 0)
        layout.addWidget(QtWidgets.QWidget(), 0, 1)
        layout.addWidget(QtWidgets.QWidget(), 0, 2)

        layout.addWidget(QtWidgets.QWidget(), 1, 0)
        layout.addWidget(QtWidgets.QWidget(), 1, 2)

        layout.addWidget(QtWidgets.QWidget(), 2, 0)
        layout.addWidget(QtWidgets.QWidget(), 2, 1)
        layout.addWidget(QtWidgets.QWidget(), 2, 2)

        if widget:
            self.setWidget(widget)

        parent = self.parent()
        parent.installEventFilter(self)

    def widget(self):
        """
        Get the current widget for the light box.
        
        :rtype: QtWidgets.QWidget 
        """
        return self._widget

    def setWidget(self, widget):
        """
        Set the widget for the lightbox.
        
        :type widget: QWidgets.QWidget
        """
        if self._widget:
            self.layout().removeWidget(self._widget)

        widget.setParent(self)
        widget.accept = self.accept
        widget.reject = self.reject

        self.layout().addWidget(widget, 1, 1)

        self._widget = widget

    def mousePressEvent(self, event):
        """
        Hide the light box if the user clicks on it.
        
        :type event: QEvent 
        """
        if not self.widget().underMouse():
            self.reject()

    def eventFilter(self, object, event):
        """
        Update the geometry when the parent widget changes size.
        
        :type object: QtWidget.QWidget
        :type event: QtCore.QEvent 
        :rtype: bool 
        """
        if event.type() == QtCore.QEvent.Resize:
            self.updateGeometry()

        return super(Lightbox, self).eventFilter(object, event)

    def showEvent(self, event):
        """
        Fade in the dialog on show.

        :type event: QtCore.QEvent 
        :rtype: None 
        """
        self.updateGeometry()
        self.fadeIn(self._duration)

    def updateGeometry(self):
        """
        Update the geometry to be in the center of it's parent.

        :rtype: None
        """
        self.setGeometry(self.parent().geometry())
        self.move(0, 0)

        geometry = self.geometry()
        centerPoint = self.geometry().center()
        geometry.moveCenter(centerPoint)
        geometry.setY(geometry.y())

        self.move(geometry.topLeft())

    def fadeIn(self, duration=200):
        """
        Fade in the dialog using the opacity effect.

        :type duration: int 
        :rtype: QtCore.QPropertyAnimation 
        """
        self._animation = studioqt.fadeIn(self, duration=duration)
        return self._animation

    def fadeOut(self, duration=200):
        """
        Fade out the dialog using the opacity effect.
        
        :type duration: int 
        :rtype: QtCore.QPropertyAnimation 
        """
        self._animation = studioqt.fadeOut(self, duration=duration)
        return self._animation

    def accept(self):
        """
        Triggered when the DialogButtonBox has been accepted.
        
        :rtype: None 
        """
        if not self._accepted:
            self._accepted = True
            animation = self.fadeOut(self._duration)

            if animation:
                animation.finished.connect(self._acceptAnimationFinished)
            else:
                self._acceptAnimationFinished()

    def reject(self):
        """
        Triggered when the DialogButtonBox has been rejected.

        :rtype: None 
        """
        if not self._rejected:
            self._rejected = True
            animation = self.fadeOut(self._duration)

            if animation:
                animation.finished.connect(self._rejectAnimationFinished)
            else:
                self._rejectAnimationFinished()

    def _acceptAnimationFinished(self):
        """
        Triggered when the animation has finished on accepted.

        :rtype: None 
        """
        try:
            self.widget().__class__.accept(self.widget())
        finally:
            self.close()

    def _rejectAnimationFinished(self):
        """
        Triggered when the animation has finished on rejected.

        :rtype: None 
        """
        try:
            self.widget().__class__.reject(self.widget())
        finally:
            self.close()


def example():

    widget = QtWidgets.QFrame()
    widget.setStyleSheet("border-radius:3px;background-color:white;")
    widget.setMinimumWidth(300)
    widget.setMinimumHeight(300)
    widget.setMaximumWidth(500)

    lightbox = Lightbox()
    lightbox.setWidget(widget)
    lightbox.show()


if __name__ == "__main__":
    with studioqt.app():
        w = example()
