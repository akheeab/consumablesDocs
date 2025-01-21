from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from gui.draggable_frame import DraggableFrame


class FilePickerWidget(QWidget):
    microbiological_file_selected = pyqtSignal(str)
    air_file_selected = pyqtSignal(str)
    surface_file_selected = pyqtSignal(str)
    peel_file_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Create individual frames for each test type
        self.microbiological_frame = DraggableFrame("Microbiological Test File")
        self.microbiological_frame.file_dropped.connect(self.microbiological_file_selected.emit)

        self.air_frame = DraggableFrame("Air Test File")
        self.air_frame.file_dropped.connect(self.air_file_selected.emit)

        self.surface_frame = DraggableFrame("Surface Test File")
        self.surface_frame.file_dropped.connect(self.surface_file_selected.emit)

        self.peel_frame = DraggableFrame("Peel Test File")
        self.peel_frame.file_dropped.connect(self.peel_file_selected.emit)

        # Add frames to layout
        layout.addWidget(self.microbiological_frame)
        layout.addWidget(self.air_frame)
        layout.addWidget(self.surface_frame)
        layout.addWidget(self.peel_frame)

        self.setLayout(layout)

    def set_frame_success_state(self):
        """Set the frame color to green for all file frames."""
        self.microbiological_frame.set_highlighted_style_green()
        self.peel_frame.set_highlighted_style_green()
        self.surface_frame.set_highlighted_style_green()
        self.air_frame.set_highlighted_style_green()

    def set_frame_error_state(self, file_type):
        """Set the frame color to red for the specified file type."""
        frame = None

        if file_type == "Surface Test":
            frame = self.surface_frame
        elif file_type == "Air Test":
            frame = self.air_frame
        elif file_type == "Peel Test":
            frame = self.peel_frame
        elif file_type == "Microbiological Test":
            frame = self.microbiological_frame

        if frame:
            frame.set_highlighted_style_red()
