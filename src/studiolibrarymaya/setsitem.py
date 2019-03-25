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

import mutils

import studiolibrary
import studiolibrarymaya

from studiolibrarymaya import baseitem


iconPath = studiolibrarymaya.resource().get("icons", "selectionSet.png")


class SetsItem(baseitem.BaseItem):

    Extensions = [".set"]
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

    def save(self, objects, path="", iconPath="", **options):
        """
        Save all the given object data to the given path on disc.

        :type objects: list[str]
        :type path: str
        :type iconPath: str
        :type options: dict
        """
        if path and not path.endswith(".set"):
            path += ".set"

        # Mapping new option names to legacy names for now
        metadata = {"description": options.get("comment", "")}

        # Remove and create a new temp directory
        tempPath = mutils.createTempPath() + "/" + self.transferBasename()

        # Save the selection set to the temp location
        mutils.saveSelectionSet(
            tempPath,
            objects,
            metadata=metadata
        )

        # Move the selection set to the given path using the base class
        super(SetsItem, self).save(path, contents=[tempPath, iconPath])


# Register the selection set item to the Studio Library
studiolibrary.registerItem(SetsItem)
