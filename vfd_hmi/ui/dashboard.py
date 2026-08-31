from PyQt5.QtWidgets import QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen

class DashboardScreen(BaseScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        grid = QGridLayout()
        self.layout.addLayout(grid)
        
        self.add_stat(grid, "VFD STATUS", "RUNNING", 0, 0, "#4caf50")
        self.add_stat(grid, "FREQUENCY", "45.0 Hz", 0, 1, "#03a9f4")
        self.add_stat(grid, "SPEED", "1450 RPM", 1, 1, "#ff9800")
        self.add_stat(grid, "CURRENT", "3.20 A", 2, 0, "#9c27b0")
        self.add_stat(grid, "VOLTAGE", "380.0 V", 2, 1, "#f44336")
        self.add_stat(grid, "TEMPERATURE", "42.5 °C", 3, 0, "#ff5722")
        self.add_stat(grid, "DC BUS", "540 V", 3, 1, "#009688")
        
    def add_stat(self, grid, label, value, row, col, fg_color):
        from PyQt5.QtWidgets import QFrame, QVBoxLayout
        frame = QFrame()
        frame.setStyleSheet(f"background-color: #1e1e1e; border-radius: 8px; border-left: 4px solid {fg_color};")
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 10, 15, 10)
        
        lbl_title = QLabel(label)
        lbl_title.setFont(QFont("Arial", 11, QFont.Bold))
        lbl_title.setStyleSheet("color: #aaaaaa; border: none;")
        
        lbl_val = QLabel(value)
        lbl_val.setFont(QFont("Arial", 22, QFont.Bold))
        lbl_val.setStyleSheet(f"color: {fg_color}; border: none;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_val)
        
        grid.addWidget(frame, row, col)
