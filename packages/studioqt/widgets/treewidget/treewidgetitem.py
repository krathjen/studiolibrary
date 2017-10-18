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

        self._path = ""
        self._bold = None
        self._iconPath = None
        self._iconColor = None
        self._textColor = None
        self._expandedIconPath = None
        self._collapsedIconPath = None

        self._settings = {}

    def iconPath(self):
        """
        Return the icon path for the item.
        
        :rtype: str 
        """
        return self._iconPath or self.defaultIconPath()

    def expandedIconPath(self):
        """
        Return the icon path to be shown when expanded.
        
        :rtype: path 
        """
        return self._expandedIconPath or studioqt.resource.get("icons", "folder_open")

    def collapsedIconPath(self):
        """
        Return the icon path to be shown when collapsed.

        :rtype: path 
        """
        return self._collapsedIconPath or studioqt.resource.get("icons", "folder")

    def defaultIconPath(self):
        """
        Return the default icon path.

        :rtype: str 
        """
        return ""

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

        return str(color)

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

        self._iconColor = color.toString()
        self.updateIcon()

    def setPath(self, path):
        """
        Set the path for the navigation item.
        
        :type path: str
        :rtype: None 
        """
        self._path = path

    def path(self):
        """
        Return the item path.
        
        :rtype: str 
        """
        return self._path

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
        path = self.iconPath()

        if not path:
            if self.isExpanded():
                path = self.expandedIconPath()
            else:
                path = self.collapsedIconPath()

        color = self.iconColor()

        pixmap = studioqt.Pixmap(path)
        pixmap.setColor(color)

        self.setIcon(0, pixmap)

    def bold(self):
        """
        Returns true if weight() is a value greater than QFont::Normal
        
        :rtype: bool 
        """
        return self.font(0).bold()

    def setBold(self, enable):
        """
        If enable is true sets the font's weight to

        :rtype: bool 
        """
        if enable:
            self._settings["bold"] = enable

        font = self.font(0)
        font.setBold(enable)
        self.setFont(0, font)

    def setTextColor(self, color):
        """
        Set the foreground color to the given color
        
        :type color: QtGui.QColor
        :rtype: None 
        """
        if isinstance(color, QtGui.QColor):
            color = studioqt.Color.fromColor(color)

        elif isinstance(color, basestring):
            color = studioqt.Color.fromString(color)

        self._settings["textColor"] = color.toString()

        brush = QtGui.QBrush()
        brush.setColor(color)
        self.setForeground(0, brush)

    def textColor(self):
        """
        Return the foreground color the item.

        :rtype: QtGui.QColor 
        """
        color = self.foreground(0).color()
        return studioqt.Color.fromColor(color)

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

        iconPath = self.iconPath()
        if iconPath != self.defaultIconPath():
            settings["iconPath"] = iconPath

        iconColor = self.iconColor()
        if iconColor != self.defaultIconColor():
            settings["iconColor"] = iconColor

        bold = self._settings.get("bold")
        if bold:
            settings["bold"] = bold

        textColor = self._settings.get("textColor")
        if textColor:
            settings["textColor"] = textColor

        return settings

    def setExpandedParents(self, expanded):
        """
        Set all the parents of the item to the value of expanded.
        
        :type expanded: bool
        :rtype: None 
        """
        parents = self.parents()
        for parent in parents:
            parent.setExpanded(expanded)

    def setSelected(self, select):
        """
        Sets the selected state of the item to select.

        :type select: bool
        :rtype: None 
        """
        QtWidgets.QTreeWidgetItem.setSelected(self, select)

        if select:
            self.setExpandedParents(select)

    def setSettings(self, settings):
        """
        Set the current state of the item from a dictionary.

        :type settings: dict 
        """
        text = settings.get("text", None)
        if text:
            self.setText(0, text)

        iconPath = settings.get("iconPath", None)
        if iconPath:
            self.setIconPath(iconPath)

        iconColor = settings.get("iconColor", None)
        if iconColor:
            self.setIconColor(iconColor)

        isSelected = settings.get("isSelected", False)
        self.setSelected(isSelected)

        isExpanded = settings.get("isExpanded", False)
        if self.childCount() > 0:
            self.setExpanded(isExpanded)

        bold = settings.get("bold", False)
        if bold:
            self.setBold(bold)

        textColor = settings.get("textColor", None)
        if textColor:
            self.setTextColor(textColor)
