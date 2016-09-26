# Studio Library Plugins


## Plugins

* poseplugin
* animationplugin
* mirrorrableplugin
* selectionsetplugin


## Examples

### Pose Plugin Example

Saving and loading a pose records

```python
from studiolibraryplugins import poseplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.pose"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

# Saving a pose record
record = poseplugin.Record(path)
record.save(path=path, objects=objects)

# Loading a pose record
record = poseplugin.Record(path)
record.load(objects=objects, namespaces=namespaces, key=True, mirror=False)
```

### Animation Plugin Example

Saving and loading animation records

```python
from studiolibraryplugins import animationplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.anim"
objects = maya.cmds.ls(selection=True) or []
option = animationplugin.PasteOption.ReplaceCompletely
namespaces = []

# Saving an animation record
record = animationplugin.Record(path)
record.save(objects=objects, startFrame=0, endFrame=200, bakeConnected=False)

# Loading an animation plugin
record = animationplugin.Record(path)
record.load(objects=objects, namespaces=namespaces,
            option=option, connect=False, currentTime=False)
```

### Mirror Table Plugin Example

Saving and loading mirror tables

```python
from studiolibraryplugins import mirrortableplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.mirror"
objects = maya.cmds.ls(selection=True) or []
option = mirrortableplugin.MirrorOption.Swap
namespaces = []

# Saving a mirror table record
record = mirrortableplugin.Record(path)
record.save(objects=objects, leftSide="Lf", rightSide="Rf")

# Loading a mirror table record
record = mirrortableplugin.Record(path)
record.load(objects=objects, namespaces=namespaces,
            option=option, animation=True, time=None)
```

### Selection Set Plugin Example

Saving and loading selection sets

```python
from studiolibraryplugins import selectionsetplugin

path = "/AnimLibrary/Characters/Malcolm/malcolm.set"
objects = maya.cmds.ls(selection=True) or []
namespaces = []

# Saving a selection sets record
record = selectionsetplugin.Record(path)
record.save(objects=objects)

# Loading a selection sets record
record = selectionsetplugin.Record(path)
record.load(objects=objects, namespaces=namespaces)
```
