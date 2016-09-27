# Copyright 2015 by Kurt Rathjen. All Rights Reserved.
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
import sys
import logging

import studiolibrary
import studioqt

__encoding__ = sys.getfilesystemencoding()

PATH = unicode(os.path.abspath(__file__), __encoding__)
DIRNAME = os.path.dirname(PATH).replace('\\', '/')
RESOURCE_DIRNAME = DIRNAME + "/resource"


_resource = None


def resource():
    """
    :rtype: studioqt.Resource
    """
    global _resource

    if not _resource:
        _resource = studioqt.Resource(dirname=RESOURCE_DIRNAME)

    return _resource


def setDebugMode(libraryWidget, value):
    """
    Triggered when the user chooses debug mode.

    :type level: int
    :rtype: None
    """
    if value:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger_ = logging.getLogger("mutils")
    logger_.setLevel(level)

    logger_ = logging.getLogger("studiolibraryitems")
    logger_.setLevel(level)


studiolibrary.LibraryWidget.globalSignal.debugModeChanged.connect(setDebugMode)
