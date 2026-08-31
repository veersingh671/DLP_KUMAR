import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Global styling with WOW Glassmorphism theme
    app.setStyleSheet("""
        QWidget {
            color: #ffffff;
            font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
            font-size: 15px;
        }
        QPushButton {
            background-color: rgba(255, 255, 255, 15);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 25);
            border-radius: 8px;
            padding: 10px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 30);
            border: 1px solid rgba(255, 255, 255, 50);
        }
        QPushButton:pressed {
            background-color: rgba(0, 0, 0, 100);
        }
        QPushButton:checked {
            background-color: rgba(255, 107, 0, 60);
            border: 1px solid #ff6b00;
            color: #ffffff;
        }
        QLabel {
            background-color: transparent;
        }
        QFrame {
            border-radius: 12px;
            background-color: rgba(10, 15, 30, 80);
            border: 1px solid rgba(255, 255, 255, 15);
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
