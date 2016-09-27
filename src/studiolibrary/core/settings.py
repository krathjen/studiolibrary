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

from . import metafile


__all__ = ["Settings"]


class Settings(metafile.MetaFile):

    _instances = {}

    DEFAULT_PATH = os.getenv('APPDATA') or os.getenv('HOME')

    @classmethod
    def instance(cls, scope, name):
        """
        :type scope: str
        :type name: str
        :rtype: Settings
        """
        key = scope + "/" + name

        if key not in cls._instances:
            cls._instances[key] = cls(scope, name)

        return cls._instances[key]

    def __init__(self, scope, name):
        """
        :type scope: str
        :type name: str
        """
        self._path = None
        self._name = name
        self._scope = scope
        metafile.MetaFile.__init__(self, "")

    def path(self):
        """
        :rtype: str
        """
        if not self._path:
            self._path = os.path.join(Settings.DEFAULT_PATH, self._scope, self._name + ".json")
        return self._path
