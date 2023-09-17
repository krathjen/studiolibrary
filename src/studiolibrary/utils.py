# Copyright 2020 by Kurt Rathjen. All Rights Reserved.
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
import sys
import json
import uuid
import errno
import ctypes
import shutil
import locale
import logging
import getpass
import tempfile
import platform
import threading
import traceback
import collections
import distutils.version

from datetime import datetime

try:
    from collections import Mapping
except ImportError:
    from collections.abc import Mapping

# Use the built-in version of scandir/walk if possible,
# otherwise use the scandir module version
try:
    from scandir import walk
except ImportError:
    from os import walk

import studiolibrary

from studiovendor import six
from studiovendor.six.moves import urllib


__all__ = [
    "reload",
    "user",
    "isMac",
    "isMaya",
    "isLinux",
    "isWindows",
    "addLibrary",
    "setLibraries",
    "removeLibrary",
    "defaultLibrary",
    "checkForUpdates",
    "read",
    "write",
    "update",
    "saveJson",
    "readJson",
    "updateJson",
    "replaceJson",
    "readSettings",
    "saveSettings",
    "updateSettings",
    "settingsPath",
    "relPath",
    "absPath",
    "tempPath",
    "realPath",
    "normPath",
    "normPaths",
    "copyPath",
    "movePath",
    "movePaths",
    "listPaths",
    "splitPath",
    "localPath",
    "removePath",
    "renamePath",
    "formatPath",
    "pathsFromUrls",
    "resolveModule",
    "createTempPath",
    "renamePathInFile",
    "walkup",
    "generateUniquePath",
    "MovePathError",
    "RenamePathError",
    "timeAgo",
    "modules",
    "setDebugMode",
    "showInFolder",
    "stringToList",
    "listToString",
    "registerItem",
    "registerItems",
    "registeredItems",
    "runTests",
    "findItemsInFolders",
]


logger = logging.getLogger(__name__)


_itemClasses = collections.OrderedDict()


class PathError(IOError):
    """
    Exception that supports unicode escape characters.
    """
    def __init__(self, msg):
        """
        :type: str or unicode 
        """
        msg = six.text_type(msg)
        super(PathError, self).__init__(msg)
        self._msg = msg

    def __unicode__(self):
        """
        Return the decoded message using 'unicode_escape'
        
        :rtype: unicode 
        """
        return six.text_type(self._msg)


class MovePathError(PathError):
    """"""


class RenamePathError(PathError):
    """"""


def reload():
    """
    Removes all Studio Library modules from the Python cache.
    
    You can use this function for developing within DCC applications, however,
    it should not be used in production. 
    
    Example:
        import studiolibrary
        studiolibrary.reload()
        
        import studiolibrary
        studiolibrary.main()
    """
    os.environ["STUDIO_LIBRARY_RELOADED"] = "1"

    from studiolibrary import librarywindow
    librarywindow.LibraryWindow.destroyInstances()

    names = modules()

    for mod in list(sys.modules.keys()):
        for name in names:
            if mod in sys.modules and mod.startswith(name):
                logger.info('Removing module: %s', mod)
                del sys.modules[mod]


def defaultLibrary():
    """
    Get the name of the default library.

    :rtype: str
    """
    libraries = readSettings()

    # Try to get the library that has been set to default
    for name in libraries:
        if libraries[name].get("default"):
            return name

    # Try to get the library named Default
    if "Default" in libraries:
        return "Default"

    # Try to get a library
    for name in libraries:
        return name

    # Otherwise just return the name "Default"
    return "Default"


def addLibrary(name, path, **settings):
    """
    Add a new library with the given name, path and settings.

    :type name: str
    :type path: path
    :type settings: dict
    """
    libraries = readSettings()
    libraries.setdefault(name, {})
    libraries[name]["path"] = path

    update(libraries[name], settings)

    saveSettings(libraries)


def removeLibrary(name):
    """
    Remove a library by name.

    :type name: str
    """
    libraries = readSettings()
    if name in libraries:
        del libraries[name]
    saveSettings(libraries)


def setLibraries(libraries):
    """
    Remove existing libraries and set the new.

    Example:
        import studiolibrary

        libraries = [
            {"name":"test1", "path":r"D:\LibraryData", "default":True}},
            {"name":"test2", "path":r"D:\LibraryData2"},
            {"name":"Temp", "path":r"C:\temp"},
        ]

        studiolibrary.setLibraries(libraries)

    :type libraries: list[dict]
    """
    for library in libraries:
        addLibrary(**library)

    old = readSettings().keys()
    new = [library["name"] for library in libraries]

    remove = set(old) - set(new)
    for name in remove:
        removeLibrary(name)


def modules():
    """
    Get all the module names for the package.

    :rtype: list[str]
    """
    names = []
    dirname = os.path.dirname(os.path.dirname(__file__))
    for filename in os.listdir(dirname):
        names.append(filename)
    return names


def setDebugMode(level):
    """
    Set the logging level to debug.

    :type level: int
    :rtype: None
    """
    if level:
        level = logging.DEBUG
    else:
        level = logging.INFO

    for name in modules():
        logger_ = logging.getLogger(name)
        logger_.setLevel(level)


def resolveModule(name):
    """Resolve a dotted name to a global object."""
    name = name.split('.')
    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used = used + '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)
    return found


def registerItems():
    """Register all the items from the config file."""
    for name in studiolibrary.config.get("itemRegistry"):
        cls = resolveModule(name)
        studiolibrary.registerItem(cls)


def registerItem(cls):
    """
    Register the given item class to the given extension.

    :type cls: studiolibrary.LibraryItem
    :rtype: None
    """
    global _itemClasses
    _itemClasses[cls.__name__] = cls


def registeredItems():
    """
    Return all registered library item classes.

    :rtype: list[studiolibrary.LibraryItem]
    """
    return _itemClasses.values()


def clearRegisteredItems():
    """
    Remove all registered item classes.

    :rtype: None
    """
    global _itemClasses
    _itemClasses = collections.OrderedDict()


def tempPath(*args):
    """
    Get the temp directory set in the config.
    
    :rtype: str 
    """
    temp = studiolibrary.config.get("tempPath")
    return normPath(os.path.join(formatPath(temp), *args))


def createTempPath(name, clean=True, makedirs=True):
    """
    Create a temp directory with the given name.
    
    :type name: str
    :type clean: bool
    :type makedirs: bool 
    
    :rtype: bool 
    """
    path = tempPath(name)

    if clean and os.path.exists(path):
        if os.path.exists(path):
            shutil.rmtree(path)

    if makedirs and not os.path.exists(path):
        os.makedirs(path)

    return path


def pathsFromUrls(urls):
    """
    Return the local file paths from the given QUrls

    :type urls: list[QtGui.QUrl]
    :rtype: collections.Iterable[str]
    """
    for url in urls:
        path = url.toLocalFile()

        # Fixes a bug when dragging from windows explorer on windows 10
        if isWindows():
            if path.startswith("/"):
                path = path[1:]

        yield path


def findItems(path, depth=3, **kwargs):
    """
    Find and create items by walking the given path.

    :type path: str
    :type depth: int

    :rtype: collections.Iterable[studiolibrary.LibraryItem]
    """
    path = normPath(path)

    maxDepth = depth
    startDepth = path.count(os.path.sep)

    for root, dirs, files in walk(path, followlinks=True):

        files.extend(dirs)

        for filename in files:
            remove = False

            # Normalise the path for consistent matching
            path = os.path.join(root, filename)
            item = itemFromPath(path, **kwargs)

            if item:
                # Yield the item that matches/supports the current path
                yield item

                # Stop walking the dir if the item doesn't support nested items
                if not item.ENABLE_NESTED_ITEMS:
                    remove = True

            if remove and filename in dirs:
                dirs.remove(filename)

        if depth == 1:
            break

        # Stop walking the directory if the maximum depth has been reached
        currentDepth = root.count(os.path.sep)
        if (currentDepth - startDepth) >= maxDepth:
            del dirs[:]


def findItemsInFolders(folders, depth=3, **kwargs):
    """
    Find and create new item instances by walking the given paths.

    :type folders: list[str]
    :type depth: int

    :rtype: collections.Iterable[studiolibrary.LibraryItem]
    """
    for folder in folders:
        for item in findItems(folder, depth=depth, **kwargs):
            yield item


def user():
    """
    Return the current user name in lowercase.
    
    :rtype: str
    """
    return getpass.getuser().lower()


def system():
    """
    Return the current platform in lowercase.
    
    :rtype: str
    """
    return platform.system().lower()


def isMaya():
    """
    Return True if the current python session is in Maya.
    
    :rtype: bool
    """
    try:
        import maya.cmds
        maya.cmds.about(batch=True)
        return True
    except ImportError:
        return False


def isMac():
    """
    Return True if the current OS is Mac.
    
    :rtype: bool
    """
    return system().startswith("os") or \
           system().startswith("mac") or \
           system().startswith("darwin")


def isWindows():
    """
    Return True if the current OS is windows.
    
    :rtype: bool
    """
    return system().startswith("win")


def isLinux():
    """    
    Return True if the current OS is linux.
    
    :rtype: bool
    """
    return system().startswith("lin")


def localPath(*args):
    """
    Return the users preferred disc location.

    :rtype: str
    """
    path = os.getenv('APPDATA') or os.getenv('HOME')
    path = os.path.join(path, "StudioLibrary", *args)

    return path


def formatPath(formatString, path="", **kwargs):
    """
    Resolve the given string with the given path and kwargs.

    Example:
        print formatPath("{dirname}/meta.json", path="C:/hello/world.json")
        # "C:/hello/meta.json"

    :type formatString: str
    :type path: str
    :type kwargs: dict
    :rtype: str
    """
    logger.debug("Format String: %s", formatString)

    dirname, name, extension = splitPath(path)

    encoding = locale.getpreferredencoding()

    # Environment variables return raw strings so we need to convert them to
    # unicode using the preferred system encoding

    temp = tempfile.gettempdir()
    if temp:

        temp = six.text_type(temp)

    username = user()
    if username:
        username = six.text_type(username)

    local = os.getenv('APPDATA') or os.getenv('HOME')
    if local:
        local = six.text_type(local)

    kwargs.update(os.environ)

    labels = {
        "name": name,
        "path": path,
        "root": path,  # legacy
        "user": username,
        "temp": temp,
        "home": local,  # legacy
        "local": local,
        "dirname": dirname,
        "extension": extension,
    }

    kwargs.update(labels)

    resolvedString = six.text_type(formatString).format(**kwargs)

    logger.debug("Resolved String: %s", resolvedString)

    return normPath(resolvedString)


def copyPath(src, dst, force=False):
    """
    Make a copy of the given src path to the given destination path.

    :type src: str
    :type dst: str
    :type force: bool
    :rtype: str
    """
    dirname = os.path.dirname(src)

    if "/" not in dst:
        dst = os.path.join(dirname, dst)

    src = normPath(src)
    dst = normPath(dst)

    logger.info(u'Copying path "{0}" -> "{1}"'.format(src, dst))

    if src == dst:
        msg = u'The source path and destination path are the same: {0}'
        raise IOError(msg.format(src))

    if not force and os.path.exists(dst):
        msg = u'Cannot copy over an existing path: "{0}"'
        raise IOError(msg.format(dst))

    if force and os.path.exists(dst):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        else:
            os.remove(dst)

    # Make sure the destination directory exists
    dstDir = os.path.dirname(dst)
    if not os.path.exists(dstDir):
        os.makedirs(dstDir)

    if os.path.isfile(src):
        shutil.copy(src, dst)
    else:
        shutil.copytree(src, dst)

    logger.info("Copied path!")

    return dst


def movePath(src, dst):
    """
    Move the given source path to the given destination path.

    :type src: str
    :type dst: str
    :rtype: str
    """
    src = six.text_type(src)
    dirname, name, extension = splitPath(src)

    if not os.path.exists(src):
        raise MovePathError(u'No such file or directory: {0}'.format(src))

    if os.path.isdir(src):
        dst = u'{0}/{1}{2}'.format(dst, name, extension)
        dst = generateUniquePath(dst)

    shutil.move(src, dst)
    return dst


def movePaths(srcPaths, dst):
    """
    Move the given src paths to the given dst path.

    :type srcPaths: list[str]
    :type dst: str
    """
    if not os.path.exists(dst):
        os.makedirs(dst)

    for src in srcPaths or []:

        if not src:
            continue

        basename = os.path.basename(src)

        dst_ = os.path.join(dst, basename)
        dst_ = normPath(dst_)

        logger.info(u'Moving Content: {0} => {1}'.format(src, dst_))
        shutil.move(src, dst_)
        

def silentRemove(filename):
    """
    Silently remove a file, ignore if it doesn't exist.
    
    Workaround for #237 where `os.path.exists` gave false
    positives and removal of files failed because of it.
    
    :type filename: str
    :rtype: None
    
    """
    try:
        os.remove(filename)
    except OSError as e:
        # Ignore case of no such file or directory
        if e.errno != errno.ENOENT: 
            raise


def removePath(path):
    """
    Delete the given path from disc.

    :type path: str
    :rtype: None
    """
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def renamePath(src, dst, extension=None, force=False):
    """
    Rename the given source path to the given destination path.

    :type src: str
    :type dst: str
    :type extension: str
    :type force: bool
    :rtype: str
    """
    dirname = os.path.dirname(src)

    if "/" not in dst:
        dst = os.path.join(dirname, dst)

    if extension and extension not in dst:
        dst += extension

    src = normPath(src)
    dst = normPath(dst)

    logger.debug(u'Renaming: {0} => {1}'.format(src, dst))

    if src == dst and not force:
        msg = u'The source path and destination path are the same: {0}'
        raise RenamePathError(msg.format(src))

    if os.path.exists(dst) and not force:
        msg = u'Cannot save over an existing path: "{0}"'
        raise RenamePathError(msg.format(dst))

    if not os.path.exists(dirname):
        msg = u'The system cannot find the specified path: "{0}".'
        raise RenamePathError(msg.format(dirname))

    if not os.path.exists(os.path.dirname(dst)) and force:
        os.mkdir(os.path.dirname(dst))

    if not os.path.exists(src):
        msg = u'The system cannot find the specified path: "{0}"'
        raise RenamePathError(msg.format(src))

    os.rename(src, dst)

    logger.debug(u'Renamed: {0} => {1}'.format(src, dst))

    return dst


def read(path):
    """
    Return the contents of the given file.
    
    :type path: str 
    :rtype: str 
    """
    data = ""
    path = normPath(path)

    if os.path.isfile(path):
        with open(path) as f:
            data = f.read() or data

    data = absPath(data, path)

    return data


def write(path, data):
    """
    Write the given data to the given file on disc.

    :type path: str 
    :type data: str 
    :rtype: None 
    """
    path = normPath(path)
    data = relPath(data, path)

    tmp = path + ".tmp"
    bak = path + ".bak"

    # Create the directory if it doesn't exists
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Use the tmp file to check for concurrent writes
    if os.path.exists(tmp):
        msg = "The path is locked for writing and cannot be accessed {}"
        msg = msg.format(tmp)
        raise IOError(msg)

    # Safely write the data to a tmp file and then rename to the given path
    try:
        # Create and write the new data
        #  to the path.tmp file
        with open(tmp, "w") as f:
            f.write(data)
            f.flush()

        # Remove any existing path.bak files
        silentRemove(bak)

        # Rename the existing path to path.bak
        if os.path.exists(path):
            os.rename(path, bak)

        # Rename the tmp path to the given path
        if os.path.exists(tmp):
            os.rename(tmp, path)

        # Clean up the bak file only if the given path exists
        if os.path.exists(path) and os.path.exists(bak):
            silentRemove(bak)

    except:
        # Remove the tmp file if there are any issues
        silentRemove(tmp)

        # Restore the path from the current .bak file
        if not os.path.exists(path) and os.path.exists(bak):
            os.rename(bak, path)

        raise


def update(data, other):
    """
    Update the value of a nested dictionary of varying depth.
    
    :type data: dict
    :type other: dict
    :rtype: dict 
    """
    for key, value in other.items():
        if isinstance(value, Mapping):
            data[key] = update(data.get(key, {}), value)
        else:
            data[key] = value
    return data


def updateJson(path, data):
    """
    Update a json file with the given data.

    :type path: str
    :type data: dict
    :rtype: None
    """
    data_ = readJson(path)
    data_ = update(data_, data)
    saveJson(path, data_)


def saveJson(path, data):
    """
    Serialize the data to a JSON string and write it to the given path.

    :type path: str
    :type data: dict
    :rtype: None
    """
    path = normPath(path)

    data = collections.OrderedDict(sorted(data.items(), key=lambda t: t[0]))
    data = json.dumps(data, indent=4)
    write(path, data)


def readJson(path):
    """
    Read the given JSON file and deserialize to a Python object.

    :type path: str
    :rtype: dict
    """
    path = normPath(path)

    logger.debug(u'Reading json file: {0}'.format(path))

    data = read(path) or "{}"
    data = json.loads(data)

    return data


def settingsPath():
    """
    Get the settings path from the config file.
    
    :rtype: str 
    """
    formatString = studiolibrary.config.get('settingsPath')
    return studiolibrary.formatPath(formatString)


def updateSettings(data):
    """
    Update the existing settings with the given data.

    :type data: dict
    """
    settings = studiolibrary.readSettings()
    update(settings, data)
    studiolibrary.saveSettings(settings)


def readSettings():
    """
    Get all the user settings.
    
    :rtype: dict 
    """
    path = settingsPath()

    logger.debug(u'Reading settings from "%s"', path)

    data = {}

    try:
        data = studiolibrary.readJson(path)
    except Exception as error:
        logger.exception('Cannot read settings from "%s"', path)

    return data


def saveSettings(data):
    """
    Save the given data to the settings path.
    
    :type data:  
    """
    path = settingsPath()

    logger.debug(u'Saving settings to "%s"', path)

    try:
        studiolibrary.saveJson(path, data)
    except Exception:
        logger.exception(u'Cannot save settings to "%s"', path)


def replaceJson(path, old, new, count=-1):
    """
    Replace the old value with the new value in the given json file.
    
    :type path: str
    :type old: str
    :type new: str
    :type count: int
    :rtype: dict
    """
    old = six.text_type(old)
    new = six.text_type(new)

    data = read(path) or "{}"
    data = data.replace(old, new, count)
    data = json.loads(data)

    saveJson(path, data)

    return data


def renamePathInFile(path, src, dst):
    """
    Rename the given src path to the given dst path.

    :type path: str
    :type src: str
    :type dst: str
    :rtype: None
    """
    src = normPath(src)
    dst = normPath(dst)

    src1 = '"' + src + '"'
    dst2 = '"' + dst + '"'

    # Replace paths that match exactly the given src and dst strings
    replaceJson(path, src1, dst2)

    src2 = '"' + src
    dst2 = '"' + dst

    # Add a slash as a suffix for better directory matching
    if not src2.endswith("/"):
        src2 += "/"

    if not dst2.endswith("/"):
        dst2 += "/"

    # Replace all paths that start with the src path with the dst path
    replaceJson(path, src2, dst2)


def relPath(data, start):
    """
    Return a relative version of all the paths in data from the start path.

    :type data: str 
    :type start: str
    :rtype: str 
    """
    rpath = start

    for i in range(0, 3):

        rpath = os.path.dirname(rpath)
        token = os.path.relpath(rpath, start)

        rpath = normPath(rpath)
        token = normPath(token)

        if rpath.endswith("/"):
            rpath = rpath[:-1]

        data = data.replace(rpath, token)

    return data


def absPath(data, start, depth=3):
    """
    Return an absolute version of all the paths in data using the start path.
    
    :type data: str 
    :type start: str
    :type depth: int
    :rtype: str 
    """
    token = ".."
    pairs = []
    path = normPath(os.path.dirname(start))

    # First create a list of tokens and paths.
    for i in range(1, depth+1):
        rel = ((token + "/") * i)
        pairs.append((rel, path))
        path = normPath(os.path.dirname(path))

    # Second replace the token with the paths.
    for pair in reversed(pairs):
        rel, path = pair

        # Replace with the trailing slash
        # '../../', 'P:/LibraryData/'
        if not rel.endswith("/"):
            rel += "/"

        if not path.endswith("/"):
            path += "/"

        data = data.replace(rel, path)

        # Replace without the trailing slash
        # '../..', 'P:/LibraryData'
        if rel.endswith("/"):
            rel = rel[:-1]

        if path.endswith("/"):
            path = path[:-1]

        data = data.replace(rel, path)

    return data


def realPath(path):
    """
    Return the given path eliminating any symbolic link.
    
    :type path: str 
    :rtype: str 
    """
    path = os.path.realpath(path)
    path = os.path.expanduser(path)
    return normPath(path)


def normPath(path):
    """
    Return a normalized path containing only forward slashes.

    :type path: str
    :rtype: unicode
    """
    # Check and support the UNC path structure
    unc = path.startswith("//") or path.startswith("\\\\")

    path = path.replace("//", "/")
    path = path.replace("\\", "/")

    if path.endswith("/") and not path.endswith(":/"):
        path = path.rstrip("/")

    # Make sure we retain the UNC path structure
    if unc and not path.startswith("//") and path.startswith("/"):
        path = "/" + path

    return path


def normPaths(paths):
    """
    Normalize all the given paths to a consistent format.

    :type paths: list[str]
    :rtype: list[str]
    """
    return [normPath(path) for path in paths]


def splitPath(path):
    """
    Split the given path into directory, basename and extension.
    
    Example:
        print splitPath("P:/production/rigs/character/mario.ma
        
        # (u'P:/production/rigs/character', u'mario', u'.ma')
    
    :type path: str
    :rtype: list[str]
    """
    path = normPath(path)
    filename, extension = os.path.splitext(path)
    return os.path.dirname(filename), os.path.basename(filename), extension


def listToString(data):
    """
    Return a string from the given list.
    
    Example:
        print listToString(['apple', 'pear', 'cherry'])
        
        # apple,pear,cherry
    
    :type data: list
    :rtype: str
    """
    # Convert all items to string and remove 'u'
    data = [str(item) for item in data]
    data = str(data).replace("[", "").replace("]", "")
    data = data.replace("'", "").replace('"', "")
    return data


def stringToList(data):
    """
    Return a list from the given string.
        
    Example:
        print listToString('apple, pear, cherry')
        
        # ['apple', 'pear', 'cherry']
    
    :type data: str
    :rtype: list
    """
    data = '["' + str(data) + '"]'
    data = data.replace(' ', '')
    data = data.replace(',', '","')
    return eval(data)


def listPaths(path):
    """
    Return a list of paths that are in the given directory.
    
    :type path: str
    :rtype: collections.Iterable[str]
    """
    for name in os.listdir(path):
        value = path + "/" + name
        yield value


def generateUniquePath(path, attempts=1000):
    """
    Generate a unique path on disc.

    Example:
        # If the following files exist then the next unique path will be 3.
        # C:/tmp/file.text
        # C:/tmp/file (2).text

        print generateUniquePath("C:/tmp/file.text")
        # C:/tmp/file (3).text

    :type path:  str
    :type attempts: int
    :rtype: str
    """
    attempt = 1  # We start at one so that the first unique name is actually 2.
    dirname, name, extension = splitPath(path)
    path_ = u'{dirname}/{name} ({number}){extension}'

    while os.path.exists(path):
        attempt += 1

        path = path_.format(
            name=name,
            number=attempt,
            dirname=dirname,
            extension=extension
        )

        if attempt >= attempts:
            msg = u'Cannot generate unique name for path {path}'
            msg = msg.format(path=path)
            raise ValueError(msg)

    return path


def walkup(path, match=None, depth=3, sep="/"):
    """
    :type path: str
    :type match: func
    :type depth: int
    :type sep: str
    :rtype: collections.Iterable[str]
    """
    path = normPath(path)

    if not path.endswith(sep):
        path += sep

    folders = path.split(sep)
    depthCount = 0

    for i, folder in enumerate(folders):
        if folder:

            if depthCount > depth:
                break
            depthCount += 1

            folder = os.path.sep.join(folders[:i*-1])
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    path = os.path.join(folder, filename)
                    if match is None or match(path):
                        yield normPath(path)


def timeAgo(timeStamp):
    """
    Return a pretty string for how long ago the given timeStamp was.
    
    Example:
        print timeAgo("2015-04-27 22:29:55"
        # 2 years ago
    
    :type timeStamp: str
    :rtype: str
    """
    t1 = int(timeStamp)
    t1 = datetime.fromtimestamp(t1)

    t2 = datetime.now()
    diff = t2 - t1

    dayDiff = diff.days
    secondsDiff = diff.seconds

    if dayDiff < 0:
        return ''

    if dayDiff == 0:
        if secondsDiff < 10:
            return "just now"
        if secondsDiff < 60:
            return "{:.0f} seconds ago".format(secondsDiff)
        if secondsDiff < 120:
            return "a minute ago"
        if secondsDiff < 3600:
            return "{:.0f} minutes ago".format(secondsDiff / 60)
        if secondsDiff < 7200:
            return "an hour ago"
        if secondsDiff < 86400:
            return "{:.0f} hours ago".format(secondsDiff / 3600)

    if dayDiff == 1:
        return "yesterday"

    if dayDiff < 7:
        return "{:.0f} days ago".format(dayDiff)

    if dayDiff < 31:
        v = dayDiff / 7
        if v == 1:
            return "{:.0f} week ago".format(v)
        return "{:.0f} weeks ago".format(dayDiff / 7)

    if dayDiff < 365:
        v = dayDiff / 30
        if v == 1:
            return "{:.0f} month ago".format(v)
        return "{:.0f} months ago".format(v)

    v = dayDiff / 365
    if v == 1:
        return "{:.0f} year ago".format(v)
    return "{:.0f} years ago".format(v)


def userUuid():
    """
    Return a unique uuid4 for each user.
    
    This does not compromise privacy as it generates a random uuid4 string
    for the current user.
    
    :rtype: str
    """
    path = os.path.join(localPath(), "settings.json")
    userUuid_ = readJson(path).get("userUuid")

    if not userUuid_:
        updateJson(path, {"userUuid": str(uuid.uuid4())})

        # Read the uuid again to make sure its persistent
        userUuid_ = readJson(path).get("userUuid")

    return userUuid_


def showInFolder(path):
    """
    Show the given path in the system file explorer.

    :type path: unicode
    :rtype: None
    """
    if isWindows():
        # os.system() and subprocess.call() can't pass command with
        # non ascii symbols, use ShellExecuteW directly
        cmd = ctypes.windll.shell32.ShellExecuteW
    else:
        cmd = os.system

    args = studiolibrary.config.get('showInFolderCmd')

    if args:
        if isinstance(args, six.string_types):
            args = [args]

    elif isLinux():
        args = [u'xdg-open "{path}"&']

    elif isWindows():
        args = [None, u'open', u'explorer', u'/select, "{path}"', None, 1]

    elif isMac():
        args = [u'open -R "{path}"']

    # Normalize the pathname for windows
    path = os.path.normpath(path)

    for i, a in enumerate(args):
        if isinstance(a, six.string_types) and '{path}' in a:
            args[i] = a.format(path=path)

    logger.info("Call: '%s' with arguments: %s", cmd.__name__, args)
    cmd(*args)


global DCC_INFO

try:
    import maya.cmds
    DCC_INFO = {
        "name": "maya",
        "version": maya.cmds.about(q=True, version=True)
    }
except Exception as error:
    DCC_INFO = {
        "name": "undefined",
        "version": "undefined",
    }


def osVersion():
    try:
        # Fix for Windows 11 returning the wrong version
        if platform.system().lower() == "windows" and platform.release() == "10" and sys.getwindowsversion().build >= 22000:
            return "11"
    finally:
        return platform.release().replace(' ', '%20')


def checkForUpdates():
    """
    This function should only be used once every session unless specified by the user.

    Returns True if a newer release is found for the given platform.

    :rtype: dict
    """
    if os.environ.get("STUDIO_LIBRARY_RELOADED") == "1":
        return {}

    if not studiolibrary.config.get('checkForUpdatesEnabled', True):
        return {}

    # In python 2.7 the getdefaultlocale function could return a None "ul"
    try:
        ul, _ = locale.getdefaultlocale()
        ul = ul or "undefined"
        ul = ul.replace("_", "-").lower()
    except Exception as error:
        ul = "undefined"

    try:
        uid = userUuid() or "undefined"
        url = "https://app.studiolibrary.com/releases?uid={uid}&v={v}&dv={dv}&dn={dn}&os={os}&ov={ov}&pv={pv}&ul={ul}"
        url = url.format(
            uid=uid,
            v=studiolibrary.__version__,
            dn=DCC_INFO.get("name").replace(' ', '%20'),
            dv=DCC_INFO.get("version").replace(' ', '%20'),
            os=platform.system().lower().replace(' ', '%20'),
            ov=osVersion(),
            pv=platform.python_version().replace(' ', '%20'),
            ul=ul,
        )

        response = urllib.request.urlopen(url)

        # Check the HTTP status code
        if response.getcode() == 200:
            json_content = response.read().decode('utf-8')
            data = json.loads(json_content)
            return data

    except Exception as error:
        logger.debug("Exception occurred:\n%s", traceback.format_exc())
        pass

    return {}


def testNormPath():
    """Test the norm path utility function. """

    assert normPath("//win-q9lu/Library Data") == "//win-q9lu/Library Data"

    assert normPath("////win-q9lu/Library Data/") == "//win-q9lu/Library Data"

    assert normPath("\\\\win-q9l\\Library Data\\") == "//win-q9l/Library Data"

    assert normPath(r"C:\folder//Library Data/") == "C:/folder/Library Data"

    assert normPath(r"\folder//Library Data/") == "/folder/Library Data"

    assert normPath("C:\\folder//Library Data/") == "C:/folder/Library Data"

    assert normPath("\\folder//Library Data/") == "/folder/Library Data"

    assert normPath("C:/") == "C:/"


def testUpdate():
    """
    Test the update dictionary command

    :rtype: None 
    """
    testData1 = {
        "../../images/beach.jpg": {
            "Custom Order": "00001"
        },
        "../../images/sky.jpg": {
            "Custom Order": "00019",
            "Other": {"Paths": "../../images/bird2.mb"}
        }
    }

    testData2 = {
        "../../images/sky.jpg": {
            "Labels": ["head", "face"],
        },
    }

    expected = {
        "../../images/beach.jpg": {
            "Custom Order": "00001"
        },
        "../../images/sky.jpg": {
            "Custom Order": "00019",
            "Labels": ["head", "face"],
            "Other": {"Paths": "../../images/bird2.mb"}
        }
    }

    # Test updating/inserting a value in a dictionary.
    result = update(testData1, testData2)

    msg = "Data does not match {} {}".format(expected, result)
    assert expected == result, msg

    # Test the update command with an empty dictionary.
    testData2 = {
        "../../images/sky.jpg": {},
    }

    result = update(testData1, testData2)

    msg = "Data does not match {} {}".format(expected, result)
    assert expected == result, msg


def testSplitPath():
    """
    Test he splitPath command.
    
    :rtype: None 
    """
    path = "P:/production/rigs/character/mario.ma"

    result = splitPath(path)
    expected = (u'P:/production/rigs/character', u'mario', u'.ma')

    msg = "Data does not match {} {}".format(expected, result)
    assert expected == result, msg


def testFormatPath():
    """
    Test the formatPath command.

    :rtype: None 
    """
    formatString = "{dirname}/versions/{name}{extension}"

    result = formatPath(formatString, path="P:/production/rigs/database.json")
    expected = "P:/production/rigs/versions/database.json"

    msg = "Data does not match {} {}".format(expected, result)
    assert expected == result, msg


def testRelativePaths():
    """
    Test absolute and relative paths.
    
    :rtype: None 
    """
    data = """
    { 
    "P:/path/head.anim": {},
    "P:/test/path/face.anim": {},
    "P:/test/relative/path/hand.anim": {},    
    }
    """

    expected = """
    { 
    "../../../path/head.anim": {},
    "../../path/face.anim": {},
    "../path/hand.anim": {},    
    }
    """

    data_ = relPath(data, "P:/test/relative/file.database")
    msg = "Data does not match {} {}".format(expected, data_)
    assert data_ == expected, msg

    data = """
    {
    "P:/": {},
    "P:/head.anim": {},
    "P:/path/head.anim": {},
    "P:/test/path/face.anim": {},
    "P:/test/relative/path/hand.anim": {},
    }
    """

    expected = """
    {
    "../../": {},
    "../../head.anim": {},
    "../../path/head.anim": {},
    "../../test/path/face.anim": {},
    "../../test/relative/path/hand.anim": {},
    }
    """

    data_ = relPath(data, "P:/.studiolibrary/database.json")
    msg = "Data does not match {} {}".format(expected, data_)
    assert data_ == expected, msg

    path = "P:/path/head.anim"
    start = "P:/test/relative/file.database"
    expected = "../../../path/head.anim"

    result = relPath(path, start)
    msg = 'Data does not match "{}" "{}"'.format(result, expected)
    assert result == expected, msg

    result = absPath(result, start)
    msg = 'Data does not match "{}" "{}"'.format(result, path)
    assert result == path, msg

    data = """
    {
    "P:/LibraryData": {},
    }
    """

    expected = """
    {
    "../..": {},
    }
    """

    data_ = relPath(data, "P:/LibraryData/.studiolibrary/database.json")

    print(data_)
    msg = "Data does not match {} {}".format(expected, data_)
    assert data_ == expected, msg

    data = """
    {
    "../..": {},
    }
    """

    expected = """
    {
    "P:/LibraryData": {},
    }
    """

    data_ = absPath(data, "P:/LibraryData/.studiolibrary/database.json")

    print(data_)
    msg = "Data does not match {} {}".format(expected, data_)
    assert data_ == expected, msg


def runTests():
    """Run all the tests for this file."""
    testUpdate()
    testSplitPath()
    testFormatPath()
    testRelativePaths()
    testNormPath()


if __name__ == "__main__":
    runTests()
