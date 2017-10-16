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
        cls=None,
        name="",
        path="",
        show=True,
        lock=False,
        superusers=None,
        lockRegExp=None,
        unlockRegExp=None,
):
    """
    Convenience method for creating and loading a library widget instance.

    :type cls: studiolibrary.LibraryWidget.__class__ or None
    :type name: str
    :type path: str
    :type show: bool
    :type lock: bool
    :type superusers: list[str] or None
    :type lockRegExp: str or None
    :type unlockRegExp: str or None

    :rtype: studiolibrary.LibraryWidget
    """
    cls = cls \
        or studiolibrary.LIBRARY_WIDGET_CLASS \
        or studiolibrary.LibraryWidget

    libraryWidget = cls.instance(
        name,
        path,
        show=show,
        lock=lock,
        superusers=superusers,
        lockRegExp=lockRegExp,
        unlockRegExp=unlockRegExp,
    )

    return libraryWidget


if __name__ == "__main__":

    # Run the Studio Library in a QApplication instance
    with studiolibrary.app():
        studiolibrary.main()
