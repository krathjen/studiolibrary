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
import logging

import studiolibrary

from studioqt import QtCore


__all__ = [
    "Library",
]

logger = logging.getLogger(__name__)


class Library(QtCore.QObject):

    ColumnLabels = [
        "icon",
        "name",
        "path",
        "type",
        "category",
        "folder",
        # "modified"
    ]

    SortLabels = [
        "name",
        "path",
        "type",
        "category",
        "folder",
        # "modified"
    ]

    GroupLabels = [
        "type",
        "category",
        # "modified",
    ]

    DatabasePath = "{path}/.studiolibrary/database.json"

    dataChanged = QtCore.Signal()

    def __init__(self, path, *args):
        QtCore.QObject.__init__(self, *args)

        self._path = None
        self._mtime = None
        self._data = {}
        self._items = []
        self._currentItems = []

        self.setPath(path)
        self.setDirty(True)

    def currentItems(self):
        """
        The items that are displayed in the view.
        
        :rtype: list[studiolibrary.LibraryItem]
        """
        return self._currentItems

    def recursiveDepth(self):
        """
        Return the recursive search depth.
        
        :rtype: int
        """
        return studiolibrary.config().get('recursiveSearchDepth')

    def path(self):
        """
        Return the disc location of the db.

        :rtype: str
        """
        return self._path

    def setPath(self, path):
        """
        Set the disc location of the db.

        :type path: str
        """
        self._path = path

    def databasePath(self):
        """
        Return the path to the database.
        
        :rtype: str 
        """
        return studiolibrary.formatPath(self.DatabasePath, path=self.path())

    def mtime(self):
        """
        Return when the database was last modified.

        :rtype: float or None
        """
        path = self.databasePath()
        mtime = None

        if os.path.exists(path):
            mtime = os.path.getmtime(path)

        return mtime

    def setDirty(self, value):
        """
        Update the model object with the current database timestamp.

        :type: bool
        """
        if value:
            self._mtime = None
        else:
            self._mtime = self.mtime()

    def isDirty(self):
        """
        Return True if the database has changed on disc.

        :rtype: bool
        """
        return not self._items or self._mtime != self.mtime()

    def read(self):
        """
        Read the database from disc and return a dict object.

        :rtype: dict
        """
        if self.isDirty():
            self._data = studiolibrary.readJson(self.databasePath())
            self.setDirty(False)

        return self._data

    def save(self, data):
        """
        Write the given dict object to the database on disc.

        :type data: dict
        :rtype: None
        """
        studiolibrary.saveJson(self.databasePath(), data)

    def sync(self):
        """
        Sync the file system with the database. 
        
        :rtype: None 
        """
        data = self.read()

        isDirty = False

        for path in data.keys():
            if not os.path.exists(path):
                isDirty = True
                del data[path]

        depth = self.recursiveDepth()
        items = studiolibrary.findItems(
            self.path(),
            depth=depth,
        )

        for item in items:
            path = item.path()
            if item.path() not in data:
                isDirty = True
                data[path] = {}

        if isDirty:
            self.save(data)
            self.dataChanged.emit()

    def findItems(self, queries, libraryWidget=None):
        """
        Get the items that match the given queries.
        
        Examples:
            
            queries = [
                {
                    'operator': 'or',
                    'filters': [
                        ('folder', 'is' '/library/proj/test'),
                        ('folder', 'startswith', '/library/proj/test'),
                    ]
                },
                {
                    'operator': 'and',
                    'filters': [
                        ('path', 'contains' 'test'),
                        ('path', 'contains', 'run'),
                    ]
                }
            ]
            
            print(library.find(queries))
            
        :type queries: list[dict]
        :type libraryWidget: studiolibrary.LibraryWIdget or None
            
        :rtype: list[studiolibrary.LibraryItem]
        """
        items = self.createItems(libraryWidget=libraryWidget)

        self._currentItems = []

        for item in items:

            matches = []

            for query in queries:

                filters = query.get('filters')
                operator = query.get('operator', 'and')

                if not filters:
                    continue

                match = False

                for key, cond, text in filters:

                    text = text.lower()
                    itemText = item.text(key).lower()

                    if cond == 'contains':
                        match = text in itemText

                    elif cond == 'is':
                        match = text == itemText

                    elif cond == 'startswith':
                        match = itemText.startswith(text)

                    if operator == 'or' and match:
                        break

                    if operator == 'and' and not match:
                        break

                matches.append(match)

            if all(matches):
                self._currentItems.append(item)

        return self._currentItems

    def addItem(self, item, data=None):
        """
        Add the given item to the database.    
    
        :type item: studiolibrary.LibraryItem
        :type data: dict or None
        :rtype: None 
        """
        self.addItems([item], data)

    def addItems(self, items, data=None):
        """
        Add the given items to the database.
        
        :type items: list[studiolibrary.LibraryItem]
        :type data: dict or None
        :rtype: None 
        """
        logger.info("Add items %s", items)

        paths = [item.path() for item in items]

        isDirty = self.isDirty()

        self.addPaths(paths, data)

        self.setDirty(isDirty)

        self._items.extend(items)

        self.dataChanged.emit()

    def createItems(self, libraryWidget=None):
        """
        Create all the items for the model.

        :rtype: list[studiolibrary.LibraryItem] 
        """
        # Check if the database has changed since the last read call
        if self.isDirty():

            paths = self.read().keys()
            items = studiolibrary.itemsFromPaths(
                paths,
                library=self,
                libraryWidget=libraryWidget
            )

            self._items = list(items)
            self.loadItemData(self._items)

        return self._items

    def saveItemData(self, items, columns=None):
        """
        Save the item data to the database for the given items and columns.

        :type columns: list[str]
        :type items: list[studiolibrary.LibraryItem]
        """
        data = {}
        columns = columns or ["Custom Order"]

        for item in items:
            path = item.path()
            data.setdefault(path, {})

            for column in columns:
                value = item.text(column)
                data[path].setdefault(column, value)

        studiolibrary.updateJson(self.databasePath(), data)

    def loadItemData(self, items):
        """
        Load the item data from the database to the given items.

        :type items: list[studiolibrary.LibraryItem]
        :rtype: None
        """
        data = self.read()

        for item in items:
            key = item.id()
            if key in data:
                item.setItemData(data[key])

    def addPaths(self, paths, data=None):
        """
        Add the given path and the given data to the database.    
    
        :type paths: list[str]
        :type data: dict or None
        :rtype: None 
        """
        data = data or {}
        self.updatePaths(paths, data)

    def updatePaths(self, paths, data):
        """
        Update the given paths with the given data in the database.

        :type paths: list[str]
        :type data: dict
        :rtype: None
        """
        data_ = self.read()
        paths = studiolibrary.normPaths(paths)

        for path in paths:
            if path in data_:
                data_[path].update(data)
            else:
                data_[path] = data

        self.save(data_)

    def copyPath(self, src, dst):
        """
        Copy the given source path to the given destination path.

        :type src: str
        :type dst: str
        :rtype: str
        """
        self.addPaths([dst])
        return dst

    def renamePath(self, src, dst):
        """
        Rename the source path to the given name.

        :type src: str
        :type dst: str
        :rtype: str
        """
        studiolibrary.renamePathInFile(self.databasePath(), src, dst)
        return dst

    def removePath(self, path):
        """
        Remove the given path from the database.

        :type path: str
        :rtype: None
        """
        self.removePaths([path])

    def removePaths(self, paths):
        """
        Remove the given paths from the database.

        :type paths: list[str]
        :rtype: None
        """
        data = self.read()

        paths = studiolibrary.normPaths(paths)

        for path in paths:
            if path in data:
                del data[path]

        self.save(data)
