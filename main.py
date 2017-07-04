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


def main(
        name=None,
        path=None,
        show=True,
        lock=False,
        superusers=None,
        lockFolder=None,
        unlockFolder=None,
):
    """
    The main entry point for creating and loading a library.
    
    This is a convenience method.

    :type name: str or None
    :type path: str or None
    :type show: bool
    :type lock: bool
    :type superusers: str
    :type lockFolder: str
    :type unlockFolder: str
    
    :rtype: studiolibrary.LibraryWidget
    """
    cls = studiolibrary.LIBRARY_WIDGET_CLASS or studiolibrary.LibraryWidget

    libraryWidget = cls.instance(name, path)

    libraryWidget.setLocked(lock)
    libraryWidget.setSuperusers(superusers)
    libraryWidget.setLockRegExp(lockFolder)
    libraryWidget.setUnlockRegExp(unlockFolder)

    if show:
        libraryWidget.show()

    return libraryWidget


if __name__ == "__main__":

    import logging
    import studioqt

    # Turn on basic logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s: %(funcName)s: %(message)s',
        filemode='w'
    )

    # Run the Studio Library in a QApplication
    with studioqt.app():
        studiolibrary.main()
