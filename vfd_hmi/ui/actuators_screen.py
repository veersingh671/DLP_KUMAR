"""
Actuators Screen for DLP KUMAR VFD HMI.
Allows operators to inspect feedback and toggle equipment states (Motor, Fan, Valve, Brake).
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen
from core.system_state import ActuatorItem

class ActuatorRowWidget(QFrame):
    def __init__(self, actuator: ActuatorItem, toggle_callback, parent=None):
        super().__init__(parent)
        self.actuator_id = actuator.id
        self.toggle_callback = toggle_callback
        self.setFixedHeight(68)
        self.setStyleSheet("""
            QFrame {
                background-color: #121824;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(14)
        
        # Name and Type
        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        
        self.lbl_name = QLabel(actuator.name.upper())
        self.lbl_name.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.lbl_name.setStyleSheet("color: #f8fafc; border: none;")
        
        self.lbl_type = QLabel(f"Equipment Type: {actuator.equipment_type}")
        self.lbl_type.setFont(QFont("Segoe UI", 8))
        self.lbl_type.setStyleSheet("color: #64748b; border: none;")
        
        info_col.addWidget(self.lbl_name)
        info_col.addWidget(self.lbl_type)
        layout.addLayout(info_col)
        
        layout.addStretch()
        
        # Feedback Badge
        self.lbl_fb = QLabel("FB: OFF")
        self.lbl_fb.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_fb.setAlignment(Qt.AlignCenter)
        self.lbl_fb.setFixedSize(80, 30)
        layout.addWidget(self.lbl_fb)
        
        # Action Toggle Button
        self.btn_toggle = QPushButton("TURN ON")
        self.btn_toggle.setFixedSize(130, 48)
        self.btn_toggle.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_toggle.clicked.connect(lambda: self.toggle_callback(self.actuator_id))
        layout.addWidget(self.btn_toggle)
        
        self.update_state(actuator)

    def update_state(self, actuator: ActuatorItem):
        # Update Feedback Badge
        if actuator.feedback_state:
            self.lbl_fb.setText("FB: RUNNING" if actuator.equipment_type == "MOTOR" else "FB: ON")
            self.lbl_fb.setStyleSheet("""
                color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 4px;
            """)
        else:
            self.lbl_fb.setText("FB: OFF")
            self.lbl_fb.setStyleSheet("""
                color: #64748b; background-color: rgba(100, 116, 139, 0.1);
                border: 1px solid rgba(100, 116, 139, 0.3); border-radius: 4px;
            """)
            
        # Update Toggle Button
        if actuator.command_state:
            self.btn_toggle.setText("STOP" if actuator.equipment_type == "MOTOR" else "TURN OFF")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444; color: #ffffff;
                    border: 1px solid #dc2626; border-radius: 6px;
                }
                QPushButton:hover { background-color: #dc2626; }
            """)
        else:
            self.btn_toggle.setText("START" if actuator.equipment_type == "MOTOR" else "TURN ON")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #10b981; color: #ffffff;
                    border: 1px solid #059669; border-radius: 6px;
                }
                QPushButton:hover { background-color: #059669; }
            """)


class ActuatorsScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        self.rows = {}
        
        if self.controller:
            for act in self.controller.actuators:
                row = ActuatorRowWidget(act, self.controller.toggle_actuator)
                self.rows[act.id] = row
                self.layout.addWidget(row)
                
            self.layout.addStretch()
            self.controller.actuators_updated.connect(self.on_actuators_updated)

    def on_actuators_updated(self, actuators_list):
        for act in actuators_list:
            if act.id in self.rows:
                self.rows[act.id].update_state(act)
