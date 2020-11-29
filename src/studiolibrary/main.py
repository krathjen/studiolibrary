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

import studioqt
import studiolibrary


def main(*args, **kwargs):
    """
    Convenience method for creating/showing a library widget instance.

    return studiolibrary.LibraryWindow.instance(
        name="",
        path="",
        show=True,
        lock=False,
        superusers=None,
        lockRegExp=None,
        unlockRegExp=None
    )

    :rtype: studiolibrary.LibraryWindow
    """
    # Reload all Studio Library modules when Shift is pressed.
    # This is for developers to test their changes in a DCC application.
    if studioqt.isShiftModifier():
        import studiolibrary
        studiolibrary.reload()

    # Register all the items from the config file.
    import studiolibrary
    studiolibrary.registerItems()

    if studiolibrary.isMaya():
        from studiolibrarymaya import mayalibrarywindow
        libraryWindow = mayalibrarywindow.MayaLibraryWindow.instance(*args, **kwargs)
    else:
        from studiolibrary import librarywindow
        libraryWindow = librarywindow.LibraryWindow.instance(*args, **kwargs)

    return libraryWindow


if __name__ == "__main__":

    # Run the Studio Library in a QApplication instance
    with studiolibrary.app():
        studiolibrary.main()
