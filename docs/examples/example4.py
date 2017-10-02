# An example for showing the message box dialog.

import os

import studiolibrary

import studioqt


if __name__ == "__main__":

    with studioqt.app():

        path = os.path.abspath("data")
        w = studiolibrary.main(name="Example4", path=path)

        text = "Before you get started please choose a folder location " \
              "for storing the data. A network folder is recommended for " \
              "sharing within a studio."

        print studioqt.MessageBox.warning(w, "Warning", text)

        print studioqt.MessageBox.question(
            w,
            "Welcome",
            text,
            width=450,
            height=350,
            enableDontShowCheckBox=True
        )

        print studioqt.MessageBox.input(
            w,
            "Rename",
            "Rename the selected item?",
            inputText="face.anim",
        )

        print studioqt.MessageBox.critical(w, "Error", text)
