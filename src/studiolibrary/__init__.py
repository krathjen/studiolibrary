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

__version__ = "2.13.2"
__build_date__ = "September 17, 2023"


def version():
    """
    Return the current version of the Studio Library

    :rtype: str
    """
    return __version__


from studiolibrary import config
from studiolibrary import resource
from studiolibrary.utils import *
from studiolibrary.library import Library
from studiolibrary.libraryitem import LibraryItem
from studiolibrary.main import main
