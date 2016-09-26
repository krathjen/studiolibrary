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

import studioqt
import studiolibrary


def main(
    name=None,
    path=None,
    show=True,
    plugins=None,
    analytics=True,
    root=None,  # Legacy
    **kwargs
):
    """
    The main entry point for creating and loading a library.

    :type name: str
    :type path: str
    :type show: bool
    :type plugins: list[str]
    :type analytics: bool
    :type root: str
    :type kwargs: dict
    :rtype: studiolibrary.Library
    """
    studiolibrary.analytics().setEnabled(analytics)

    if not name:
        library = studiolibrary.Library.default()
    else:
        library = studiolibrary.Library.instance(name)

    if plugins is None:
        library.setPlugins(studiolibrary.Library.DEFAULT_PLUGINS)
    else:
        library.setPlugins(plugins)

    if root:  # Legacy
        path = root

    if path:
        library.setPath(path)

    studiolibrary.enableMayaClosedEvent()

    if show:
        with studioqt.app():
            library.show(**kwargs)

    return library
