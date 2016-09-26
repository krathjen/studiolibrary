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
import imp
import logging

from . import utils


__all__ = ["PluginManager"]

logger = logging.getLogger(__name__)


class PluginManager:

    def __init__(self):
        """
        """
        self._plugins = {}

    def plugins(self):
        """
        :rtype: dict
        """
        return self._plugins

    def unloadPlugins(self):
        """
        :rtype: None
        """
        for plugin in self.plugins().values():
            self.unloadPlugin(plugin)

    def unloadPlugin(self, plugin):
        """
        :type plugin: Plugin
        """
        logger.debug("Unloading plugin: %s" % plugin.path())
        plugin.unload()
        if plugin.path() in self.plugins():
            del self.plugins()[plugin.path()]

    def loadedPlugins(self):
        """
        :rtype: dict
        """
        return self.plugins()

    def loadPlugin(self, path, **kwargs):
        """
        :type path: str
        """
        logger.debug("Loading plugin: %s" % path)
        path = path.replace("\\", "/")

        if path in self.plugins():
            plugin = self.plugins().get(path)
            logger.debug("Skipping: Plugin '%s' is already loaded!" % plugin.name())
            return plugin

        if os.path.exists(path):
            dirname, basename, extension = utils.splitPath(path)
            module = imp.load_source(basename, path)
        else:
            exec ("import " + path)
            module = eval(path)

        plugin = module.Plugin(**kwargs)
        plugin.setPath(path)
        plugin.load()
        self.plugins().setdefault(path, plugin)

        return plugin
