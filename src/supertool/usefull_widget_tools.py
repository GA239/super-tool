"""Set of tools for Qt widgets"""
from PyQt5 import QtWidgets


def create_button(obj_name: str, text: str,
                  parent: 'QObject',
                  font: 'QFont',
                  size_policy:
                  'QSizePolicy') -> 'QPushButton':
    """
    Creates a button with the specified parameters

    :param obj_name: object name in the hierarchy of the qt object model
    :param text: button text
    :param parent: widget parent
    :param font: text font
    :param size_policy: size policy
    :return: QPushButton -- PushButton
    """
    button = QtWidgets.QPushButton(parent)
    button.setSizePolicy(size_policy)
    button.setFont(font)
    button.setObjectName(f'button_{obj_name}')
    button.setText(text)
    return button


class LineEditWithBottoms(QtWidgets.QWidget):
    """A widget containing an input field and an array of buttons."""

    def __init__(self, greeting='', parent=None):
        """Init lineEdit with bottoms."""
        super(LineEditWithBottoms, self).__init__(parent)
        self.data_layout = QtWidgets.QHBoxLayout(self)
        self.line_edit = QtWidgets.QLineEdit()
        self.data_layout.setContentsMargins(0, 0, 0, 0)
        self.data_layout.setObjectName("horizontal_layout")

        self.line_edit.setText(greeting)

        self.data_layout.addWidget(self.line_edit)
        self.buttons = []

    def add_button(self, button):
        """Adds a button to the widget"""
        self.data_layout.addWidget(button)
        self.buttons.append(button)

    def set_font(self, font):
        """
        Sets the font for the input field and each button

        :param font: 'QFont'
        :return: None
        """
        self.line_edit.setFont(font)
        for btn in self.buttons:
            btn.setFont(font)

    def get_text(self):
        """Returns the value of the text from the input field."""
        return self.line_edit.text()

    def set_text(self, text):
        """Sets the value of the text to the input field."""
        self.line_edit.setText(text)

    def connect_button_with_slot(self, button_number: int, func: 'callable') -> None:
        """
        Connects a button press signal to the handler.

        :param button_number: index in button array
        :param func: handler
        :return: None
        """
        if button_number >= len(self.buttons):
            raise ValueError('Incorrect button number')
        self.buttons[button_number].clicked.connect(func)
