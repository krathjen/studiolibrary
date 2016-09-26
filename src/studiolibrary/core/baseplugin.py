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

import os
import inspect
import logging

from studioqt import QtCore


__all__ = ["BasePlugin"]

logger = logging.getLogger(__name__)


class BasePlugin(QtCore.QObject):

    def __init__(self, parent=None):
        """
        :type parent: QtWidgets.QWidget
        """
        QtCore.QObject.__init__(self, parent)
        self._name = ""
        self._path = ""
        self._loaded = False

    def dirname(self):
        """
        :rtype: str
        """
        path = inspect.getfile(self.__class__)
        return os.path.dirname(path)

    def setName(self, name):
        """
        :type name: str
        :rtype: None
        """
        self._name = name

    def name(self):
        """
        :rtype: str
        """
        return self._name

    def setPath(self, path):
        """
        :type path: str
        """
        self._path = path

    def path(self):
        """
        :rtype: str
        """
        return self._path

    def isLoaded(self):
        """
        :rtype: bool
        """
        return self._loaded

    def setLoaded(self, value):
        """
        :type value: bool
        """
        self._loaded = value

    def load(self):
        """
        :rtype: None
        """

    def unload(self):
        """
        :rtype: None
        """