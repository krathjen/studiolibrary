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
