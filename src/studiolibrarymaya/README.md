# Studio Library Items



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
animitem.save(path, objects=objects, startFrame=0, endFrame=200, bakeConnected=False)

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
