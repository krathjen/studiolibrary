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

import studiolibrary

studiolibrary.Library.DEFAULT_PLUGINS = [
    "studiolibraryplugins.lockplugin",
    "studiolibraryplugins.poseplugin",
    "studiolibraryplugins.animationplugin",
    "studiolibraryplugins.mirrortableplugin",
    "studiolibraryplugins.selectionsetplugin",
]

studiolibrary.CHECK_FOR_UPDATES_ENABLED = True

studiolibrary.Analytics.ENABLED = True
studiolibrary.Analytics.DEFAULT_ID = "UA-50172384-1"

# Shared data
# studiolibrary.Library.ITEM_DATA_PATH = "{root}/.studiolibrary/item_data.json"
# studiolibrary.Library.FOLDER_DATA_PATH = "{root}/.studiolibrary/folder_data.json"

# Meta paths are camel case for legacy reasons
studiolibrary.Record.META_PATH = "{path}/.studioLibrary/record.json"
