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

import shutil
import mutils

import studiolibrary
import studiolibrarymaya

from studiolibrarymaya import baseitem


iconPath = studiolibrarymaya.resource().get("icons", "selectionSet.png")


class SetsItem(baseitem.BaseItem):

    Extensions = [".set"]
    Extension = ".set"
    MenuName = "Selection Set"
    MenuIconPath = iconPath
    TypeIconPath = iconPath

    def __init__(self, *args, **kwargs):
        """
        :rtype: None
        """
        super(SetsItem, self).__init__(*args, **kwargs)

        self.setTransferBasename("set.json")
        self.setTransferClass(mutils.SelectionSet)

    def loadFromCurrentOptions(self):
        """Load the selection set using the settings for this item."""
        namespaces = self.namespaces()
        self.load(namespaces=namespaces)

    def load(self, namespaces=None):
        """
        :type namespaces: list[str] | None
        """
        self.selectContent(namespaces=namespaces)

    def write(self, path, objects, iconPath="", **options):
        """
        Write all the given object data to the given path on disc.

        :type path: str
        :type objects: list[str]
        :type iconPath: str
        :type options: dict
        """
        super(SetsItem, self).write(path, objects, iconPath, **options)

        # Save the selection set to the given path
        mutils.saveSelectionSet(
            path + "/set.json",
            objects,
            metadata={"description": options.get("comment", "")}
        )


# Register the selection set item to the Studio Library
studiolibrary.registerItem(SetsItem)
