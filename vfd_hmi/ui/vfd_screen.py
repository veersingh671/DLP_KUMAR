"""
VFD Control Screen for DLP KUMAR VFD HMI.
ISA-101 High-Performance SCADA Control for Fuji Electric FRENIC-Mini C2.
Disciplined industrial color scheme with high-contrast readouts and tactile touch targets.
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
        
        # 1. Top Real-time Readout Strip
        telemetry_strip = QFrame()
        telemetry_strip.setFixedHeight(56)
        telemetry_strip.setStyleSheet("""
            QFrame {
                background-color: #131923;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        ts_layout = QHBoxLayout(telemetry_strip)
        ts_layout.setContentsMargins(10, 2, 10, 2)
        ts_layout.setSpacing(6)
        
        self.lbl_vfd_status = self._create_strip_block(ts_layout, "STATUS", "STOPPED", "#94a3b8")
        self.lbl_act_freq = self._create_strip_block(ts_layout, "ACTUAL FREQ", "0.0 Hz", "#f8fafc")
        self.lbl_act_curr = self._create_strip_block(ts_layout, "CURRENT", "0.00 A", "#f8fafc")
        self.lbl_act_volt = self._create_strip_block(ts_layout, "VOLTAGE", "0 V", "#f8fafc")
        self.lbl_act_speed = self._create_strip_block(ts_layout, "SHAFT SPEED", "0 RPM", "#f8fafc")
        self.lbl_act_torque = self._create_strip_block(ts_layout, "TORQUE", "0.0 N·m", "#f8fafc")
        self.lbl_act_power = self._create_strip_block(ts_layout, "POWER", "0.00 kW", "#10b981")
        
        self.layout.addWidget(telemetry_strip)
        
        # 2. Fuji FRENIC-Mini (M14) Status Indicators & Motor Physics Bar
        status_bar = QFrame()
        status_bar.setFixedHeight(28)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #090d13;
                border: 1px solid #1e293b;
                border-radius: 4px;
            }
        """)
        sb_layout = QHBoxLayout(status_bar)
        sb_layout.setContentsMargins(8, 0, 8, 0)
        sb_layout.setSpacing(6)
        
        # M14 Indicator Badges
        lbl_badges_title = QLabel("M14 BITS:")
        lbl_badges_title.setFont(QFont("Consolas", 8, QFont.Bold))
        lbl_badges_title.setStyleSheet("color: #64748b; border: none;")
        sb_layout.addWidget(lbl_badges_title)
        
        self.badge_run = self._create_badge("RUN", "#15803d")
        self.badge_far = self._create_badge("FAR", "#0284c7")
        self.badge_il  = self._create_badge("IL",  "#b45309")
        self.badge_rl  = self._create_badge("RL",  "#059669")
        self.badge_alm = self._create_badge("ALM", "#b91c1c")
        
        sb_layout.addWidget(self.badge_run)
        sb_layout.addWidget(self.badge_far)
        sb_layout.addWidget(self.badge_il)
        sb_layout.addWidget(self.badge_rl)
        sb_layout.addWidget(self.badge_alm)
        
        sb_layout.addStretch()
        
        # Motor Analytical Physics Tag
        self.lbl_motor_meta = QLabel("SYNC: 1500 RPM | SLIP: 0.0 Hz | TH: 0% FLA | P01: 4P")
        self.lbl_motor_meta.setFont(QFont("Consolas", 8))
        self.lbl_motor_meta.setStyleSheet("color: #94a3b8; border: none;")
        sb_layout.addWidget(self.lbl_motor_meta)
        
        self.layout.addWidget(status_bar)
        
        # 3. Middle: Frequency Setpoint Control
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("""
            QFrame {
                background-color: #131923;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        cf_layout = QVBoxLayout(ctrl_frame)
        cf_layout.setContentsMargins(12, 6, 12, 6)
        cf_layout.setSpacing(4)
        
        # Title & Preset row
        top_ctrl = QHBoxLayout()
        lbl_sp_title = QLabel("FUJI FRENIC-Mini C2 — FREQUENCY REFERENCE (S05: 0.01Hz)")
        lbl_sp_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_sp_title.setStyleSheet("color: #cbd5e1; border: none;")
        top_ctrl.addWidget(lbl_sp_title)
        top_ctrl.addStretch()
        
        # Quick Presets
        lbl_preset = QLabel("PRESETS:")
        lbl_preset.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_preset.setStyleSheet("color: #64748b; border: none;")
        top_ctrl.addWidget(lbl_preset)
        
        for p_val in [10.0, 25.0, 40.0, 50.0, 60.0]:
            btn_p = QPushButton(f"{int(p_val)} Hz")
            btn_p.setFixedSize(54, 24)
            btn_p.setFont(QFont("Consolas", 8, QFont.Bold))
            btn_p.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    color: #cbd5e1;
                    border: 1px solid #334155;
                    border-radius: 3px;
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
        
        btn_minus5 = self._create_step_btn("- 5.0", -5.0)
        btn_minus1 = self._create_step_btn("- 1.0", -1.0)
        btn_minus01 = self._create_step_btn("- 0.1", -0.1)
        
        step_row.addWidget(btn_minus5)
        step_row.addWidget(btn_minus1)
        step_row.addWidget(btn_minus01)
        
        # Center Target Display (Recessed Data Display)
        self.lbl_set_freq = QLabel("45.0 Hz")
        self.lbl_set_freq.setFont(QFont("Consolas", 32, QFont.Bold))
        self.lbl_set_freq.setAlignment(Qt.AlignCenter)
        self.lbl_set_freq.setMinimumWidth(170)
        self.lbl_set_freq.setStyleSheet("""
            color: #f8fafc;
            background-color: #090d13;
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 2px 8px;
        """)
        step_row.addWidget(self.lbl_set_freq)
        
        btn_plus01 = self._create_step_btn("+ 0.1", 0.1)
        btn_plus1 = self._create_step_btn("+ 1.0", 1.0)
        btn_plus5 = self._create_step_btn("+ 5.0", 5.0)
        
        step_row.addWidget(btn_plus01)
        step_row.addWidget(btn_plus1)
        step_row.addWidget(btn_plus5)
        
        cf_layout.addLayout(step_row)
        self.layout.addWidget(ctrl_frame)
        
        # 4. Industrial Motor Action Buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        # START Button (Industrial Emerald)
        self.btn_start = QPushButton("▶  START VFD")
        self.btn_start.setFixedHeight(54)
        self.btn_start.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #15803d;
                color: #ffffff;
                border: 1px solid #16a34a;
                border-radius: 6px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover { background-color: #16a34a; }
            QPushButton:pressed { background-color: #14532d; }
        """)
        self.btn_start.clicked.connect(self._on_start)
        action_layout.addWidget(self.btn_start, 3)
        
        # STOP Button (Industrial Crimson)
        self.btn_stop = QPushButton("■  STOP VFD")
        self.btn_stop.setFixedHeight(54)
        self.btn_stop.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #b91c1c;
                color: #ffffff;
                border: 1px solid #dc2626;
                border-radius: 6px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover { background-color: #dc2626; }
            QPushButton:pressed { background-color: #7f1d1d; }
        """)
        self.btn_stop.clicked.connect(self._on_stop)
        action_layout.addWidget(self.btn_stop, 3)
        
        # JOG Button (Slate Blue)
        self.btn_jog = QPushButton("JOG (5Hz)")
        self.btn_jog.setFixedHeight(54)
        self.btn_jog.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.btn_jog.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #93c5fd;
                border: 1px solid #3b82f6;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #2563eb; color: #ffffff; }
            QPushButton:pressed { background-color: #1d4ed8; }
        """)
        self.btn_jog.clicked.connect(self._on_jog)
        action_layout.addWidget(self.btn_jog, 2)
        
        # Direction Toggle Button
        self.btn_dir = QPushButton("DIR: FWD")
        self.btn_dir.setFixedHeight(54)
        self.btn_dir.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.btn_dir.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f1f5f9;
                border: 1px solid #334155;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        self.btn_dir.clicked.connect(self._on_toggle_dir)
        action_layout.addWidget(self.btn_dir, 2)
        
        # Fault Reset Button
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setFixedHeight(54)
        self.btn_reset.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #78350f;
                color: #fef3c7;
                border: 1px solid #b45309;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #b45309; color: #ffffff; }
        """)
        self.btn_reset.clicked.connect(self._on_reset)
        action_layout.addWidget(self.btn_reset, 2)
        
        # Emergency Coast Stop Button
        self.btn_estop = QPushButton("E-STOP")
        self.btn_estop.setFixedHeight(54)
        self.btn_estop.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.btn_estop.setStyleSheet("""
            QPushButton {
                background-color: #450a0a;
                color: #fca5a5;
                border: 1px solid #991b1b;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #7f1d1d; color: #ffffff; }
        """)
        self.btn_estop.clicked.connect(self._on_estop)
        action_layout.addWidget(self.btn_estop, 2)
        
        self.layout.addLayout(action_layout)
        
        # 5. Modbus RTU Register Mapping Indicator
        reg_strip = QFrame()
        reg_strip.setFixedHeight(22)
        reg_strip.setStyleSheet("""
            QFrame {
                background-color: #090d13;
                border: 1px solid #1e293b;
                border-radius: 3px;
            }
        """)
        rs_layout = QHBoxLayout(reg_strip)
        rs_layout.setContentsMargins(8, 0, 8, 0)
        
        lbl_rs_info = QLabel("FUJI C2: CMD S06 [0x0706] | FREQ S05 [0x0705] | STAT M14 [0x080E] | TORQUE M13 [0x080D] | OUT M09 [0x0809]")
        lbl_rs_info.setFont(QFont("Consolas", 8))
        lbl_rs_info.setStyleSheet("color: #64748b; border: none;")
        rs_layout.addWidget(lbl_rs_info)
        rs_layout.addStretch()
        
        self.lbl_rs_link = QLabel("RS-485: SYNCED")
        self.lbl_rs_link.setFont(QFont("Consolas", 8, QFont.Bold))
        self.lbl_rs_link.setStyleSheet("color: #10b981; border: none;")
        rs_layout.addWidget(self.lbl_rs_link)
        
        self.layout.addWidget(reg_strip)
        
        # Connect controller updates
        if self.controller:
            self.controller.vfd_updated.connect(self.update_vfd_state)
            self.controller.rs485_updated.connect(self._on_rs485_updated)
            
    def _create_strip_block(self, layout, title, val, color):
        box = QVBoxLayout()
        box.setContentsMargins(2, 1, 2, 1)
        box.setSpacing(0)
        
        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Segoe UI", 7, QFont.Bold))
        lbl_t.setStyleSheet("color: #64748b; border: none;")
        
        lbl_v = QLabel(val)
        lbl_v.setFont(QFont("Consolas", 13, QFont.Bold))
        lbl_v.setStyleSheet(f"color: {color}; border: none;")
        
        box.addWidget(lbl_t)
        box.addWidget(lbl_v)
        layout.addLayout(box)
        layout.addStretch()
        return lbl_v

    def _create_badge(self, text, active_color):
        badge = QLabel(text)
        badge.setFixedSize(36, 18)
        badge.setFont(QFont("Consolas", 8, QFont.Bold))
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet("""
            QLabel {
                background-color: #131923;
                color: #475569;
                border: 1px solid #1e293b;
                border-radius: 3px;
            }
        """)
        badge.setProperty("active_color", active_color)
        return badge

    def _set_badge_state(self, badge, active: bool):
        act_col = badge.property("active_color") or "#15803d"
        if active:
            badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {act_col};
                    color: #ffffff;
                    border: 1px solid {act_col};
                    border-radius: 3px;
                }}
            """)
        else:
            badge.setStyleSheet("""
                QLabel {
                    background-color: #131923;
                    color: #475569;
                    border: 1px solid #1e293b;
                    border-radius: 3px;
                }
            """)

    def _create_step_btn(self, text, delta):
        btn = QPushButton(text)
        btn.setFixedHeight(48)
        btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f1f5f9;
                border: 1px solid #334155;
                border-radius: 4px;
                min-width: 50px;
            }
            QPushButton:hover { background-color: #334155; }
            QPushButton:pressed { background-color: #2563eb; color: #ffffff; }
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

    def _on_jog(self):
        if self.controller:
            self.controller.jog_vfd(self.controller.vfd.direction, 5.0)

    def _on_toggle_dir(self):
        if self.controller:
            self.controller.toggle_direction()

    def _on_reset(self):
        if self.controller:
            self.controller.reset_fault()

    def _on_estop(self):
        if self.controller:
            self.controller.emergency_stop_vfd()

    def update_vfd_state(self, state: VFDState):
        self.lbl_vfd_status.setText(state.status_text)
        status_color = "#10b981" if ("RUNNING" in state.status_text or "ACCEL" in state.status_text or "JOG" in state.status_text) else ("#ef4444" if "TRIP" in state.status_text else "#94a3b8")
        self.lbl_vfd_status.setStyleSheet(f"color: {status_color}; border: none;")
        
        self.lbl_act_freq.setText(f"{state.actual_frequency:.1f} Hz")
        self.lbl_act_curr.setText(f"{state.output_current:.2f} A")
        self.lbl_act_volt.setText(f"{int(state.output_voltage)} V")
        self.lbl_act_speed.setText(f"{state.motor_speed} RPM")
        self.lbl_act_torque.setText(f"{state.shaft_torque_nm:.1f} N·m")
        self.lbl_act_power.setText(f"{state.power_kw:.2f} kW")
        
        self.lbl_set_freq.setText(f"{state.set_frequency:.1f} Hz")
        self.btn_dir.setText(f"DIR: {state.direction}")

        # Update M14 Indicator Badges
        self._set_badge_state(self.badge_run, state.running)
        self._set_badge_state(self.badge_far, state.frenic_at_speed)
        self._set_badge_state(self.badge_il,  state.frenic_current_limit)
        self._set_badge_state(self.badge_rl,  state.frenic_link_ok)
        self._set_badge_state(self.badge_alm, bool(state.fault_code))

        # Update Motor Analytical Physics Label
        self.lbl_motor_meta.setText(
            f"SYNC: {state.sync_speed} RPM | SLIP: {state.slip_hz:.1f} Hz | TH: {state.thermal_load_percent:.0f}% FLA | P01: {state.motor_poles}P"
        )

    def _on_rs485_updated(self, diag: dict):
        is_sim = diag.get("is_simulation", True)
        crc_err = diag.get("crc_errors", 0)
        port = diag.get("port", "COM3")
        if is_sim:
            self.lbl_rs_link.setText("RS-485: VIRTUAL BUS")
            self.lbl_rs_link.setStyleSheet("color: #93c5fd; border: none;")
        elif crc_err > 0:
            self.lbl_rs_link.setText(f"RS-485: {crc_err} CRC ERR")
            self.lbl_rs_link.setStyleSheet("color: #ef4444; border: none;")
        else:
            self.lbl_rs_link.setText(f"RS-485: {port} OK")
            self.lbl_rs_link.setStyleSheet("color: #10b981; border: none;")
