# An example for how to lock specific folders using the lockRegExp param

import studiolibrary


if __name__ == "__main__":

    import studioqt

    # Use the studioqt.app context to create and run a QApplication instance.
    with studioqt.app():

        # Lock all folders that contain the words "icon" & "Pixar" in the path.
        studiolibrary.main(
            name="Example3",
            path="data",
            lockRegExp="icon|Pixar",
        )
