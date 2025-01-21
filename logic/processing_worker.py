import os
import shutil
# import debugpy

from PyQt6.QtCore import QObject, pyqtSignal
from logic.po_data_extractor import (
    extract_surface_test_data,
    extract_air_test_data,
    extract_peel_test_data,
    extract_microbiological_test_data,
)
from logic.ocr_processor import perform_ocr_peel_test, perform_ocr_microbiologica_test
from logic.report_generator import generate_report

class ProcessingWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, files, po_number, po_folder_path):
        super().__init__()
        self.files = files
        self.po_number = po_number
        self.po_folder_path = po_folder_path
        self.results_structure = {
            "Surface Test": {},
            "Air Test": {},
            "Peel Test": {},
            "Microbiological Test": {},
        }

    def copy_and_rename_file(self, file_path, test_name):
        """Copy and rename a file to the PO folder."""

        new_filename = f"PO {self.po_number} {test_name}.pdf"
        new_file_path = os.path.join(self.po_folder_path, new_filename)
        shutil.copy(file_path, new_file_path)
        print(f"Copied and renamed: {new_file_path}")

    def check_test_name(self, extracted_test_name, expected_test_name):
        """Check if the test name matches the expected name."""
        if extracted_test_name != expected_test_name:
            raise ValueError(f"Make sure to pick the correct file")

    def run(self):
        """Run the processing logic."""
        try:
            total_tasks = 5 # the processing goes through 5 steps, this is used for the progress bar
            completed_tasks = 0 # start with 0 steps completed
            # debugpy.debug_this_thread() # Multi threading debugging
            error_occurred = False  # Flag to indicate an error occurred
            print("Processing Started")
            print("-"*20)

            if self.files["Surface Test"] and not error_occurred:
                try:
                    print("Processing Surface Test")
                    result = extract_surface_test_data(self.files["Surface Test"])
                    self.check_test_name(result.get("Test Name"), "Surface test")
                    self.results_structure["Surface Test"] = result
                    self.copy_and_rename_file(self.files["Surface Test"], "Surface Test")
                except Exception as e:
                    print(f"Error processing Surface Test")
                    self.error.emit(f"Surface Test:\nMake sure to pick the correct file")
                    error_occurred = True

                completed_tasks += 1
                self.progress.emit(int((completed_tasks / total_tasks) * 100))

            if self.files["Air Test"] and not error_occurred:
                try:
                    print("Processing Air Test")
                    result = extract_air_test_data(self.files["Air Test"])
                    self.check_test_name(result.get("Test Name"), "Air test")
                    self.results_structure["Air Test"] = result
                    self.copy_and_rename_file(self.files["Air Test"], "Air Test")
                except Exception as e:
                    print(f"Error processing Air Test")
                    self.error.emit(f"Air Test:\nMake sure to pick the correct file")
                    error_occurred = True

                completed_tasks += 1
                self.progress.emit(int((completed_tasks / total_tasks) * 100))

            if self.files["Peel Test"] and not error_occurred:
                try:
                    print("Processing Peel Test")
                    ocr_output = perform_ocr_peel_test(self.files["Peel Test"])
                    result = extract_peel_test_data(ocr_output)
                    self.check_test_name(result.get("Test Name"), "Package Integrity Test")
                    self.results_structure["Peel Test"] = result
                    self.copy_and_rename_file(self.files["Peel Test"], "Peel Test")
                except Exception as e:
                    print(f"Error processing Peel Test")
                    self.error.emit(f"Peel Test:\nMake sure to pick the correct file")
                    error_occurred = True

                completed_tasks += 1
                self.progress.emit(int((completed_tasks / total_tasks) * 100))

            if self.files["Microbiological Test"] and not error_occurred:
                try:
                    print("Processing Microbiological Test")
                    ocr_output= perform_ocr_microbiologica_test(self.files["Microbiological Test"])
                    result = extract_microbiological_test_data(ocr_output)
                    self.check_test_name(result.get("Test Name"), "Microbiological Test")
                    self.results_structure["Microbiological Test"] = result
                    self.copy_and_rename_file(self.files["Microbiological Test"], "Microbiological Test")
                except Exception as e:
                    print(f"Error processing Microbiological Test")
                    self.error.emit(f"Microbiological Test:\nMake sure to pick the correct file")
                    error_occurred = True
            
                completed_tasks += 1
                self.progress.emit(int((completed_tasks / total_tasks) * 100))

            if error_occurred:
                print("Processing stopped due to an error while processing files.")
                return

            # Log data to word document
            try:
                generate_report(self.results_structure, self.po_number, self.po_folder_path)
                print("Report generated successfully")
                completed_tasks += 1
                self.progress.emit(int((completed_tasks / total_tasks) * 100))
            except Exception as e:
                print(f"Report generation ran through an error\n{e}")
                # self.error.emit("Report generation ran through an error")
                raise Exception("Report generation ran through an error")

            # Emit the results when processing is complete
            self.finished.emit(self.results_structure)
            
        except Exception as e:
             print(e)
             self.error.emit(f"Unexpected error")
             return
