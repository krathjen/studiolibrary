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

import studiolibrary
import studiolibraryplugins


class Plugin(studiolibrary.Plugin):

    def __init__(self, *args, **kwargs):
        """
        :type args:
        """
        studiolibrary.Plugin.__init__(self, *args, **kwargs)

        iconPath = studiolibraryplugins.resource().get("icons", "lock.png")

        self.setName("lock")  # Must set a name for the plugin
        self.setIconPath(iconPath)

    def newAction(self, parent=None):
        """
        Overriding this method so that it doesn't show in the "+" new menu.
        """
        pass

    def superusers(self):
        """
        Return a list of the superusers by name.

        :rtype: list[str]
        """
        return self.library().kwargs().get("superusers", [])

    def reLockedFolders(self):
        """
        Return a regex for the locked folders.
        """
        return re.compile(self.library().kwargs().get("lockFolder", ""))

    def reUnlockedFolders(self):
        """
        Return a regex for the unlocked folders.
        """
        return re.compile(self.library().kwargs().get("unlockFolder", ""))

    def folderSelectionChanged(self):
        """
        :rtype: None
        """
        self.updateLock()

    def updateLock(self):    
        """
        :rtype: None
        """
        superusers = self.superusers()
        reLockedFolders = self.reLockedFolders()
        reUnlockedFolders = self.reUnlockedFolders()

        if studiolibrary.user() in superusers or []:
            self.libraryWidget().setLocked(False)
            return

        if reLockedFolders.match("") and reUnlockedFolders.match(""):
            if superusers:  # Lock if only the superusers arg is used
                self.libraryWidget().setLocked(True)
            else:  # Unlock if no keyword arguments are used
                self.libraryWidget().setLocked(False)
            return

        folders = self.libraryWidget().selectedFolders()

        # Lock the selected folders that match the self._lockFolder regx
        if not reLockedFolders.match(""):
            for folder in folders or []:
                if reLockedFolders.search(folder.path()):
                    self.libraryWidget().setLocked(True)
                    return
            self.libraryWidget().setLocked(False)

        # Unlock the selected folders that match the self._unlockFolder regx
        if not reUnlockedFolders.match(""):
            for folder in folders or []:
                if reUnlockedFolders.search(folder.path()):
                    self.libraryWidget().setLocked(False)
                    return
            self.libraryWidget().setLocked(True)


def example():

    plugins = ["examplePlugin"]
    superusers = ["kurt.rathjen"]

    # Lock all folders unless you're a superuser.
    studiolibrary.main(superusers=superusers, plugins=plugins, add=True)

    # This command will lock only folders that contain the word "Approved" in their path.
    # studiolibrary.main(name=name, root=root, superusers=superusers, lockFolder="Approved")

    # This command will lock all folders except folders that contain the words "Users" or "Shared" in their path.
    # studiolibrary.main(name=name, root=root, superusers=superusers, unlockFolder="Users|Shared")


if __name__ == "__main__":
    example()
