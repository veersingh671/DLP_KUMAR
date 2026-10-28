"""
Dashboard screen for DLP KUMAR VFD HMI.
Provides real-time primary telemetry overview for operators.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen, IndustrialCard
from core.system_state import VFDState

class DashboardScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        
        # 1. Top Status Banner (Status, FWD/REV, Load)
        banner = QFrame()
        banner.setFixedHeight(54)
        banner.setStyleSheet("""
            QFrame {
                background-color: #0f1624;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        b_layout = QHBoxLayout(banner)
        b_layout.setContentsMargins(12, 4, 12, 4)
        b_layout.setSpacing(12)
        
        # VFD Status Badge
        self.status_badge = QLabel("STOPPED")
        self.status_badge.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setFixedHeight(34)
        self.status_badge.setFixedWidth(140)
        self._set_status_badge("STOPPED")
        b_layout.addWidget(self.status_badge)
        
        # Direction Pill
        self.lbl_dir = QLabel("DIR: FWD")
        self.lbl_dir.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_dir.setStyleSheet("""
            color: #38bdf8;
            background-color: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 6px;
            padding: 4px 10px;
        """)
        b_layout.addWidget(self.lbl_dir)
        
        # Target Freq
        self.lbl_target = QLabel("TARGET: 45.0 Hz")
        self.lbl_target.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_target.setStyleSheet("color: #94a3b8; border: none;")
        b_layout.addWidget(self.lbl_target)
        
        b_layout.addStretch()
        
        # Load % & Mini Bar
        load_box = QHBoxLayout()
        lbl_load_title = QLabel("LOAD:")
        lbl_load_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_load_title.setStyleSheet("color: #64748b; border: none;")
        load_box.addWidget(lbl_load_title)
        
        self.load_bar = QProgressBar()
        self.load_bar.setRange(0, 100)
        self.load_bar.setValue(0)
        self.load_bar.setFixedSize(110, 16)
        self.load_bar.setTextVisible(False)
        self.load_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #ff7a00;
                border-radius: 3px;
            }
        """)
        load_box.addWidget(self.load_bar)
        
        self.lbl_load_pct = QLabel("0 %")
        self.lbl_load_pct.setFont(QFont("Consolas", 10, QFont.Bold))
        self.lbl_load_pct.setStyleSheet("color: #f8fafc; border: none; min-width: 45px;")
        load_box.addWidget(self.lbl_load_pct)
        b_layout.addLayout(load_box)
        
        self.layout.addWidget(banner)
        
        # 2. Main 6-Tile Telemetry Grid (2 rows x 3 columns)
        grid = QGridLayout()
        grid.setSpacing(8)
        
        self.card_freq = IndustrialCard("Output Frequency", "0.0", "Hz")
        self.card_speed = IndustrialCard("Motor Speed", "0", "RPM")
        self.card_current = IndustrialCard("Output Current", "0.00", "A")
        self.card_voltage = IndustrialCard("Motor Voltage", "0", "V")
        self.card_temp = IndustrialCard("Motor Temp", "38.0", "°C")
        self.card_dcbus = IndustrialCard("DC Bus Voltage", "540", "V")
        
        grid.addWidget(self.card_freq, 0, 0)
        grid.addWidget(self.card_speed, 0, 1)
        grid.addWidget(self.card_current, 0, 2)
        grid.addWidget(self.card_voltage, 1, 0)
        grid.addWidget(self.card_temp, 1, 1)
        grid.addWidget(self.card_dcbus, 1, 2)
        
        self.layout.addLayout(grid)
        
        # 3. Quick System Alert Footer
        footer = QFrame()
        footer.setFixedHeight(36)
        footer.setStyleSheet("""
            QFrame {
                background-color: #0b0f19;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(10, 0, 10, 0)
        
        self.lbl_footer_status = QLabel("COMMUNICATION: Modbus RTU / 9600 8N1 [POLLING ACTIVE]")
        self.lbl_footer_status.setFont(QFont("Segoe UI", 9))
        self.lbl_footer_status.setStyleSheet("color: #64748b; border: none;")
        
        self.lbl_active_alarms = QLabel("0 ALARMS")
        self.lbl_active_alarms.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_active_alarms.setStyleSheet("""
            color: #10b981;
            background-color: rgba(16, 185, 129, 0.12);
            border-radius: 4px;
            padding: 2px 8px;
        """)
        
        f_layout.addWidget(self.lbl_footer_status)
        f_layout.addStretch()
        f_layout.addWidget(self.lbl_active_alarms)
        self.layout.addWidget(footer)
        
        # Connect to controller if provided
        if self.controller:
            self.controller.vfd_updated.connect(self.update_telemetry)
            self.controller.alarms_updated.connect(self.update_alarms_count)

    def _set_status_badge(self, status: str):
        self.status_badge.setText(status.upper())
        if "RUNNING" in status or "ACCEL" in status:
            self.status_badge.setStyleSheet("""
                color: #ffffff;
                background-color: #10b981;
                border-radius: 6px;
                letter-spacing: 1px;
            """)
        elif "TRIP" in status or "FAULT" in status:
            self.status_badge.setStyleSheet("""
                color: #ffffff;
                background-color: #ef4444;
                border-radius: 6px;
                letter-spacing: 1px;
            """)
        elif "DECEL" in status:
            self.status_badge.setStyleSheet("""
                color: #ffffff;
                background-color: #f59e0b;
                border-radius: 6px;
                letter-spacing: 1px;
            """)
        else:
            self.status_badge.setStyleSheet("""
                color: #94a3b8;
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
                letter-spacing: 1px;
            """)

    def update_telemetry(self, state: VFDState):
        self._set_status_badge(state.status_text)
        self.lbl_dir.setText(f"DIR: {state.direction}")
        self.lbl_target.setText(f"TARGET: {state.set_frequency:.1f} Hz")
        
        # Cards
        freq_color = "#ff7a00" if state.actual_frequency > 0 else "#94a3b8"
        self.card_freq.set_value(f"{state.actual_frequency:.1f}", freq_color)
        self.card_speed.set_value(f"{state.motor_speed}")
        self.card_current.set_value(f"{state.output_current:.2f}")
        self.card_voltage.set_value(f"{int(state.output_voltage)}")
        
        temp_color = "#ef4444" if state.motor_temp > 70 else ("#f59e0b" if state.motor_temp > 60 else "#f8fafc")
        self.card_temp.set_value(f"{state.motor_temp:.1f}", temp_color)
        self.card_dcbus.set_value(f"{int(state.dc_bus_voltage)}")
        
        # Load
        load = int(state.load_percent)
        self.load_bar.setValue(load)
        self.lbl_load_pct.setText(f"{load} %")

    def update_alarms_count(self, alarms_list):
        count = len(alarms_list)
        if count > 0:
            self.lbl_active_alarms.setText(f"{count} ACTIVE ALARM{'S' if count > 1 else ''}")
            self.lbl_active_alarms.setStyleSheet("""
                color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444; border-radius: 4px; padding: 2px 8px;
            """)
        else:
            self.lbl_active_alarms.setText("0 FAULTS")
            self.lbl_active_alarms.setStyleSheet("""
                color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                border-radius: 4px; padding: 2px 8px;
            """)
