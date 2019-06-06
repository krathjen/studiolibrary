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

import studiolibrary.widgets
import studioqt
from studioqt import QtWidgets


class PreviewWidget(QtWidgets.QWidget):

    def __init__(self, item, *args):
        QtWidgets.QWidget.__init__(self, *args)
        studioqt.loadUi(self)

        self._item = item

        pixmap = studioqt.Pixmap(item.thumbnailPath())
        pixmap.setColor('rgb(255,255,255,20)')
        self.ui.thumbnailLabel.setPixmap(pixmap)

        self._infoWidget = studiolibrary.widgets.FormWidget(self)
        self._infoWidget.setTitle("Info")
        self._infoWidget.setTitleVisible(True)
        self._infoWidget.setSchema(item.info())

        self.ui.infoFrame.layout().addWidget(self._infoWidget)

        self._optionsWidget = studiolibrary.widgets.FormWidget(self)
        self._optionsWidget.setTitle("Options")

        options = item.loadSchema()
        if options:
            self._optionsWidget.setSchema(options)
            self._optionsWidget.setTitleVisible(True)

        self.ui.optionsFrame.layout().addWidget(self._optionsWidget)

        self.ui.acceptButton.hide()
        self.ui.acceptButton.setText("Load")
        self.ui.acceptButton.clicked.connect(self.accept)

        self.loadSettings()

    def close(self):
        """Triggered when the user changes the options."""
        self.saveSettings()
        super(PreviewWidget, self).close()

    def settingsPath(self):
        """
        Get the user settings path for the item.
        
        :rtype: str
        """
        return studiolibrary.localPath("ItemSettings.json")

    def readSettings(self):
        """
        Return the local settings from the location of the SETTING_PATH.
    
        :rtype: dict
        """
        return studiolibrary.readJson(self.settingsPath())

    def loadSettings(self):
        """Load the user settings for the preview widget."""
        data = self.readSettings()

        name = self._item.__class__.__name__

        state = data.get(name, {}).get("optionsWidget")
        if state is not None:
            self._optionsWidget.setState(state)

        expand = data.get("infoExpanded")
        if expand is not None:
            self._infoWidget.setExpanded(expand)

        expand = data.get("optionsExpanded")
        if expand is not None:
            self._optionsWidget.setExpanded(expand)

    def saveSettings(self):
        """Save the current user state for the preview widget."""

        name = self._item.__class__.__name__

        data = {
            "infoExpanded": self._infoWidget.isExpanded(),
            "optionsExpanded": self._optionsWidget.isExpanded(),
            name: {"optionsWidget": self._optionsWidget.state()}
        }

        studiolibrary.updateJson(self.settingsPath(), data)

    def accept(self):
        """Called when the user clicks the load button."""
        kwargs = self._optionsWidget.values()
        self._item.load(**kwargs)
