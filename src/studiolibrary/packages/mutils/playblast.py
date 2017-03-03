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
import logging

import mutils

try:
    import maya.cmds
except Exception:
    import traceback
    traceback.print_exc()


__all__ = [
    "playblast",
]

logger = logging.getLogger(__name__)


# Valid Renderers:
# [u'vp2Renderer', u'base_OpenGL_Renderer',
#  u'hwRender_OpenGL_Renderer', u'stub_Renderer']
DEFAULT_PLAYBLAST_RENDERER = None


class PlayblastError(Exception):
    """Base class for exceptions in this module."""
    pass


def playblast(filename, modelPanel, startFrame, endFrame, width, height, step=1):
    """
    Wrapper for Maya's Playblast command.
    
    :type filename: str
    :type modelPanel: str
    :type startFrame: int
    :type endFrame: int
    :type width: int
    :type height: int
    :type step: list[int]
    :rtype: str
    """
    logger.info("Playblasting '{filename}'".format(filename=filename))

    if startFrame == endFrame and os.path.exists(filename):
        os.remove(filename)

    frame = [i for i in range(startFrame, endFrame + 1, step)]

    modelPanel = modelPanel or mutils.currentModelPanel()
    if maya.cmds.modelPanel(modelPanel, query=True, exists=True):
        maya.cmds.setFocus(modelPanel)
        if DEFAULT_PLAYBLAST_RENDERER:
            maya.cmds.modelEditor(
                modelPanel,
                edit=True,
                rendererName=DEFAULT_PLAYBLAST_RENDERER
            )

    name, compression = os.path.splitext(filename)
    filename = filename.replace(compression, "")
    compression = compression.replace(".", "")
    offScreen = mutils.isLinux()

    path = maya.cmds.playblast(
        format="image",
        viewer=False,
        percent=100,
        quality=100,
        frame=frame,
        width=width,
        height=height,
        filename=filename,
        endTime=endFrame,
        startTime=startFrame,
        offScreen=offScreen,
        forceOverwrite=True,
        showOrnaments=False,
        compression=compression,
    )

    if not path:
        raise PlayblastError("Playblast was canceled")

    src = path.replace("####", str(int(0)).rjust(4, "0"))

    if startFrame == endFrame:
        dst = src.replace(".0000.", ".")
        logger.info("Renaming '%s' => '%s" % (src, dst))
        os.rename(src, dst)
        src = dst

    logger.info("Playblasted '%s'" % src)
    return src
