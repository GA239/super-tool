import functools
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from supertool import usefull_widget_tools as uwt

OPERATION_CLEAR = 'clear'
OPERATION_ESTIMATE = 'estimate'
OPERATION_ADDITION = 'addition'
OPERATION_SUBTRACTION = 'subtraction'
OPERATION_MULTIPLICATION = 'multiplication'
OPERATION_DIVISION = 'division'
OPERATION_POW = 'pow'


class NumericKeypad(QtWidgets.QWidget):
    """
    A widget that contains a numeric keypad and a point
    """

    # Notifies of a key press on the numeric keypad
    numeric_keypad_signal = QtCore.pyqtSignal(str)

    def __init__(self, button_size_policy=None, button_font=None, parent=None):
        super(NumericKeypad, self).__init__(parent)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("num_gridLayout")
        button_creator = functools.partial(uwt.create_button, parent=self,
                                           font=button_font,
                                           size_policy=button_size_policy)
        for i in range(10):
            button = button_creator(str(i), str(i))
            button.clicked.connect(functools.partial(self.button_pressed, str(i)))
            if i == 0:
                self.gridLayout.addWidget(button, 3, 0, 1, 2)
            else:
                self.gridLayout.addWidget(button, (i-1) // 3, (i-1) % 3, 1, 1)

        button = button_creator('point', '.')
        button.clicked.connect(functools.partial(self.button_pressed, '.'))
        self.gridLayout.addWidget(button, 3, 2, 1, 1)

    def button_pressed(self, number: str) -> None:
        """
        Notifies of a key press on the numeric keypad

        :param number: string representation of the pressed key
        :return: None
        """
        self.numeric_keypad_signal.emit(number)


class Keypad(QtWidgets.QWidget):
    """
    A widget that contains a numeric keypad widget anв operation buttons
    """

    key_pad_signal = QtCore.pyqtSignal(str)

    def __init__(self, operations, button_font=None, parent=None):
        super(Keypad, self).__init__(parent)

        self.operations = operations

        self.button_font = button_font
        self.button_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                        QtWidgets.QSizePolicy.Expanding)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self._create_operation_buttons()
        self.num_key_pad = NumericKeypad(button_size_policy=self.button_size_policy,
                                         button_font=self.button_font,
                                         parent=None)
        self.gridLayout.addWidget(self.num_key_pad, 1, 0, 4, 3)

    def _create_operation_buttons(self):
        """
        An internal method that creates and initializes operation buttons
        :return: None
        """

        # coordinates of buttons in grid layout
        operations_cords = (
            (0, 0, 1, 1),
            (0, 2, 1, 1),
            (0, 3, 1, 1),
            (1, 3, 1, 1),
            (2, 3, 1, 1),
            (3, 3, 1, 1),
            (4, 3, 1, 1)
        )

        for val, coord in zip(self.operations.values(), operations_cords):
            val['coordinates'] = coord

        button_creator = functools.partial(uwt.create_button, parent=self,
                                           font=self.button_font,
                                           size_policy=self.button_size_policy)

        for operation_name, operation_value in self.operations.items():
            button = button_creator(operation_name, operation_value['text'])
            button.clicked.connect(functools.partial(self.button_pressed,
                                                     operation_name))
            self.gridLayout.addWidget(button, *operation_value['coordinates'])

    def button_pressed(self, text):
        """
        Notifies of a operation key press

        :param text: string representation of the pressed key
        :return: None
        """

        self.key_pad_signal.emit(text)


class Estimator(QtCore.QObject):
    """
    The core of the application,
    in which the values are calculated
    """

    estimation_info_signal = QtCore.pyqtSignal(str)

    def __init__(self, operations, parent=None):
        super(Estimator, self).__init__(parent)
        self.first_number = None
        self.second_number = None
        self.current_number = ''
        self.current_info = ''
        self.current_operation = None
        self.operations = operations

        # basic operations that the calculator supports
        estimators = [
            None,
            None,
            lambda x, y: x + y,
            lambda x, y: x - y,
            lambda x, y: x * y,
            lambda x, y: x / y,
            lambda x, y: x ** y
        ]
        for operation, estimation in zip(self.operations.values(), estimators):
            operation['estimator'] = estimation

    def _clear(self):
        """
        Clears the buffer values and
        emits a signal to clear the widget

        :return: None
        """

        self.first_number = None
        self.second_number = None
        self.current_number = ''
        self.current_info = ''
        self.current_operation = None
        self.estimation_info_signal.emit(self.current_info)

    def _estimate(self) -> float:
        """
        Performs calculations according to the list of supported functions
        :return: float -- estimated value
        """

        if self.current_operation == OPERATION_DIVISION and self.second_number == 0:
            raise ValueError('Zero division')
        return self.operations[self.current_operation]['estimator'](self.first_number,
                                                                    self.second_number)

    def num_pad_button_pressed(self, value: str) -> None:
        """
        Processes the key press on the numeric keypad
        :param value:
        :return:
        """

        self.current_number += value
        self.estimation_info_signal.emit(f'{self.current_info}{self.current_number}')

    def operation_button_pressed(self, operation: str) -> None:
        """
        Handles pressing the operation button
        :param operation: string representation of the operation
        :return:
        """

        if operation == OPERATION_CLEAR:
            self._clear()
        elif operation == OPERATION_ESTIMATE:
            self._equally_handler()
        else:
            self._computational_operation_handler(operation)

    def _equally_handler(self):
        """
        Handles the button press

        :return: None
        """

        try:
            self.second_number = float(self.current_number)
            result = self._estimate()
        except (ValueError, KeyError):
            self._clear()
            self.estimation_info_signal.emit('Error!')
            return

        result_str = f"{self.current_info}{self.rounding(self.second_number)}={result}"
        self._clear()
        self.estimation_info_signal.emit(result_str)

    def _computational_operation_handler(self, operation: str) -> None:
        """
        Handles pressing of the button with computing operation
        :param operation: string representation of the operation
        :return: None
        """

        if operation == OPERATION_SUBTRACTION and \
                (self.current_number == '' or self.current_operation is not None):
            self.num_pad_button_pressed(self.operations[operation]['text'])
            return

        try:
            self.first_number = float(self.current_number)
        except ValueError:
            self._clear()
            self.estimation_info_signal.emit('Error!')
            return

        self.current_operation = operation
        self.current_number = ''

        self.current_info = str(self.rounding(self.first_number)) + self.operations[operation]['text']
        self.estimation_info_signal.emit(self.current_info)

    @staticmethod
    def rounding(value: float) -> int or float:
        """
        Rounds a value if it is an integer

        :param value: -- float
        :return: int or float input value
        """

        if int(value) != 0 and value % int(value) == 0:
            return int(value)
        return value


class Calculator(QtWidgets.QWidget):
    """Main calculator widget"""

    def __init__(self, parent=None):
        super(Calculator, self).__init__(parent)

        self.setWindowTitle("Calculator")
        self.setGeometry(QtCore.QRect(100, 100, 100, 400))

        # make some beauty
        self.set_style()

        self.Layout = QtWidgets.QVBoxLayout(self)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.Layout.setObjectName("Calculator_gridLayout")

        self.font = QtGui.QFont()
        self.font.setPointSize(20)
        self.font.setBold(True)
        self.font.setWeight(75)

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setReadOnly(True)
        self.line_edit.setText('Hello')
        self.line_edit.setFont(self.font)

        operations_keys = (
            OPERATION_CLEAR,
            OPERATION_ESTIMATE,
            OPERATION_ADDITION,
            OPERATION_SUBTRACTION,
            OPERATION_MULTIPLICATION,
            OPERATION_DIVISION,
            OPERATION_POW
        )
        operations_texts = (
            'AC', '=', '+', '-', '*', '/', '^',
        )

        operations = {
            op[0]: {
                'text': op[1],
            } for op in zip(operations_keys,
                            operations_texts)}

        self.key_pad = Keypad(operations, self.font, self)
        self.Layout.addWidget(self.line_edit)
        self.Layout.addWidget(self.key_pad)

        # interaction logic
        estimator = Estimator(operations, self)

        # we ask the kernel and set the current status to the scoreboard
        estimator.estimation_info_signal.connect(self.set_line_edit_text)

        # send keystrokes to the kernel for handling
        self.key_pad.num_key_pad.numeric_keypad_signal.connect(estimator.num_pad_button_pressed)
        self.key_pad.key_pad_signal.connect(estimator.operation_button_pressed)

    def set_line_edit_text(self, text: str) -> None:
        """
        Sets the text value in the lineEdit

        :param text: text value
        :return: None
        """

        self.line_edit.setText(text)

    def set_style(self):
        self.setStyleSheet("""
                QWidget { background-color: #3C3F41 }

                .QLineEdit {
                    color: #92BD6C;
                    background-color: #3C3F41;
                    selection-color: #C1C1C1;
                    selection-background-color: #545555;
                    border: 1px solid #313335;
                    font: 25pt "Monaco";
                    }

                QPushButton {
                    background-color: #3C3F41;
                    color: #C1C1C1;
                    border: 1px solid #313335;
                    padding: 1px;
                    min-width: 80px;
                    text-align: center;
                    font: 14pt "Monaco";
                }

                QPushButton:hover  {
                    color: #C1C1C1;
                    border: 2px solid #92BD6C;
                    padding: 1px;
                    min-width: 80px;
                }

                QPushButton:pressed{
                    color: #92BD6C;
                    border: 2px solid #92BD6C;
                    padding: 1px;
                    min-width: 80px;
                }

                """)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())
