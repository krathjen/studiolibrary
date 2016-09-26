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

from studioqt import QtGui
from studioqt import QtWidgets

import studioqt


class Resource(object):

    DEFAULT_DIRNAME = ""

    def __init__(self, dirname=None):
        """
        :type dirname: str
        """
        dirname = dirname.replace("\\", "/")
        self._dirname = dirname or self.DEFAULT_DIRNAME

    def dirname(self):
        """
        :rtype: str
        """
        return self._dirname

    def get(self, *token):
        """
        :rtype: str
        """
        return os.path.join(self.dirname(), *token)

    def icon(self, name, extension="png", color=None):
        """
        :type name: str
        :type extension: str
        :rtype: QtGui.QIcon
        """
        pixmap = self.pixmap(name, extension=extension, color=color)
        return QtGui.QIcon(pixmap)

    def pixmap(self, name, scope="icons", extension="png", color=None):
        """
        :type name: str
        :type extension: str
        :rtype: QtWidgets.QPixmap
        """
        path = self.get(scope, name + "." + extension)
        pixmap = studioqt.Pixmap(path)

        if color:
            pixmap.setColor(color)

        return pixmap
