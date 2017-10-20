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

import os
import mutils

import studiolibrary
import studiolibrarymaya

from studiolibrarymaya import baseitem
from studiolibrarymaya import basecreatewidget
from studiolibrarymaya import basepreviewwidget

__all__ = [
    "SetsItem",
    "SetsCreateWidget",
    "SetsPreviewWidget",
]


class SetsItem(baseitem.BaseItem):

    def __init__(self, *args, **kwargs):
        """
        :rtype: None
        """
        super(SetsItem, self).__init__(*args, **kwargs)

        self.setTransferBasename("set.json")
        self.setTransferClass(mutils.SelectionSet)

    def doubleClicked(self):
        """Overriding this method to load the item on double click."""
        self.loadFromSettings()

    def loadFromSettings(self):
        """Load the selection set using the settings for this item."""
        namespaces = self.namespaces()
        self.load(namespaces=namespaces)

    def load(self, namespaces=None):
        """
        :type namespaces: list[str] | None
        """
        self.selectContent(namespaces=namespaces)

    def save(self, objects, path="", iconPath="", **kwargs):
        """
        Save all the given object data to the given path on disc.

        :type objects: list[str]
        :type path: str
        :type iconPath: str
        """
        if path and not path.endswith(".set"):
            path += ".set"

        super(SetsItem, self).save(objects, path=path, iconPath=iconPath, **kwargs)


class SetsCreateWidget(basecreatewidget.BaseCreateWidget):

    def __init__(self, item=None, parent=None):
        """
        :type parent: QtWidgets.QWidget
        :type item: SelectionSetItem
        """
        item = item or SetsItem()
        super(SetsCreateWidget, self).__init__(item, parent=parent)


class SetsPreviewWidget(basepreviewwidget.BasePreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :type parent: QtWidgets.QWidget
        :type item: SelectionSetItem
        """
        super(SetsPreviewWidget, self).__init__(*args, **kwargs)

        self.ui.optionsToggleBox.setVisible(False)

    def accept(self):
        """Triggered when the user clicks the apply button."""
        self.item().loadFromSettings()


# Register the selection set item to the Studio Library
iconPath = studiolibrarymaya.resource().get("icons", "selectionSet.png")

SetsItem.Extensions = [".set"]
SetsItem.MenuName = "Selection Set"
SetsItem.MenuIconPath = iconPath
SetsItem.TypeIconPath = iconPath
SetsItem.CreateWidgetClass = SetsCreateWidget
SetsItem.PreviewWidgetClass = SetsPreviewWidget

studiolibrary.registerItem(SetsItem)
