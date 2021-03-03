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

import mutils
import mutils.gui

from studiovendor.Qt import QtCore
from studiovendor.Qt import QtWidgets

try:
    import maya.cmds
    import maya.OpenMayaUI as mui
    isMaya = True
except ImportError:
    isMaya = False


__all__ = ["ModelPanelWidget"]


class ModelPanelWidget(QtWidgets.QWidget):

    def __init__(self, parent, name="capturedModelPanel", **kwargs):
        super(ModelPanelWidget, self).__init__(parent, **kwargs)

        uniqueName = name + str(id(self))
        self.setObjectName(uniqueName + 'Widget')

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setObjectName(uniqueName + "Layout")
        self.setLayout(layout)

        maya.cmds.setParent(layout.objectName())
        self._modelPanel = maya.cmds.modelPanel(uniqueName, label="ModelPanel")
        self.setModelPanelOptions()

    def setModelPanelOptions(self):

        modelPanel = self.name()

        maya.cmds.modelEditor(modelPanel, edit=True, allObjects=False)
        maya.cmds.modelEditor(modelPanel, edit=True, grid=False)
        maya.cmds.modelEditor(modelPanel, edit=True, dynamics=False)
        maya.cmds.modelEditor(modelPanel, edit=True, activeOnly=False)
        maya.cmds.modelEditor(modelPanel, edit=True, manipulators=False)
        maya.cmds.modelEditor(modelPanel, edit=True, headsUpDisplay=False)
        maya.cmds.modelEditor(modelPanel, edit=True, selectionHiliteDisplay=False)

        maya.cmds.modelEditor(modelPanel, edit=True, polymeshes=True)
        maya.cmds.modelEditor(modelPanel, edit=True, nurbsSurfaces=True)
        maya.cmds.modelEditor(modelPanel, edit=True, subdivSurfaces=True)
        maya.cmds.modelEditor(modelPanel, edit=True, displayTextures=True)
        maya.cmds.modelEditor(modelPanel, edit=True, displayAppearance="smoothShaded")

        currentModelPanel = mutils.currentModelPanel()

        if currentModelPanel:
            camera = maya.cmds.modelEditor(currentModelPanel, query=True, camera=True)
            displayLights = maya.cmds.modelEditor(currentModelPanel, query=True, displayLights=True)
            displayTextures = maya.cmds.modelEditor(currentModelPanel, query=True, displayTextures=True)

            maya.cmds.modelEditor(modelPanel, edit=True, camera=camera)
            maya.cmds.modelEditor(modelPanel, edit=True, displayLights=displayLights)
            maya.cmds.modelEditor(modelPanel, edit=True, displayTextures=displayTextures)

    def name(self):
        return self._modelPanel

    def modelPanel(self):
        ptr = mui.MQtUtil.findControl(self._modelPanel)
        return mutils.gui.wrapInstance(int(ptr), QtWidgets.QWidget)

    def barLayout(self):
        name = maya.cmds.modelPanel(self._modelPanel, query=True, barLayout=True)
        ptr = mui.MQtUtil.findControl(name)
        return mutils.gui.wrapInstance(int(ptr), QtCore.QObject)

    def hideBarLayout(self):
        self.barLayout().hide()

    def hideMenuBar(self):
        maya.cmds.modelPanel(self._modelPanel, edit=True, menuBarVisible=False)

    def setCamera(self, name):
        maya.cmds.modelPanel(self._modelPanel, edit=True, cam=name)


if __name__ == "__main__":
    widget = ModelPanelWidget(None, "modelPanel")
    widget.show()
