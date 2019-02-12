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


import studioqt
from studioqt import QtWidgets


class PreviewWidget(QtWidgets.QWidget):

    def __init__(self, item, *args):
        QtWidgets.QWidget.__init__(self, *args)
        studioqt.loadUi(self)

        pixmap = studioqt.Pixmap(item.thumbnailPath())
        pixmap.setColor('rgb(255,255,255,20)')
        self.ui.thumbnailLabel.setPixmap(pixmap)
