# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
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

import os

from studiovendor.Qt import QtGui
from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

import studioqt
import studiolibrary.widgets


class PreviewWidget(QtWidgets.QWidget):

    def __init__(self, item, *args):
        QtWidgets.QWidget.__init__(self, *args)
        studioqt.loadUi(self)

        self._item = item

        iconGroupBoxWidget = studiolibrary.widgets.GroupBoxWidget("Icon", self.ui.iconGroup)
        iconGroupBoxWidget.setObjectName("iconGroupBoxWidget")
        iconGroupBoxWidget.setPersistent(True)
        self.ui.iconTitleFrame.layout().addWidget(iconGroupBoxWidget)

        schema = item.loadSchema()
        if schema:
            self._formWidget = studiolibrary.widgets.FormWidget(self)
            self._formWidget.setObjectName(item.__class__.__name__ + "Form")
            self._formWidget.setSchema(item.loadSchema())
            self._formWidget.setValidator(self.validator)

            self.ui.formFrame.layout().addWidget(self._formWidget)

        self.ui.acceptButton.hide()
        self.ui.acceptButton.setText("Load")
        self.ui.acceptButton.clicked.connect(self.accept)

        self.createSequenceWidget()

        if item.NAME:
            self.ui.titleFrame.setVisible(True)
            self.ui.titleLabel.setText(item.NAME)
        else:
            self.ui.titleFrame.setVisible(False)

        if item.TYPE_ICON_PATH:
            self.ui.titleIcon.setVisible(True)
            self.ui.titleIcon.setPixmap(QtGui.QPixmap(item.TYPE_ICON_PATH))
        else:
            self.ui.titleIcon.setVisible(False)

        self._item.dataChanged.connect(self._itemDataChanged)

        self.updateThumbnailSize()

    def _itemDataChanged(self, *args, **kwargs):
        """
        Triggered when the current item data changes.

        :type args: list
        :type kwargs: dict
        """
        self.updateIcon()

    def setTitle(self, title):
        """
        Set the title of the preview widget.

        :type title: str
        """
        self.ui.titleLabel.setText(title)

    def validator(self, **kwargs):
        """
        Validator used for validating the load arguments.

        :type kwargs: dict
        """
        self._item.loadValidator(**kwargs)
        self.updateIcon()

    def createSequenceWidget(self):
        """
        Create a sequence widget to replace the static thumbnail widget.

        :rtype: None
        """
        self.ui.sequenceWidget = studiolibrary.widgets.ImageSequenceWidget(self.ui.iconFrame)

        self.ui.iconFrame.layout().insertWidget(0, self.ui.sequenceWidget)

        self.updateIcon()

    def updateIcon(self):
        """Update the thumbnail icon."""
        icon = self._item.thumbnailIcon()
        if icon:
            self.ui.sequenceWidget.setIcon(icon)

        if self._item.imageSequencePath():
            self.ui.sequenceWidget.setDirname(self.item().imageSequencePath())

    def close(self):
        """
        Overriding the close method so save the persistent data.

        :rtype: None
        """
        if self._formWidget:
            self._formWidget.savePersistentValues()
        QtWidgets.QWidget.close(self)

    def resizeEvent(self, event):
        """
        Overriding to adjust the image size when the widget changes size.

        :type event: QtCore.QSizeEvent
        """
        self.updateThumbnailSize()

    def updateThumbnailSize(self):
        """
        Update the thumbnail button to the size of the widget.

        :rtype: None
        """
        width = self.width() - 5
        if width > 150:
            width = 150

        size = QtCore.QSize(width, width)

        self.ui.iconFrame.setMaximumSize(size)
        self.ui.iconGroup.setMaximumHeight(width)

        self.ui.sequenceWidget.setIconSize(size)
        self.ui.sequenceWidget.setMinimumSize(size)
        self.ui.sequenceWidget.setMaximumSize(size)

    def accept(self):
        """Called when the user clicks the load button."""
        kwargs = self._formWidget.values()
        self._item.load(**kwargs)
