[comment]: # "Please view this page using github: https://github.com/krathjen/studiolibrary/blob/master/DOCS.md"

<a name="top"></a>
<img src="./src/studiolibrary/resource/icons/header.png" width="252" height="42"/>

Please feel free to improve this page as needed. Thank you.

### Index

* [How to run from code](#linkA)
* [How to set the name and path from code](#linkB)
* [How to create a local and shared library](#linkC1)
* [How to create more than one library instance](#linkC2)
* [How to reload for development](#linkD)
* [How to load a library for several projects](#linkE)
* [How to debug "No object match when loading data"](#linkF)
* [How to fix a scene that has unknown nodes](#linkG)
* [How to lock and unlock specific folders](#linkH)

### FAQ

Also, see the frequently asked questions.

https://github.com/krathjen/studiolibrary/labels/FAQ

<br>


### <a name="linkA"></a> How to run from code

```python
import studiolibrary
studiolibrary.main()
```

[Top](#top)

<br>


### <a name="linkB"></a> How to set the name and path from code

Create and show a library with the name "Figaro Pho - Anim" that points to a custom path.

```python
import studiolibrary
studiolibrary.main(name="Figaro Pho - Anim", path="P:/figaro/studiolibrary/anim")
```

[Top](#top)

<br>


### <a name="linkC1"></a> How to create a local and shared library

Create and show both a shared library and a local library.

```python
import studiolibrary
studiolibrary.main(name="Local", path="C:/temp/studiolibrary/")
studiolibrary.main(name="Shared", path="P:/shared/studiolibrary/")
```

[Top](#top)

<br>


### <a name="linkC2"></a> How to create more than one library instance

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


### <a name="linkD"></a> How to reload for development

This code removes all previously imported Studio Library modules and caches before loading.

```python
import studiolibrary
studiolibrary.reload()

import studiolibrary
studiolibrary.main()
```

[Top](#top)

<br>


### <a name="linkE"></a> How to load a library for several projects

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


### <a name="linkF"></a> How to debug "No object match when loading data": (version 1.3.9+)

In version 1.3.9+ you can now switch on debug mode which should log any strange behavior in the script editor.

Make sure “Debug mode” is checked under the settings menu. Apply the pose and It should print any strange behavior in the script editor. This can make applying poses much slower.

You might see something like...

```
// mutils : Cannot find matching destination object for ...
// mutils : load function took 0.38400 sec /
```

[Top](#top)

<br>


### <a name="linkG"></a> How to fix a scene that has unknown nodes

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


### <a name="linkH"></a> How to lock and unlock specific folders

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