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

import studiolibrary

import maya.cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


# @note workspace control could exists if module was reloaded
_workspaceControl = 'studiolibraryWorkspaceControl'
if maya.cmds.workspaceControl(_workspaceControl, exists=True):
    maya.cmds.deleteUI(_workspaceControl)


class MayaLibraryWidget(MayaQWidgetDockableMixin, studiolibrary.LibraryWidget):
    def show(self):
        super(MayaLibraryWidget, self).show(dockable=True)
