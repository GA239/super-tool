"""Find similar files in directory with GUI"""
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from supertool import similar_files_finder
from supertool import usefull_widget_tools as uwt


class SimilarFilesFinderWidget(QtWidgets.QWidget):
    """Widget for finding duplicate files."""

    def __init__(self, parent=None):
        """Init Widget for finding duplicate files."""
        super(SimilarFilesFinderWidget, self).__init__(parent)
        self.title = 'Similar files GUI'
        self.model = QtGui.QStandardItemModel()
        self.tree_view = QtWidgets.QTreeView()
        self.data_layout = QtWidgets.QVBoxLayout(self)
        self.line_edit_with_buttons = uwt.LineEditWithBottoms('Введите путь к каталогу', self)
        self.init_ui()

    def init_ui(self):
        """Additional actions for initializing the interface"""
        self.setWindowTitle(self.title)
        self.setGeometry(QtCore.QRect(100, 100, 400, 400))
        self.data_layout.setContentsMargins(0, 0, 0, 0)
        self.data_layout.setObjectName("data_layout")

        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setModel(self.model)

        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Minimum)

        button = uwt.create_button('starter', 'Find',
                                   self.line_edit_with_buttons,
                                   font, size_policy)

        button_browser = uwt.create_button('dir_finder', 'Browse',
                                           self.line_edit_with_buttons,
                                           font, size_policy)

        button.clicked.connect(self.search_button_pressed)
        button_browser.clicked.connect(self.dir_find)

        self.line_edit_with_buttons.add_button(button_browser)
        self.line_edit_with_buttons.add_button(button)
        self.line_edit_with_buttons.set_font(font)

        self.data_layout.addWidget(self.line_edit_with_buttons)
        self.data_layout.addWidget(self.tree_view)
        self.setLayout(self.data_layout)

    def keyPressEvent(self, event):  # noqa
        """Starts a search for duplicate files when you press enter."""
        if event.key() == 16777220:
            self.search_button_pressed()

    def dir_find(self):
        """It helps to select a directory by showing the directory selection window."""
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите каталог")
        self.line_edit_with_buttons.set_text(directory)

    def add_items(self, elements: dict) -> None:
        """
        Adds dictionary elements to the model

        :param elements: dict of similar files
        :return: None
        """
        for element in enumerate(elements.values()):
            item = QtGui.QStandardItem(f'Similar group {element[0]}')
            self.model.appendRow(item)
            for val in element[1]:
                item_2 = QtGui.QStandardItem(val)
                item.appendRow(item_2)

    def search(self):
        """Starts the same file search."""
        self.model.clear()
        self.model.setHorizontalHeaderLabels([self.tr("")])

        try:
            sim_files = similar_files_finder.check_for_duplicates(self.line_edit_with_buttons.get_text())
        except ValueError as e:
            QtWidgets.QMessageBox.about(self, 'Error!', f'{e}')
        else:
            if not sim_files:
                label = 'Duplicates not found!'
            else:
                label = 'Duplicates:'
            self.model.setHorizontalHeaderLabels([self.tr(label)])
            self.add_items(sim_files)

    def search_button_pressed(self):
        """Action for search button"""
        self.search()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SimilarFilesFinderWidget()
    window.show()
    sys.exit(app.exec_())
