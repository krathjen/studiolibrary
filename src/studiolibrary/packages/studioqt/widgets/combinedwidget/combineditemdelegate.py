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
        # This will be called for each column.
        item = self.combinedWidget().itemFromIndex(index)
        return item.sizeHint()

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
