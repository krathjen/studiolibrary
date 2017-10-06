# An example for how to lock specific folders using the lockRegExp param

import studiolibrary


if __name__ == "__main__":

    # Use the studiolibrary.app context for creating a QApplication instance
    with studiolibrary.app():

        # Lock all folders that contain the words "icon" & "Pixar" in the path
        lockRegExp = "icon|Pixar"

        studiolibrary.main(name="Example3", path="data", lockRegExp=lockRegExp)
