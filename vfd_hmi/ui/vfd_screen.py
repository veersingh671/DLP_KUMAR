"""
VFD Control Screen for DLP KUMAR VFD HMI.
Allows direct motor operation, frequency adjustment, and fault reset.
Designed with large, separated touch targets for safe industrial operation.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen
from core.system_state import VFDState

class VFDScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        
        # 1. Top Real-time Readout Strip (Height ~60px)
        telemetry_strip = QFrame()
        telemetry_strip.setFixedHeight(62)
        telemetry_strip.setStyleSheet("""
            QFrame {
                background-color: #0f1624;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        ts_layout = QHBoxLayout(telemetry_strip)
        ts_layout.setContentsMargins(12, 4, 12, 4)
        
        # Mini stat blocks
        self.lbl_vfd_status = self._create_strip_block(ts_layout, "STATUS", "STOPPED", "#94a3b8")
        self.lbl_act_freq = self._create_strip_block(ts_layout, "ACTUAL FREQ", "0.0 Hz", "#ff7a00")
        self.lbl_act_curr = self._create_strip_block(ts_layout, "CURRENT", "0.00 A", "#f8fafc")
        self.lbl_act_volt = self._create_strip_block(ts_layout, "VOLTAGE", "0 V", "#f8fafc")
        self.lbl_act_speed = self._create_strip_block(ts_layout, "SPEED", "0 RPM", "#f8fafc")
        
        self.layout.addWidget(telemetry_strip)
        
        # 2. Middle: Frequency Setpoint Control (Height ~140px)
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("""
            QFrame {
                background-color: #121824;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        cf_layout = QVBoxLayout(ctrl_frame)
        cf_layout.setContentsMargins(12, 8, 12, 8)
        cf_layout.setSpacing(6)
        
        # Title & Preset row
        top_ctrl = QHBoxLayout()
        lbl_sp_title = QLabel("FREQUENCY SETPOINT")
        lbl_sp_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_sp_title.setStyleSheet("color: #64748b; border: none;")
        top_ctrl.addWidget(lbl_sp_title)
        top_ctrl.addStretch()
        
        # Quick Presets
        lbl_preset = QLabel("PRESETS:")
        lbl_preset.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_preset.setStyleSheet("color: #64748b; border: none;")
        top_ctrl.addWidget(lbl_preset)
        
        for p_val in [15.0, 25.0, 40.0, 50.0]:
            btn_p = QPushButton(f"{int(p_val)} Hz")
            btn_p.setFixedSize(58, 28)
            btn_p.setFont(QFont("Segoe UI", 9, QFont.Bold))
            btn_p.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    color: #94a3b8;
                    border: 1px solid #334155;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #334155;
                    color: #ffffff;
                }
            """)
            btn_p.clicked.connect(lambda checked, v=p_val: self._on_set_freq(v))
            top_ctrl.addWidget(btn_p)
            
        cf_layout.addLayout(top_ctrl)
        
        # Large Center Stepper Row
        step_row = QHBoxLayout()
        step_row.setSpacing(6)
        
        # Decrement Steppers
        btn_minus5 = self._create_step_btn("- 5.0", -5.0)
        btn_minus1 = self._create_step_btn("- 1.0", -1.0)
        btn_minus01 = self._create_step_btn("- 0.1", -0.1)
        
        step_row.addWidget(btn_minus5)
        step_row.addWidget(btn_minus1)
        step_row.addWidget(btn_minus01)
        
        # Center Target Display
        self.lbl_set_freq = QLabel("45.0 Hz")
        self.lbl_set_freq.setFont(QFont("Consolas", 32, QFont.Bold))
        self.lbl_set_freq.setAlignment(Qt.AlignCenter)
        self.lbl_set_freq.setMinimumWidth(180)
        self.lbl_set_freq.setStyleSheet("""
            color: #ff7a00;
            background-color: #0b0f19;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 4px 10px;
        """)
        step_row.addWidget(self.lbl_set_freq)
        
        # Increment Steppers
        btn_plus01 = self._create_step_btn("+ 0.1", 0.1)
        btn_plus1 = self._create_step_btn("+ 1.0", 1.0)
        btn_plus5 = self._create_step_btn("+ 5.0", 5.0)
        
        step_row.addWidget(btn_plus01)
        step_row.addWidget(btn_plus1)
        step_row.addWidget(btn_plus5)
        
        cf_layout.addLayout(step_row)
        self.layout.addWidget(ctrl_frame)
        
        # 3. Bottom Industrial Action Buttons (Height ~80px)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        # START Button (Big Green)
        self.btn_start = QPushButton("▶  START VFD")
        self.btn_start.setFixedHeight(64)
        self.btn_start.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: #ffffff;
                border: 2px solid #059669;
                border-radius: 8px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.btn_start.clicked.connect(self._on_start)
        action_layout.addWidget(self.btn_start, 2)
        
        # STOP Button (Big Red)
        self.btn_stop = QPushButton("■  STOP VFD")
        self.btn_stop.setFixedHeight(64)
        self.btn_stop.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: #ffffff;
                border: 2px solid #dc2626;
                border-radius: 8px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        self.btn_stop.clicked.connect(self._on_stop)
        action_layout.addWidget(self.btn_stop, 2)
        
        # Direction Toggle Button
        self.btn_dir = QPushButton("DIR: FWD")
        self.btn_dir.setFixedHeight(64)
        self.btn_dir.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_dir.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #38bdf8;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #ffffff;
            }
        """)
        self.btn_dir.clicked.connect(self._on_toggle_dir)
        action_layout.addWidget(self.btn_dir, 1)
        
        # Fault Reset Button
        self.btn_reset = QPushButton("RESET FAULT")
        self.btn_reset.setFixedHeight(64)
        self.btn_reset.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f59e0b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #f59e0b;
                color: #000000;
            }
        """)
        self.btn_reset.clicked.connect(self._on_reset)
        action_layout.addWidget(self.btn_reset, 1)
        
        self.layout.addLayout(action_layout)
        
        # Connect controller updates
        if self.controller:
            self.controller.vfd_updated.connect(self.update_vfd_state)
            
    def _create_strip_block(self, layout, title, val, color):
        box = QVBoxLayout()
        box.setContentsMargins(4, 2, 4, 2)
        box.setSpacing(1)
        
        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_t.setStyleSheet("color: #64748b; border: none;")
        
        lbl_v = QLabel(val)
        lbl_v.setFont(QFont("Consolas", 14, QFont.Bold))
        lbl_v.setStyleSheet(f"color: {color}; border: none;")
        
        box.addWidget(lbl_t)
        box.addWidget(lbl_v)
        layout.addLayout(box)
        layout.addStretch()
        return lbl_v

    def _create_step_btn(self, text, delta):
        btn = QPushButton(text)
        btn.setFixedHeight(54)
        btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 6px;
                min-width: 55px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
            QPushButton:pressed {
                background-color: #ff7a00;
                color: #ffffff;
            }
        """)
        btn.clicked.connect(lambda: self._on_step(delta))
        return btn

    def _on_step(self, delta):
        if self.controller:
            self.controller.adjust_frequency(delta)

    def _on_set_freq(self, val):
        if self.controller:
            self.controller.set_frequency(val)

    def _on_start(self):
        if self.controller:
            self.controller.start_vfd()

    def _on_stop(self):
        if self.controller:
            self.controller.stop_vfd()

    def _on_toggle_dir(self):
        if self.controller:
            self.controller.toggle_direction()

    def _on_reset(self):
        if self.controller:
            self.controller.reset_fault()

    def update_vfd_state(self, state: VFDState):
        self.lbl_vfd_status.setText(state.status_text)
        status_color = "#10b981" if ("RUNNING" in state.status_text or "ACCEL" in state.status_text) else ("#ef4444" if "TRIP" in state.status_text else "#94a3b8")
        self.lbl_vfd_status.setStyleSheet(f"color: {status_color}; border: none;")
        
        self.lbl_act_freq.setText(f"{state.actual_frequency:.1f} Hz")
        self.lbl_act_curr.setText(f"{state.output_current:.2f} A")
        self.lbl_act_volt.setText(f"{int(state.output_voltage)} V")
        self.lbl_act_speed.setText(f"{state.motor_speed} RPM")
        
        self.lbl_set_freq.setText(f"{state.set_frequency:.1f} Hz")
        self.btn_dir.setText(f"DIR: {state.direction}")
