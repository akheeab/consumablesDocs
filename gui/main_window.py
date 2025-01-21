from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from gui.po_input_widget import POInputWidget
from gui.file_picker_widget import FilePickerWidget
from gui.log_data_widget import LogDataWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Miloda Documents Tool")

        main_widget = QWidget()
        layout = QVBoxLayout()

        self.po_input = POInputWidget()
        self.file_picker = FilePickerWidget()
        self.log_data = LogDataWidget(po_input=self.po_input, file_picker=self.file_picker)

        # Connect the surface, air, peel, and microbiological test file signals
        self.file_picker.surface_file_selected.connect(self.log_data.set_surface_test_file)
        self.file_picker.air_file_selected.connect(self.log_data.set_air_test_file)
        self.file_picker.peel_file_selected.connect(self.log_data.set_peel_test_file)
        self.file_picker.microbiological_file_selected.connect(self.log_data.set_microbiological_test_file)

        layout.addWidget(self.po_input)
        layout.addWidget(self.file_picker)
        layout.addWidget(self.log_data)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        