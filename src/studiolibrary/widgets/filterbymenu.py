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
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt

from .separatoraction import SeparatorAction


NEW_STYLE = True


class LabelAction(QtWidgets.QWidgetAction):

    def _triggered(self, checked=None):
        """Triggered when the checkbox value has changed."""
        self.triggered.emit()
        self.parent().close()

    def createWidget(self, menu):
        """
        This method is called by the QWidgetAction base class.

        :type menu: QtWidgets.QMenu
        """
        widget = QtWidgets.QFrame(self.parent())
        widget.setObjectName("filterByAction")

        title = self._name

        # Using a checkbox so that the text aligns with the other actions
        label = QtWidgets.QCheckBox(widget)
        label.setText(title)
        label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        label.toggled.connect(self._triggered)
        label.setStyleSheet("""
#QCheckBox::indicator:checked {
    image: url(none.png)
}
QCheckBox::indicator:unchecked {
    image: url(none.png)
}
""")
        actionLayout = QtWidgets.QHBoxLayout(widget)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(label, stretch=1)
        widget.setLayout(actionLayout)

        return widget


class FilterByAction(QtWidgets.QWidgetAction):

    def __init__(self, parent=None):
        """
        :type parent: QtWidgets.QMenu
        """
        QtWidgets.QWidgetAction.__init__(self, parent)

        self._facet = None
        self._checked = False

    def setChecked(self, checked):
        self._checked = checked

    def setFacet(self, facet):
        self._facet = facet

    def _triggered(self, checked=None):
        """Triggered when the checkbox value has changed."""
        self.triggered.emit()
        self.parent().close()

    def createWidget(self, menu):
        """
        This method is called by the QWidgetAction base class.

        :type menu: QtWidgets.QMenu
        """
        widget = QtWidgets.QFrame(self.parent())
        widget.setObjectName("filterByAction")

        facet = self._facet

        name = facet.get("name") or ""
        count = str(facet.get("count", 0))

        title = name.replace(".", "").title()

        label = QtWidgets.QCheckBox(widget)
        label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        label.setText(title)
        label.installEventFilter(self)
        label.toggled.connect(self._triggered)
        label.setChecked(self._checked)

        label2 = QtWidgets.QLabel(widget)
        label2.setObjectName("actionCounter")
        label2.setText(count)

        layout = QtWidgets.QHBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label, stretch=1)
        layout.addWidget(label2)
        widget.setLayout(layout)

        return widget


class FilterByMenu(QtWidgets.QMenu):

    def __init__(self, *args, **kwargs):
        super(FilterByMenu, self).__init__(*args, **kwargs)

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

        if NEW_STYLE:
            action = LabelAction(self)
            action._name = "Show All"
            self.addAction(action)
        else:
            action = self.addAction("Show All")

        action.setEnabled(not self.isShowAllEnabled())
        callback = partial(self._showAllClicked)
        action.triggered.connect(callback)

        self.addSeparator()

        for facet in self._facets:

            name = facet.get("name") or ""
            count = facet.get("count", 0)
            checked = self.settings().get(name, True)

            title = "{name}\t({count})"
            title = title.format(name=name.replace(".", "").title(), count=count)

            if NEW_STYLE:
                action = FilterByAction(self)
                action.setFacet(facet)
                action.setChecked(checked)
                self.addAction(action)
            else:
                action = self.addAction(title)
                action.setCheckable(True)
                action.setChecked(checked)

            callback = partial(self._actionChecked, name, not checked)
            action.triggered.connect(callback)

        if not point:
            point = QtGui.QCursor.pos()

        self.exec_(point)
