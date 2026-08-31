from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QScrollArea, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.components import BaseScreen

class AlarmsScreen(BaseScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        title = QLabel("ACTIVE ALARMS")
        title.setFont(QFont("Inter", 16, QFont.Bold))
        title.setStyleSheet("color: #ff3b30;")
        self.layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        alarms = [
            ("[HIGH] MOTOR TEMPERATURE", "72 °C / Limit 70 °C", "#ff9800"),
            ("[FAULT] VFD OVERCURRENT", "Check motor load", "#f44336"),
            ("[WARN] SENSOR COMM LOST", "Check wiring", "#ff9800")
        ]
        
        for title_text, desc_text, color in alarms:
            frame = QFrame()
            frame.setStyleSheet(f"border-left: 4px solid {color};")
            
            f_layout = QVBoxLayout(frame)
            f_layout.setContentsMargins(15, 10, 15, 10)
            
            lbl_title = QLabel(title_text)
            lbl_title.setFont(QFont("Inter", 14, QFont.Bold))
            lbl_title.setStyleSheet(f"color: {color}; border: none;")
            
            lbl_desc = QLabel(desc_text)
            lbl_desc.setFont(QFont("Inter", 12))
            lbl_desc.setStyleSheet("color: #8e8e93; border: none;")
            
            f_layout.addWidget(lbl_title)
            f_layout.addWidget(lbl_desc)
            
            scroll_layout.addWidget(frame)
            
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        self.layout.addWidget(scroll)
        
        btn_layout = QHBoxLayout()
        btn_ack = QPushButton("ACKNOWLEDGE")
        btn_ack.setFixedHeight(50)
        
        btn_clear = QPushButton("CLEAR")
        btn_clear.setFixedHeight(50)
        
        btn_layout.addWidget(btn_ack)
        btn_layout.addWidget(btn_clear)
        self.layout.addLayout(btn_layout)
