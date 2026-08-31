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
        
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("START")
        self.btn_start.setStyleSheet("background-color: #ff6b00; color: white; min-height: 60px; font-size: 18px;")
        self.btn_start.clicked.connect(self.start_vfd)
        
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setStyleSheet("background-color: rgba(255, 59, 48, 40); border: 1px solid #ff3b30; color: #ff3b30; min-height: 60px; font-size: 18px;")
        self.btn_stop.clicked.connect(self.stop_vfd)
        
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setStyleSheet("background-color: rgba(255, 255, 255, 10); color: #8e8e93; min-height: 60px; font-size: 18px; border: 1px solid rgba(255,255,255,30);")
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
        self.lbl_status_val.setStyleSheet("color: #ff6b00;")

    def stop_vfd(self):
        self.is_running = False
        self.lbl_status_val.setText("STOPPED")
        self.lbl_status_val.setStyleSheet("color: #8e8e93;")
        
    def add_stat(self, grid, label, value, row, col, color="#ffffff"):
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
        
        return lbl_val
