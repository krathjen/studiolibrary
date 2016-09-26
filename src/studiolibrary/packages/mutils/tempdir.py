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
import shutil
import getpass
import tempfile


__all__ = ["TempDir"]


class TempDir(object):

    def __init__(self, *args, **kwargs):
        """
        :type subDirs: list[str]
        """
        user = getpass.getuser().lower()
        tempdir = tempfile.gettempdir().replace("\\", "/")
        self._path = os.path.join(tempdir, "mutils", user, *args)

        if kwargs.get("clean", False):
            self.clean()

        if kwargs.get("makedirs", True):
            self.makedirs()

    def path(self):
        """
        :rtype: str
        """
        return self._path

    def clean(self):
        """
        :rtype: str
        """
        if os.path.exists(self.path()):
            shutil.rmtree(self.path())

    def makedirs(self):
        """
        :rtype: str
        """
        if not os.path.exists(self.path()):
            os.makedirs(self.path())

