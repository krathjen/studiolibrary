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
    analytics=True,
    **kwargs
):
    """
    The main entry point for creating and loading a library.

    :type name: str
    :type path: str
    :type show: bool
    :type analytics: bool
    :type kwargs: dict

    :rtype: studiolibrary.Library
    """
    studiolibrary.analytics().setEnabled(analytics)

    isNewUser = not path and not studiolibrary.libraries()

    if show and isNewUser:
        library = studiolibrary.showWelcomeDialog(showOnAccepted=False)
    elif name:
        library = studiolibrary.Library.instance(name)
    else:
        library = studiolibrary.Library.default()

    if path:
        library.setPath(path)

    library.setKwargs(kwargs)

    studiolibrary.enableMayaClosedEvent()

    if show:
        library.show()

    return library
