# Studio Library Items


## Items

* poseitem
* animitem
* setsItem
* mirroritem


## Examples

### Pose Item Example

Saving and loading a pose items

```python
from studiolibrarymaya import poseitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

# Saving a pose item
item = poseitem.PoseItem(path)
item.save(objects=objects)

# Loading a pose item
item = poseitem.PoseItem(path)
item.load(objects=objects, namespaces=namespaces, key=True, mirror=False)
```

### Animation Item Example

Saving and loading animation items

```python
from studiolibrarymaya import animitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.anim"
objects = maya.cmds.ls(selection=True) or []
option = animitem.PasteOption.ReplaceCompletely
namespaces = []

# Saving an animation item
item = animitem.AnimItem(path)
item.save(objects=objects, startFrame=0, endFrame=200, bakeConnected=False)

# Loading an animation item
item = animitem.AnimItem(path)
item.load(objects=objects, namespaces=namespaces,
            option=option, connect=False, currentTime=False)
```

### Mirror Table Item Example

Saving and loading mirror tables

```python
from studiolibrarymaya import mirroritem

path = "/AnimLibrary/Characters/Malcolm/malcolm.mirror"
objects = maya.cmds.ls(selection=True) or []
option = mirroritem.MirrorOption.Swap
namespaces = []

# Saving a mirror table item
item = mirroritem.MirrorItem(path)
item.save(objects=objects, leftSide="Lf", rightSide="Rf")

# Loading a mirror table item
item = mirroritem.MirrorItem(path)
item.load(objects=objects, namespaces=namespaces,
            option=option, animation=True, time=None)
```

### Selection Set Item Example

Saving and loading selection sets

```python
from studiolibrarymaya import setsitem

path = "/AnimLibrary/Characters/Malcolm/malcolm.set"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

# Saving a selection sets item
item = setsitem.SetsItem(path)
item.save(objects=objects)

# Loading a selection sets item
item = setsitem.SetsItem(path)
item.load(objects=objects, namespaces=namespaces)
```
