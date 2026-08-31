from PyQt5.QtWidgets import QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen

class DashboardScreen(BaseScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        grid = QGridLayout()
        self.layout.addLayout(grid)
        
        self.add_stat(grid, "VFD Status", "RUNNING", 0, 0)
        self.add_stat(grid, "Frequency (Hz)", "45.0", 0, 1)
        self.add_stat(grid, "Speed (RPM)", "1450", 1, 1)
        self.add_stat(grid, "Current (A)", "3.20", 2, 0)
        self.add_stat(grid, "Voltage (V)", "380.0", 2, 1)
        self.add_stat(grid, "Temp (°C)", "42.5", 3, 0)
        self.add_stat(grid, "DC Bus (V)", "540", 3, 1)
        
    def add_stat(self, grid, label, value, row, col):
        from PyQt5.QtWidgets import QFrame, QVBoxLayout
        frame = QFrame()
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 10, 15, 10)
        
        lbl_title = QLabel(label)
        lbl_title.setFont(QFont("Inter", 11))
        lbl_title.setStyleSheet("color: #8e8e93; border: none;")
        
        lbl_val = QLabel(value)
        lbl_val.setFont(QFont("Inter", 24, QFont.Bold))
        lbl_val.setStyleSheet("color: #ffffff; border: none;")
        lbl_val.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        layout.addWidget(lbl_title)
        layout.addStretch()
        layout.addWidget(lbl_val)
        
        grid.addWidget(frame, row, col)
