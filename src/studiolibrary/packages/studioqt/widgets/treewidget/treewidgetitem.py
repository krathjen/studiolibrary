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

from studioqt import QtGui
from studioqt import QtCore
from studioqt import QtWidgets

import studioqt


__all__ = ["TreeWidgetItem"]


logger = logging.getLogger(__name__)


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, *args):
        QtWidgets.QTreeWidgetItem.__init__(self, *args)

        self._iconPath = None
        self._iconColor = None

    def iconPath(self):
        """
        Return the icon path for the item.
        
        :rtype: str 
        """
        return self._iconPath or self.defaultIconPath()

    def defaultIconPath(self):
        """
        Return the default icon path.

        :rtype: str 
        """
        return studioqt.resource().get("icons/folder_14pt.png")

    def setIconPath(self, path):
        """
        Return the icon path for the item.

        :type path: str
        :rtype: None 
        """
        self._iconPath = path
        self.updateIcon()

    def iconColor(self):
        """
        Return the icon color.

        :rtype: QtGui.QColor or None
        """
        return self._iconColor or self.defaultIconColor()

    def defaultIconColor(self):
        """
        Return the default icon color.
        
        :rtype: QtGui.QColor or None
        """
        palette = self.treeWidget().palette()

        color = palette.color(self.treeWidget().foregroundRole())
        color = studioqt.Color.fromColor(color).toString()

        return color

    def setIconColor(self, color):
        """
        Set the icon color.
        
        :type color: QtGui.QColor
        :rtype: None 
        """
        if isinstance(color, QtGui.QColor):
            color = studioqt.Color.fromColor(color)

        elif isinstance(color, basestring):
            color = studioqt.Color.fromString(color)

        self._iconColor = color
        self.updateIcon()

    def path(self):
        """
        Return the item location from the url.
        
        :rtype: str 
        """
        item = self
        paths = [item.text(0)]

        while item.parent():
            item = item.parent()
            paths.append(item.text(0))

        return "/".join(reversed(paths))

    def parents(self):
        """
        Return all item parents.

        :rtype: list[TreeWidgetItem]
        """
        parents = []
        parent = self.parent()

        if parent:
            parents.append(parent)

            while parent.parent():
                parent = parent.parent()
                parents.append(parent)

        return parents

    def url(self):
        """
        Return the url path.
        
        :rtype: str 
        """
        return QtCore.QUrl(self.path())

    def update(self):
        """
        :rtype: None 
        """
        self.updateIcon()

    def updateIcon(self):
        """
        Force the icon to update.
        
        :rtype: None 
        """
        if self.isExpanded():
            path = studioqt.resource().get("icons", "folder_open")
        else:
            path = studioqt.resource().get("icons", "folder")

        color = self.iconColor()

        pixmap = studioqt.Pixmap(path)
        pixmap.setColor(color)

        self.setIcon(0, pixmap)

    def settings(self):
        """
        Return the current state of the item as a dictionary.
        
        :rtype: dict 
        """
        settings = {}

        isSelected = self.isSelected()
        if isSelected:
            settings["isSelected"] = isSelected

        isExpanded = self.isExpanded()
        if isExpanded:
            settings["isExpanded"] = isExpanded

        return settings

    def setSettings(self, settings, ignoreSelected=False, ignoreExpanded=False):
        """
        Set the current state of the item from a dictionary.

        :type settings: dict 
        """
        if not ignoreSelected:
            isSelected = settings.get("isSelected", False)
            self.setSelected(isSelected)

        if not ignoreExpanded:
            isExpanded = settings.get("isExpanded", False)
            self.setExpanded(isExpanded)