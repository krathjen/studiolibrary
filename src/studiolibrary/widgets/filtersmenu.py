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

import studioqt

from .separatoraction import SeparatorAction


class FiltersMenu(QtWidgets.QMenu):

    def __init__(self, *args, **kwargs):
        super(FiltersMenu, self).__init__(*args, **kwargs)

        self._facets = []
        self._dataset = None
        self._options = {"field": "type"}
        self._settings = {}

    def name(self):
        """
        The name of the filter used by the dataset.
        
        :rtype: str
        """
        return self._options.get("field") + "FilterMenu"

    def _actionChecked(self, name, checked):
        """
        Triggered when an action has been clicked.
        
        :type name: str
        :type checked: bool
        """
        if studioqt.isControlModifier():
            self.setAllEnabled(False)
            self._settings[name] = True
        else:
            self._settings[name] = checked

        self.dataset().search()

    def _showAllClicked(self):
        """Triggered when the user clicks the show all action."""
        self.setAllEnabled(True)
        self.dataset().search()

    def setAllEnabled(self, enabled):
        """
        Set all the filters enabled.
        
        :type enabled: bool 
        """
        for facet in self._facets:
            self._settings[facet.get("name")] = enabled

    def isShowAllEnabled(self):
        """
        Check if all the current filters are enabled.
        
        :rtype: bool 
        """
        for facet in self._facets:
            if not self._settings.get(facet.get("name"), True):
                return False
        return True

    def isActive(self):
        """
        Check if there are any filters currently active using the settings.
        
        :rtype: bool 
        """
        settings = self.settings()
        for name in settings:
            if not settings.get(name):
                return True
        return False

    def setOptions(self, options):
        """
        Set the options to be used by the filters menu.
        
        :type options: dict
        """
        self._options = options

    def dataset(self):
        """
        Get the dataset model for the menu.
        
        :rtype: studiolibrary.Dataset 
        """
        return self._dataset

    def settings(self):
        """
        Get the settings for the filter menu.
        
        :rtype: dict
        """
        return self._settings

    def setSettings(self, settings):
        """
        Set the settings filter menu.
        
        :type settings: dict
        """
        self._settings = settings

    def setDataset(self, dataset):
        """
        Set the dataset model for the menu:
        
        :type dataset: studiolibrary.Dataset
        """
        self._dataset = dataset
        dataset.searchStarted.connect(self.searchInit)

    def searchInit(self):
        """Triggered before each search to update the filter menu query."""
        filters = []

        settings = self.settings()
        field = self._options.get("field")

        for name in settings:
            checked = settings.get(name, True)
            if not checked:
                filters.append((field, "not", name))

        query = {
            "name": self.name(),
            "operator": "and",
            "filters": filters
        }

        self.dataset().addQuery(query)

    def show(self, point=None):
        """
        Show the menu options.
        
        :type point: QtGui.QPoint or None
        """
        self.clear()

        field = self._options.get("field")
        queries = self.dataset().queries(exclude=self.name())

        self._facets = self.dataset().distinct(field, queries=queries)

        action = SeparatorAction("Show " + field.title(), self)
        self.addAction(action)

        action = self.addAction("Show All")
        action.setEnabled(not self.isShowAllEnabled())
        callback = partial(self._showAllClicked)
        action.triggered.connect(callback)

        self.addSeparator()

        for facet in self._facets:

            title = "{name}\t({count})"

            name = facet.get("name")
            count = facet.get("count")

            title = title.format(name=name.replace(".", "").title(), count=count)

            action = self.addAction(title)
            action.setCheckable(True)

            checked = self.settings().get(name, True)
            action.setChecked(checked)

            callback = partial(self._actionChecked, name, not checked)
            action.triggered.connect(callback)

        if not point:
            point = QtGui.QCursor.pos()

        self.exec_(point)
