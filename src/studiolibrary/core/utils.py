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

import re
import os
import json
import shutil
import logging
import platform
import subprocess
from datetime import datetime


__all__ = [
    "user",
    "walk",
    "isMaya",
    "isMac",
    "isLinux",
    "isWindows",
    "timeAgo",
    "saveDict",
    "readDict",
    "saveJson",
    "readJson",
    "listPaths",
    "findPaths",
    "copyPath",
    "movePath",
    "splitPath",
    "renamePath",
    "formatPath",
    "moveContents",
    "Direction",
    "stringToList",
    "listToString",
    "openLocation",
    "generateUniquePath",
    "generateUniqueName",
    "PathRenameError",
    "PathNotFoundError",
]


logger = logging.getLogger(__name__)


class PathRenameError(IOError):
    """
    """


class PathNotFoundError(IOError):
    """
    """


class Direction:
    Up = "up"
    Down = "down"


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


def renamePath(src, dst, extension=None, force=False):
    """
    Rename the given src path to given destination path.

    :type src: str
    :type dst: str
    :type extension: str
    :type force: bool
    :rtype: str
    """
    src = src.replace("\\", "/")
    dst = dst.replace("\\", "/")

    dirname = os.path.dirname(src)

    if "/" not in dst:
        dst = dirname + "/" + dst

    if extension and extension not in dst:
        dst += extension

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
    """
    for src in contents or []:
        basename = os.path.basename(src)
        dst = path + "/" + basename
        logger.info(u'Moving Content: {0} => {1}'.format(src, dst))
        shutil.move(src, dst)


def saveJson(path, data):
    """
    Write a python dict to a json file.

    :type path: str
    :type data: dict
    :rtype: None
    """
    dirname = os.path.dirname(path)

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(path, "w") as f:
        data = json.dumps(data, indent=4)
        f.write(data)


def readJson(path):
    """
    Read a json file to a python dict.

    :type path: str
    :rtype: dict
    """
    logger.debug(u'Reading json file: {0}'.format(path))

    data = {}

    if os.path.isfile(path):
        with open(path, "r") as f:
            data_ = f.read()
            if data_:
                try:
                    data = json.loads(data_)
                except Exception, e:
                    logger.exception(e)
    return data


def saveDict(path, data):
    """
    Write a python dict to the given path on disc.

    :type path: str
    :type data: dict
    :rtype: None
    """
    dirname = os.path.dirname(path)

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(path, "w") as f:
        d = str(data)
        test = eval(d, {})  # Test that the data can be converted.
        f.write(d)


def readDict(path):
    """
    Read a python dict from the given path on disc.

    :type path: str
    :rtype: dict
    """
    data = {}
    logger.debug(u'Reading dict file: {0}'.format(path))

    if os.path.isfile(path):
        with open(path, "r") as f:
            data_ = f.read()
            if data_:
                try:
                    data = eval(data_, {})
                except Exception, e:
                    logger.exception(e)
    return data


def generateUniqueName(name, names, attempts=1000):
    """
    :type name: str
    :type names: list[str]
    :type attempts: int
    :rtype: str
    """
    for i in range(1, attempts):
        result = name + str(i)
        if result not in names:
            return result

    msg = u'Cannot generate unique name for "{name}"'
    msg = msg.format(name=name)
    raise StudioLibraryError(msg)


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


def openLocation(path):
    """
    Open the file explorer at the given path location.

    :type path: str
    :rtype: None
    """
    if isLinux():
        os.system('konqueror "%s"&' % path)
    elif isWindows():
        os.startfile('%s' % path)
    elif isMac():
        subprocess.call(["open", "-R", path])


def splitPath(path):
    """
    :type path: str
    :rtype: list[str]
    """
    path = path.replace("\\", "/")
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


def findPaths(path, match=None, ignore=None, direction=Direction.Down, depth=3):
    """
    Return a list of file paths by walking the root path either up or down.

    Example:
        path = r'C:\Users\Hovel\Dropbox\libraries\animation\Malcolm\anim'

        for path in findPaths(path, match=lambda path: path.endswith(".set"), direction=Direction.Up, depth=5):
            print path

        for path in findPaths(path, match=lambda path: path.endswith(".anim"), direction=Direction.Down, depth=3):
            print path

    :type path: str
    :type match: func
    :type depth: int
    :type direction: Direction
    :rtype: collections.Iterable[str]
    """
    if os.path.isfile(path):
        path = os.path.dirname(path)

    if depth <= 1 and direction == Direction.Down:
        paths = listPaths(path)

    elif direction == Direction.Down:
        paths = walk(path, match=match, depth=depth, ignore=ignore)

    elif direction == Direction.Up:
        paths = walkup(path, match=match, depth=depth)

    else:
        raise Exception("Direction not supported {0}".format(direction))

    return paths


def walkup(path, match=None, depth=3):
    """
    :type path: str
    :type match: func
    :type depth: int
    :rtype: collections.Iterable[str]
    """
    sep = "/"
    path = os.path.realpath(path)
    path = path.replace("\\", "/")

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
                        yield path


def walk(path, match=None, ignore=None, depth=3):
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

            valid = True
            for pattern in ignore or []:
                if pattern in path:
                    valid = False
                    break

            if valid and (match is None or match(path)):
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