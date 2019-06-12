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

import studiolibrary
import studiolibrary.widgets

from studioqt import QtWidgets


class FolderItem(studiolibrary.LibraryItem):

    RegisterOrder = 100
    EnableNestedItems = True
    DisplayInSidebar = True

    MenuName = "Folder"
    MenuOrder = 1
    MenuIconPath = studiolibrary.resource().get("icons/folder.png")
    PreviewWidgetClass = studiolibrary.widgets.PreviewWidget
    DefaultThumbnailPath = studiolibrary.resource().get("icons/folder_item.png")
    TrashIconPath = studiolibrary.resource().get("icons", "delete_96.png")

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

    def info(self):
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
            }
        ]

    @classmethod
    def showCreateWidget(cls, libraryWindow):
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
            item.save(path)

            if libraryWindow:
                libraryWindow.refresh()
                libraryWindow.selectFolderPath(path)

    def createItemData(self):
        """Overriding this method to force the item type to Folder"""
        itemData = super(FolderItem, self).createItemData()
        itemData["type"] = "Folder"
        return itemData

    def itemData(self):
        """Overriding this method to set the trash icon"""
        data = super(FolderItem, self).itemData()

        if data.get("path", "").endswith("Trash"):
            data["iconPath"] = self.TrashIconPath

        return data

    def doubleClicked(self):
        """Overriding this method to show the items contained in the folder."""
        self.libraryWindow().selectFolderPath(self.path())

    def write(self, *args, **kwargs):
        """Adding this method to avoid NotImpementedError."""
        pass


studiolibrary.registerItem(FolderItem)
