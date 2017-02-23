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
