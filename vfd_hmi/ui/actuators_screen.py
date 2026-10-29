"""
Actuators Screen for DLP KUMAR VFD HMI.
ISA-101 Industrial Switchgear Control for Motor, Cooling Fan, Solenoid Valve, and Brake.
Features verified contactor feedback and interlock validation.
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
        self.setFixedHeight(64)
        self.setStyleSheet("""
            QFrame {
                background-color: #131923;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(14)
        
        # Name and Type
        info_col = QVBoxLayout()
        info_col.setSpacing(1)
        
        self.lbl_name = QLabel(actuator.name.upper())
        self.lbl_name.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_name.setStyleSheet("color: #f1f5f9; border: none;")
        
        coil_addrs = {
            "A01": "Coil 0x0000 (VFD Main Run)",
            "A02": "Coil 0x0001 (Forced Fan)",
            "A03": "Coil 0x0002 (Lube Valve)",
            "A04": "Coil 0x0003 (Mech Brake)"
        }
        addr = coil_addrs.get(actuator.id, "Coil 0x0000")
        self.lbl_type = QLabel(f"Equipment: {actuator.equipment_type}  •  RS-485 Modbus: {addr}")
        self.lbl_type.setFont(QFont("Consolas", 8))
        self.lbl_type.setStyleSheet("color: #64748b; border: none;")
        
        info_col.addWidget(self.lbl_name)
        info_col.addWidget(self.lbl_type)
        layout.addLayout(info_col)
        
        layout.addStretch()
        
        # Feedback Badge
        self.lbl_fb = QLabel("FB: OFF")
        self.lbl_fb.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.lbl_fb.setAlignment(Qt.AlignCenter)
        self.lbl_fb.setFixedSize(86, 28)
        layout.addWidget(self.lbl_fb)
        
        # Action Toggle Button
        self.btn_toggle = QPushButton("TURN ON")
        self.btn_toggle.setFixedSize(120, 42)
        self.btn_toggle.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.btn_toggle.clicked.connect(lambda: self.toggle_callback(self.actuator_id))
        layout.addWidget(self.btn_toggle)
        
        self.update_state(actuator)

    def update_state(self, actuator: ActuatorItem):
        if actuator.feedback_state:
            self.lbl_fb.setText("FB: RUNNING" if actuator.equipment_type == "MOTOR" else "FB: ON")
            self.lbl_fb.setStyleSheet("""
                color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 4px;
            """)
        else:
            self.lbl_fb.setText("FB: OFF")
            self.lbl_fb.setStyleSheet("""
                color: #64748b; background-color: rgba(100, 116, 139, 0.10);
                border: 1px solid rgba(100, 116, 139, 0.25); border-radius: 4px;
            """)
            
        if actuator.command_state:
            self.btn_toggle.setText("STOP" if actuator.equipment_type == "MOTOR" else "TURN OFF")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #b91c1c; color: #ffffff;
                    border: 1px solid #dc2626; border-radius: 4px;
                }
                QPushButton:hover { background-color: #dc2626; }
            """)
        else:
            self.btn_toggle.setText("START" if actuator.equipment_type == "MOTOR" else "TURN ON")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b; color: #f1f5f9;
                    border: 1px solid #334155; border-radius: 4px;
                }
                QPushButton:hover { background-color: #2563eb; color: #ffffff; border: 1px solid #3b82f6; }
            """)


class ActuatorsScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        self.rows = {}
        
        # Section Header
        hdr = QHBoxLayout()
        lbl_title = QLabel("DIGITAL ACTUATOR RELAY PANEL")
        lbl_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_title.setStyleSheet("color: #cbd5e1; border: none;")
        hdr.addWidget(lbl_title)
        hdr.addStretch()
        
        lbl_sub = QLabel("RS-485 MODBUS SLAVE #2 (COILS 0x0000 - 0x0003)")
        lbl_sub.setFont(QFont("Consolas", 8, QFont.Bold))
        lbl_sub.setStyleSheet("color: #10b981; border: none;")
        hdr.addWidget(lbl_sub)
        self.layout.addLayout(hdr)
        
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
