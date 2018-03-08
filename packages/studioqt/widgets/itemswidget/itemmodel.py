# Copyright 2017 by Kurt Rathjen. All Rights Reserved.
#
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


from studioqt import QtCore

import studioqt


class ItemModel(QtCore.QObject):

    ColumnLabels = ["icon", "name", "path"]
    GroupByLabels = []

    def __init__(self, *args):
        QtCore.QObject.__init__(self, *args)

    def sortItems(self, items, sortKey, sortOrder):
        """
        Sort the given items by the given sort key.

        :type items: list[studioqt.Item]
        :type sortKey: str
        :type sortOrder: int or None

        :rtype: list[studioqt.Item]
        """
        isCustomOrder = sortKey == "Custom Order"
        if isCustomOrder and sortOrder != QtCore.Qt.AscendingOrder:
            sortOrder = QtCore.Qt.AscendingOrder

        sortReverse = sortOrder == QtCore.Qt.DescendingOrder

        def _sortKey(item):
            return item.sortText(sortKey).lower()

        items = sorted(items, key=_sortKey, reverse=sortReverse)

        return items

    def groupItems(self, items, groupKey, groupOrder):
        """
        Group the given items by the given group key.

        :type items: list[studioqt.Item]
        :type groupKey: str
        :type groupOrder: int or None

        :rtype: list[studioqt.Item]
        """
        groupReverse = groupOrder == QtCore.Qt.DescendingOrder

        groups = {}
        sortKeys = []

        if groupKey:

            # Group the items into a dictionary
            for item in items:

                groupText = item.displayText(groupKey)

                if groupText not in groups:
                    sortText = item.sortText(groupKey)

                    groups[groupText] = []
                    sortKeys.append((sortText, groupText))

                groups[groupText].append(item)

            # Sort the groups using the sort text and group text
            sortKeys = sorted(sortKeys, reverse=groupReverse)

            # Flatten the grouped items to a list of items
            items = []
            for sortText, groupText in sortKeys:

                groupItem = self.createGroupItem(groupText, None)

                items.append(groupItem)
                items.extend(groups.get(groupText))

        return items

    def createGroupItem(self, text, children):
        """
        Create a new group item for the given text and children.

        :type text: str
        :type children: list[studioqt.Item]
        :rtype: studioqt.ItemGroup
        """
        groupItem = studioqt.ItemGroup()
        groupItem.setName(text)
        groupItem.setStretchToWidget(self.parent())
        groupItem.setChildren(children)
        return groupItem
