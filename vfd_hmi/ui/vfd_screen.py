from PyQt5.QtWidgets import QLabel, QGridLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen

class VFDScreen(BaseScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        grid = QGridLayout()
        self.layout.addLayout(grid)
        
        # Status Variables
        self.freq_val = 45.0
        self.is_running = True
        
        # Status
        self.lbl_status_val = self.add_stat(grid, "STATUS", "RUNNING", 0, 0, "#4caf50")
        self.lbl_freq_stat = self.add_stat(grid, "FREQUENCY", f"{self.freq_val:.1f} Hz", 0, 1)
        self.add_stat(grid, "CURRENT", "3.2 A", 1, 0)
        self.add_stat(grid, "VOLTAGE", "380 V", 1, 1)
        self.add_stat(grid, "SPEED", "1450 RPM", 2, 0)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        self.btn_minus = QPushButton("-")
        self.btn_minus.setFixedSize(60, 60)
        self.btn_minus.clicked.connect(self.decrease_freq)
        
        self.lbl_freq = QLabel(f"{self.freq_val:.1f} Hz")
        self.lbl_freq.setFont(QFont("Arial", 24, QFont.Bold))
        self.lbl_freq.setAlignment(Qt.AlignCenter)
        
        self.btn_plus = QPushButton("+")
        self.btn_plus.setFixedSize(60, 60)
        self.btn_plus.clicked.connect(self.increase_freq)
        
        ctrl_layout.addWidget(self.btn_minus)
        ctrl_layout.addWidget(self.lbl_freq)
        ctrl_layout.addWidget(self.btn_plus)
        
        grid.addLayout(ctrl_layout, 2, 1)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("START")
        self.btn_start.setStyleSheet("background-color: #4caf50; color: white; min-height: 60px;")
        self.btn_start.clicked.connect(self.start_vfd)
        
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setStyleSheet("background-color: #f44336; color: white; min-height: 60px;")
        self.btn_stop.clicked.connect(self.stop_vfd)
        
        self.btn_reset = QPushButton("RESET FAULT")
        self.btn_reset.setStyleSheet("background-color: #ff9800; color: white; min-height: 60px;")
        self.btn_reset.clicked.connect(lambda: print("Fault Reset Clicked"))
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_reset)
        
        self.layout.addSpacing(20)
        self.layout.addLayout(btn_layout)
        
    def decrease_freq(self):
        self.freq_val = max(0.0, self.freq_val - 0.5)
        self.lbl_freq.setText(f"{self.freq_val:.1f} Hz")
        self.lbl_freq_stat.setText(f"{self.freq_val:.1f} Hz")

    def increase_freq(self):
        self.freq_val = min(50.0, self.freq_val + 0.5)
        self.lbl_freq.setText(f"{self.freq_val:.1f} Hz")
        self.lbl_freq_stat.setText(f"{self.freq_val:.1f} Hz")

    def start_vfd(self):
        self.is_running = True
        self.lbl_status_val.setText("RUNNING")
        self.lbl_status_val.setStyleSheet("color: #4caf50;")

    def stop_vfd(self):
        self.is_running = False
        self.lbl_status_val.setText("STOPPED")
        self.lbl_status_val.setStyleSheet("color: #f44336;")
        
    def add_stat(self, grid, label, value, row, col, color="#ffffff"):
        lbl_title = QLabel(label)
        lbl_title.setFont(QFont("Arial", 10))
        lbl_title.setStyleSheet("color: #aaaaaa;")
        
        lbl_val = QLabel(value)
        lbl_val.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_val.setStyleSheet(f"color: {color};")
        
        grid.addWidget(lbl_title, row * 2, col)
        grid.addWidget(lbl_val, row * 2 + 1, col)
        
        return lbl_val
