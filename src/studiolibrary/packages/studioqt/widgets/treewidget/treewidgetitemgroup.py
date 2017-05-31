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

from studioqt import QtCore
from studioqt import QtWidgets


__all__ = ["TreeWidgetItemGroup"]


class TreeWidgetItemGroup(QtWidgets.QTreeWidgetItem):

    def __init__(self, parent, text):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self._url = None
        self._path = None

        self.setDisabled(True)

        self.setText(0, text)

        font = self.font(0)
        font.setBold(True)

        self.setFont(0, font)

    def update(self):
        pass

    def text(self, column=0):
        return QtWidgets.QTreeWidgetItem.text(self, column)

    def path(self):
        if not self._path:
            self._path = self.text()
        return self._path

    def setPath(self, path):
        self._path = path

    def url(self):
        if not self._url:
            self._url = QtCore.QUrl(self.path())
        return self._url

    def setUrl(self, url):
        self._url = url

    def settings(self):
        return {}

    def setSettings(self, settings):
        pass
