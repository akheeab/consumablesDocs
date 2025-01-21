from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

class DraggableFrame(QFrame):
    file_dropped = pyqtSignal(str)  # Signal emitted when a file is dropped

    def __init__(self, label_text):
        super().__init__()
        self.setAcceptDrops(True)  # Enable drag-and-drop
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setFixedHeight(100)
        self.set_default_style()

        # Add label
        layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

        self.label_text = label_text

    def set_default_style(self):
        """Set the default style for the frame."""
        self.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #aaa;")

    def set_highlighted_style_green(self):
        """Set the highlighted style when a file is dropped."""
        self.setStyleSheet("background-color: #d4f8d4; border: 2px dashed #5cb85c;")  # Green color

    def set_highlighted_style_red(self):
        """Set the highlighted style when en error occurs."""
        self.setStyleSheet("background-color: #f8d4d4; border: 2px dashed #b85c5c;")  # Green color

    def set_highlighted_style_blue(self):
        """Set the highlighted style when en error occurs."""
        self.setStyleSheet("background-color: #d4d4f8; border: 2px dashed #5c5cb8;")  # Green color

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Allow drag events only for files."""
        if event.mimeData().hasUrls():  # Ensure it's a file
            event.accept()
            print(f"Drag entered valid file. {self.label_text}")  # Debugging
        else:
            event.ignore()
            print("Drag ignored.")  # Debugging

    def dropEvent(self, event: QDropEvent):
        """Handle the file drop."""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file in files:
            if file.lower().endswith(".pdf"):  # Only accept PDF files
                self.file_dropped.emit(file)  # Emit the file path
                print(f"File dropped: {file}. {self.label_text}")  # Debugging
                self.set_highlighted_style_blue()
            else:
                print(f"Ignored non-PDF file: {file}")

    def mousePressEvent(self, event):
        """Open a file dialog when the frame is clicked."""
        print(f"{self.label_text} Frame clicked.")  # Debugging
        file_dialog = QFileDialog(self, f"Select {self.label_text}", "", "PDF Files (*.pdf)")
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            self.file_dropped.emit(selected_file)  # Emit the file path
            print(f"{self.label_text} selected: {selected_file}")  # Debugging
            self.set_highlighted_style_blue()
            