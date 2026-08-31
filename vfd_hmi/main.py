import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Global styling with colorful, modern industrial theme
    app.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 15px;
        }
        QPushButton {
            background-color: #2b2b2b;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #3b3b3b;
            border: 1px solid #5a5a5a;
        }
        QPushButton:pressed {
            background-color: #1f1f1f;
        }
        QPushButton:checked {
            background-color: #00bcd4;
            color: #ffffff;
            border: 1px solid #0097a7;
        }
        QLabel {
            background-color: transparent;
        }
        QFrame {
            border-radius: 8px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
