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
import json


_config = None


def get(*args):
    """
    This is a convenience function for getting values from the config.

    :rtype: str
    """
    return config().get(*args)


def config():
    """
    Get the config object for the current environment.

    :rtype: Config
    """
    global _config

    if not _config:
        _config = Config()
        _config.read()

    return _config


class Config(dict):
    """
    A custom config parser for passing JSON files.

    We use this instead of the standard ConfigParser as the JSON format
    can support list and dict types.

    This parser can also support comments using the following style "//"
    """

    @staticmethod
    def paths():
        """
        Return all possible config paths.

        :rtype: list[str]
        """
        cwd = os.path.dirname(__file__)
        paths = [os.path.join(cwd, "config", "default.json")]

        path = os.environ.get("STUDIO_LIBRARY_CONFIG_PATH")
        path = path or os.path.join(cwd, "config", "config.json")

        if not os.path.exists(path):
            cwd = os.path.dirname(os.path.dirname(cwd))
            path = os.path.join(cwd, "config", "config.json")

        if os.path.exists(path):
            paths.append(path)

        return paths

    def read(self):
        """Read all paths and overwrite the keys with each successive file."""
        self.clear()

        for path in self.paths():
            lines = []

            with open(path) as f:
                for line in f.readlines():
                    if not line.strip().startswith('//'):
                        lines.append(line)

            data = '\n'.join(lines)
            if data:
                self.update(json.loads(data))
