"""
Entry point for DLP KUMAR VFD HMI Application.
Sets global industrial stylesheet and starts the 800x480 frameless application.
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

def main():
    # Enable high DPI scaling if needed
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Industrial Dark Slate / High Contrast Machinery Theme
    app.setStyleSheet("""
        QWidget {
            color: #f8fafc;
            font-family: 'Segoe UI', -apple-system, 'Roboto', 'Helvetica Neue', sans-serif;
            font-size: 13px;
        }
        QScrollBar:vertical {
            border: none;
            background: #0f1624;
            width: 10px;
            margin: 0px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #334155;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #ff7a00;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
