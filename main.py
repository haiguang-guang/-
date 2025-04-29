from PyQt6.QtWidgets import QApplication
from ui.main_window import ToolsApp

if __name__ == "__main__":
    app = QApplication([])
    window = ToolsApp()
    window.show()
    app.exec() 