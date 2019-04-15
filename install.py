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
"""
Drag and drop for Maya 2018+
"""
import os
import sys


try:
    import maya.mel
    import maya.cmds
    isMaya = True
except ImportError:
    isMaya = False


def onMayaDroppedPythonFile(*args, **kwargs):
    """This function is only supported since Maya 2017 Update 3"""
    pass


def _onMayaDropped():
    """Dragging and dropping this file into the scene executes the file."""

    srcPath = os.path.join(os.path.dirname(__file__), 'src')
    iconPath = os.path.join(srcPath, 'studiolibrary', 'resource', 'icons', 'icon.png')

    srcPath = os.path.normpath(srcPath)
    iconPath = os.path.normpath(iconPath)

    if not os.path.exists(iconPath):
        raise IOError('Cannot find ' + iconPath)

    for path in sys.path:
        if os.path.exists(path + '/studiolibrary/__init__.py'):
            maya.cmds.warning('Studio Library is already installed at ' + path)

    command = '''
# -----------------------------------
# Studio Library
# www.studiolibrary.com
# -----------------------------------

import os
import sys
    
if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')
    
if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')
    
import studiolibrary
studiolibrary.main()
'''.format(path=srcPath)

    shelf = maya.mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = maya.cmds.tabLayout(shelf, query=True, selectTab=True)
    maya.cmds.shelfButton(
        command=command,
        annotation='Studio Library',
        sourceType='Python',
        image=iconPath,
        image1=iconPath,
        parent=parent
    )

    # print("\n// Studio Library has been added to current shelf.")


if isMaya:
    _onMayaDropped()
