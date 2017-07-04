# An example for creating a custom settings action

import studiolibrary


class CustomLibraryWidget(studiolibrary.LibraryWidget):

    def createSettingsMenu(self):
        """Reimplementing this method to add a custom action."""
        menu = super(CustomLibraryWidget, self).createSettingsMenu()

        menu.addSeparator()

        action = menu.addAction("Custom Action")
        action.triggered.connect(self.customActionClicked)

        return menu

    def customActionClicked(self):
        """Triggered when the custom action has been clicked."""
        print "Hello World"


if __name__ == "__main__":

    import studioqt

    # Use the studioqt.app context to run a QApplication instance.
    with studioqt.app():
        libraryWidget = CustomLibraryWidget.instance()
        libraryWidget.show()
