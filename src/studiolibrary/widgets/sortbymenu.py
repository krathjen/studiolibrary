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

from functools import partial

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtWidgets

from .separatoraction import SeparatorAction


class SortByMenu(QtWidgets.QMenu):

    def __init__(self, name, parent, dataset):
        super(SortByMenu, self).__init__(name, parent)

        self._dataset = dataset
        self.aboutToShow.connect(self.populateMenu)

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

    def populateMenu(self):
        """
        Show the menu options.
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

        fields = self.dataset().fields()

        for field in fields:

            if not field.get("sortable"):
                continue

            name = field.get("name")

            action = self.addAction(name.title())
            action.setCheckable(True)

            if currentField == name:
                action.setChecked(True)
            else:
                action.setChecked(False)

            callback = partial(self.setSortBy, name, currentOrder)
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
