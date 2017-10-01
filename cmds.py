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
    "isMaya",
    "isMac",
    "isLinux",
    "isWindows",
    "logScreen",
    "timeAgo",
    "read",
    "write",
    "saveJson",
    "readJson",
    "updateJson",
    "listPaths",
    "findPaths",
    "copyPath",
    "movePath",
    "normPath",
    "splitPath",
    "removePath",
    "renamePath",
    "localPath",
    "formatPath",
    "moveContents",
    "Direction",
    "stringToList",
    "listToString",
    "generateUniquePath",
    "PathRenameError",
    "registerItem",
    "itemClasses",
    "itemExtensions",
    "itemFromPath",
    "itemsFromPaths",
    "itemsFromUrls",
    "findItems",
    "findItemsInFolders",
]


logger = logging.getLogger(__name__)


_itemClasses = collections.OrderedDict()


class PathRenameError(IOError):
    """
    """


class StudioLibraryError(Exception):
    """"""
    pass


class StudioLibraryValidateError(StudioLibraryError):
    """"""
    pass


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
    Register the given item class to the given extension.

    :rtype: list[str]
    """
    extensions = []

    for cls in itemClasses():
        extensions.extend(cls.Extensions)

    return extensions


def clearItemClasses():
    """
    Remove all registered item class.

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
    invalidNames = [
        ".studiolibrary",
        ".studioLibrary",
    ]

    for invalidName in invalidNames:
        if invalidName in path:
            return None

    for cls in itemClasses():
        if cls.isValidPath(path):
            return cls(path, **kwargs)

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
    for url in urls:
        path = url.toLocalFile()

        # Fixes a bug when dragging from windows explorer on windows 10
        if isWindows():
            if path.startswith("/"):
                path = path[1:]

        item = itemFromPath(path, **kwargs)

        if item:
            items.append(item)
        else:
            msg = 'Cannot find the item for path "{0}"'
            msg = msg.format(path)
            logger.warning(msg)

    return items


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
        match=itemFromPath,
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
    :rtype: str
    """
    import getpass
    return getpass.getuser().lower()


def system():
    """
    :rtype: str
    """
    return platform.system().lower()


def isMaya():
    """
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
    :rtype: bool
    """
    return system().startswith("mac") or system().startswith("os") \
        or system().startswith("darwin")


def isWindows():
    """
    :rtype: bool
    """
    return system().startswith("win")


def isLinux():
    """
    :rtype: bool
    """
    return system().startswith("lin")


def localPath(*args):
    """
    Return the users local disc location.

    :rtype: str
    """
    path = os.getenv('APPDATA') or os.getenv('HOME')
    path = os.path.join(path, "StudioLibrary", *args)

    return path


def formatPath(src, dst, labels=None):
    """
    Resolve the given destination path.

    Example:
        print formatPath("C:/hello/world.json", "{dirname}/meta.json")
        # "C:/hello/meta.json"

    :type src: str
    :type dst: str
    :type labels: dict
    :rtype: str
    """
    dirname, name, extension = splitPath(src)

    labels_ = {
        "name": name,
        "path": src,
        "dirname": dirname,
        "extension": extension,
    }

    if labels:
        labels_.update(labels)

    return unicode(dst).format(**labels_)


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
        raise IOError(u'No such file or directory: {0}'.format(src))

    if os.path.isdir(src):
        dst = u'{0}/{1}{2}'.format(dst, name, extension)
        dst = generateUniquePath(dst)

    shutil.move(src, dst)
    return dst


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
    Rename the given src path to given destination path.

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
        raise PathRenameError(msg.format(src))

    if os.path.exists(dst) and not force:
        msg = u'Cannot save over an existing path: "{0}"'
        raise PathRenameError(msg.format(dst))

    if not os.path.exists(dirname):
        msg = u'The system cannot find the specified path: "{0}".'
        raise PathRenameError(msg.format(dirname))

    if not os.path.exists(os.path.dirname(dst)) and force:
        os.mkdir(os.path.dirname(dst))

    if not os.path.exists(src):
        msg = u'The system cannot find the specified path: "{0}"'
        raise PathRenameError(msg.format(src))

    os.rename(src, dst)

    logger.debug(u'Renamed: {0} => {1}'.format(src, dst))

    return dst


def moveContents(contents, path):
    """
    Move the given contents to the specified path.

    :type contents: list[str]
    :type path: str
    """
    if not os.path.exists(path):
        os.makedirs(path)

    for src in contents or []:
        basename = os.path.basename(src)
        dst = path + "/" + basename
        logger.info(u'Moving Content: {0} => {1}'.format(src, dst))
        shutil.move(src, dst)


def read(path):
    """
    Return the contents of the given path
    
    :type path: str 
    :rtype: str 
    """
    data = ""
    path = normPath(path)

    if os.path.isfile(path):
        with open(path, "r") as f:
            data = f.read() or data

    data = resolveRelativePath(path, data)

    return data


def write(path, data):
    """
    Write the given data to the given path location on disc.

    :type path: str 
    :type data: str 
    :rtype: None 
    """
    path = normPath(path)
    dirname = os.path.dirname(path)

    data = formatRelativePath(path, data)

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(path, "w") as f:
        f.write(data)


def updateJson(path, data):
    """
    Update a json file with the given data.

    :type path: str
    :type data: dict
    :rtype: None
    """
    data_ = readJson(path)
    data_.update(data)
    saveJson(path, data_)


def saveJson(path, data):
    """
    Write a python dict to a json file.

    :type path: str
    :type data: dict
    :rtype: None
    """
    path = normPath(path)
    data = json.dumps(data, indent=4)
    write(path, data)


def readJson(path):
    """
    Read a json file to a python dict.

    :type path: str
    :rtype: dict
    """
    logger.debug(u'Reading json file: {0}'.format(path))

    path = normPath(path)

    data = read(path) or "{}"

    try:
        data = json.loads(data)
    except Exception, e:
        logger.exception(e)

    return data


def resolveRelativePath(path, data, sep="/"):
    """
    Resolve all relative paths in the given data object.
    
    This function is not pretty, however, the complexity increases when 
    making it a loop.
    
    :type path: str
    :type data: str 
    :type sep: str 
    :rtype: str 
    """
    relPath = os.path.dirname(path)
    relPath2 = os.path.dirname(relPath)
    relPath3 = os.path.dirname(relPath2)

    if relPath.endswith(sep):
        relPath = relPath[:-1]

    if relPath2.endswith(sep):
        relPath2 = relPath2[:-1]

    if relPath3.endswith(sep):
        relPath3 = relPath3[:-1]

    data = data.replace('\"...' + sep, '"' + relPath3 + sep)
    data = data.replace('\"..' + sep, '"' + relPath2 + sep)
    data = data.replace('\".' + sep, '"' + relPath + sep)

    return data


def formatRelativePath(path, data, sep="/"):
    """
    Replace all paths in the data that start with the given path.

    This function is not pretty, however, the complexity increases when 
    making it a loop.

    :type path: str
    :type data: str 
    :rtype: str 
    """
    relPath = os.path.dirname(path)
    relPath2 = os.path.dirname(relPath)
    relPath3 = os.path.dirname(relPath2)

    if not relPath.endswith(sep):
        relPath = relPath + sep

    if not relPath2.endswith(sep):
        relPath2 = relPath2 + sep

    if not relPath3.endswith(sep):
        relPath3 = relPath3 + sep

    data = data.replace(relPath, '.' + sep)
    data = data.replace(relPath2, '..' + sep)
    data = data.replace(relPath3, '...' + sep)

    return data


def generateUniquePath(path, attempts=1000):
    """
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


def normPath(path):
    """
    Return a normalized path with forward slashes
    
    :type path: str
    :rtype: str 
    """
    return path.replace("\\", "/")


def splitPath(path):
    """
    :type path: str
    :rtype: list[str]
    """
    path = normPath(path)
    filename, extension = os.path.splitext(path)
    return os.path.dirname(filename), os.path.basename(filename), extension


def listToString(data):
    """
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
    :type data: str
    :rtype: list
    """
    data = '["' + str(data) + '"]'
    data = data.replace(' ', '')
    data = data.replace(',', '","')
    return eval(data)


def listPaths(path):
    """
    :type path: str
    :rtype: collections.Iterable[str]
    """
    for name in os.listdir(path):
        value = path + "/" + name
        yield value


def findPaths(
        path,
        match=None,
        direction=Direction.Down,
        depth=3
):
    """
    Return a list of file paths by walking the root path either up or down.

    Example:
        path = r'C:\Users\Hovel\Dropbox\libraries\animation\Malcolm\anim'

        def matchSets(path):
            return path.endswith(".set")

        for path in findPaths(path, match=matchSets, direction=Direction.Up, depth=5):
            print path

        for path in findPaths(path, match=lambda path: path.endswith(".anim"),
                              direction=Direction.Down, depth=3):
            print path

    :type path: str
    :type key: func
    :type depth: int
    :type direction: Direction
    :rtype: collections.Iterable[str]
    """
    if os.path.isfile(path):
        path = os.path.dirname(path)

    if depth <= 1 and direction == Direction.Down:
        paths = listPaths(path)

    elif direction == Direction.Down:
        paths = walk(path, match=match, depth=depth)

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


def walk(path, match=None, depth=3):
    """
    :type path: str
    :type match: func
    :type depth: int
    :rtype: collections.Iterable[str]
    """
    path = path.rstrip(os.path.sep)
    path = os.path.realpath(path)

    maxDepth = depth

    assert os.path.isdir(path)
    startDepth = path.count(os.path.sep)

    for root, dirs, files in os.walk(path):
        files.extend(dirs)

        for filename in files:
            path = os.path.join(root, filename)
            path = normPath(path)
            if match is None or match(path):
                yield path

        currentDepth = root.count(os.path.sep)
        if (currentDepth - startDepth) >= maxDepth:
            del dirs[:]


def timeAgo(timeStamp):
    """
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


def logScreen(name, version="1.0.0", an="StudioLibrary", tid="UA-50172384-2"):
    """
    Send a screen view to google analytics.

    Example:
    logScreen("fudgeOpenUI")

    :type name: str
    :type version: str
    :type an: str
    :type tid: str
    :rtype: None
    """
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
            urllib2.urlopen(url, None, 1.0)
        except Exception:
            pass

    t = threading.Thread(target=_send, args=(url,))
    t.start()


def testRelativePaths():
    """
    A simple test for resolving relative paths.
    
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
    ".../path/head.anim": {},
    "../path/face.anim": {},
    "./path/hand.anim": {},    
    }
    """

    data_ = formatRelativePath("P:/test/relative/file.database", data)
    msg = "Data does not match {} {}".format(expected, data_)
    assert data_ == expected, msg

    data_ = resolveRelativePath("P:/test/relative/file.database", data_)
    msg = "Data does not match {} {}".format(data, data_)
    assert data_ == data, msg


if __name__ == "__main__":
    testRelativePaths()
