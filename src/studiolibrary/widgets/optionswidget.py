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


__all__ = [
    'OptionsWidget'
]


logger = logging.getLogger(__name__)


def toTitle(name):
    """Convert camel case strings to title strings"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).title()


class OptionWidget(QtWidgets.QFrame):

    """The base widget for all option widgets.
    
    Examples:
        
        option = {
            'name': 'startFrame',
            'type': 'int'
            'value': 1,
        }
        
        optionWidget = OptionWidget(option)
        
    """
    valueChanged = QtCore.Signal()

    DefaultLayout = "horizontal"

    def __init__(self, parent=None, options=None):
        super(OptionWidget, self).__init__(parent)

        self._option = options or {}
        self._widget = None
        self._default = None
        self._required = None
        self._menuButton = None
        self._actionResult = None

        direction = self._option.get("layout", self.DefaultLayout)
        self.setProperty("layout", direction)

        if direction == "vertical":
            layout = QtWidgets.QVBoxLayout(self)
        else:
            layout = QtWidgets.QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)

        self._label = QtWidgets.QLabel(self)
        self._label.setObjectName('label')
        self._label.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred,
        )

        layout.addWidget(self._label)

        if direction == "vertical":
            self._label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        else:
            layout.setStretchFactor(self._label, 2)

            self._label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    def label(self):
        """
        Get the label widget.
        
        :rtype: QtWidgets.QLabel 
        """
        return self._label

    def state(self):
        """
        Get the current state of the option.
        
        :rtype: dict
        """
        return {
            "name": self._option["name"],
            "value": self.value()
        }

    def option(self):
        """
        Get the option data for the widget.
        
        :rtype: dict 
        """
        return self._option

    def setOption(self, state):
        """
        Set the current state of the option widget using a dictionary.
        
        :type state: dict
        """
        self._option.update(state)
        state = self._option

        self.blockSignals(True)

        items = state.get('items')
        if items is not None:
            self.setItems(items)

        value = state.get('value')
        default = state.get('default')

        # Must set the default before value
        if default is not None:
            self.setDefault(default)
        else:
            self.setDefault(value)

        if value is not None:
            self.setValue(value)

        enabled = state.get('enabled')
        if enabled is not None:
            self.setEnabled(enabled)

        hidden = state.get('hidden')
        if hidden is not None:
            self.setHidden(hidden)

        required = state.get('required')
        if required is not None:
            self.setRequired(required)

        message = state.get('error', '')
        self.setError(message)

        annotation = state.get('annotation', '')
        self.setToolTip(annotation)

        label = state.get('label')
        if label is None:
            label = state.get('name')

        if label is not None:
            self.setText(label)

        text = state.get("menu", {}).get("name")
        if text is not None:
            self.setMenuText(text)

        self.refresh()

        self.blockSignals(False)

    def setError(self, message):
        """
        Set the error message to be displayed for the options widget.
        
        :type message: str
        """
        error = True if message else False

        if error:
            self.setToolTip(message)
        else:
            self.setToolTip(self.option().get('annotation'))

        self.setProperty('error', error)
        self.setStyleSheet(self.styleSheet())

    def setText(self, text):
        """
        Set the label text for the option.
        
        :type text: str 
        """
        if text:
            text = toTitle(text)

            if self.isRequired():
                text += '*'

            self._label.setText(text)

    def setValue(self, value):
        """
        Set the value of the option widget.
        
        Will emit valueChanged() if the new value is different from the old one.
        
        :type value: object
        """
        self.emitValueChanged()

    def value(self):
        """
        Get the value of the option widget.
        
        :rtype: object
        """
        raise NotImplementedError('The method "value" needs to be implemented')

    def setItems(self, items):
        """
        Set the items for the options widget.
        
        :type items: list[str]
        """
        raise NotImplementedError('The method "setItems" needs to be implemented')

    def reset(self):
        """Reset the option widget back to the defaults."""
        self.setState(self._option)

    def setRequired(self, required):
        """
        Set True if a value is required for this option.
        
        :type required: bool
        """
        self._required = required
        self.setProperty('required', required)
        self.setStyleSheet(self.styleSheet())

    def isRequired(self):
        """
        Check if a value is required for the option widget.
        
        :rtype: bool
        """
        return bool(self._required)

    def setDefault(self, default):
        """
        Set the default value for the option widget.
        
        :type default: object
        """
        self._default = default

    def default(self):
        """
        Get the default value for the option widget.
        
        :rtype: object
        """
        return self._default

    def isDefault(self):
        """
        Check if the current value is the same as the default value.
        
        :rtype: bool
        """
        return self.value() == self.default()

    def emitValueChanged(self, *args):
        """
        Emit the value changed signal.
        
        :type args: list
        """
        self.valueChanged.emit()
        self.refresh()

    def setWidget(self, widget):
        """
        Set the widget used to set and get the option value.
        
        :type widget: QtWidgets.QWidget
        """
        self._widget = widget
        self._widget.setObjectName('widget')
        self._widget.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Preferred,
        )

        self.layout().addWidget(self._widget)
        self.layout().setStretchFactor(self._widget, 4)

        self.createMenuButton()

    def setMenuText(self, text):
        self._menuButton.setText(text)

    def createMenuButton(self):
        """Create the menu button to show the actions."""
        menu = self.option().get("menu", {})
        actions = self.option().get("actions", {})

        if menu or actions:

            name = menu.get("name", "...")
            callback = menu.get("callback", self.showMenu)

            self._menuButton = QtWidgets.QPushButton(name)
            self._menuButton.setObjectName("menuButton")
            self._menuButton.clicked.connect(callback)

            self.layout().addWidget(self._menuButton)

    def actionCallback(self, callback):
        """
        Wrap schema callback to get the return value.
        
        :type callback: func 
        """
        self._actionResult = callback()

    def showMenu(self):
        """Show the menu using the actions from the options."""
        menu = QtWidgets.QMenu(self)
        actions = self.option().get("actions", [])

        for action in actions:

            name = action.get("name", "No name found")
            callback = action.get("callback")

            func = functools.partial(self.actionCallback, callback)

            action = menu.addAction(name)
            action.triggered.connect(func)

        point = QtGui.QCursor.pos()
        point.setX(point.x() + 3)
        point.setY(point.y() + 3)

        # Reset the action results
        self._actionResult = None

        menu.exec_(point)

        if self._actionResult is not None:
            self.setValue(self._actionResult)

    def widget(self,):
        """
        Get the widget used to set and get the option value.
        
        :rtype: QtWidgets.QWidget
        """
        return self._widget

    def refresh(self):
        """Refresh the style properties."""
        self.setProperty('default', self.isDefault())
        self.setStyleSheet(self.styleSheet())


class Label(QtWidgets.QLabel):

    """A custom label which supports elide right."""

    def __init__(self, *args):
        super(Label, self).__init__(*args)
        self._text = ''

    def setText(self, text):
        """
        Overriding this method to store the original text.
        
        :type text: str
        """
        self._text = text
        QtWidgets.QLabel.setText(self, text)

    def resizeEvent(self, event):
        """Overriding this method to modify the text with elided text."""
        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elidedText(self._text, QtCore.Qt.ElideRight, self.width())
        QtWidgets.QLabel.setText(self, elided)


class LabelOptionWidget(OptionWidget):

    def __init__(self, *args, **kwargs):
        super(LabelOptionWidget, self).__init__(*args, **kwargs)

        widget = Label(self)
        widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.setWidget(widget)

    def value(self):
        """
        Get the value of the label.
        
        :rtype: str 
        """
        return unicode(self.widget().text())

    def setValue(self, value):
        """
        Set the value of the label.
        
        :type value: str 
        """
        self.widget().setText(value)
        super(LabelOptionWidget, self).setValue(value)


class StringOptionWidget(OptionWidget):

    def __init__(self, *args, **kwargs):
        super(StringOptionWidget, self).__init__(*args, **kwargs)

        widget = QtWidgets.QLineEdit(self)
        widget.textChanged.connect(self.emitValueChanged)
        self.setWidget(widget)

    def value(self):
        """
        Get the value of the widget.
        
        :rtype: str 
        """
        return str(self.widget().text())

    def setValue(self, value):
        """
        Set the string value for the widget.
        
        :type value: str 
        """
        self.widget().setText(value)
        super(StringOptionWidget, self).setValue(value)


class TextOptionWidget(OptionWidget):

    DefaultLayout = "Vertical"

    def __init__(self, *args, **kwargs):
        super(TextOptionWidget, self).__init__(*args, **kwargs)

        widget = QtWidgets.QTextEdit(self)
        widget.textChanged.connect(self.emitValueChanged)
        self.setWidget(widget)

    def value(self):
        """
        Get the text value of the text edit.
        
        :rtype: str 
        """
        return str(self.widget().toPlainText())

    def setValue(self, value):
        """
        Set the text value for the text edit.
        
        :type value: str 
        """
        self.widget().setText(value)
        super(TextOptionWidget, self).setValue(value)


class IntOptionWidget(OptionWidget):

    def __init__(self, *args, **kwargs):
        super(IntOptionWidget, self).__init__(*args, **kwargs)

        validator = QtGui.QIntValidator(-50000000, 50000000, self)

        widget = QtWidgets.QLineEdit(self)
        widget.setValidator(validator)
        widget.textChanged.connect(self.emitValueChanged)
        self.setWidget(widget)

    def value(self):
        """
        Get the int value for the widget.
        
        :rtype: int 
        """
        value = self.widget().text()
        if value.strip() == '':
            value = self.default()

        return int(str(value))

    def setValue(self, value):
        """
        Set the int value for the widget.
        
        :type value: int
        """
        if value == '':
            value = self.default()

        self.widget().setText(str(int(value)))


class BoolOptionWidget(OptionWidget):

    def __init__(self, *args, **kwargs):
        super(BoolOptionWidget, self).__init__(*args, **kwargs)

        widget = QtWidgets.QCheckBox(self)
        widget.stateChanged.connect(self.emitValueChanged)

        self.setWidget(widget)

    def value(self):
        """
        Get the value of the checkbox.
        
        :rtype: bool 
        """
        return bool(self.widget().isChecked())

    def setValue(self, value):
        """
        Set the value of the checkbox.
        
        :type value: bool 
        """
        self.widget().setChecked(value)
        super(BoolOptionWidget, self).setValue(value)


class RangeOptionWidget(OptionWidget):

    def __init__(self, *args, **kwargs):
        super(RangeOptionWidget, self).__init__(*args, **kwargs)

        widget = QtWidgets.QFrame(self)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        widget.setLayout(layout)

        validator = QtGui.QIntValidator(-50000000, 50000000, self)

        self._minwidget = QtWidgets.QLineEdit(self)
        self._minwidget.setValidator(validator)
        self._minwidget.textChanged.connect(self.emitValueChanged)
        widget.layout().addWidget(self._minwidget)

        self._maxwidget = QtWidgets.QLineEdit(self)
        self._maxwidget.setValidator(validator)
        self._maxwidget.textChanged.connect(self.emitValueChanged)
        widget.layout().addWidget(self._maxwidget)

        self.setWidget(widget)

    def value(self):
        """
        Get the current range.
        
        :rtype: list[int] 
        """
        min = int(float(self._minwidget.text() or "0"))
        max = int(float(self._maxwidget.text() or "0"))

        return min, max

    def setValue(self, value):
        """
        Set the current range.
        
        :type value: list[int] 
        """
        minValue, maxValue = int(value[0]), int(value[1])

        self._minwidget.setText(str(minValue))
        self._maxwidget.setText(str(maxValue))

        super(RangeOptionWidget, self).setValue(value)


class EnumOptionWidget(OptionWidget):

    def __init__(self, *args, **kwargs):
        super(EnumOptionWidget, self).__init__(*args, **kwargs)

        widget = QtWidgets.QComboBox(self)
        widget.currentIndexChanged.connect(self.emitValueChanged)

        self.setWidget(widget)

    def value(self):
        """
        Get the value of the combobox.
        
        :rtype: str 
        """
        return str(self.widget().currentText())

    def setState(self, state):
        """
        Set the current state with support for editable.
        
        :type state: dict
        """
        super(EnumOptionWidget, self).setState(state)

        editable = state.get('editable')
        if editable is not None:
            self.widget().setEditable(editable)

    def setValue(self, item):
        """
        Set the current value of the combobox.
        
        :type item: str 
        """
        self.widget().setCurrentText(item)

    def setItems(self, items):
        """
        Set the current items of the combobox.
        
        :type items: list[str]
        """
        self.widget().clear()
        self.widget().addItems(items)


class SeparatorOptionWidget(OptionWidget):

    def __init__(self, *args, **kwargs):
        super(SeparatorOptionWidget, self).__init__(*args, **kwargs)

        separator = QtWidgets.QLabel(self)
        separator.setObjectName('widget')
        separator.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred
        )

        self.setWidget(separator)

        self.label().hide()

    def setValue(self, value):
        """
        Set the current text of the separator.
        
        :type value: str 
        """
        self.widget().setText(value)

    def value(self):
        """
        Get the current text of the combobox.
        
        :rtype: str 
        """
        return self.widget().text()


class OptionsWidget(QtWidgets.QFrame):

    accepted = QtCore.Signal(object)
    stateChanged = QtCore.Signal()

    OptionWidgetMap = {
        "int": IntOptionWidget,
        "bool": BoolOptionWidget,
        "enum": EnumOptionWidget,
        "text": TextOptionWidget,
        "label": LabelOptionWidget,
        "range": RangeOptionWidget,
        "string": StringOptionWidget,
        "separator": SeparatorOptionWidget
    }

    def __init__(self, *args, **kwargs):
        super(OptionsWidget, self).__init__(*args, **kwargs)

        self._widgets = []
        self._options = []
        self._validator = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)

        self._optionsFrame = QtWidgets.QFrame(self)
        self._optionsFrame.setObjectName('optionsFrame')

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

    def setOptions(self, options):
        """Set the options for the widget."""
        self._options = options

        for option in options:

            cls = self.OptionWidgetMap.get(option.get('type', 'label'))

            if not cls:
                logger.warning("Cannot find widget for %s", option)
                continue

            widget = cls(options=option)
            widget.setOption(option)

            value = option.get('value')
            default = option.get('default')
            if value is None and default is not None:
                widget.setValue(default)

            self._widgets.append(widget)

            callback = functools.partial(self._optionChanged, widget)
            widget.valueChanged.connect(callback)

            self._optionsFrame.layout().addWidget(widget)

    def _optionChanged(self, widget):
        """
        Triggered when the given option widget changes value.
        
        :type widget: OptionWidget 
        """
        self.stateChanged.emit()
        self.validate()

    def accept(self):
        """Accept the current options"""
        self.emitAcceptedCallback()

    def closeEvent(self, event):
        super(OptionsWidget, self).closeEvent(event)

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
        :rtype: OptionWidget 
        """
        for widget in self._widgets:
            if widget.options().get('name') == name:
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
            options[widget.option().get('name')] = widget.value()
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
        expanded = state.get('expanded')
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
                if option.get("name") == widget.option().get('name'):
                    widget.setOption(option)

        for widget in self._widgets:
            widget.blockSignals(False)


STYLE = """

/*
FormWidget > #title {
    font: bold;
    font-size: 12pt;
    text-align: left;
}

FormWidget ThumbnailOptionWidget #thumbnailLabel {
    background-color: rgb(100, 100, 100);
}

FormWidget {
    margin: 4px;
    background-color: rgb(240, 240, 240);
}

FormWidget #acceptButton {
    font: bold;
    color: rgb(250, 250, 250);
    height: 32px;
    border: 1px solid rgb(100, 160, 200);
    background-color: rgb(100, 140, 255);
}

FormWidget > #optionsFrame {
    background-color: rgb(255, 255, 255);
}

FormWidget QLineEdit {
    height: 24px;
    border: 1px solid rgb(240, 0, 0, 255);
}

PathOptionWidget QPushButton {
    height: 20px;
    min-width: 24px;
    max-width: 24px;
}


OptionWidget[default=true] QLineEdit,
OptionWidget[default=true] QTextEdit {
    border: 1px solid rgb(240, 150, 0, 255);
    background-color: rgb(240, 150, 0, 100);
}

OptionWidget[default=true] QComboBox {
    border: 1px solid rgb(150, 150, 150, 255);

}

OptionWidget[default=false] QComboBox {
    border: 1px solid rgb(240, 150, 0, 255);
    background-color: rgb(240, 150, 0, 100);
}

OptionWidget[default=false] QRadioButton:checked {
    color: rgb(240, 150, 0);
}

OptionWidget[default=false] #label {
    color: rgb(240, 150, 0);
}
  
OptionWidget[error=true] QLineEdit,
OptionWidget[error=true] QTextEdit {
    border: 1px solid rgb(240, 0, 0, 255);
    background-color: rgb(240, 0, 0, 100);
}

OptionWidget[error=true] QRadioButton:checked {
    color: rgb(240, 0, 0);
}

OptionWidget[error=true] #label {
    color: rgb(240, 0, 0);
}

OptionWidget QLineEdit:disabled,
OptionWidget QTextEdit:disabled {
    border: 1px solid rgb(100, 100, 100, 255);
    background-color: rgb(100, 100, 100, 100);
}
*/
"""


def example1():

    options = [
        {
            'name': 'name',
            'value': 'Face.anim',
            'type': 'label',
        },
        {
            'name': 'objects',
            'value': '125 objects',
            'type': 'label',
        },
        {
            'name': 'comment',
            'value': 'this is a comment',
            'type': 'label',
        },
    ]

    w = OptionsWidget()
    w.setOptions(options)
    w.setStyleSheet(STYLE)

    return w


if __name__ == '__main__':
    import studioqt
    with studioqt.app():
        w = example1()
        w.show()



