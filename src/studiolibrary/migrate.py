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

import studiolibrary


logger = logging.getLogger(__name__)


def migrate():
    """
    Migrate any old data to new data.

    :rtype: None
    """
    try:
        migrateLibraries()
    except Exception, e:
        logger.exception(e)


def migrateLibraries():
    """
    Migrate all the old libraries to the new 1.21+ library location.

    :rtype: None
    """
    HOME_PATH = os.getenv('APPDATA') or os.getenv('HOME')
    OLD_LIBRARIES_PATH = HOME_PATH + "/StudioLibrary/Library"
    NEW_LIBRARIES_PATH = HOME_PATH + "/StudioLibrary/Libraries"

    if os.path.exists(OLD_LIBRARIES_PATH):
        for filename in os.listdir(OLD_LIBRARIES_PATH):

            libraryName = filename.replace(".dict", "").replace(".json", "")

            oldDictPath = os.path.join(OLD_LIBRARIES_PATH, libraryName + ".dict")
            oldJsonPath = os.path.join(OLD_LIBRARIES_PATH, libraryName + ".json")
            migratedPath = os.path.join(OLD_LIBRARIES_PATH, libraryName + ".migrated")

            newJsonPath = os.path.join(NEW_LIBRARIES_PATH, libraryName, "library.json")

            if os.path.exists(newJsonPath) or os.path.exists(migratedPath):
                continue

            msg = "Migrating old library: {0} -> {1}..."
            data = None

            if os.path.exists(oldJsonPath):
                msg = msg.format(oldJsonPath, newJsonPath)
                data = studiolibrary.readJson(oldJsonPath)

            elif os.path.exists(oldDictPath):
                msg = msg.format(oldDictPath, newJsonPath)
                data = studiolibrary.readDict(oldJsonPath)

            if data:
                logger.info(msg)
                studiolibrary.saveJson(newJsonPath, data)
                studiolibrary.saveJson(migratedPath, data)


if __name__ == "__main__":
    migrate()
