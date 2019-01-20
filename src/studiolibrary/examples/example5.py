# An example for creating two libraryWidget instances in one session.


import studiolibrary


def showExample5():
    """
    Show two Studio Library widget instances.

    :rtype: None 
    """
    with studiolibrary.app():

        widget = studiolibrary.main(name="Example5-A", path="data")
        widget.setLocked(True)
        widget.move(100, 100)
        widget.theme().setAccentColor("rgb(250, 100, 50)")
        widget.theme().setBackgroundColor("rgb(80, 150, 120)")
        widget.show()

        widget = studiolibrary.main(name="Example5-B", path="data")
        widget.show()


if __name__ == "__main__":
    showExample5()
