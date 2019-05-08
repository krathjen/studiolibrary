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
import copy
import time
import logging
import collections

import studiolibrary

from studioqt import QtCore


__all__ = [
    "Library",
]

logger = logging.getLogger(__name__)


class Library(QtCore.QObject):

    Fields = [
        "icon",
        "name",
        "path",
        "type",
        "folder",
        "category",
        # "modified"
    ]

    SortFields = [
        "name",
        "path",
        "type",
        "folder",
        "category",
        "Custom Order",  # legacy case
        # "modified"
    ]

    GroupFields = [
        "type",
        "category",
        # "modified",
    ]

    dataChanged = QtCore.Signal()
    searchStarted = QtCore.Signal()
    searchFinished = QtCore.Signal()
    searchTimeFinished = QtCore.Signal()

    def __init__(self, path=None, libraryWindow=None, *args):
        QtCore.QObject.__init__(self, *args)

        self._path = path
        self._mtime = None
        self._data = {}
        self._items = []
        self._fields = []
        self._sortBy = []
        self._groupBy = []
        self._results = []
        self._queries = {}
        self._globalQueries = {}
        self._groupedResults = {}
        self._searchTime = 0
        self._searchEnabled = True
        self._libraryWindow = libraryWindow

        self.setPath(path)
        self.setDirty(True)

    def sortBy(self):
        """
        Get the list of fields to sort by.
        
        :rtype: list[str] 
        """
        return self._sortBy

    def setSortBy(self, fields):
        """
        Set the list of fields to group by.
        
        Example:
            library.setSortBy(["name:asc", "type:asc"])
        
        :type fields: list[str] 
        """
        self._sortBy = fields

    def groupBy(self):
        """
        Get the list of fields to group by.
        
        :rtype: list[str] 
        """
        return self._groupBy

    def setGroupBy(self, fields):
        """
        Set the list of fields to group by.
        
        Example:
            library.setGroupBy(["name:asc", "type:asc"])
        
        :type fields: list[str] 
        """
        self._groupBy = fields

    def settings(self):
        """
        Get the settings for the dataset.
        
        :rtype: dict 
        """
        return {
            "sortBy": self.sortBy(),
            "groupBy": self.groupBy()
        }

    def setSettings(self, settings):
        """
        Set the settings for the dataset object.
        
        :type settings: dict
        """
        value = settings.get('sortBy')
        if value is not None:
            self.setSortBy(value)

        value = settings.get('groupBy')
        if value is not None:
            self.setGroupBy(value)

    def setSearchEnabled(self, enabled):
        """Enable or disable the search the for the library."""
        self._searchEnabled = enabled

    def isSearchEnabled(self):
        """Check if search is enabled for the library."""
        return self._searchEnabled

    def recursiveDepth(self):
        """
        Return the recursive search depth.
        
        :rtype: int
        """
        return studiolibrary.config().get('recursiveSearchDepth')

    def fields(self):
        """Return all the fields for the library."""
        return self._fields

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

    def distinct(self, field, queries=None, sortBy="name"):
        """
        Get all the values for the given field.
        
        :type field: str
        :type queries None or list[dict]
        :type sortBy: str
        :rtype: list 
        """
        results = {}
        queries = queries or []
        queries.extend(self._globalQueries.values())

        items = self.createItems()
        for item in items:
            value = item.itemData().get(field)
            if value:
                results.setdefault(value, {'count': 0, 'name': value})
                match = self.match(item.itemData(), queries)
                if match:
                    results[value]['count'] += 1

        def sortKey(facet):
            return facet.get(sortBy)

        return sorted(results.values(), key=sortKey)

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
        if self.path():
            if self.isDirty():
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

    def clear(self):
        """Clear all the item data."""
        self._items = []
        self._results = []
        self._groupedResults = {}
        self.dataChanged.emit()


    def sync(self, progressCallback=None):
        """Sync the file system with the database."""
        if not self.path():
            logger.info('No path set for syncing data')
            return

        if progressCallback:
            progressCallback("Syncing")

        data = self.read()

        for path in data.keys():
            if not os.path.exists(path):
                del data[path]

        depth = self.recursiveDepth()
        items = studiolibrary.findItems(
            self.path(),
            depth=depth,
        )

        items = list(items)
        count = len(items)

        for i, item in enumerate(items):
            percent = (float(i+1)/float(count))
            if progressCallback:
                percent *= 100
                label = "{0:.0f}%".format(percent)
                progressCallback(label, percent)

            path = item.path()

            itemData = data.get(path, {})
            itemData.update(item.createItemData())

            data[path] = itemData

        if progressCallback:
            progressCallback("Post Callbacks")

        self.postSync(data)

        if progressCallback:
            progressCallback("Saving Cache")

        self.save(data)

        self.dataChanged.emit()

    def postSync(self, data):
        """
        Use this function to execute code on the data after sync, but before save and dataChanged.emit

        :type data: dict
        :rtype: None
        """
        pass

    def createItems(self):
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
                libraryWindow=self._libraryWindow
            )

            self._items = list(items)
            self.loadItemData(self._items)

        return self._items

    def findItems(self, queries):
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
        :rtype: list[studiolibrary.LibraryItem]
        """
        fields = []
        results = []

        queries = copy.copy(queries)
        queries.extend(self._globalQueries.values())

        logger.debug("Search queries:")
        for query in queries:
            logger.debug('Query: %s', query)

        items = self.createItems()
        for item in items:
            match = self.match(item.itemData(), queries)
            if match:
                results.append(item)
            fields.extend(item.itemData().keys())

        self._fields = list(set(fields))

        if self.sortBy():
            results = self.sorted(results, self.sortBy())

        return results

    def queries(self, exclude=None):
        """
        Get all the queries for the dataset excluding the given ones.
        
        :type exclude: list[str] or None
        
        :rtype: list[dict] 
        """
        queries = []
        exclude = exclude or []

        for query in self._queries.values():
            if query.get('name') not in exclude:
                queries.append(query)

        return queries

    def addGlobalQuery(self, query):
        """
        Add a global query to library.
        
        :type query: dict 
        """
        self._globalQueries[query["name"]] = query

    def addQuery(self, query):
        """
        Add a search query to the library.
        
        Examples:
            addQuery({
                'name': 'My Query',
                'operator': 'or',
                'filters': [
                    ('folder', 'is' '/library/proj/test'),
                    ('folder', 'startswith', '/library/proj/test'),
                ]
            })
        
        :type query: dict
        """
        self._queries[query["name"]] = query

    def removeQuery(self, name):
        """
        Remove the query with the given name.
        
        :type name: str 
        """
        if name in self._queries:
            del self._queries[name]

    def queryExists(self, name):
        """
        Check if the given query name exists.
        
        :type name: str
        :rtype: bool 
        """
        return name in self._queries

    def search(self):
        """Run a search using the queries added to this dataset."""
        if not self.isSearchEnabled():
            logger.debug('Search is disabled')
            return

        t = time.time()

        logger.debug("Searching items")

        self.searchStarted.emit()

        self._results = self.findItems(self.queries())

        self._groupedResults = self.groupItems(self._results, self.groupBy())

        self.searchFinished.emit()

        self._searchTime = time.time() - t

        self.searchTimeFinished.emit()

        logger.debug('Search time: %s', self._searchTime)

    def results(self):
        """
        Return the items found after a search is ran.
        
        :rtype: list[Item] 
        """
        return self._results

    def groupedResults(self):
        """
        Get the results grouped after a search is ran.
        
        :rtype: dict
        """
        return self._groupedResults

    def searchTime(self):
        """
        Return the time taken to run a search.
        
        :rtype: float 
        """
        return self._searchTime

    def addItem(self, item):
        """
        Add the given item to the database.    
    
        :type item: studiolibrary.LibraryItem
        :rtype: None 
        """
        self.saveItemData([item])

    def addItems(self, items):
        """
        Add the given items to the database.
        
        :type items: list[studiolibrary.LibraryItem]
        """
        self.saveItemData(items)

    def updateItem(self, item):
        """
        Update the given item in the database.    
    
        :type item: studiolibrary.LibraryItem
        :rtype: None 
        """
        self.saveItemData([item])

    def saveItemData(self, items, emitDataChanged=True):
        """
        Add the given items to the database.

        :type items: list[studiolibrary.LibraryItem]
        :type emitDataChanged: bool
        """
        logger.debug("Save item data %s", items)

        data_ = self.read()

        for item in items:
            path = item.path()
            data = item.itemData()
            data_.setdefault(path, {})
            data_[path].update(data)

        self.save(data_)

        if emitDataChanged:
            self.search()
            self.dataChanged.emit()

    def loadItemData(self, items):
        """
        Load the item data from the database to the given items.

        :type items: list[studiolibrary.LibraryItem]
        """
        logger.debug("Loading item data %s", items)

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

                elif cond == 'not':
                    match = value != itemValue

                elif cond == 'startswith':
                    match = itemValue.startswith(value)

                if operator == 'or' and match:
                    break

                if operator == 'and' and not match:
                    break

            matches.append(match)

        return all(matches)

    @staticmethod
    def sorted(items, sortBy):
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
            
        :type items: list[Item]
        :type sortBy: list[str]
        :rtype: list[Item]
        """
        logger.debug('Sort by: %s', sortBy)

        t = time.time()

        for field in reversed(sortBy):

            tokens = field.split(':')

            reverse = False
            if len(tokens) > 1:
                field = tokens[0]
                reverse = tokens[1] != 'asc'

            def sortKey(item):

                default = False if reverse else ''

                return item.itemData().get(field, default)

            items = sorted(items, key=sortKey, reverse=reverse)

        logger.debug("Sort items took %s", time.time() - t)

        return items

    @staticmethod
    def groupItems(items, fields):
        """
        Group the given items by the given field.

        :type items: list[Item]
        :type fields: list[str]
        :rtype: dict
        """
        logger.debug('Group by: %s', fields)

        # Only support for top level grouping at the moment.
        if fields:
            field = fields[0]
        else:
            return {'None': items}

        t = time.time()

        results_ = {}
        tokens = field.split(':')

        reverse = False
        if len(tokens) > 1:
            field = tokens[0]
            reverse = tokens[1] != 'asc'

        for item in items:
            value = item.itemData().get(field)
            if value:
                results_.setdefault(value, [])
                results_[value].append(item)

        groups = sorted(results_.keys(), reverse=reverse)

        results = collections.OrderedDict()
        for group in groups:
            results[group] = results_[group]

        logger.debug("Group Items Took %s", time.time() - t)

        return results


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
