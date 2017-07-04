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

import logging

from studioqt import QtWidgets
from studioqt import QtCore

import studioqt


logger = logging.getLogger(__name__)


class CombinedItemViewMixin(object):

    """
    The CombinedItemViewMixin class is a mixin for any widgets that
    inherit from the QAbstractItemView class. This class should be used
    for similar methods between views.
    """

    def __init__(self, *args):
        self._hoverItem = None
        self._mousePressButton = None
        self._currentItem = None
        self._currentSelection = []

    def cleanDirtyObjects(self):
        """
        Remove any objects that may have been deleted.

        :rtype: None
        """
        if self._currentItem:
            try:
                self._currentItem.text(0)
            except RuntimeError:
                self._hoverItem = None
                self._currentItem = None
                self._currentSelection = None

    def combinedWidget(self):
        """
        Return True if a control modifier is currently active.

        :rtype: studioqt.CombinedWidget
        """
        return self.parent()

    def isControlModifier(self):
        """
        Return True if a control modifier is currently active.

        :rtype: bool
        """
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        isAltModifier = modifiers == QtCore.Qt.AltModifier
        isControlModifier = modifiers == QtCore.Qt.ControlModifier
        return isAltModifier or isControlModifier

    def itemsFromIndexes(self, indexes):
        """
        Return a list of Tree Widget Items assocated with the given indexes.

        :type indexes: list[QtCore.QModelIndex]
        :rtype: list[QtWidgets.QTreeWidgetItem]
        """
        items = {}
        for index in indexes:
            item = self.itemFromIndex(index)
            items[id(item)] = item

        return items.values()

    def selectionChanged(self, selected, deselected):
        """
        Triggered when the current item has been selected or deselected.

        :type selected: QtWidgets.QItemSelection
        :type deselected: QtWidgets.QItemSelection
        """
        selectedItems_ = self.selectedItems()

        if self._currentSelection != selectedItems_:
            self._currentSelection = selectedItems_

            indexes1 = selected.indexes()
            selectedItems = self.itemsFromIndexes(indexes1)

            indexes2 = deselected.indexes()
            deselectedItems = self.itemsFromIndexes(indexes2)

            items = selectedItems + deselectedItems
            for item in items:
                item.selectionChanged()
            #
            QtWidgets.QAbstractItemView.selectionChanged(self, selected, deselected)

    def mousePressButton(self):
        """
        Return the mouse button that has been pressed.

        :rtype: None or QtCore.Qt.MouseButton
        """
        return self._mousePressButton

    def wheelEvent(self, event):
        """
        Triggered on any wheel events for the current viewport.

        :type event: QtWidgets.QWheelEvent
        :rtype: None
        """
        if self.isControlModifier():
            event.ignore()
        else:
            QtWidgets.QAbstractItemView.wheelEvent(self, event)

        item = self.itemAt(event.pos())
        self.itemUpdateEvent(item, event)

    def keyPressEvent(self, event):
        """
        Triggered on user key press events for the current viewport.

        :type event: QtCore.QKeyEvent
        :rtype: None
        """
        item = self.selectedItem()
        if item:
            self.itemKeyPressEvent(item, event)

        validKeys = [
            QtCore.Qt.Key_Up,
            QtCore.Qt.Key_Left,
            QtCore.Qt.Key_Down,
            QtCore.Qt.Key_Right,
        ]

        if event.isAccepted():
            if event.key() in validKeys:
                QtWidgets.QAbstractItemView.keyPressEvent(self, event)

    def mousePressEvent(self, event):
        """
        Triggered on user mouse press events for the current viewport.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        self._mousePressButton = event.button()

        item = self.itemAt(event.pos())

        if item:
            self.itemMousePressEvent(item, event)

        QtWidgets.QAbstractItemView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Triggered on user mouse release events for the current viewport.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        self._mousePressButton = None

        item = self.selectedItem()
        if item:
            self.itemMouseReleaseEvent(item, event)

    def mouseMoveEvent(self, event):
        """
        Triggered on user mouse move events for the current viewport.

        :type event: QtCore.QMouseEvent
        :rtype: None
        """
        if self._mousePressButton == QtCore.Qt.MiddleButton:
            item = self.selectedItem()
        else:
            item = self.itemAt(event.pos())

        self.itemUpdateEvent(item, event)

    def leaveEvent(self, event):
        """
        Triggered when the mouse leaves the widget.

        :type event: QtCore.QMouseEvent
        :rtype: None
        """
        if self._mousePressButton != QtCore.Qt.MiddleButton:
            self.itemUpdateEvent(None, event)

        QtWidgets.QAbstractItemView.leaveEvent(self, event)

    def itemUpdateEvent(self, item, event):
        """
        Triggered on user key press events for the current viewport.

        :type item: CombinedWidgetItem
        :type event: QtCore.QKeyEvent
        :rtype: None
        """
        self.cleanDirtyObjects()

        if id(self._currentItem) != id(item):

            if self._currentItem:
                self.itemMouseLeaveEvent(self._currentItem, event)
                self._currentItem = None

            if item and not self._currentItem:
                self._currentItem = item
                self.itemMouseEnterEvent(item, event)

        if self._currentItem:
            self.itemMouseMoveEvent(item, event)

    def itemMouseEnterEvent(self, item, event):
        """
        Triggered when the mouse enters the given item.

        :type item: QtWidgets.QTreeWidgetItem
        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        item.mouseEnterEvent(event)
        logger.debug("Mouse Enter: " + item.text(0))

    def itemMouseLeaveEvent(self, item, event):
        """
        Triggered when the mouse leaves the given item.

        :type item: QtWidgets.QTreeWidgetItem
        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        item.mouseLeaveEvent(event)
        logger.debug("Mouse Leave: " + item.text(0))

    def itemMouseMoveEvent(self, item, event):
        """
        Triggered when the mouse moves within the given item.

        :type item: QtWidgets.QTreeWidgetItem
        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        item.mouseMoveEvent(event)

    def itemMousePressEvent(self, item, event):
        """
        Triggered when the mouse is pressed on the given item.

        :type item: QtWidgets.QTreeWidgetItem
        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        item.mousePressEvent(event)
        logger.debug("Mouse Press: " + item.text(0))

    def itemMouseReleaseEvent(self, item, event):
        """
        Triggered when the mouse is released on the given item.

        :type item: QtWidgets.QTreeWidgetItem
        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        item.mouseReleaseEvent(event)
        logger.debug("Mouse Released: " + item.text(0))

    def itemKeyPressEvent(self, item, event):
        """
        Triggered when a key is pressed for the selected item.

        :type item: QtWidgets.QTreeWidgetItem
        :type event: QtWidgets.QKeyEvent
        :rtype: None
        """
        item.keyPressEvent(event)
        logger.debug("Key Press: " + item.text(0))

    def itemKeyReleaseEvent(self, item, event):
        """
        Triggered when a key is released for the selected item.

        :type item: QtWidgets.QTreeWidgetItem
        :type event: QtWidgets.QKeyEvent
        :rtype: None
        """
        item.keyReleaseEvent(event)
        logger.debug("Key Release: " + item.text(0))
