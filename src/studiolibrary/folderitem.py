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

    SyncOrder = 100
    MenuOrder = 0
    EnableNestedItems = True

    Name = "Folder"
    IconPath = studiolibrary.resource.get("icons/folder.png")
    TypeIconPath = ""
    LoadWidgetClass = studiolibrary.widgets.PreviewWidget
    DefaultThumbnailPath = studiolibrary.resource.get("icons/folder_item.png")
    TrashIconPath = studiolibrary.resource.get("icons", "delete_96.png")

    DEFAULT_ICON_COLORS =[
                    "rgb(239, 112, 99)",
                    "rgb(239, 207, 103)",
                    "rgb(136, 200, 101)",
                    "rgb(111, 183, 239)",
                    "rgb(199, 142, 220)",
                    "rgb(200, 200, 200)",
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

    def contextEditMenu(self, menu, items=None):
        super(FolderItem, self).contextEditMenu(menu, items=items)

        action = studiolibrary.widgets.colorpicker.ColorPickerAction(menu)

        action.picker().setColors(self.DEFAULT_ICON_COLORS)
        action.picker().colorChanged.connect(self.setIconColor)
        action.picker().setCurrentColor(self.iconColor())
        action.picker().menuButton().hide()

        menu.addAction(action)

    def iconColor(self):
        """
        Get the icon color for the folder.

        :rtype: str
        """
        return self.readMetadata().get("color", "")

    def setIconColor(self, color):
        """
        Set the icon color for the folder.

        :type color: str
        """
        if color == "rgb(200, 200, 200)":
            color = ""

        self.saveMetadata({"color": color})
        self.syncItemData(emitDataChanged=False)

        if self.libraryWindow():
            self.libraryWindow().setFolderSettings(self.path(), self.itemData())
            self.updateIcon()

    def loadValidator(self, **kwargs):
        """
        The validator used for validating the load arguments.

        :type kwargs: dict
        """
        if kwargs.get("fieldChanged") == "color":
            self.setIconColor(kwargs.get("color"))

    def thumbnailIcon(self):
        """
        Overriding this method add support for dynamic icon colors.

        :rtype: QtGui.QIcon
        """
        path = studiolibrary.resource.get("icons/folder_item.png")
        icon = studioqt.Icon(path)

        if self.iconColor():
            color = studioqt.Color.fromString(self.iconColor())
            icon.setColor(color)

        return icon

    def loadSchema(self):
        """
        Get the info to display to user.
        
        :rtype: list[dict]
        """
        created = os.stat(self.path()).st_ctime
        created = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M %p")

        modified = os.stat(self.path()).st_mtime
        modified = datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M %p")

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
                "colors": self.DEFAULT_ICON_COLORS,
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

    def createItemData(self):

        data = self.readMetadata()

        data.update(super(FolderItem, self).createItemData())
        data["type"] = "Folder"

        return data

    def itemData(self):
        """Overriding this method to set the trash icon"""
        data = super(FolderItem, self).itemData()

        if data.get("path", "").endswith("Trash"):
            data["iconPath"] = self.TrashIconPath

        return data

    def doubleClicked(self):
        """Overriding this method to show the items contained in the folder."""
        self.libraryWindow().selectFolderPath(self.path())

    def save(self, *args, **kwargs):
        """Adding this method to avoid NotImpementedError."""
        pass


studiolibrary.registerItem(FolderItem)
