from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.components import BaseScreen

class ActuatorsScreen(BaseScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        actuators = [
            ("MOTOR", "RUNNING", "#4caf50"),
            ("FAN", "OFF", "#f44336"),
            ("VALVE", "OPEN", "#4caf50"),
            ("BRAKE", "OFF", "#f44336")
        ]
        
        for name, state, color in actuators:
            frame = QFrame()
            frame.setStyleSheet("background-color: #333; border-radius: 5px;")
            frame.setFixedHeight(60)
            
            h_layout = QHBoxLayout(frame)
            
            lbl_name = QLabel(name)
            lbl_name.setFont(QFont("Arial", 14, QFont.Bold))
            lbl_name.setStyleSheet("color: #aaaaaa;")
            
            lbl_state = QLabel(state)
            lbl_state.setFont(QFont("Arial", 16, QFont.Bold))
            lbl_state.setStyleSheet(f"color: {color};")
            lbl_state.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            h_layout.addWidget(lbl_name)
            h_layout.addWidget(lbl_state)
            
            self.layout.addWidget(frame)
            
        self.layout.addStretch()
        
        btn_control = QPushButton("CONTROL ACTUATORS")
        btn_control.setFixedHeight(50)
        self.layout.addWidget(btn_control)
