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

import traceback

try:
    import maya.cmds
except ImportError:
    traceback.print_exc()


class ScriptJob(object):
    """
    self._scriptJob = mutils.ScriptJob(e=['SelectionChanged', self.selectionChanged])
    """
    def __init__(self, *args, **kwargs):
        self.id = maya.cmds.scriptJob(*args, **kwargs)

    def kill(self):
        if self.id:
            maya.cmds.scriptJob(kill=self.id, force=True)
            self.id = None

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        if t is not None:
            self.kill()
