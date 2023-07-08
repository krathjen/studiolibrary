# Copyright 2020 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or modify it 
# under the terms of the GNU Lesser General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. This library is distributed in the 
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import copy

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore

import studioqt


class Icon(QtGui.QIcon):

    @classmethod
    def fa(cls, path, **kwargs):
        """
        Create a new icon with the given path, options and state.
        
        Example:
            icon = studioqt.Icon.fa(
                path,
                color="rgb(255,255,255)"
                color_disabled="rgba(0,200,200,20)",
            )

        :type path: str
        :type kwargs: dict
        
        :rtype: studioqt.Icon 
        """
        color = kwargs.get('color', QtGui.QColor(0, 0, 0))

        pixmap = studioqt.Pixmap(path)
        pixmap.setColor(color)

        valid_options = [
            'active',
            'selected',
            'disabled',
            'on',
            'off',
            'on_active',
            'on_selected',
            'on_disabled',
            'off_active',
            'off_selected',
            'off_disabled',
            'color',
            'color_on',
            'color_off',
            'color_active',
            'color_selected',
            'color_disabled',
            'color_on_selected',
            'color_on_active',
            'color_on_disabled',
            'color_off_selected',
            'color_off_active',
            'color_off_disabled',
        ]

        default = {
            "on_active": kwargs.get("active", studioqt.Pixmap(path)),
            "off_active": kwargs.get("active", studioqt.Pixmap(path)),
            "on_disabled": kwargs.get("disabled", studioqt.Pixmap(path)),
            "off_disabled": kwargs.get("disabled", studioqt.Pixmap(path)),
            "on_selected": kwargs.get("selected", studioqt.Pixmap(path)),
            "off_selected": kwargs.get("selected", studioqt.Pixmap(path)),
            "color_on_active": kwargs.get("color_active", color),
            "color_off_active": kwargs.get("color_active", color),
            "color_on_disabled": kwargs.get("color_disabled", color),
            "color_off_disabled": kwargs.get("color_disabled", color),
            "color_on_selected": kwargs.get("color_selected", color),
            "color_off_selected": kwargs.get("color_selected", color),
        }

        default.update(kwargs)
        kwargs = copy.copy(default)

        for option in valid_options:
            if 'color' in option:
                kwargs[option] = kwargs.get(option, color)
            else:
                svg_path = kwargs.get(option, path)
                kwargs[option] = studioqt.Pixmap(svg_path)

        options = {
            QtGui.QIcon.On: {
                QtGui.QIcon.Normal: (kwargs['color_on'], kwargs['on']),
                QtGui.QIcon.Active: (kwargs['color_on_active'], kwargs['on_active']),
                QtGui.QIcon.Disabled: (kwargs['color_on_disabled'], kwargs['on_disabled']),
                QtGui.QIcon.Selected: (kwargs['color_on_selected'], kwargs['on_selected'])
            },

            QtGui.QIcon.Off: {
                QtGui.QIcon.Normal: (kwargs['color_off'], kwargs['off']),
                QtGui.QIcon.Active: (kwargs['color_off_active'], kwargs['off_active']),
                QtGui.QIcon.Disabled: (kwargs['color_off_disabled'], kwargs['off_disabled']),
                QtGui.QIcon.Selected: (kwargs['color_off_selected'], kwargs['off_selected'])
            }
        }

        icon = cls(pixmap)

        for state in options:
            for mode in options[state]:
                color, pixmap = options[state][mode]

                pixmap = studioqt.Pixmap(pixmap)
                pixmap.setColor(color)

                icon.addPixmap(pixmap, mode, state)

        return icon

    def setColor(self, color, size=None):
        """
        :type color: QtGui.QColor
        :rtype: None
        """
        icon = self
        size = size or icon.actualSize(QtCore.QSize(256, 256))
        pixmap = icon.pixmap(size)

        if not self.isNull():
            painter = QtGui.QPainter(pixmap)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
            painter.setBrush(color)
            painter.setPen(color)
            painter.drawRect(pixmap.rect())
            painter.end()

        icon = QtGui.QIcon(pixmap)
        self.swap(icon)

        if self._badgeEnabled:
            self.updateBadge()

    def __init__(self, *args, **kwargs):
        super(Icon, self).__init__(*args, **kwargs)

        self._badgeColor = None
        self._badgeEnabled = False

    def badgeColor(self):
        return self._badgeColor

    def setBadgeColor(self, color):
        self._badgeColor = color

    def badgeEnabled(self):
        return self._badgeEnabled

    def setBadgeEnabled(self, enabled):
        self._badgeEnabled = enabled

    def updateBadge(self):
        """
        """
        color = self.badgeColor() or QtGui.QColor(240, 240, 100)
        size = self.actualSize(QtCore.QSize(256, 256))

        pixmap = self.pixmap(size)
        painter = QtGui.QPainter(pixmap)

        pen = QtGui.QPen(color)
        pen.setWidth(0)
        painter.setPen(pen)

        painter.setBrush(color)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawEllipse(0, 0, size.height()/3.0, size.width()/3.0)
        painter.end()

        icon = QtGui.QIcon(pixmap)
        self.swap(icon)
