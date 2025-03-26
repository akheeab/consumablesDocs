from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout

class POInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("PO Number:")
        self.input_field = QLineEdit()
        self.input_field.setInputMask("999999") # Setting the input field to take numbers only of 6 digits
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        self.setLayout(layout)
