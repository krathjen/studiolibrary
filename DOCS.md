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
* [How to manually install Studio Library](#qiot1k3)


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

Create and show a library with the name "MY_PROJECT - Anim" that points to a custom path.

```python
import studiolibrary
studiolibrary.main(name="MY_PROJECT - Anim", path="P:/MY_PROJECT/studiolibrary/anim")
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
studiolibrary.main(name="MY_PROJECT - Anim", path="P:/MY_PROJECT/studiolibrary/anim", show=False)
studiolibrary.main(name="MY_PROJECT - Previs", path="P:/MY_PROJECT/studiolibrary/previs")
```

[Top](#top)

<br>


### <a name="lvx2med"></a> How to create a library for several projects

When implementing the Studio Library for several projects we can get the current project name and then set the name and path.

```python
import studiolibrary

# You could use an environment variable or an in-house python module to get the project name.
project = "MY_PROJECT"

path = "/shared/libraries/" + project + "_Library"
name = project + " Library"

studiolibrary.main(name=name, path=path)
```

[Top](#top)

<br>

### <a name="h2rz6Km"></a> How to set a library for several projects

```python
import studiolibrary

libraries = [
    {"name":"Project1", "path":r"D:\Library_Data", "default":True, "theme":{"accentColor":"rgb(0,200,100)"}},
    {"name":"Project2", "path":r"D:\Library_Data2"},
    {"name":"Temp", "path":r"C:\temp"},
]

studiolibrary.setLibraries(libraries)
studiolibrary.main()
```

[Top](#top)

<br>

### <a name="zi20df5"></a> How to debug "No object match when loading data"

Make sure “Debug mode” is checked under the settings menu. Apply the pose and it should print any strange behavior in the script editor. This can make applying poses much slower.

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

path= "C:/MY_PROJECT/studiolibrary/anim"
name = "MY_PROJECT - Anim"
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

### <a name="qiot1k3"></a> How to manually install


#### Download

1 . Download and unzip the studiolibrary.zip file from the following link.

www.studiolibrary.com

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
