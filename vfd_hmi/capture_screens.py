"""
Script to capture screenshots of all 7 HMI screens at exact 800x480 resolution.
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

def capture_all():
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Apply stylesheet
    from main import main
    # Use same styling
    app.setStyleSheet("""
        QWidget {
            color: #f8fafc;
            font-family: 'Segoe UI', -apple-system, 'Roboto', sans-serif;
            font-size: 13px;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    
    # Tick simulation once
    window.controller.start_vfd()
    for _ in range(25):
        window.controller._simulation_tick()
        
    for idx, name in enumerate(window.screen_names):
        window.switch_screen(idx)
        app.processEvents()
        
        pixmap = window.grab()
        clean_name = name.lower().replace(" ", "_").replace("&", "and")
        file_path = os.path.join(out_dir, f"{idx+1}_{clean_name}.png")
        pixmap.save(file_path, "PNG")
        print(f"Captured: {file_path}")

    window.close()

if __name__ == "__main__":
    capture_all()
