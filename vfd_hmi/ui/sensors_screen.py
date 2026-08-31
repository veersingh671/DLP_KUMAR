from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.components import BaseScreen

class SensorsScreen(BaseScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        sensors = [
            ("TEMPERATURE", "42.5 °C"),
            ("VOLTAGE", "380.2 V"),
            ("CURRENT", "3.21 A"),
            ("PRESSURE", "4.2 bar"),
            ("SPEED", "1450 RPM")
        ]
        
        for name, value in sensors:
            frame = QFrame()
            frame.setFixedHeight(70)
            
            h_layout = QHBoxLayout(frame)
            h_layout.setContentsMargins(20, 10, 20, 10)
            
            lbl_name = QLabel(name)
            lbl_name.setFont(QFont("Inter", 14, QFont.Bold))
            lbl_name.setStyleSheet("color: #8e8e93;")
            
            lbl_val = QLabel(value)
            lbl_val.setFont(QFont("Inter", 18, QFont.Bold))
            lbl_val.setStyleSheet("color: #ffffff;")
            lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            h_layout.addWidget(lbl_name)
            h_layout.addWidget(lbl_val)
            
            self.layout.addWidget(frame)
            
        self.layout.addStretch()
