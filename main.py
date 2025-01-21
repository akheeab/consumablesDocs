import sys
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtGui

from gui.main_window import MainWindow

# For taskbar icon
try:
    from ctypes import windll
    myappid = "AlphaOmega.Consumables.MilodaAutomation.1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(f"resources/img/AO-icon.ico"))
    window = MainWindow()
    window.show()
    print("Program Started")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
