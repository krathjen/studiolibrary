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

import os
from datetime import datetime

from studiovendor.Qt import QtWidgets

import studioqt
import studiolibrary
import studiolibrary.widgets


class FolderItem(studiolibrary.LibraryItem):

    NAME = "Folder"

    MENU_ORDER = 0  # Show at the top of the menu
    SYNC_ORDER = 100  # Last item to run when syncing

    LOAD_WIDGET_CLASS = studiolibrary.widgets.PreviewWidget
    ENABLE_NESTED_ITEMS = True

    ICON_PATH = studiolibrary.resource.get("icons", "folder.svg")
    TYPE_ICON_PATH = ""  # Don't show a type icon for the folder item
    TRASH_ICON_PATH = studiolibrary.resource.get("icons", "trash.svg")
    THUMBNAIL_PATH = studiolibrary.resource.get("icons", "folder_item.png")

    DEFAULT_ICON_COLOR = "rgb(220,220,220)"

    DEFAULT_ICON_COLORS = [
        "rgb(239, 112, 99)",
        "rgb(239, 207, 103)",
        "rgb(136, 200, 101)",
        "rgb(111, 183, 239)",
        "rgb(199, 142, 220)",
        DEFAULT_ICON_COLOR,
    ]

    DEFAULT_ICONS = [
        "folder.svg",
        "user.svg",
        "character.svg",
        "users.svg",
        "inbox.svg",
        "favorite.svg",
        "shot.svg",
        "asset.svg",
        "assets.svg",
        "cloud.svg",
        "book.svg",
        "archive.svg",
        "circle.svg",
        "share.svg",
        "tree.svg",
        "environment.svg",
        "vehicle.svg",
        "trash.svg",
        "layers.svg",
        "database.svg",
        "video.svg",
        "face.svg",
        "hand.svg",
        "globe.svg",
    ]

    @classmethod
    def match(cls, path):
        """
        Return True if the given path is supported by the item.

        :type path: str 
        :rtype: bool 
        """
        if os.path.isdir(path):
            return True

    def createOverwriteMenu(self, menu):
        """
        Overwriting this method to ignore/hide the overwrite menu action.

        :type menu: QtWidgets.QMenu
        """
        pass

    def _showPreviewFromMenu(self):

        self.libraryWindow().itemsWidget().clearSelection()
        self.showPreviewWidget(self.libraryWindow())

    def contextEditMenu(self, menu, items=None):
        super(FolderItem, self).contextEditMenu(menu, items=items)

        action = QtWidgets.QAction("Show in Preview", menu)

        action.triggered.connect(self._showPreviewFromMenu)
        menu.addAction(action)

        action = studiolibrary.widgets.colorpicker.ColorPickerAction(menu)

        action.picker().setColors(self.DEFAULT_ICON_COLORS)
        action.picker().colorChanged.connect(self.setIconColor)
        action.picker().setCurrentColor(self.iconColor())
        action.picker().menuButton().hide()
        menu.addAction(action)

        iconName = self.readMetadata().get("icon", "")

        action = studiolibrary.widgets.iconpicker.IconPickerAction(menu)

        action.picker().setIcons(self.DEFAULT_ICONS)
        action.picker().setCurrentIcon(iconName)
        action.picker().iconChanged.connect(self.setCustomIcon)
        action.picker().menuButton().hide()

        menu.addAction(action)

    def iconColor(self):
        """
        Get the icon color for the folder item.

        :rtype: str
        """
        return self.readMetadata().get("color", "")

    def setIconColor(self, color):
        """
        Set the icon color for the folder item.

        :type color: str
        """
        if color == self.DEFAULT_ICON_COLOR:
            color = ""

        self.updateMetadata({"color": color})

    def customIconPath(self):
        """
        Get the icon for the folder item.

        :rtype: str
        """
        return self.readMetadata().get("icon", "")

    def setCustomIcon(self, name):
        """
        Set the icon for the folder item.

        :type name: str
        """
        if name == "folder.svg":
            name = ""

        self.updateMetadata({"icon": name})

    def thumbnailIcon(self):
        """
        Overriding this method add support for dynamic icon colors.

        :rtype: QtGui.QIcon
        """
        iconPath = self.customIconPath()

        if iconPath and "/" not in iconPath and "\\" not in iconPath:
            iconPath = studiolibrary.resource.get("icons", iconPath)

        if not iconPath or not os.path.exists(iconPath):
            iconPath = self.THUMBNAIL_PATH

        icon = studioqt.Icon(iconPath)
        color = self.iconColor()

        # We use the default color for SVG files
        if not color and iconPath.endswith(".svg"):
            color = self.DEFAULT_ICON_COLOR

        if color:
            color = studioqt.Color.fromString(color)
            icon.setColor(color)

        return icon

    def loadValidator(self, **kwargs):
        """
        The validator used for validating the load arguments.

        :type kwargs: dict
        """
        if kwargs.get("fieldChanged") == "color":
            self.setIconColor(kwargs.get("color"))

        if kwargs.get("fieldChanged") == "icon":
            self.setCustomIcon(kwargs.get("icon"))

    def loadSchema(self):
        """
        Get the info to display to user.
        
        :rtype: list[dict]
        """
        created = os.stat(self.path()).st_ctime
        created = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M %p")

        modified = os.stat(self.path()).st_mtime
        modified = datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M %p")

        iconName = self.readMetadata().get("icon", "")

        return [
            {
                "name": "infoGroup",
                "title": "Info",
                "value": True,
                "type": "group",
                "persistent": True,
                "persistentKey": "BaseItem",
            },
            {
                "name": "name",
                "value": self.name()
            },
            {
                "name": "path",
                "value": self.path()
            },
            {
                "name": "created",
                "value":  created,
            },
            {
                "name": "modified",
                "value": modified,
            },
            {
                "name": "optionsGroup",
                "title": "options",
                "type": "group",
            },

            {
                "name": "color",
                "type": "color",
                "value": self.iconColor(),
                "layout": "vertical",
                "label": {"visible": False},
                "colors": self.DEFAULT_ICON_COLORS,
            },

            {
                "name": "icon",
                "type": "iconPicker",
                "value": iconName,
                "layout": "vertical",
                "label": {"visible": False},
                "items": self.DEFAULT_ICONS,
            }
        ]

    @classmethod
    def showSaveWidget(cls, libraryWindow):
        """
        Show the dialog for creating a new folder.

        :rtype: None
        """
        path = libraryWindow.selectedFolderPath() or libraryWindow.path()

        name, button = studiolibrary.widgets.MessageBox.input(
            libraryWindow,
            "Create folder",
            "Create a new folder with the name:",
        )

        name = name.strip()

        if name and button == QtWidgets.QDialogButtonBox.Ok:
            path = os.path.join(path, name)

            item = cls(path, libraryWindow=libraryWindow)
            item.safeSave()

            if libraryWindow:
                libraryWindow.refresh()
                libraryWindow.selectFolderPath(path)

    def updateMetadata(self, metadata):
        super(FolderItem, self).updateMetadata(metadata)

        if self.libraryWindow():
            self.libraryWindow().setFolderSettings(self.path(), self.itemData())
            self.updateIcon()

    def createItemData(self):

        data = self.readMetadata()
        data.update(super(FolderItem, self).createItemData())
        data["type"] = "Folder"

        return data

    def itemData(self):
        """Overriding this method to set the trash icon"""
        data = super(FolderItem, self).itemData()

        if data.get("path", "").endswith("Trash"):
            data["icon"] = self.TRASH_ICON_PATH

        return data

    def doubleClicked(self):
        """Overriding this method to show the items contained in the folder."""
        self.libraryWindow().selectFolderPath(self.path())

    def save(self, *args, **kwargs):
        """Adding this method to avoid NotImpementedError."""
        pass
