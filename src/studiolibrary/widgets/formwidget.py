# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or modify it 
# under the terms of the GNU Lesser General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. This library is distributed in the 
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.

import re
import logging
import functools

from studioqt import QtGui, QtCore, QtWidgets

from . import fieldwidgets


__all__ = [
    "FormWidget"
]


logger = logging.getLogger(__name__)


def toTitle(name):
    """Convert camel case strings to title strings"""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1 \2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1 \2", s1).title()


class FormWidget(QtWidgets.QFrame):

    accepted = QtCore.Signal(object)
    stateChanged = QtCore.Signal()

    FieldWidgetMap = {
        "int": fieldwidgets.IntFieldWidget,
        "bool": fieldwidgets.BoolFieldWidget,
        "enum": fieldwidgets.EnumFieldWidget,
        "text": fieldwidgets.TextFieldWidget,
        "label": fieldwidgets.LabelFieldWidget,
        "range": fieldwidgets.RangeFieldWidget,
        "string": fieldwidgets.StringFieldWidget,
        "slider": fieldwidgets.SliderFieldWidget,
        "separator": fieldwidgets.SeparatorFieldWidget
    }

    def __init__(self, *args, **kwargs):
        super(FormWidget, self).__init__(*args, **kwargs)

        self._widgets = []
        self._options = []
        self._validator = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

        self._optionsFrame = QtWidgets.QFrame(self)
        self._optionsFrame.setObjectName("optionsFrame")

        layout = QtWidgets.QVBoxLayout(self._optionsFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._optionsFrame.setLayout(layout)

        self._titleWidget = QtWidgets.QPushButton(self)
        self._titleWidget.setCheckable(True)
        self._titleWidget.setObjectName("titleWidget")
        self._titleWidget.toggled.connect(self._titleClicked)
        self._titleWidget.hide()

        self.layout().addWidget(self._titleWidget)
        self.layout().addWidget(self._optionsFrame)

    def _titleClicked(self, toggle):
        """Triggered when the user clicks the title widget."""
        self.setExpanded(not toggle)
        self.stateChanged.emit()

    def titleWidget(self):
        """
        Get the title widget.
        
        :rtype: QWidget
        """
        return self._titleWidget

    def setTitle(self, title):
        """
        Set the text for the title widget.
        
        :type title: str
        """
        self.titleWidget().setText(title)

    def setExpanded(self, expand):
        """
        Expands the options if expand is true, otherwise collapses the options.
        
        :type expand: bool
        """
        self._titleWidget.blockSignals(True)

        try:
            self._titleWidget.setChecked(not expand)
            self._optionsFrame.setVisible(expand)
        finally:
            self._titleWidget.blockSignals(False)

    def isExpanded(self):
        """
        Returns true if the item is expanded, otherwise returns false.
        
        :rtype: bool
        """
        return self._optionsFrame.isVisible()

    def setTitleVisible(self, visible):
        """
        A convenience method for setting the title visible.
        
        :type visible: bool
        """
        self.titleWidget().setVisible(visible)

    def reset(self):
        """Reset all option widgets back to their default value."""
        for widget in self._widgets:
            widget.reset()
        self.validate()

    def setSchema(self, options):
        """Set the options for the widget."""
        self._options = options

        for option in options:

            cls = self.FieldWidgetMap.get(option.get("type", "label"))

            if not cls:
                logger.warning("Cannot find widget for %s", option)
                continue

            widget = cls(options=option)
            widget.setOption(option)

            value = option.get("value")
            default = option.get("default")
            if value is None and default is not None:
                widget.setValue(default)

            self._widgets.append(widget)

            callback = functools.partial(self._optionChanged, widget)
            widget.valueChanged.connect(callback)

            self._optionsFrame.layout().addWidget(widget)

    def _optionChanged(self, widget):
        """
        Triggered when the given option widget changes value.
        
        :type widget: FieldWidget 
        """
        self.stateChanged.emit()
        self.validate()

    def accept(self):
        """Accept the current options"""
        self.emitAcceptedCallback()

    def closeEvent(self, event):
        super(FormWidget, self).closeEvent(event)

    def setValidator(self, validator):
        """
        Set the validator for the options.
        
        :type validator: func
        """
        self._validator = validator

    def validate(self):
        """Validate the current options using the validator."""
        if self._validator:
            state = self._validator(**self.optionsToDict())

            if state is not None:
                self._setState(state)
        else:
            logger.debug("No validator set.")

    def value(self, name):
        """
        Get the value for the given widget name.
        
        :type name: str 
        :rtype: object 
        """
        widget = self.widget(name)
        return widget.value()

    def widget(self, name):
        """
        Get the widget for the given widget name.
        
        :type name: str 
        :rtype: FieldWidget 
        """
        for widget in self._widgets:
            if widget.option().get("name") == name:
                return widget

    def options(self):
        options = []
        for widget in self._widgets:
            options.append(widget.option())
        return options

    def optionsToDict(self):
        """
        Get all the option data.
        
        :rtype: dict 
        """
        options = {}
        for widget in self._widgets:
            options[widget.option().get("name")] = widget.value()
        return options

    def state(self):
        """
        Get the current state.
        
        :rtype: dict 
        """
        options = []

        for widget in self._widgets:
            options.append(widget.state())

        state = {
            "options": options,
            "expanded": self.isExpanded()
        }

        return state

    def setState(self, state):
        """
        Set the current state.
        
        :type state: dict 
        """
        expanded = state.get("expanded")
        if expanded is not None:
            self.setExpanded(expanded)

        options = state.get("options")
        if options is not None:
            self._setState(options)

        self.validate()

    def optionsState(self):
        state = {}
        options = self.options()
        values = self.optionsToDict()

        for option in options:
            name = option.get("name")
            persistent = option.get("persistent")
            if name and persistent:
                state[name] = values[name]

        return state

    def setStateFromOptions(self, options):
        state = []
        for option in options:
            state.append({"name": option, "value": options[option]})

        self._setState(state)

    def _setState(self, options):
        for widget in self._widgets:
            widget.blockSignals(True)

        for widget in self._widgets:
            for option in options:
                if option.get("name") == widget.option().get("name"):
                    widget.setOption(option)

        for widget in self._widgets:
            widget.blockSignals(False)


STYLE = """

FormWidget QWidget {
    /*font-size: 12px;*/
    text-align: left;
}

FieldWidget {
    min-height: 16px;
    margin-bottom: 3px;
}

FieldWidget[layout=vertical] #label {
    margin-bottom: 4px;
}

FieldWidget[layout=horizontal] #label {
    margin-left: 4px;
}

FieldWidget #menuButton {
    margin-left: 4px;
    border-radius: 2px;
    min-width: 25px;
    max-height: 25px;
    text-align: center;
    background-color: rgb(0,0,0,20);
}

FieldWidget #label {
    min-width: 72px;
    color: rgb(FOREGROUND_COLOR_R, FOREGROUND_COLOR_G, FOREGROUND_COLOR_B, 100);
}

FormWidget #titleWidget {
    font-size: 12px;
    padding: 2px;
    padding-left: 5px;
    background-color: rgb(255, 255, 255, 20);
    border-bottom: 0px solid rgb(255, 255, 255, 20);
}

FormWidget #titleWidget:checked {
    background-color: rgb(255, 255, 255, 5);
}

FormWidget #optionsFrame {
    margin: 2px;
}

FieldWidget QComboBox {
    border: 1px solid transparent;
}
"""


def example():
    """
    import studiolibrary
    studiolibrary.reload()
    
    import studiolibrary
    studiolibrary.widgets.formwidget.example()
    """
    schema = [
        {
            "name": "name",
            "value": "Face.anim",
            "type": "string",
        },
        {
            "name": "objects",
            "value": "125 objects",
            "type": "label",
        },
        {
            "name": "sep1",
            "type": "separator",
        },
        {
            "name": "blend",
            "type": "slider",
        },
        {
            "name": "Bake",
            "type": "bool",
        },
        {
            "name": "frameRange",
            "type": "range"
        },
        {
            "name": "frameRange",
            "type": "enum",
            "items": ["Test1", "Test2", "Test4"]
        },
        {
            "name": "comment",
            "value": "this is a comment",
            "type": "text",
            "layout": "vertical"
        },
    ]

    def validator(**fields):
        print(fields)

    w = FormWidget()
    w.setValidator(validator)
    w.setSchema(schema)
    w.setStyleSheet(STYLE)
    w.show()

    return w


if __name__ == "__main__":
    import studioqt
    with studioqt.app():
        w = example()



