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

import studiolibrary

# The following items are registered on import.
from studiolibraryitems import poseitem
from studiolibraryitems import animitem
from studiolibraryitems import mirroritem
from studiolibraryitems import setsitem


studiolibrary.Analytics.ENABLED = True
studiolibrary.Analytics.DEFAULT_ID = "UA-50172384-1"

# Shared data
# studiolibrary.Library.ITEM_DATA_PATH = "{root}/.studiolibrary/item_data.json"
# studiolibrary.Library.FOLDER_DATA_PATH = "{root}/.studiolibrary/folder_data.json"

# Meta paths are still named record.json and camel case for legacy reasons
studiolibrary.LibraryItem.META_PATH = "{path}/.studioLibrary/record.json"
