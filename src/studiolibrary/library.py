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
import time
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

    dataChanged = QtCore.Signal()
    searchStarted = QtCore.Signal()
    searchFinished = QtCore.Signal()

    def __init__(self, path=None, libraryWidget=None, *args):
        QtCore.QObject.__init__(self, *args)

        self._path = path
        self._mtime = None
        self._data = {}
        self._items = []
        self._results = []
        self._queries = []
        self._currentItems = []
        self._libraryWidget = libraryWidget

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
        formatString = studiolibrary.config().get('databasePath')
        return studiolibrary.formatPath(formatString, path=self.path())

    def distinct(self, field, sortBy=None):
        """
        Get all the values for the given field.
        
        :type field: str
        :type sortBy: None or list[str]
        :rtype: list 
        """
        # sortBy = sortBy or [field]

        data = self._results
        # data = self.sortedData(data, sortBy=sortBy)

        values = []

        for item in data:
            value = item.get(field)
            if value:
                values.append(value)

        return list(set(values))

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
        if self.isDirty() and self.path():
            self._data = studiolibrary.readJson(self.databasePath())
            self.setDirty(False)
        else:
            logger.info('No path set for reading the data from disc.')

        return self._data

    def save(self, data):
        """
        Write the given dict object to the database on disc.

        :type data: dict
        :rtype: None
        """
        if self.path():
            studiolibrary.saveJson(self.databasePath(), data)
            self.setDirty(True)
        else:
            logger.info('No path set for saving the data to disc.')

    def sync(self):
        """Sync the file system with the database."""
        if not self.path():
            logger.info('No path set for syncing data')
            return

        data = self.read()

        for path in data.keys():
            if not os.path.exists(path):
                del data[path]

        depth = self.recursiveDepth()
        items = studiolibrary.findItems(
            self.path(),
            depth=depth,
        )

        for item in items:
            path = item.path()

            itemData = data.get(path, {})
            itemData.update(item.itemData())

            data[path] = itemData

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

        logger.debug("Queries")
        for query in queries:
            logger.debug(query)

        for item in items:
            match = self.match(item.itemData(), queries)
            if match:
                self._currentItems.append(item)

        return self._currentItems

    def addQuery(self, query):
        """
        Add the given query to the dataset.
        
        Examples:
            addQuery({
                'operator': 'or',
                'filters': [
                    ('folder', 'is' '/library/proj/test'),
                    ('folder', 'startswith', '/library/proj/test'),
                ]
            })
        
        :type query: dict
        """
        if query.get('name'):
            for i, query_ in enumerate(self._queries):
                if query_.get('name') == query.get('name'):
                    self._queries[i] = query

        if query not in self._queries:
            self._queries.append(query)

    def search(self):
        """Run a search using the queries added to this dataset."""
        t = time.time()
        results = []

        self.searchStarted.emit()

        logger.debug('Search queries: %s', self._queries)

        items = self.createItems(libraryWidget=self._libraryWidget)
        for item in items:
            match = self.match(item.itemData(), self._queries)
            if match:
                results.append(item)

        self._results = results

        self.searchFinished.emit()
        logger.debug('Search took: %s', time.time()-t)

    def updateItem(self, item):
        """
        Update the given item in the database.    
    
        :type item: studiolibrary.LibraryItem
        :rtype: None 
        """
        self.addItems([item])

    def addItem(self, item):
        """
        Add the given item to the database.    
    
        :type item: studiolibrary.LibraryItem
        :rtype: None 
        """
        self.addItems([item])

    def addItems(self, items):
        """
        Add the given items to the database.
        
        :type items: list[studiolibrary.LibraryItem]
        """
        logger.info("Add items %s", items)

        data_ = self.read()

        for item in items:
            path = item.path()
            data = item.itemData()
            data_.setdefault(path, {})
            data_[path].update(data)

        self.save(data_)

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

    def saveItemData(self, items):
        """
        Save the item data to the database for the given items and columns.

        :type items: list[studiolibrary.LibraryItem]
        """
        data = {}

        for item in items:
            path = item.path()
            itemData = item.itemData()

            data.setdefault(path, itemData)

        if self.path():
            studiolibrary.updateJson(self.databasePath(), data)
        else:
            logger.info('No path set for updating the data on disc.')

    def loadItemData(self, items):
        """
        Load the item data from the database to the given items.

        :type items: list[studiolibrary.LibraryItem]
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
        self.setDirty(True)
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

    @staticmethod
    def match(data, queries):
        """
        Match the given data with the given queries.
        
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
        """
        matches = []

        for query in queries:

            filters = query.get('filters')
            operator = query.get('operator', 'and')

            if not filters:
                continue

            match = False

            for key, cond, value in filters:

                if key == '*':
                    itemValue = unicode(data)
                else:
                    itemValue = data.get(key)

                if isinstance(value, basestring):
                    value = value.lower()

                if isinstance(itemValue, basestring):
                    itemValue = itemValue.lower()

                if not itemValue:
                    match = False

                elif cond == 'contains':
                    match = value in itemValue

                elif cond == 'not_contains':
                    match = value not in itemValue

                elif cond == 'is':
                    match = value == itemValue

                elif cond == 'startswith':
                    match = itemValue.startswith(value)

                if operator == 'or' and match:
                    break

                if operator == 'and' and not match:
                    break

            matches.append(match)

        return all(matches)

    @staticmethod
    def sorted(data, sortBy):
        """
        Return the given data sorted using the sortBy argument.
        
        Example:
            data = [
                {'name':'red', 'index':1},
                {'name':'green', 'index':2},
                {'name':'blue', 'index':3},
            ]
            
            sortBy = ['index:asc', 'name']
            # sortBy = ['index:dsc', 'name']
            
            print(sortedData(data, sortBy))
            
        :type data: list[dict]
        :type sortBy: list[str]
        :rtype: list[dict]
        """
        for field in reversed(sortBy):

            tokens = field.split(':')

            reverse = False
            if len(tokens) > 1:
                field = tokens[0]
                reverse = tokens[1] != 'asc'

            def sortKey(_data):

                default = False if reverse else ''

                return _data.get(field, default)

            data = sorted(data, key=sortKey, reverse=reverse)

        return data


def testsuite():

    data = [
        {'name': 'blue', 'index': 3},
        {'name': 'red', 'index': 1},
        {'name': 'green', 'index': 2},
    ]

    sortBy = ['index:asc', 'name']
    data2 = (Library.sortedData(data, sortBy))

    assert(data2[0].get('index') == 1)
    assert(data2[1].get('index') == 2)
    assert(data2[2].get('index') == 3)

    sortBy = ['index:dsc', 'name']
    data3 = (Library.sortedData(data, sortBy))

    assert(data3[0].get('index') == 3)
    assert(data3[1].get('index') == 2)
    assert(data3[2].get('index') == 1)

    data = {'name': 'blue', 'index': 3}
    queries = [{'filters': [('name', 'is', 'blue')]}]
    assert Library.match(data, queries)

    data = {'name': 'red', 'index': 3}
    queries = [{'filters': [('name', 'is', 'blue')]}]
    assert not Library.match(data, queries)

    data = {'name': 'red', 'index': 3}
    queries = [{'filters': [('name', 'startswith', 're')]}]
    assert Library.match(data, queries)

    data = {'name': 'red', 'index': 3}
    queries = [{'filters': [('name', 'startswith', 'ed')]}]
    assert not Library.match(data, queries)

    data = {'name': 'red', 'index': 3}
    queries = [{
        'operator': 'or',
        'filters': [('name', 'is', 'pink'), ('name', 'is', 'red')]
    }]
    assert Library.match(data, queries)

    data = {'name': 'red', 'index': 3}
    queries = [{
        'operator': 'and',
        'filters': [('name', 'is', 'pink'), ('name', 'is', 'red')]
    }]
    assert not Library.match(data, queries)

    data = {'name': 'red', 'index': 3}
    queries = [{
        'operator': 'and',
        'filters': [('name', 'is', 'red'), ('index', 'is', 3)]
    }]
    assert Library.match(data, queries)

    data = {'name': 'red', 'index': 3}
    queries = [{
        'operator': 'and',
        'filters': [('name', 'is', 'red'), ('index', 'is', '3')]
    }]
    assert not Library.match(data, queries)


if __name__ == "__main__":
    testsuite()
