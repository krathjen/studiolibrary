# Copyright 2016 by Kurt Rathjen. All Rights Reserved.
#
# Permission to use, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Kurt Rathjen
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# KURT RATHJEN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# KURT RATHJEN BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import logging
import collections

from studioqt import QtWidgets

import studiolibrary

logger = logging.getLogger(__name__)


__all__ = [
    "register",
    "registerItem",
    "itemClasses",
    "itemExtensions",
    "itemFromPath",
    "itemsFromPaths",
    "findItems",
    "validatePath",
    "validateName",
    "showWelcomeDialog",
    "showNewLibraryDialog",
]


_itemClasses = collections.OrderedDict()


class StudioLibraryError(Exception):
    """"""
    pass


class StudioLibraryValidateError(StudioLibraryError):
    """"""
    pass


def register(*args, **kwargs):
    """
    This method is now deprecated.
    
    Please use studiolibrary.registerItem instead.
    """
    registerItem(*args, **kwargs)


def registerItem(cls, extension, isDir=True, isFile=True, ignore=None):
    """
    Register the given item class to the given extension.

    :type extension: str
    :type cls: studiolibrary.LibraryItem
    :type isDir: bool
    :type isFile: bool
    :type ignore: str or None
    """
    global _itemClasses
    _itemClasses[extension] = {}
    _itemClasses[extension]["cls"] = cls
    _itemClasses[extension]["isDir"] = isDir
    _itemClasses[extension]["isFile"] = isFile
    _itemClasses[extension]["ignore"] = ignore


def itemClasses():
    """
    Return all registered library item classes.

    :rtype: list[studiolibrary.LibraryItem]
    """
    return [val['cls'] for val in _itemClasses.values()]


def itemExtensions():
    """
    Register the given item class to the given extension.

    :rtype: list[str]
    """
    return _itemClasses.keys()


def clearItemClasses():
    """
    Remove all registered item class.

    :rtype: None
    """
    global _itemClasses
    _itemClasses = collections.OrderedDict()


def itemFromPath(path):
    """
    Return a new item instance for the given path.

    :type path: str
    :rtype: studiolibrary.LibraryItem or None
    """
    item = None

    for ext in _itemClasses:

        val = _itemClasses[ext]

        cls = val["cls"]
        isDir = val.get("isDir")
        isFile = val.get("isFile")
        ignore = val.get("ignore")

        if path.endswith(ext):

            if ignore and ignore in path:
                continue

            if isDir and os.path.isdir(path) or isFile and os.path.isfile(path):
                item = cls(path)
                break

    return item


def itemsFromPaths(paths):
    """
    Return the items for the given paths.

    :type paths: list[str]:
    :rtype: collections.Iterable[studiolibrary.LibraryItem]
    """
    for path in paths:
        item = itemFromPath(path)
        if item:
            yield item


def findItems(path, direction=studiolibrary.Direction.Down, depth=3):
    """
    Find the items by walking the given path.

    :type path: str
    :type direction: studiolibrary.Direction or str
    :rtype: collections.Iterable[studiolibrary.LibraryItem]
    """
    match = lambda path: itemFromPath(path)

    ignore = [
        ".studiolibrary",
        ".studioLibrary",
    ]

    paths = studiolibrary.findPaths(
        path,
        match=match,
        ignore=ignore,
        direction=direction,
        depth=depth
    )

    return itemsFromPaths(paths)


def validatePath(path):
    """
    Validate the given path.

    :raises: StudioLibraryValidateError

    :rtype: None
    """
    if "\\" in path:
        msg = "Invalid token found in path. Please use '/' instead of '\\'"
        raise StudioLibraryValidateError(msg)

    if not path or not path.strip():
        msg = u'Cannot set an empty path "{0}"!'.format(path)
        raise StudioLibraryValidateError(msg)

    if not os.path.exists(path):
        msg = u'Cannot find the folder path "{0}"!'.format(path)
        raise StudioLibraryValidateError(msg)


def validateName(name, valid=None, caseSensitive=True):
    """
    Validate the given name.

    :type name: str
    :type valid: list[str] or None
    :type caseSensitive: bool

    :raises: StudioLibraryValidateError

    :rtype: None
    """
    libraries = {}

    valid = valid or []

    if not name or not name.strip():
        raise StudioLibraryValidateError('Cannot set an empty name!')

    if name in valid:
        return

    if name in studiolibrary.Library._instances:
        msg = u'The Library "{0}" already exists!'.format(name)
        raise StudioLibraryValidateError(msg)

    if caseSensitive:
        for n in studiolibrary.Library._instances:
            libraries[n.lower()] = studiolibrary.Library._instances[n]

        if name.lower() in libraries:
            msg = u'The Library "{0}" already exists. It is case sensitive!'
            msg = msg.format(name)
            raise StudioLibraryValidateError(msg)


def showWelcomeDialog(name="", path="", **kwargs):
    """
    Show the welcome dialog.

    :type name: str
    :type path: str
    :rtype: studiolibrary.Library
    """
    name = name or studiolibrary.Library.DEFAULT_NAME

    return showNewLibraryDialog(
        name=name,
        path=path,
        title="Hello!",
        header="Welcome to the Studio Library",
        text="""Before you get started please choose a folder location for storing the data.
A network folder is recommended for sharing within a studio.""",
        **kwargs
    )


def showNewLibraryDialog(
    name="",
    path="",
    title="New Library!",
    header="Create a new library",
    text="""Create a new library with a different folder location and switch between them.
For example; This could be useful when working on different film productions,
or for having a shared library and a local library.""",
    validNames=None,
    showOnAccepted=True,
    errorOnRejected=True
):
    """
    Show the settings dialog for creating a new library.

    :type name: str
    :type path: str
    :type title: str
    :type header: str
    :type text: str
    :type validNames: list[str]
    :type showOnAccepted: bool
    :type errorOnRejected: bool

    :rtype: studiolibrary.Library
    """
    library = None

    def validator():
        name = settingsDialog.name()
        path = settingsDialog.path()

        studiolibrary.validateName(name, validNames)
        studiolibrary.validatePath(path)

    settingsDialog = studiolibrary.SettingsDialog()
    settingsDialog.setValidator(validator)
    settingsDialog.setName(name)
    settingsDialog.setPath(path)
    settingsDialog.setText(text)
    settingsDialog.setTitle(title)
    settingsDialog.setHeader(header)

    result = settingsDialog.exec_()

    if result == QtWidgets.QDialog.Accepted:
        name = settingsDialog.name()
        path = settingsDialog.path()

        library = studiolibrary.Library.instance(name)
        library.setPath(path)
        library.setAccentColor(settingsDialog.accentColor())
        library.setBackgroundColor(settingsDialog.backgroundColor())
        library.saveSettings()

        if showOnAccepted:
            library.show()

    else:
        logger.info("New library dialog was canceled!")
        if errorOnRejected:
            raise Exception("Dialog was rejected.")

    return library
