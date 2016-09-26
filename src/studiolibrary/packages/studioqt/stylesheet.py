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
import re

import studioqt


class StyleSheet(object):

    @classmethod
    def fromPath(cls, path, **kwargs):
        """
        :type path: str
        :rtype: str
        """
        styleSheet = cls()
        data = styleSheet.read(path)
        data = StyleSheet.format(data, **kwargs)
        styleSheet.setData(data)
        return styleSheet

    @classmethod
    def fromText(cls, text, options=None):
        """
        :type text: str
        :rtype: str
        """
        styleSheet = cls()
        data = StyleSheet.format(text, options=options)
        styleSheet.setData(data)
        return styleSheet

    def __init__(self):
        self._data = ""

    def setData(self, data):
        """
        :type data: str
        """
        self._data = data

    def data(self):
        """
        :rtype: str
        """
        return self._data

    @staticmethod
    def read(path):
        """
        :type path: str
        :rtype: str
        """
        data = ""

        if os.path.isfile(path):
            with open(path, "r") as f:
                data = f.read()

        return data

    @staticmethod
    def format(data=None, options=None, dpi=1):
        """
        :type data:
        :type options: dict
        :rtype: str
        """
        if options is not None:
            keys = options.keys()
            keys.sort(key=len, reverse=True)
            for key in keys:
                data = data.replace(key, options[key])

        reDpi = re.compile("[0-9]+[*]DPI")
        newData = []

        for line in data.split("\n"):
            dpi_ = reDpi.search(line)

            if dpi_:
                new = dpi_.group().replace("DPI", str(dpi))
                val = int(eval(new))
                line = line.replace(dpi_.group(), str(val))

            newData.append(line)

        data = "\n".join(newData)
        return data
