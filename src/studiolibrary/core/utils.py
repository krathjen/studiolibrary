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

import re
import os
import json
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
    "splitPath",
    "findPaths",
    "Direction",
    "downloadUrl",
    "stringToList",
    "listToString",
    "openLocation",
    "validatePath",
    "validateString",
    "generateUniquePath",
    "generateUniqueName",
    "ValidatePathError",
    "ValidateStringError",
]


RE_VALIDATE_PATH = re.compile("^[\\\.:/\sA-Za-z0-9_-]*$")
RE_VALIDATE_STRING = re.compile("^[\sA-Za-z0-9_-]+$")


class StudioLibraryError(Exception):

    """Base exception for any studio library errors."""


class ValidatePathError(StudioLibraryError):

    """Raised when a path has invalid characters."""


class ValidateStringError(StudioLibraryError):

    """Raised when a string has invalid characters."""


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


def validatePath(path):
    """
    :type path: str
    :raise ValidatePathError
    """
    if not RE_VALIDATE_PATH.match(path):

        msg = (
            'Invalid characters in path "{0}"! '
            'Please only use letters, numbers and forward slashes.'
        )

        msg = msg.format(path)
        raise ValidatePathError(msg)


def validateString(text):
    """
    :type text: str
    :raise ValidateStringError
    """
    if not RE_VALIDATE_STRING.match(text):

        msg = 'Invalid string "{0}"! Please only use letters and numbers'
        msg = msg.format(str(text))
        raise ValidateStringError(msg)


def moveContents(contents, path):
    """
    Move the given contents to the specified path.

    :type contents: list[str]
    """
    for src in contents or []:
        basename = os.path.basename(src)
        dst = path + "/" + basename
        logger.info('Moving Content: {0} => {1}'.format(src, dst))
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
    data = {}

    if os.path.exists(path):
        with open(path, "r") as f:
            data_ = f.read()
            if data_:
                data = json.loads(data_)
    return data


def saveDict(path, data):
    """
    Write a python dict to disc.

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
    Read a python dict from disc.

    :type path: str
    :rtype: dict
    """
    data = {}

    if os.path.exists(path):
        with open(path, "r") as f:
            data_ = f.read()
            if data_:
                data = eval(data_, {})
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

    msg = "Cannot generate unique name for '{name}'"
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
    path_ = "{dirname}/{name} ({number}){extension}"

    while os.path.exists(path):
        attempt += 1

        path = path_.format(
            name=name,
            number=attempt,
            dirname=dirname,
            extension=extension
        )

        if attempt >= attempts:
            msg = "Cannot generate unique name for path {path}"
            msg = msg.format(path=path)
            raise ValueError(msg)

    return path


def openLocation(path):
    """
    :type path: str
    :rtype: None
    """
    if isLinux():
        os.system('konqueror "%s"&' % path)
    elif isWindows():
        os.startfile('%s' % path)
    elif isMac():
        subprocess.call(["open", "-R", path])


def copyPath(srcPath, dstPath):
    """
    :type srcPath: str
    :type dstPath: str
    :rtype: None
    """
    import stat
    import shutil

    if not os.path.exists(srcPath):
        raise IOError("Path doesn't exists '%s'" % srcPath)

    if os.path.isfile(srcPath):
        shutil.copyfile(srcPath, dstPath)
    elif os.path.isdir(srcPath):
        shutil.copytree(srcPath, dstPath)

    ctime = os.stat(srcPath)[stat.ST_CTIME]
    mtime = os.stat(srcPath)[stat.ST_MTIME]
    os.utime(dstPath, (ctime, mtime))


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
    :type data: list[]
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
    :rtype: list[]
    """
    data = '["' + str(data) + '"]'
    data = data.replace(' ', '')
    data = data.replace(',', '","')
    return eval(data)


def listPaths(path):
    """
    :type path: str
    :rtype: list[str]
    """
    results = []
    for name in os.listdir(path):
        value = path + "/" + name
        results.append(value)
    return results


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
    :rtype: list[str]
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
    :rtype: list[str]
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


def walk(path, match=None, ignore=None, depth=3,):
    """
    :type path: str
    :type match: func
    :type depth: int
    :rtype: list[str]
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


# TODO: Add better error handling
def downloadUrl(url, destination=None):
    """
    :type url: str
    :type destination: str
    :rtype : str
    """
    try:
        if destination:
            try:
                f = open(destination, 'w')
                f.close()
            except:
                print "Studio Library: The current user does not have permission for the directory %s" % destination
                #  Should raise a permissions error
                return

        try:
            import urllib2
            f = urllib2.urlopen(url, None, 2.0)
        except Exception:
            return

        data = f.read()

        if destination:
            f = open(destination, 'wb')
            f.write(data)
            f.close()

        return data
    except:
        raise
        # Sould raise an error


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