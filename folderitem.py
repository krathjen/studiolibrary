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

import studiolibrary

import studioqt
from studioqt import QtWidgets


class FolderItem(studiolibrary.LibraryItem):

    RegisterOrder = 100
    EnableNestedItems = True
    DisplayInSidebar = True

    MenuName = "Folder"
    MenuOrder = 1
    MenuIconPath = studiolibrary.resource().get("icons/folder.png")
    ThumbnailPath = studiolibrary.resource().get("icons/folder_item.png")

    @classmethod
    def match(cls, path):
        """
        Return True if the given path is supported by the item.

        :type path: str 
        :rtype: bool 
        """
        if os.path.isdir(path):
            return True

    @classmethod
    def showCreateWidget(cls, libraryWidget):
        """
        Show the dialog for creating a new folder.

        :rtype: None
        """
        path = libraryWidget.selectedFolderPath() or libraryWidget.path()

        name, button = studioqt.MessageBox.input(
            libraryWidget,
            "Create folder",
            "Create a new folder with the name:",
        )

        name = name.strip()

        if name and button == QtWidgets.QDialogButtonBox.Ok:
            path = os.path.join(path, name)

            item = cls(path, libraryWidget=libraryWidget)
            item.save()

    def updatePathData(self):
        """Overriding this method to force the item type to Folder"""
        super(FolderItem, self).updatePathData()
        self.setText("type", "Folder")

    def doubleClicked(self):
        """Overriding this method to show the items contained in the folder."""
        self.libraryWidget().selectFolderPath(self.path())

    def save(self, *args, **kwargs):
        """
        Create a new folder on disc at the given path.

        :rtype: str
        """
        super(FolderItem, self).save(*args, **kwargs)

        if self.libraryWidget():
            self.libraryWidget().selectFolderPath(self.path())


studiolibrary.registerItem(FolderItem)
