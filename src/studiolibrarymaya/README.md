# Studio Library Items

Items are used for loading and saving data.


### Pose Item

Saving and loading a pose items

```python
from studiolibrarymaya import poseitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

# Saving a pose item
poseitem.save(path, objects=objects)

# Loading a pose item
poseitem.load(path, objects=objects, namespaces=namespaces, key=True, mirror=False)
```

### Animation Item

Saving and loading animation items

```python
from studiolibrarymaya import animitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.anim"
objects = maya.cmds.ls(selection=True) or []

# Saving an animation item
animitem.save(path, objects=objects, frameRange=(0, 200), bakeConnected=False)

# Loading an animation item
animitem.load(path, objects=objects, option="replace all", connect=False, currentTime=False)
```

Loading an animation to multiple namespaces

```python
from studiolibrarymaya import animitem
animitem.load(path, namespaces=["character1", "character2"], option="replace all")
```

### Mirror Table Item

Saving and loading mirror tables

```python
from studiolibrarymaya import mirroritem

path = "/AnimLibrary/Characters/Malcolm/malcolm.mirror"
objects = maya.cmds.ls(selection=True) or []

# Saving a mirror table item
mirroritem.save(path, objects=objects, leftSide="Lf", rightSide="Rf")

# Loading a mirror table item
mirroritem.load(path, objects=objects, namespaces=[], option="swap", animation=True, time=None)
```

### Selection Set Item

Saving and loading selection sets

```python
from studiolibrarymaya import setsitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.set"
objects = maya.cmds.ls(selection=True) or []

# Saving a selection sets item
setsitem.save(path, objects=objects)

# Loading a selection sets item
setsitem.load(path, objects=objects, namespaces=[])
```


### Maya File Item (Development)

Saving and loading a Maya file item

This item can be used to load and save any Maya nodes. For example:
locators and geometry.

```python
from studiolibrarymaya import mayafileitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.mayafile"
objects = maya.cmds.ls(selection=True) or []

# Saving the item to disc
mayafileitem.save(path, objects=objects)

# Loading the item from disc
mayafileitem.load(path)
```

### Example Item

If you would like to create a custom item for saving and loading different data types, then please have a look at the [exampleitem.py](exampleitem.py)

When developing a new item you can "Shift + Click" on the shelf icon which will reload all Studio Library modules including your changes to the item.

Make sure you register any new items using either the "itemRegistry" key in the [config file](../studiolibrary/config/default.json) or by calling `studiolibrary.registerItem(cls)`.
