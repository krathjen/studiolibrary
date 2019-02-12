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

    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs)

        self._option = {}
        self._widget = None
        self._default = None
        self._required = None

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
        self.setContentsMargins(0, 0, 0, 0)

        self._label = QtWidgets.QLabel(self)
        self._label.setObjectName('label')
        self._label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        layout.addWidget(self._label)

    def label(self):
        """
        Get the label widget.
        
        :rtype: QtWidgets.QLabel 
        """
        return self._label

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
        default = state.get('default') or value

        # Must set the default before value
        if default is not None:
            self.setDefault(default)

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

        self.layout().addWidget(self._widget)

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


class LabelOption(OptionWidget):

    def __init__(self, *args, **kwargs):
        super(LabelOption, self).__init__(*args, **kwargs)

        widget = Label(self)
        widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.setWidget(widget)

    def value(self):
        return unicode(self.widget().text())

    def setValue(self, value):
        self.widget().setText(value)
        super(LabelOption, self).setValue(value)


class Label(QtWidgets.QLabel):

    def __init__(self, *args):
        super(Label, self).__init__(*args)
        self._text = ''

    def setText(self, text):
        self._text = text
        QtWidgets.QLabel.setText(self, text)

    def resizeEvent(self, event):
        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elidedText(self._text, QtCore.Qt.ElideRight, self.width())
        QtWidgets.QLabel.setText(self, elided)


class OptionsWidget(QtWidgets.QFrame):

    accepted = QtCore.Signal(object)

    OptionWidgetMap = {
        'label': LabelOption
    }

    def __init__(self, *args, **kwargs):
        super(OptionsWidget, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet(STYLE)
        self.setLayout(layout)

        self._widgets = []
        self._validator = None

        self._optionsFrame = QtWidgets.QFrame(self)
        self._optionsFrame.setObjectName('optionsFrame')

        layout = QtWidgets.QVBoxLayout(self._optionsFrame)
        self._optionsFrame.setLayout(layout)

        self.layout().addWidget(self._optionsFrame)

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

            widget = cls()
            widget.setOption(option)

            self._widgets.append(widget)

            callback = functools.partial(self._optionChanged, widget)
            widget.valueChanged.connect(callback)

            self._optionsFrame.layout().addWidget(widget)

        self._optionsFrame.layout().addStretch(0)

    def _optionChanged(self, widget):
        """
        Triggered when the given option widget changes value.
        
        :type widget: OptionWidget 
        """
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
            options = self.options()
            state = self._validator(**options)
            self._setState(state)
        else:
            logger.warning("No validator set.")

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
        state = {}
        for widget in self._widgets:
            name = widget.option().get('name')
            state.setdefault(name, {})
            state[name]['value'] = widget.value()
        return state

    def setState(self, state):
        """
        Set the current state.
        
        :type state: dict 
        """
        self._setState(state)
        self.validate()

    def _setState(self, state):
        for widget in self._widgets:
            widget.blockSignals(True)

        for widget in self._widgets:
            name = widget.option().get('name')
            widget.setState(state.get(name, {}))

        for widget in self._widgets:
            widget.blockSignals(False)


STYLE = """

QWidget {
    /*font-size: 12px;*/
    text-align: left;
}

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

/*--- Options Frame ---*/
FormWidget > #optionsFrame {
    background-color: rgb(255, 255, 255);
}

FormWidget QLineEdit {
    height: 24px;
    border: 1px solid rgb(240, 0, 0, 255);
}

/*--- Path Options ---*/
PathOptionWidget QPushButton {
    height: 20px;
    min-width: 24px;
    max-width: 24px;
}

SeparatorOptionWidget {
    min-height: 12px;
    max-height: 12px;
}

SeparatorOptionWidget > #separator {
    font: bold;
    background-color: rgb(0, 0, 0, 25);
    min-height: 1px;
    max-height: 1px;
}

OptionWidget > #label {
    margin-right: 2px;
    min-width: 52px;
    max-width: 52px;
    color: rgb(255, 255, 255, 100);
}

LabelOption > #widget {
    color: rgb(255, 255, 255, 200);
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



