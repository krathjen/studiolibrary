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

import os
import json
import ctypes
import shutil
import urllib2
import logging
import getpass
import platform
import threading
import collections

from datetime import datetime


__all__ = [
    "user",
    "walk",
    "isMac",
    "isMaya",
    "isLinux",
    "isWindows",
    "read",
    "write",
    "update",
    "saveJson",
    "readJson",
    "updateJson",
    "replaceJson",
    "relPath",
    "absPath",
    "realPath",
    "normPath",
    "copyPath",
    "movePath",
    "movePaths",
    "listPaths",
    "findPaths",
    "splitPath",
    "localPath",
    "removePath",
    "renamePath",
    "formatPath",
    "generateUniquePath",
    "MovePathError",
    "RenamePathError",
    "timeAgo",
    "sendEvent",
    "showInFolder",
    "Direction",
    "stringToList",
    "listToString",
    "registerItem",
    "itemClasses",
    "itemExtensions",
    "itemFromPath",
    "itemsFromPaths",
    "itemsFromUrls",
    "itemClassFromPath",
    "isValidItemPath",
    "findItems",
    "findItemsInFolders",
    "IGNORE_PATHS",
    "ANALYTICS_ID",
    "ANALYTICS_ENABLED",
    "SHOW_IN_FOLDER_CMD",
]


logger = logging.getLogger(__name__)


_itemClasses = collections.OrderedDict()


IGNORE_PATHS = ["/."]  # Ignore all paths the start with a "."
ANALYTICS_ID = "UA-50172384-1"
ANALYTICS_ENABLED = True
SHOW_IN_FOLDER_CMD = None


class PathError(IOError):
    """
    Exception that supports unicode escape characters.
    """
    def __init__(self, msg):
        """
        :type: str or unicode 
        """
        msg = unicode(msg).encode('unicode_escape')
        super(PathError, self).__init__(msg)
        self._msg = msg

    def __unicode__(self):
        """
        Return the decoded message using 'unicode_escape'
        
        :rtype: unicode 
        """
        msg = unicode(self._msg).decode('unicode_escape')
        return msg


class MovePathError(PathError):
    """"""


class RenamePathError(PathError):
    """"""


class Direction:
    Up = "up"
    Down = "down"


def registerItem(cls):
    """
    Register the given item class to the given extension.

    :type cls: studiolibrary.LibraryItem
    :rtype: None
    """
    global _itemClasses
    _itemClasses[cls.__name__] = cls


def itemClasses():
    """
    Return all registered library item classes.

    :rtype: list[studiolibrary.LibraryItem]
    """
    return _itemClasses.values()


def itemExtensions():
    """
    Return all the registered item extensions.

    :rtype: list[str]
    """
    extensions = []

    for cls in itemClasses():
        extensions.extend(cls.Extensions)

    return extensions


def clearItemClasses():
    """
    Remove all registered item classes.

    :rtype: None
    """
    global _itemClasses
    _itemClasses = collections.OrderedDict()


def itemFromPath(path, **kwargs):
    """
    Return a new item instance for the given path.

    :type path: str
    :rtype: studiolibrary.LibraryItem or None
    """
    cls = itemClassFromPath(path)
    if cls:
        return cls(path, **kwargs)
    else:
        return None


def itemsFromPaths(paths, **kwargs):
    """
    Return new item instances for the given paths.

    :type paths: list[str]:
    :rtype: collections.Iterable[studiolibrary.LibraryItem]
    """
    for path in paths:
        item = itemFromPath(path, **kwargs)
        if item:
            yield item


def itemsFromUrls(urls, **kwargs):
    """
    Return new item instances for the given QUrl objects.

    :type urls: list[QtGui.QUrl]
    :rtype: list[studiolibrary.LibraryItem]
    """
    items = []
    for path in pathsFromUrls(urls):

        item = itemFromPath(path, **kwargs)

        if item:
            items.append(item)
        else:
            msg = 'Cannot find the item for path "{0}"'
            msg = msg.format(path)
            logger.warning(msg)

    return items


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


def isValidItemPath(path):
    """
    Return True if the given path is supported by a registered item.

    :type path: str
    :rtype: bool 
    """
    return itemClassFromPath(path) is not None


def itemClassFromPath(path):
    """
    Return the registered LibraryItem class that supports the given path.

    :type path: str
    :rtype: studiolibrary.LibraryItem.__class__ or None
    """
    for ignore in IGNORE_PATHS:
        if ignore in path:
            return None

    for cls in itemClasses():
        if cls.isValidPath(path):
            return cls

    return None


def findItems(path, direction=Direction.Down, depth=3, **kwargs):
    """
    Find and create new item instances by walking the given path.

    :type path: str
    :type direction: studiolibrary.Direction or str
    :type depth: int

    :rtype: collections.Iterable[studiolibrary.LibraryItem]
    """
    paths = findPaths(
        path,
        match=isValidItemPath,
        direction=direction,
        depth=depth
    )

    return itemsFromPaths(paths, **kwargs)


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
    dirname, name, extension = splitPath(path)

    local = os.getenv('APPDATA') or os.getenv('HOME')

    labels = {
        "name": name,
        "path": path,
        "local": local,
        "dirname": dirname,
        "extension": extension,
    }

    kwargs.update(labels)

    return unicode(formatString).format(**kwargs)


def copyPath(src, dst):
    """
    Make a copy of the given src path to the given destination path.

    :type src: str
    :type dst: str
    :rtype: str
    """
    if os.path.isfile(src):
        shutil.copy(src, dst)
    else:
        shutil.copytree(src, dst)

    return dst


def movePath(src, dst):
    """
    Move the given source path to the given destination path.

    :type src: str
    :type dst: str
    :rtype: str
    """
    src = unicode(src)
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
        basename = os.path.basename(src)

        dst_ = os.path.join(dst, basename)
        dst_ = normPath(dst_)

        logger.info(u'Moving Content: {0} => {1}'.format(src, dst_))
        shutil.move(src, dst_)


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
        with open(path, "r") as f:
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
        if os.path.exists(bak):
            os.remove(bak)

        # Rename the existing path to path.bak
        if os.path.exists(path):
            os.rename(path, bak)

        # Rename the tmp path to the given path
        if os.path.exists(tmp):
            os.rename(tmp, path)

        # Clean up the bak file only if the given path exists
        if os.path.exists(path) and os.path.exists(bak):
            os.remove(bak)

    except:
        # Remove the tmp file if there are any issues
        if os.path.exists(tmp):
            os.remove(tmp)

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
    for key, value in other.iteritems():
        if isinstance(value, collections.Mapping):
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


def replaceJson(path, old, new, count=-1):
    """
    Replace the old value with the new value in the given json file.
    
    :type path: str
    :type old: str
    :type new: str
    :type count: int
    :rtype: dict
    """
    old = old.encode("unicode_escape")
    new = new.encode("unicode_escape")

    data = read(path) or "{}"
    data = data.replace(old, new, count)
    data = json.loads(data)

    saveJson(path, data)

    return data


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


def absPath(data, start):
    """
    Return an absolute version of all the paths in data using the start path.
    
    :type data: str 
    :type start: str
    :rtype: str 
    """
    relPath1 = normPath(os.path.dirname(start))
    relPath2 = normPath(os.path.dirname(relPath1))
    relPath3 = normPath(os.path.dirname(relPath2))

    if not relPath1.endswith("/"):
        relPath1 = relPath1 + "/"

    if not relPath2.endswith("/"):
        relPath2 = relPath2 + "/"

    if not relPath3.endswith("/"):
        relPath3 = relPath3 + "/"

    data = data.replace('../../../', relPath3)
    data = data.replace('../../', relPath2)
    data = data.replace('../', relPath1)

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
    :rtype: str or unicode 
    """
    return unicode(path.replace("\\", "/"))


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


def findPaths(
        path,
        match=None,
        direction=Direction.Down,
        depth=3,
        **kwargs
):
    """
    Return a list of file paths by walking the root path either up or down.

    Example:
        path = r'P:\production\characters\Malcolm'

        def match(path):
            return path.endswith(".set")

        for path in findPaths(path, match=match, depth=5):
            print path

    :type path: str
    :type match: func or None
    :type depth: int
    :type direction: Direction
    :rtype: collections.Iterable[str]
    """
    if os.path.isfile(path):
        path = os.path.dirname(path)

    if depth <= 1 and direction == Direction.Down:
        paths = listPaths(path)

    elif direction == Direction.Down:
        paths = walk(path, match=match, depth=depth, **kwargs)

    elif direction == Direction.Up:
        paths = walkup(path, match=match, depth=depth)

    else:
        raise Exception("Direction not supported {0}".format(direction))

    return paths


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


def walk(path, match=None, ignore=None, depth=3, **kwargs):
    """
    Return the files by walking down the given directory.
    
    :type path: str
    :type match: func or None
    :type ignore: func or None
    :type depth: int
    :rtype: collections.Iterable[str]
    """
    path = path.rstrip(os.path.sep)
    path = os.path.realpath(path)

    maxDepth = depth

    assert os.path.isdir(path)
    startDepth = path.count(os.path.sep)

    for root, dirs, files in os.walk(path, **kwargs):

        files.extend(dirs)

        for filename in files:
            remove = False

            # Normalise the path for consistent matching
            path = os.path.join(root, filename)
            path = normPath(path)

            # Stop walking the current dir if the ignore func returns True
            if ignore and ignore(path):
                remove = True

            # Yield and stop walking the current dir if a match has been found
            elif match and match(path):
                remove = True
                yield path

            # Yield all paths if no match or ignore has been set
            else:
                yield path

            if remove and filename in dirs:
                dirs.remove(filename)

        currentDepth = root.count(os.path.sep)
        if (currentDepth - startDepth) >= maxDepth:
            del dirs[:]


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
            return str(secondsDiff) + " seconds ago"
        if secondsDiff < 120:
            return "a minute ago"
        if secondsDiff < 3600:
            return str(secondsDiff / 60) + " minutes ago"
        if secondsDiff < 7200:
            return "an hour ago"
        if secondsDiff < 86400:
            return str(secondsDiff / 3600) + " hours ago"

    if dayDiff == 1:
        return "yesterday"

    if dayDiff < 7:
        return str(dayDiff) + " days ago"

    if dayDiff < 31:
        v = dayDiff / 7
        if v == 1:
            return str(v) + " week ago"
        return str(dayDiff / 7) + " weeks ago"

    if dayDiff < 365:
        v = dayDiff / 30
        if v == 1:
            return str(v) + " month ago"
        return str(v) + " months ago"

    v = dayDiff / 365
    if v == 1:
        return str(v) + " year ago"
    return str(v) + " years ago"


def sendEvent(name, version="1.0.0", an="StudioLibrary", tid=None):
    """
    Send a screen view event to google analytics.

    Example:
        sendEvent("mainWindow")

    :type name: str
    :type version: str
    :type an: str
    :type tid: str
    :rtype: None
    """
    if not ANALYTICS_ENABLED:
        return

    tid = tid or ANALYTICS_ID
    cid = getpass.getuser() + "-" + platform.node()

    url = "http://www.google-analytics.com/collect?" \
          "v=1" \
          "&ul=en-us" \
          "&a=448166238" \
          "&_u=.sB" \
          "&_v=ma1b3" \
          "&qt=2500" \
          "&z=185" \
          "&tid={tid}" \
          "&an={an}" \
          "&av={av}" \
          "&cid={cid}" \
          "&t=appview" \
          "&cd={name}"

    url = url.format(
        tid=tid,
        an=an,
        av=version,
        cid=cid,
        name=name,
    )

    def _send(url):
        try:
            url = url.replace(" ", "")
            f = urllib2.urlopen(url, None, 1.0)
        except Exception:
            pass

    t = threading.Thread(target=_send, args=(url,))
    t.start()


def showInFolder(path):
    """
    Show the given path in the system file explorer.

    :type path: unicode
    :rtype: None
    """
    cmd = os.system
    args = []

    if SHOW_IN_FOLDER_CMD:
        args = [unicode(SHOW_IN_FOLDER_CMD)]

    elif isLinux():
        args = [u'konqueror "{path}"&']

    elif isWindows():
        # os.system() and subprocess.call() can't pass command with
        # non ascii symbols, use ShellExecuteW directly
        args = [None, u'open', u'explorer.exe', u'/n,/select, "{path}"', None, 1]
        cmd = ctypes.windll.shell32.ShellExecuteW

    elif isMac():
        args = [u'open -R "{path}"']

    # Normalize the pathname for windows
    path = os.path.normpath(path)

    for i, a in enumerate(args):
        if isinstance(a, basestring) and '{path}' in a:
            args[i] = a.format(path=path)

    logger.info("Call: '%s' with arguments: %s", cmd.__name__, args)
    cmd(*args)


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
    formatString = "{dirname}/vesions/{name}{extension}"

    result = formatPath(formatString, path="P:/production/rigs/database.json")
    expected = "P:/production/rigs/vesions/database.json"

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

    data_ = absPath(data_, "P:/test/relative/file.database")
    msg = "Data does not match {} {}".format(data, data_)
    assert data_ == data, msg

    path = "P:/path/head.anim"
    start = "P:/test/relative/file.database"
    expected = "../../../path/head.anim"

    result = relPath(path, start)
    msg = 'Data does not match "{}" "{}"'.format(result, expected)
    assert result == expected, msg

    result = absPath(result, start)
    msg = 'Data does not match "{}" "{}"'.format(result, path)
    assert result == path, msg


if __name__ == "__main__":
    testUpdate()
    testSplitPath()
    testFormatPath()
    testRelativePaths()
