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

"""
#---------------------------------------------------------------------------
# Saving a pose record
#---------------------------------------------------------------------------

from studiolibraryplugins import poseplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []

record = poseplugin.Record(path)
record.save(objects=objects)

#---------------------------------------------------------------------------
# Loading a pose record
#---------------------------------------------------------------------------

from studiolibraryplugins import poseplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

record = poseplugin.Record(path)
record.load(objects=objects, namespaces=namespaces, key=True, mirror=False)
"""

import os
import logging

from studioqt import QtCore

import studiolibrary
import studiolibraryplugins

from studiolibraryplugins import mayabaseplugin

try:
    import mutils
    import maya.cmds
except ImportError, msg:
    print msg


logger = logging.getLogger(__name__)


class Plugin(mayabaseplugin.Plugin):

    def __init__(self, library):
        """
        :type library: studiolibrary.Library
        """
        mayabaseplugin.Plugin.__init__(self, library)

        iconPath = studiolibraryplugins.resource().get("icons", "pose.png")

        self.setName("Pose")
        self.setExtension("pose")
        self.setIconPath(iconPath)

    def record(self, path=None):
        """
        :type path: str or None
        :rtype: Record
        """
        return Record(path=path, plugin=self)

    def createWidget(self, parent):
        """
        :type parent: QtWidgets.QWidget
        :rtype: PoseCreateWidget
        """
        record = self.record()
        return PoseCreateWidget(parent=parent, record=record)

    def previewWidget(self, parent, record):
        """
        :type parent: QtWidgets.QWidget
        :rtype: PosePreviewWidget
        """
        return PosePreviewWidget(parent=parent, record=record)


class PoseSignal(QtCore.QObject):
    """"""
    mirrorChanged = QtCore.Signal(bool)


class Record(mayabaseplugin.Record):

    poseSignal = PoseSignal()
    mirrorChanged = poseSignal.mirrorChanged

    def __init__(self, *args, **kwargs):
        """
        :type args: list
        :type kwargs: dict
        """
        mayabaseplugin.Record.__init__(self, *args, **kwargs)

        self._options = None
        self._isLoading = False
        self._autoKeyFrame = None

        self.setBlendingEnabled(True)
        self.setTransferClass(mutils.Pose)
        self.setTransferBasename("pose.dict")

        if not os.path.exists(self.transferPath()):
            self.setTransferBasename("pose.json")

    def isLoading(self):
        """
        :rtype: bool
        """
        return self._isLoading

    def isMirrorEnabled(self):
        """
        :rtype: bool
        """
        return self.settings().get("mirrorEnabled", False)

    def toggleMirror(self):
        """
        :rtype: None
        """
        mirror = self.isMirrorEnabled()
        mirror = False if mirror else True
        self.setMirrorEnabled(mirror)

    def setMirrorEnabled(self, value):
        """
        :type value: bool
        """
        self.settings().set("mirrorEnabled", value)
        self.mirrorChanged.emit(bool(value))

    def keyEnabled(self):
        """
        :rtype: bool
        """
        return self.settings().get("keyEnabled", False)

    def setKeyEnabled(self, value):
        """
        :type value: bool
        """
        self.settings().set("keyEnabled", value)

    def keyPressEvent(self, event):
        """
        :type event: QtGui.QEvent
        """
        mayabaseplugin.Record.keyPressEvent(self, event)

        if not event.isAutoRepeat():
            if event.key() == QtCore.Qt.Key_M:
                self.toggleMirror()

                blend = self.blendValue()
                mirror = self.isMirrorEnabled()

                if self.isBlending():
                    self.loadFromSettings(
                        blend=blend,
                        mirror=mirror,
                        batchMode=True,
                        showBlendMessage=True
                    )
                else:
                    self.loadFromSettings(
                        blend=blend,
                        refresh=True,
                        mirror=mirror,
                        batchMode=False,
                    )

    def mouseReleaseEvent(self, event):
        """
        Triggered when the mouse button is released on this record.

        :type event: QtCore.QMouseEvent
        """
        if self.isBlending():
            self.loadFromSettings(blend=self.blendValue(), refresh=False)

    def doubleClicked(self):
        """
        Triggered when the user double clicks the record.

        :rtype: None
        """
        self.loadFromSettings(clearSelection=False)

    def selectionChanged(self):
        """
        Triggered when the item is selected or deselected.

        :rtype: None
        """
        self._transferObject = None
        mayabaseplugin.Record.selectionChanged(self)

    def stopBlending(self):
        """
        This method is called from the base class to stop blending.

        :rtype: None
        """
        self._options = None
        mayabaseplugin.Record.stopBlending(self)

    def setBlendValue(self, value, load=True):
        """
        This method is called from the base class when blending.

        :type value: float
        :rtype: None
        """
        mayabaseplugin.Record.setBlendValue(self, value)

        if load:
            self.loadFromSettings(
                blend=value,
                batchMode=True,
                showBlendMessage=True
            )

    def loadFromSettings(
        self,
        blend=100.0,
        mirror=None,
        refresh=True,
        batchMode=False,
        clearSelection=True,
        showBlendMessage=False,
    ):
        """
        :type blend: float
        :type refresh: bool
        :type batchMode: bool
        :type clearSelection: bool
        :type showBlendMessage: bool
        """
        if self._options is None:
            self._options = dict()
            self._options["key"] = self.keyEnabled()
            self._options['mirror'] = self.isMirrorEnabled()
            self._options['namespaces'] = self.namespaces()
            self._options['mirrorTable'] = self.mirrorTable()
            self._options['objects'] = maya.cmds.ls(selection=True) or []

        if mirror is not None:
            self._options['mirror'] = mirror

        try:
            self.load(
                blend=blend,
                refresh=refresh,
                batchMode=batchMode,
                clearSelection=clearSelection,
                showBlendMessage=showBlendMessage,
                **self._options
            )
        except Exception, msg:
            self.showErrorDialog(msg)
            raise

    def load(
        self,
        objects=None,
        namespaces=None,
        blend=100.0,
        key=None,
        attrs=None,
        mirror=None,
        refresh=True,
        batchMode=False,
        mirrorTable=None,
        clearSelection=False,
        showBlendMessage=False,
    ):
        """
        :type objects: list[str]
        :type blend: float
        :type key: bool | None
        :type namespaces: list[str] | None
        :type refresh: bool | None
        :type mirror: bool | None
        :type batchMode: bool
        :type showBlendMessage: bool
        :type mirrorTable: mutils.MirrorTable
        """
        logger.debug("Loading pose '%s'" % self.path())

        mirror = mirror or self.isMirrorEnabled()

        # Update the blend value in case this method is called
        # without blending.
        self.setBlendValue(blend, load=False)

        if showBlendMessage and self.libraryWidget():
            self.libraryWidget().setToast("Blend: {0}%".format(blend))

        try:
            mayabaseplugin.Record.load(
                self,
                objects=objects,
                namespaces=namespaces,
                key=key,
                blend=blend,
                attrs=attrs,
                mirror=mirror,
                refresh=refresh,
                batchMode=batchMode,
                mirrorTable=mirrorTable,
                clearSelection=clearSelection,
            )
        except Exception:
            self.stopBlending()
            raise

        finally:
            if not batchMode:
                self.stopBlending()

        logger.debug("Loaded pose '%s'" % self.path())


class PoseCreateWidget(mayabaseplugin.CreateWidget):
    def __init__(self, *args, **kwargs):
        """"""
        mayabaseplugin.CreateWidget.__init__(self, *args, **kwargs)


class PosePreviewWidget(mayabaseplugin.PreviewWidget):

    def __init__(self, *args, **kwargs):
        """
        :rtype: None
        """
        mayabaseplugin.PreviewWidget.__init__(self, *args, **kwargs)

        self.connect(self.ui.keyCheckBox, QtCore.SIGNAL("clicked()"), self.updateState)
        self.connect(self.ui.mirrorCheckBox, QtCore.SIGNAL("clicked()"), self.updateState)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL("sliderMoved(int)"), self.sliderMoved)
        self.connect(self.ui.blendSlider, QtCore.SIGNAL("sliderReleased()"), self.sliderReleased)

        self.record().blendChanged.connect(self.updateSlider)
        self.record().mirrorChanged.connect(self.updateMirror)

    def setRecord(self, record):
        """
        :type record: Record
        :rtype: None
        """
        mayabaseplugin.PreviewWidget.setRecord(self, record)

        # Mirror check box
        mirrorTip = "Cannot find a mirror table!"
        mirrorTable = record.mirrorTable()
        if mirrorTable:
            mirrorTip = "Using mirror table: %s" % mirrorTable.path()

        self.ui.mirrorCheckBox.setToolTip(mirrorTip)
        self.ui.mirrorCheckBox.setEnabled(mirrorTable is not None)

    def updateMirror(self, mirror):
        """
        :type mirror: bool
        """
        if mirror:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.mirrorCheckBox.setCheckState(QtCore.Qt.Unchecked)

    def setState(self, state):
        """
        :rtype: None
        """
        key = state.get("keyEnabled", False)
        mirror = state.get("mirrorEnabled", False)

        self.ui.keyCheckBox.setChecked(key)
        self.ui.mirrorCheckBox.setChecked(mirror)

        super(PosePreviewWidget, self).setState(state)

    def state(self):
        """
        :rtype: None
        """
        state = super(PosePreviewWidget, self).state()

        key = bool(self.ui.keyCheckBox.isChecked())
        mirror = bool(self.ui.mirrorCheckBox.isChecked())

        state["keyEnabled"] = key
        state["mirrorEnabled"] = mirror

        return state

    def updateSlider(self, value):
        """
        :type value: int
        """
        self.ui.blendSlider.setValue(value)

    def sliderReleased(self):
        """
        :rtype: None
        """
        blend = self.ui.blendSlider.value()
        self.record().loadFromSettings(
            blend=blend,
            refresh=False,
            showBlendMessage=True
        )

    def sliderMoved(self, value):
        """
        :type value: float
        """
        self.record().loadFromSettings(
            blend=value,
            batchMode=True,
            showBlendMessage=True
        )

    def accept(self):
        """
        :rtype: None
        """
        self.record().loadFromSettings(clearSelection=False)
