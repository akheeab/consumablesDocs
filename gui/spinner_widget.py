import os
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie


class SpinnerWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout
        self.setFixedSize(200, 150)  # Adjust the size as needed
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

        # Label for displaying text or spinner animation
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.label)

        # Load spinner animation
        spinner_gif_path = os.path.join(os.path.dirname(__file__), "../resources/img/spinner.gif")
        self.spinner_movie = QMovie(spinner_gif_path)

        # Set spinner as invisible initially
        self.reset_spinner()

    def start_spinner(self):
        """Start the spinner animation."""
        self.spinner_active = True
        self.label.setMovie(self.spinner_movie)
        self.spinner_movie.start()

    def stop_spinner(self):
        """Stop the spinner and show 'Done!' text."""
        self.spinner_active = False
        self.spinner_movie.stop()
        self.label.setText("Done!")

    def reset_spinner(self):
        """Reset the widget to its initial state."""
        self.spinner_active = False
        self.spinner_movie.stop()
        self.label.setText("Please Select Files")
