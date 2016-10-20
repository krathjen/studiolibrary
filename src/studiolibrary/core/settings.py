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
    def instance(cls, *args):
        """
        Return the settings instance for the given scope.

        :type args: list[str]
        :rtype: Settings
        """
        key = "/".join(args)

        if key not in cls._instances:
            cls._instances[key] = cls(*args)

        return cls._instances[key]

    def __init__(self, *args):
        """
        :type args: list[str]
        """
        self._path = None
        self._args = args
        metafile.MetaFile.__init__(self, "")

    def path(self):
        """
        Return the path.

        :rtype: str
        """
        if not self._path:
            scope = os.path.join(*self._args)
            self._path = os.path.join(Settings.DEFAULT_PATH, scope + ".json")
        return self._path
