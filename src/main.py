import sys
from PyQt6.QtWidgets import QApplication
from src.ui import MainWindow


def main() -> None:
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("FacultyElectronicArchive")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
