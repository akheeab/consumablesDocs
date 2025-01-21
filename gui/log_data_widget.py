import os

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QProgressBar

from gui.spinner_widget import SpinnerWidget
from logic.processing_worker import ProcessingWorker

class LogDataWidget(QWidget):
    def __init__(self, po_input, file_picker):
        super().__init__()
        self.po_input = po_input
        self.file_picker = file_picker
        layout = QVBoxLayout()

        self.log_data_button = QPushButton("Log Data")
        self.log_data_button.clicked.connect(self.log_data)
        layout.addWidget(self.log_data_button)

        # spinner_layout = QHBoxLayout()
        progress_layout = QVBoxLayout()
        self.spinner = SpinnerWidget()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)  # Initialize at 0
        progress_layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)

        self.setLayout(layout)

        self.surface_test_file = None
        self.air_test_file = None
        self.peel_test_file = None
        self.microbiological_test_file = None

        self.thread = None
        self.worker = None

    def set_surface_test_file(self, file):
        self.surface_test_file = file

    def set_air_test_file(self, file):
        self.air_test_file = file

    def set_peel_test_file(self, file):
        self.peel_test_file = file

    def set_microbiological_test_file(self, file):
        self.microbiological_test_file = file

    def create_po_folder(self, po_number):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        po_folder_path = os.path.join(desktop, f"{po_number}")
        os.makedirs(po_folder_path, exist_ok=True)
        print(f"Created PO folder: {po_folder_path}")
        return po_folder_path

    def log_data(self):
        try:
            # Get the PO number
            po_number = self.po_input.input_field.text().strip()
            if not po_number:
                print("PO number is not entered.")
                self.spinner.reset_spinner()
                return
            
            files = {
                "Surface Test": self.surface_test_file,
                "Air Test": self.air_test_file,
                "Peel Test": self.peel_test_file,
                "Microbiological Test": self.microbiological_test_file
            }

            # Check if files are picked
            if not any(files.values()):
                print("No files selected.")
                self.spinner.reset_spinner()
                return

            # Prevent duplicate threads
            if self.thread and self.thread.isRunning():
                print("Processing is already running.")
                return

            # Disable the Log Data button
            self.log_data_button.setEnabled(False)

            # Start the spinner and reset progress bar
            self.progress_bar.setValue(0)
            self.spinner.start_spinner()

            # Create the folder on the desktop
            po_folder_path = self.create_po_folder(po_number)

            # Create the worker and thread
            self.worker = ProcessingWorker(files, po_number, po_folder_path)
            self.thread = QThread()
            self.worker.moveToThread(self.thread)

            # Connect signals
            self.thread.started.connect(self.worker.run)
            self.worker.progress.connect(self.update_progress_bar)
            self.worker.finished.connect(self.processing_complete)
            self.worker.error.connect(self.processing_error)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            # Start the thread
            self.thread.start()

        except Exception as e:
            print(f"Error during logging data: {e}")
            self.log_data_button.setEnabled(True)
            self.spinner.reset_spinner()

    def update_progress_bar(self, value):
        """Update the progress bar."""
        self.progress_bar.setValue(value)

    def processing_complete(self, results_structure):
        """Handle completion of processing."""
        try:
            print("Processing completed successfully.")
            print("Final Results Structure:")
            print(results_structure)
            print('-'*20)

            # Change frames colors to green
            self.file_picker.set_frame_success_state()

            # Stop the spinner
            self.spinner.stop_spinner()

            # Reset progress bar
            self.progress_bar.setValue(100)

            # Re-enable the Log Data button
            self.log_data_button.setEnabled(True)

            # Stop and clean up the thread
            if self.thread:
                self.thread.quit()
                self.thread.wait()
                self.thread = None
            
        except Exception as e:
            print(f"Error after processing file completion: {e}")

    def processing_error(self, error_message):
        """Handle errors during processing."""
        try:
            print(f"Error during processing: {error_message}")

            # Determine the file type that caused the error and turn its frame red
            if "Surface Test" in error_message:
                self.file_picker.set_frame_error_state("Surface Test")
            elif "Air Test" in error_message:
                self.file_picker.set_frame_error_state("Air Test")
            elif "Peel Test" in error_message:
                self.file_picker.set_frame_error_state("Peel Test")
            elif "Microbiological Test" in error_message:
                self.file_picker.set_frame_error_state("Microbiological Test")

            # Stop and clean up the thread
            if self.thread:
                self.thread.quit()
                self.thread.wait()
                self.thread = None

            # Reset spinner and re-enable the button
            self.spinner.reset_spinner()
            self.log_data_button.setEnabled(True)

            # Show error dialog
            self.show_error_dialog(error_message)

        except Exception as e:
            print(f"Error handling ran into an issue: {e}")

    def show_error_dialog(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        # msg.setText("Processing Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec()

