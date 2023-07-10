[comment]: # "Please view this page using github: https://github.com/krathjen/studiolibrary/blob/master/DOCS.md"

<a name="top"></a>
<img src="./src/studiolibrary/resource/icons/header.png" width="252" height="42"/>

Please feel free to improve this page as needed. Thank you.

### Index

* [How to run from code](#jf82ksc)
* [How to reload for development](#gw4un1m)
* [How to set the name and path from code](#nc2dokp)
* [How to create a local and shared library](#k25lyqw)
* [How to create more than one library instance](#ou3nb4z)
* [How to create a library for several projects](#lvx2med)
* [How to set a library for several projects](#h2rz6Km)
* [How to debug "No object match when loading data"](#zi20df5)
* [How to fix a scene that has unknown nodes](#ufj2oi4)
* [How to lock and unlock specific folders](#we7zm9m)
* [How to install & run for Maya 2011-2015](#qiot1k3)
* [How to use relative posing](#4251ca)
* [How to auto specify the relative posing control list file](#2afb7a)


### FAQ

Also, see the frequently asked questions.

https://github.com/krathjen/studiolibrary/labels/FAQ

<br>


### <a name="jf82ksc"></a> How to run from code

```python
import studiolibrary
studiolibrary.main()
```

[Top](#top)

<br>


### <a name="gw4un1m"></a> How to reload for development

This code removes all previously imported Studio Library modules and caches before loading.

Tip: You can also hold "Shift" when clicking the shelf button to reload the modules.

```python
import studiolibrary
studiolibrary.reload()

import studiolibrary
studiolibrary.main()
```

[Top](#top)

<br>


### <a name="nc2dokp"></a> How to set the name and path from code

Create and show a library with the name "Figaro Pho - Anim" that points to a custom path.

```python
import studiolibrary
studiolibrary.main(name="Figaro Pho - Anim", path="P:/figaro/studiolibrary/anim")
```

[Top](#top)

<br>


### <a name="k25lyqw"></a> How to create a local and shared library

Create and show both a shared library and a local library.

```python
import studiolibrary
studiolibrary.main(name="Local", path="C:/temp/studiolibrary/")
studiolibrary.main(name="Shared", path="P:/shared/studiolibrary/")
```

[Top](#top)

<br>


### <a name="ou3nb4z"></a> How to create more than one library instance

In this example we create a library for the animation department, previs department and another library for a local temp folder.

Create three libraries and only show the third one. You can access the others via the settings menu.

```python
import studiolibrary

studiolibrary.main(name="Local", path="C:/temp/studiolibrary", show=False)
studiolibrary.main(name="Figaro Pho - Anim", path="P:/figaro/studiolibrary/anim", show=False)
studiolibrary.main(name="Figaro Pho - Previs", path="P:/figaro/studiolibrary/previs")
```

[Top](#top)

<br>


### <a name="lvx2med"></a> How to create a library for several projects

When implementing the Studio Library for several projects we can get the current project name and then set the name and path.

```python
import studiolibrary

# You could use an environment variable or an in-house python module to get the project name.
project = "MyProject"

path = "/shared/libraries/" + project + "Library"
name = project + " Library"

studiolibrary.main(name=name, path=path)
```

[Top](#top)

<br>

### <a name="h2rz6Km"></a> How to set a library for several projects (version 2.5.0.b7+)

```python
import studiolibrary

libraries = [
    {"name":"Project1", "path":r"D:\Library Data", "default":True, "theme":{"accentColor":"rgb(0,200,100)"}},
    {"name":"Project2", "path":r"D:\Library Data2"},
    {"name":"Temp", "path":r"C:\temp"},
]

studiolibrary.setLibraries(libraries)
studiolibrary.main()
```

[Top](#top)

<br>

### <a name="zi20df5"></a> How to debug "No object match when loading data": (version 1.3.9+)

In version 1.3.9+ you can now switch on debug mode which should log any strange behavior in the script editor.

Make sure “Debug mode” is checked under the settings menu. Apply the pose and It should print any strange behavior in the script editor. This can make applying poses much slower.

You might see something like...

```
// mutils : Cannot find matching destination object for ...
// mutils : load function took 0.38400 sec /
```

[Top](#top)

<br>


### <a name="ufj2oi4"></a> How to fix a scene that has unknown nodes

Unknown nodes are because a plugin is missing. An easy way to fix this issue is to execute the following code in the **Python** script editor. The other way is to find the missing plugin and make sure it’s loaded.


```python
# Delete all unknown nodes in the current scene
import maya.cmds
n = maya.cmds.ls(type="unknown")
if n:
    maya.cmds.delete(n)
```

[Top](#top)

<br>


### <a name="we7zm9m"></a> How to lock and unlock specific folders

```python
import studiolibrary

path= "P:/figaro/studiolibrary/anim"
name = "Figaro Pho - Anim"
superusers = ["kurt.rathjen"]

# Unlock all folders. This is the default behaviour.
studiolibrary.main(name=name, path=path)

# Lock all folders unless you're a super user.
studiolibrary.main(name=name, path=path, superusers=superusers)

# This command will lock only folders that contain the word "Approved" in their path.
studiolibrary.main(name=name, path=path, superusers=superusers, lockFolder="Approved")

# This command will lock all folders except folders that contain the words "Users" or "Shared" in their path.
studiolibrary.main(name=name, path=path, superusers=superusers, unlockFolder="Users|Shared")
```

[Top](#top)


<br>

### <a name="qiot1k3"></a> How to install & run for Maya 2011-2015


#### Download

1 . Download and unzip the studiolibrary.zip file from the following link.

Version 1.32.0 for Maya __2014__, __2015__.

[studiolibrary.1.32.0.zip](https://github.com/krathjen/studiolibrary/releases/download/1.32.0/studiolibrary.zip)


Version 1.6.14 for Maya __2011__, __2012__ and __2013__.

[studiolibrary.1.6.14.zip](https://www.dropbox.com/s/ow968cm5su94ozb/studiolibrary.zip?dl=1) (Requires PyQt4 or PySide)

[studiolibrary.1.6.14.exe](https://www.dropbox.com/s/fh4vl1fzsj1xv3o/studiolibrary.exe?dl=1) (Windows Installer) 

#### Installation

2 . Move the unzipped studiolibrary folder to the following path depending on your OS.


##### Linux

```~/maya/scripts```

##### Windows

```C:/Users/USERNAME/Documents/maya/scripts```

##### OSX

Use ⌘+Shift+G in the finder and copy the studiolibrary folder to

```~/Library/Preferences/Autodesk/maya/scripts```

#### Run

3 . Start Maya and run the following code in the Python script editor.

```
import studiolibrary
studiolibrary.main()
```

[Top](#top)

<br>

### <a name="4251ca"></a> How to use relative posing

Relative posing allows users to place a control, for example the ik foot, and then apply
a pose so that the selected control, in this example the ik foot,
remains in place and the pose is applied relative to that location.

In order for this to work, two new options were added:

- A boolean toggle called "relativeTo" to enable this functionality

- A file path to a text file listing the top level controls and controls that have a
world space constraint.

The text file listing the controls is required in order to properly place
controls. It should list a control per line and list the top level controls
and controls with a world space constraint option. For
example with the Mery rig, we list the main torso control, the upper arm fk
controls because they have a global space switch option, the pole vector controls,
the ik controls, the head, and eyes.

```
Mery_ac_cn_torso
Mery_ac_lf_uparm
Mery_ac_rg_uparm
Mery_ac_lf_elbowPivot
Mery_ac_rg_elbowPivot
Mery_ac_lf_ikhand
Mery_ac_rg_ikhand
Mery_ac_cn_head
Mery_ac_cn_eyes
Mery_ac_lf_kneePivot
Mery_ac_lf_ikfoot
Mery_ac_rg_kneePivot
Mery_ac_rg_ikfoot
```

The control list definition file could not be automated because
controls could be driven by arbitrary networks.

To use the functionality, enable the relativeTo option and set the
path to the control list. Then select the control you want to use
as the "anchor" and apply the pose. If you get an unexpected
result, verify that the controls are listed in evaulation order.
Relative posing also works with mirroring.

[Top](#top)
 
<br>

### <a name="2afb7a"></a> How to auto specify the relative posing control list file
 
Rather than setting the relative pose control list file path manually in the UI,
you can set up a callback to query for the file path based on the current selection.

```python
import studiolibrary
import maya.cmds as cmds

def get_control_list_file(selection):
    # Maybe the path is saved on an attribute in this namespace
    if not selection:
        return None
    namespace = selection[0].split(":")[0]
    attribute = "controlListAttribute"
    attr = cmds.ls("{}:*.{}".format(namespace, attribute))
    if not attr:
        return None
    return cmds.getAttr(attr[0])

studiolibrary.setRelativePoseControlListCallback(get_control_list_file)
studiolibrary.main()
```

[Top](#top)
