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

import re

from . import utils


__all__ = ["Package"]


class Package:

    def __init__(self):
        """
        """
        self._jsonUrl = ""
        self._helpUrl = ""
        self._version = "0.0.0"

    def openHelp(self):
        """
        :type:
        """
        import webbrowser
        webbrowser.open(self._helpUrl)

    def setJsonUrl(self, url):
        """
        :type url: str
        """
        self._jsonUrl = url

    def setHelpUrl(self, url):
        """
        :type url: str
        """
        self._helpUrl = url

    def helpUrl(self):
        """
        :rtype:
        """
        return self._helpUrl

    def jsonUrl(self):
        """
        :rtype: str
        """
        return self._jsonUrl

    def setVersion(self, version):
        """
        :type version: str
        """
        self._version = version

    def version(self):
        """
        :rtype: str
        """
        return self._version

    def latestVersion(self):
        """
        :rtype: str or None
        """
        data = utils.downloadUrl(self.jsonUrl())
        if data:
            if data.startswith("{"):
                data = eval(data.strip(), {})
                return data.get("version", self.version())

    def splitVersion(self, version=None):
        """
        :type version: str
        :rtype: (int, int, int)
        """
        version = version or self.version()
        reNumbers = re.compile("[0-9]+")
        major, miner, patch = [int(reNumbers.search(value).group(0)) for value in version.split(".")]
        return major, miner, patch

    def isUpdateAvailable(self):
        """
        :rtype: bool | None
        """
        latestVersion = self.latestVersion()

        if latestVersion:
            major1, miner1, patch1 = self.splitVersion()
            major2, miner2, patch2 = self.splitVersion(latestVersion)

            if major1 < major2:
                return True

            if major1 <= major2 and miner1 < miner2:
                return True

            if major1 <= major2 and miner1 <= miner2 and patch1 < patch2:
                return True

        return False


def test_package():
    """
    :rtype: None
    """
    jsonUrl = "http://dl.dropbox.com/u/28655980/studiolibrary/studiolibrary.json"

    package = Package()
    package.setVersion("1.5.8")
    package.setJsonUrl(jsonUrl)

    print package.splitVersion()
    print package.latestVersion()
    print package.isUpdateAvailable()


if __name__ == "__main__":
    test_package()


