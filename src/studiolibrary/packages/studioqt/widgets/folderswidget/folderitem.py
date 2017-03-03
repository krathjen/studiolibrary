# Copyright 2016 by Kurt Rathjen. All Rights Reserved.
#
# Permission to use, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Kurt Rathjen
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# KURT RATHJEN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# KURT RATHJEN BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import logging

from studioqt import QtGui
from studioqt import QtWidgets

import studioqt


__all__ = ["Folder"]

logger = logging.getLogger(__name__)


class InvalidPathError(Exception):
    """
    """


class FolderItem(object):

    def __init__(self, path, treeWidget=None):
        """
        :type path: str
        """
        self._path = path
        self._pixmap = None
        self._orderIndex = -1
        self._settings = {}
        self._treeWidget = treeWidget

    def treeWidget(self):
        return self._treeWidget

    def setOrderIndex(self, orderIndex):
        """
        :type orderIndex: int
        """
        self._orderIndex = orderIndex

    def showInFolder(self):
        studioqt.showInFolder(self.path())

    def orderIndex(self):
        """
        :rtype:
        """
        return self._orderIndex

    def path(self):
        return self._path

    def exists(self):
        return os.path.exists(self.path())

    def dirname(self):
        return os.path.dirname(self.path())

    def rename(self, name):
        src = self.path()
        path = self.dirname() + "/" + name
        os.rename(src, path)
        self._path = path

    def settings(self):
        """
        :rtype: None
        """
        return self._settings

    def setSettings(self, settings):
        """
        :rtype: None
        """
        self._pixmap = None
        self._settings = settings

    def reset(self):
        self._pixmap = None
        self._settings = {}

    def setColor(self, color):
        """
        :type color: QtGui.QColor
        """
        if isinstance(color, QtGui.QColor):
            color = ('rgb(%d, %d, %d, %d)' % color.getRgb())

        self._settings["color"] = color
        self._pixmap = None

    def color(self):
        """
        :rtype: QtGui.QColor or None
        """
        color = self._settings.get("color", None)
        iconPath = self._settings.get("iconPath", None)

        if not color and not iconPath:
            color = self.treeWidget().palette().color(self.treeWidget().foregroundRole())
            color = studioqt.Color.fromColor(color).toString()

        return color

    def setIconVisible(self, value):
        """
        :type value: bool
        """
        self._settings["iconVisibility"] = value

    def isIconVisible(self):
        """
        :rtype: bool
        """
        return self._settings.get("iconVisibility", True)

    def setBold(self, value):
        """
        :type value: bool
        """
        self._settings["bold"] = value

    def isBold(self):
        """
        :rtype: bool
        """
        return self._settings.get("bold", False)

    def name(self):
        """
        :rtype: str
        """
        return os.path.basename(self.path())

    def isDefaultIcon(self):
        """
        :rtype: bool
        """
        return not self._settings.get("iconPath")

    def setIconPath(self, iconPath):
        """
        :type iconPath: str
        """
        self._pixmap = None
        self._settings['iconPath'] = iconPath

    def iconPath(self):
        """
        :rtype: str
        """
        iconPath = self._settings.get("iconPath", None)

        index = self.treeWidget().indexFromPath(self.path())
        expanded = self.treeWidget().isExpanded(index)

        if not iconPath:
            if "Trash" in self.name():
                iconPath = studioqt.resource().get("icons", "delete")
            elif expanded:
                iconPath = studioqt.resource().get("icons", "folder_open")
            else:
                iconPath = studioqt.resource().get("icons", "folder")

        return iconPath

    def setPixmap(self, pixmap):
        """
        :type pixmap: QtGui.QPixmap
        """
        self._pixmap = pixmap

    def pixmap(self):
        """
        :rtype: QtGui.QPixmap
        """
        if not self.isIconVisible():
            return studioqt.resource().pixmap("")

        color = self.color()
        iconPath = self.iconPath()

        self._pixmap = studioqt.Pixmap(iconPath)
        if color:
            self._pixmap.setColor(color)

        return self._pixmap
