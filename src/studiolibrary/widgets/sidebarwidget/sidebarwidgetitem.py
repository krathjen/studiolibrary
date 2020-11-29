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

import os
import logging

from studiovendor import six
from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt
import studiolibrary


__all__ = ["SidebarWidgetItem"]


logger = logging.getLogger(__name__)


class SidebarWidgetItem(QtWidgets.QTreeWidgetItem):

    PIXMAP_CACHE = {}

    def __init__(self, *args):
        QtWidgets.QTreeWidgetItem.__init__(self, *args)

        self._path = ""
        self._bold = None
        self._iconVisible = True
        self._iconPath = None
        self._iconColor = None
        self._textColor = None
        self._iconKey = None
        self._expandedIconPath = None
        self._collapsedIconPath = None

        self._settings = {}

    def iconPath(self):
        """
        Return the icon path for the item.
        
        :rtype: str 
        """
        return self._iconPath or self.defaultIconPath()

    def createPixmap(self, path, color):
        """
        Create a new Pixmap from the given path.

        :type path: str
        :type color: str or QtCore.QColor
        :rtype: QtCore.QPixmap
        """
        dpi = self.treeWidget().dpi()
        key = path + color + "DPI-" + str(dpi)
        pixmap = self.PIXMAP_CACHE.get(key)

        if not pixmap:

            width = 20 * dpi
            height = 18 * dpi

            if "/" not in path and "\\" not in path:
                path = studiolibrary.resource.get("icons", path)

            if not os.path.exists(path):
                path = self.defaultIconPath()

            pixmap2 = studioqt.Pixmap(path)
            pixmap2.setColor(color)
            pixmap2 = pixmap2.scaled(
                16 * dpi,
                16 * dpi,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )

            x = (width - pixmap2.width()) / 2
            y = (height - pixmap2.height()) / 2

            pixmap = QtGui.QPixmap(QtCore.QSize(width, height))
            pixmap.fill(QtCore.Qt.transparent)

            painter = QtGui.QPainter(pixmap)
            painter.drawPixmap(x, y, pixmap2)
            painter.end()

            self.PIXMAP_CACHE[key] = pixmap

        return pixmap

    def expandedIconPath(self):
        """
        Return the icon path to be shown when expanded.
        
        :rtype: str 
        """
        return self._iconPath or studiolibrary.resource.get("icons", "folder_open.png")

    def collapsedIconPath(self):
        """
        Return the icon path to be shown when collapsed.

        :rtype: str 
        """
        return self._iconPath or self.defaultIconPath()

    def defaultIconPath(self):
        """
        Return the default icon path.

        :rtype: str 
        """
        return studiolibrary.resource.get("icons", "folder.svg")

    def setIconPath(self, path):
        """
        Return the icon path for the item.

        :type path: str
        :rtype: None 
        """
        self._iconPath = path
        self.updateIcon()

    def setIconVisible(self, visible):
        """
        Set the icon visibility for the folder item

        :type visible: bool
        """
        self._iconVisible = visible

    def isIconVisible(self):
        """
        Check if the icon is visible.

        :rtype: bool
        """
        return self.treeWidget().iconsVisible() and self._iconVisible

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
        
        :type color: QtGui.QColor or str
        :rtype: None 
        """
        if color:

            if isinstance(color, QtGui.QColor):
                color = studioqt.Color.fromColor(color)

            elif isinstance(color, six.string_types):
                color = studioqt.Color.fromString(color)

            self._iconColor = color.toString()
        else:
            self._iconColor = None

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

        :rtype: list[SidebarWidgetItem]
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
        if self.isIconVisible():
            if self.isExpanded():
                path = self.expandedIconPath()
            else:
                path = self.collapsedIconPath()

            pixmap = self.createPixmap(path, self.iconColor())

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
        
        :type color: QtGui.QColor or str
        :rtype: None 
        """
        if isinstance(color, QtGui.QColor):
            color = studioqt.Color.fromColor(color)

        elif isinstance(color, six.string_types):
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
            settings["selected"] = isSelected

        isExpanded = self.isExpanded()
        if isExpanded:
            settings["expanded"] = isExpanded

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
        text = settings.get("text")
        if text:
            self.setText(0, text)

        iconPath = settings.get("icon")
        if iconPath is not None:
            self.setIconPath(iconPath)

        iconColor = settings.get("color")
        if iconColor is not None:
            self.setIconColor(iconColor)

        selected = settings.get("selected")
        if selected is not None:
            self.setSelected(selected)

        expanded = settings.get("expanded")
        if expanded is not None and self.childCount() > 0:
            self.setExpanded(expanded)
            self.updateIcon()

        bold = settings.get("bold")
        if bold is not None:
            self.setBold(bold)

        textColor = settings.get("textColor")
        if textColor:
            self.setTextColor(textColor)
