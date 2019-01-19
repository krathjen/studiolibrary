
# ![logo](./resource/icons/icon_black_on_white.png) Studio Library

A free tool written in python for managing poses and animation in Maya.


## Features 

* Save poses and animation
* Mirror poses and animation
* Create easy to use selection sets
* MMB drag for fast pose blending
* LMB drag and drop to organize items
* Insert, merge and replace animation
* Supports Windows, Linux and OSX
* Supports Maya 2016, 2017 and 2018

## Tutorials

* [How to use poses](https://www.youtube.com/watch?v=lpaWrT7VXfM)
* [How to use selection sets](https://www.youtube.com/watch?v=xejWubal_j8)
* [How to use mirror tables](https://www.youtube.com/watch?v=kCv0XleJfjU&t=3s)

## Contributing

Contributions to Studio Library are always welcome! Whether it's reporting bugs, feature requests, discussing ideas or committing code.

We follow the below guides for...

* [Commit messages style](https://github.com/erlang/otp/wiki/Writing-good-commit-messages)
* [GitHub Forking Workflow](https://gist.github.com/Chaser324/ce0505fbed06b947d962)
* [Python Qt Style Guidelines](http://bitesofcode.blogspot.co.uk/2011/10/pyqt-coding-style-guidelines.html)


## Download

Download and unzip the *studiolibrary.zip* file from [github releases](https://github.com/krathjen/studiolibrary/releases) or [website](http://www.studiolibrary.com/download).


## Setup

### OSX
Use SHIFT+G in the finder and copy the *studiolibrary* folder to *~/Library/Preferences/Autodesk/maya/scripts*.

### Linux
Open the file manager and copy the *studiolibrary* folder to *~/maya/scripts*.

### Windows
Open the file explorer and copy the *studiolibrary* folder to *C:/Users/USERNAME/Documents/maya/scripts*.


## Run

Start Maya and run the following code in the **Python** script editor.

```python
import studiolibrary
studiolibrary.main()
```

## Develop

You can use the following for developing within Maya/DCC applications.

The 'studiolibrary.reload' function should not be used in production.

```python
import studiolibrary
studiolibrary.reload()

import studiolibrary
studiolibrary.main()
```

## License

The Studio Library is free to use in production under the GNU Lesser General Public License v3.0.
For more information please click [here](https://github.com/krathjen/studiolibrary/blob/master/LICENSE.md).


## Support

Comments, suggestions and bug reports are welcome.

Feel free to submit any issues with the error message and a detailed step by step process of how you got the error in [github issues](https://github.com/krathjen/studiolibrary/issues/new) or contact [krathjen](http://www.studiolibrary.com/contact).