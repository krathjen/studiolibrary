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


def main(*args, **kwargs):
    """
    Convenience method for creating/showing a MayaLibraryWidget instance.

    return studiolibrarymaya.MayaLibraryWidget.instance(
        name="",
        path="",
        show=True,
        lock=False,
        superusers=None,
        lockRegExp=None,
        unlockRegExp=None
    )

    :rtype: studiolibrarymaya.MayaLibraryWidget
    """
    import studiolibrarymaya

    studiolibrarymaya.registerItems()
    studiolibrarymaya.enableMayaClosedEvent()

    if studiolibrary.isMaya():
        import studiolibrarymaya.mayalibrarywidget
        cls = studiolibrarymaya.mayalibrarywidget.MayaLibraryWidget
    else:
        cls = studiolibrary.LibraryWidget

    libraryWidget = cls.instance(*args, **kwargs)

    return libraryWidget


if __name__ == "__main__":

    # Run the Studio Library in a QApplication instance
    with studiolibrary.app():
        main()
