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
from studioqt import QtCore

import studioqt


class CombinedItemDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self):
        """
        This class is used to display data for the items in a CombinedWidget.
        """
        QtWidgets.QStyledItemDelegate.__init__(self)

        self._combinedWidget = None

    def combinedWidget(self):
        """
        Return the CombinedWidget that contains the item delegate.

        :rtype: studioqt.CombinedWidget
        """
        return self._combinedWidget

    def setCombinedWidget(self, combinedWidget):
        """
        Set the CombinedWidget for the delegate.

        :type combinedWidget: studioqt.CombinedWidget
        :rtype: None
        """
        self._combinedWidget = combinedWidget

    def sizeHint(self, option, index):
        """
        Return the size for the given index.

        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        :rtype: QtCore.QSize
        """
        # This will be called for each row.
        item = self.combinedWidget().itemFromIndex(index)
        return item.sizeHint(0)

    def paint(self, painter, option, index):
        """
        Paint performs low-level painting for the given model index.

        :type painter:  QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        :rtype: None
        """
        item = self.combinedWidget().itemFromIndex(index)
        item.paint(painter, option, index)
