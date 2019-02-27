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

from functools import partial

from studioqt import QtGui
from studioqt import QtWidgets

from .separatoraction import SeparatorAction


class SortByMenu(QtWidgets.QMenu):

    def __init__(self, *args, **kwargs):
        super(SortByMenu, self).__init__(*args, **kwargs)

        self._dataset = None

    def setDataset(self, dataset):
        """
        Set the dataset model for the menu:
        
        :type dataset: studiolibrary.Dataset
        """
        self._dataset = dataset

    def dataset(self):
        """
        Get the dataset model for the menu.
        
        :rtype: studiolibrary.Dataset 
        """
        return self._dataset

    def setSortBy(self, sortName, sortOrder):
        """
        Set the sort by value for the dataset.
        
        :type sortName: str 
        :type sortOrder: str
        """
        if sortName == "Custom Order":
            sortOrder = "asc"

        value = sortName + ":" + sortOrder
        self.dataset().setSortBy([value])
        self.dataset().search()

    def show(self, point=None):
        """
        Show the menu options.
        
        :type point: QtGui.QPoint or None
        """
        self.clear()

        sortby = self.dataset().sortBy()
        if sortby:
            currentField = self.dataset().sortBy()[0].split(":")[0]
            currentOrder = "dsc" if "dsc" in self.dataset().sortBy()[0] else "asc"
        else:
            currentField = ""
            currentOrder = ""

        action = SeparatorAction("Sort By", self)
        self.addAction(action)

        fields = self.dataset().SortFields

        for field in fields:

            action = self.addAction(field.title())
            action.setCheckable(True)

            if currentField == field:
                action.setChecked(True)
            else:
                action.setChecked(False)

            callback = partial(self.setSortBy, field, currentOrder)
            action.triggered.connect(callback)

        action = SeparatorAction("Sort Order", self)
        self.addAction(action)

        action = self.addAction("Ascending")
        action.setCheckable(True)
        action.setChecked(currentOrder == "asc")

        callback = partial(self.setSortBy, currentField, "asc")
        action.triggered.connect(callback)

        action = self.addAction("Descending")
        action.setCheckable(True)
        action.setChecked(currentOrder == "dsc")

        callback = partial(self.setSortBy, currentField, "dsc")
        action.triggered.connect(callback)

        if not point:
            point = QtGui.QCursor.pos()

        self.exec_(point)
