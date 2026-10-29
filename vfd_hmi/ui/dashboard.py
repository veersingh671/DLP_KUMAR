"""
Dashboard screen for DLP KUMAR VFD HMI.
ISA-101 High-Performance SCADA Overview for Fuji Electric FRENIC-Mini C2.
Structured, high-contrast, low-glare slate surfaces with disciplined status reporting.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen, AnimatedProgressBar
from core.system_state import VFDState

class DashboardScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        
        # Main 2-Column Split: Left (Drive Dynamics), Right (Power & Electrical Matrix)
        main_h = QHBoxLayout()
        main_h.setSpacing(8)
        
        # =====================================================================
        # LEFT COLUMN: PRIMARY MOTION & SPEED DYNAMICS
        # =====================================================================
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #131923;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        lp_layout = QVBoxLayout(left_panel)
        lp_layout.setContentsMargins(12, 8, 12, 8)
        lp_layout.setSpacing(6)
        
        # Header: Operational Status & Direction
        lp_hdr = QHBoxLayout()
        self.status_pill = QLabel("STOPPED")
        self.status_pill.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.status_pill.setAlignment(Qt.AlignCenter)
        self.status_pill.setFixedHeight(26)
        self.status_pill.setFixedWidth(110)
        self._set_status_style("STOPPED")
        lp_hdr.addWidget(self.status_pill)
        
        self.lbl_dir = QLabel("DIR: FWD ▶")
        self.lbl_dir.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_dir.setStyleSheet("""
            color: #93c5fd; background-color: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 4px; padding: 2px 8px;
        """)
        lp_hdr.addWidget(self.lbl_dir)
        lp_hdr.addStretch()
        
        self.lbl_target_info = QLabel("SETPOINT: 45.0 Hz")
        self.lbl_target_info.setFont(QFont("Consolas", 9, QFont.Bold))
        self.lbl_target_info.setStyleSheet("color: #94a3b8; border: none;")
        lp_hdr.addWidget(self.lbl_target_info)
        lp_layout.addLayout(lp_hdr)
        
        # Large Frequency Readout Box (Recessed Data Well)
        freq_box = QFrame()
        freq_box.setStyleSheet("background-color: #090d13; border: 1px solid #1e293b; border-radius: 5px;")
        fb_layout = QVBoxLayout(freq_box)
        fb_layout.setContentsMargins(10, 6, 10, 6)
        fb_layout.setSpacing(2)
        
        fb_top = QHBoxLayout()
        lbl_f_title = QLabel("OUTPUT FREQUENCY (M09)")
        lbl_f_title.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_f_title.setStyleSheet("color: #64748b; border: none;")
        self.lbl_delta = QLabel("Δ: 0.0 Hz")
        self.lbl_delta.setFont(QFont("Consolas", 8, QFont.Bold))
        self.lbl_delta.setStyleSheet("color: #94a3b8; border: none;")
        fb_top.addWidget(lbl_f_title)
        fb_top.addStretch()
        fb_top.addWidget(self.lbl_delta)
        fb_layout.addLayout(fb_top)
        
        self.lbl_actual_freq = QLabel("0.0 Hz")
        self.lbl_actual_freq.setFont(QFont("Consolas", 32, QFont.Bold))
        self.lbl_actual_freq.setAlignment(Qt.AlignCenter)
        self.lbl_actual_freq.setStyleSheet("color: #f8fafc; border: none;")
        fb_layout.addWidget(self.lbl_actual_freq)
        
        # Animated Frequency Bar (Steel Blue)
        self.freq_bar = AnimatedProgressBar()
        self.freq_bar.setRange(0, 500)  # 0.0 to 50.0 Hz
        self.freq_bar.setValue(0)
        self.freq_bar.setFixedHeight(10)
        self.freq_bar.setTextVisible(False)
        self.freq_bar.setStyleSheet("""
            QProgressBar {
                background-color: #131923; border: 1px solid #1e293b; border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #2563eb; border-radius: 2px;
            }
        """)
        fb_layout.addWidget(self.freq_bar)
        
        # Scale markings
        scale_row = QHBoxLayout()
        for tick in ["0 Hz", "10", "20", "30", "40", "50 Hz"]:
            lbl_t = QLabel(tick)
            lbl_t.setFont(QFont("Consolas", 7))
            lbl_t.setStyleSheet("color: #475569; border: none;")
            scale_row.addWidget(lbl_t)
            if tick != "50 Hz":
                scale_row.addStretch()
        fb_layout.addLayout(scale_row)
        lp_layout.addWidget(freq_box)
        
        # Speed & Mechanical Load Row
        sub_row = QHBoxLayout()
        sub_row.setSpacing(6)
        
        # Speed Tile
        speed_tile = QFrame()
        speed_tile.setStyleSheet("background-color: #090d13; border: 1px solid #1e293b; border-radius: 5px;")
        sp_l = QVBoxLayout(speed_tile)
        sp_l.setContentsMargins(8, 4, 8, 4)
        sp_l.setSpacing(1)
        lbl_sp_t = QLabel("MOTOR SPEED (M44)")
        lbl_sp_t.setFont(QFont("Segoe UI", 7, QFont.Bold))
        lbl_sp_t.setStyleSheet("color: #64748b; border: none;")
        self.lbl_speed_val = QLabel("0 RPM")
        self.lbl_speed_val.setFont(QFont("Consolas", 15, QFont.Bold))
        self.lbl_speed_val.setStyleSheet("color: #f1f5f9; border: none;")
        sp_l.addWidget(lbl_sp_t)
        sp_l.addWidget(self.lbl_speed_val)
        sub_row.addWidget(speed_tile, 1)
        
        # Load Tile with Animated Bar
        load_tile = QFrame()
        load_tile.setStyleSheet("background-color: #090d13; border: 1px solid #1e293b; border-radius: 5px;")
        ld_l = QVBoxLayout(load_tile)
        ld_l.setContentsMargins(8, 4, 8, 4)
        ld_l.setSpacing(2)
        
        ld_hdr = QHBoxLayout()
        lbl_ld_t = QLabel("DRIVE LOAD (M13)")
        lbl_ld_t.setFont(QFont("Segoe UI", 7, QFont.Bold))
        lbl_ld_t.setStyleSheet("color: #64748b; border: none;")
        self.lbl_load_val = QLabel("0 %")
        self.lbl_load_val.setFont(QFont("Consolas", 9, QFont.Bold))
        self.lbl_load_val.setStyleSheet("color: #10b981; border: none;")
        ld_hdr.addWidget(lbl_ld_t)
        ld_hdr.addStretch()
        ld_hdr.addWidget(self.lbl_load_val)
        ld_l.addLayout(ld_hdr)
        
        self.load_bar = AnimatedProgressBar()
        self.load_bar.setRange(0, 100)
        self.load_bar.setValue(0)
        self.load_bar.setFixedHeight(8)
        self.load_bar.setTextVisible(False)
        self.load_bar.setStyleSheet("""
            QProgressBar {
                background-color: #131923; border: 1px solid #1e293b; border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #10b981; border-radius: 2px;
            }
        """)
        ld_l.addWidget(self.load_bar)
        sub_row.addWidget(load_tile, 1)
        lp_layout.addLayout(sub_row)
        
        main_h.addWidget(left_panel, 55)
        
        # =====================================================================
        # RIGHT COLUMN: ELECTRICAL & THERMAL ENVELOPE (Segmented Matrix)
        # =====================================================================
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #131923;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        rp_layout = QVBoxLayout(right_panel)
        rp_layout.setContentsMargins(10, 8, 10, 8)
        rp_layout.setSpacing(6)
        
        rp_hdr = QHBoxLayout()
        lbl_rp_title = QLabel("ELECTRICAL & THERMAL MATRIX")
        lbl_rp_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_rp_title.setStyleSheet("color: #cbd5e1; border: none;")
        rp_hdr.addWidget(lbl_rp_title)
        rp_hdr.addStretch()
        
        lbl_rating = QLabel("400V CLASS • 3.7 kW")
        lbl_rating.setFont(QFont("Consolas", 7, QFont.Bold))
        lbl_rating.setStyleSheet("color: #94a3b8; background-color: #090d13; padding: 2px 6px; border-radius: 3px;")
        rp_hdr.addWidget(lbl_rating)
        rp_layout.addLayout(rp_hdr)
        
        # 4-Tile Grid for Electrical Metrics
        grid = QGridLayout()
        grid.setSpacing(6)
        
        self.tile_curr = self._create_metric_tile("OUTPUT CURRENT", "0.00", "A", "#f8fafc", "FLA: 7.5A (F09)")
        self.tile_volt = self._create_metric_tile("TERMINAL VOLT", "0", "V", "#f8fafc", "Base: 380V (F05)")
        self.tile_dcbus = self._create_metric_tile("DC BUS VOLTAGE", "540", "V", "#f8fafc", "Nominal: 540V DC")
        self.tile_temp = self._create_metric_tile("HEATSINK TEMP", "38.0", "°C", "#10b981", "Trip: 95°C (M26)")
        
        grid.addWidget(self.tile_curr["frame"], 0, 0)
        grid.addWidget(self.tile_volt["frame"], 0, 1)
        grid.addWidget(self.tile_dcbus["frame"], 1, 0)
        grid.addWidget(self.tile_temp["frame"], 1, 1)
        rp_layout.addLayout(grid)
        
        # Bottom Power & Mechanical Summary Strip
        pwr_strip = QFrame()
        pwr_strip.setStyleSheet("background-color: #090d13; border: 1px solid #1e293b; border-radius: 5px;")
        ps_l = QHBoxLayout(pwr_strip)
        ps_l.setContentsMargins(10, 4, 10, 4)
        
        self.lbl_power = QLabel("POWER: 0.00 kW | TORQUE: 0.0 N·m (0%) | SYNC: 1500 RPM")
        self.lbl_power.setFont(QFont("Consolas", 8, QFont.Bold))
        self.lbl_power.setStyleSheet("color: #cbd5e1; border: none;")
        
        lbl_modbus_tag = QLabel("NODE #1")
        lbl_modbus_tag.setFont(QFont("Consolas", 8, QFont.Bold))
        lbl_modbus_tag.setStyleSheet("color: #10b981; border: none;")
        
        ps_l.addWidget(self.lbl_power)
        ps_l.addStretch()
        ps_l.addWidget(lbl_modbus_tag)
        rp_layout.addWidget(pwr_strip)
        
        main_h.addWidget(right_panel, 45)
        self.layout.addLayout(main_h)
        
        # 2. Bottom Process Bus Footer
        footer = QFrame()
        footer.setFixedHeight(28)
        footer.setStyleSheet("background-color: #090d13; border: 1px solid #1e293b; border-radius: 4px;")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(10, 0, 10, 0)
        
        self.lbl_footer_status = QLabel("FUJI FRENIC-Mini C2 | Modbus RTU / 9600 8N1 [POLLING ACTIVE]")
        self.lbl_footer_status.setFont(QFont("Consolas", 8))
        self.lbl_footer_status.setStyleSheet("color: #64748b; border: none;")
        
        self.lbl_active_alarms = QLabel("0 FAULTS")
        self.lbl_active_alarms.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.lbl_active_alarms.setStyleSheet("""
            color: #10b981; background-color: rgba(16, 185, 129, 0.12);
            border-radius: 3px; padding: 1px 6px;
        """)
        
        f_layout.addWidget(self.lbl_footer_status)
        f_layout.addStretch()
        f_layout.addWidget(self.lbl_active_alarms)
        self.layout.addWidget(footer)
        
        # Connect to controller
        if self.controller:
            self.controller.vfd_updated.connect(self.update_telemetry)
            self.controller.alarms_updated.connect(self.update_alarms_count)
            self.controller.rs485_updated.connect(self._on_rs485_updated)

    def _create_metric_tile(self, title, val, unit, color, note=""):
        frame = QFrame()
        frame.setStyleSheet("background-color: #090d13; border: 1px solid #1e293b; border-radius: 5px;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(1)
        
        hdr = QHBoxLayout()
        lt = QLabel(title)
        lt.setFont(QFont("Segoe UI", 7, QFont.Bold))
        lt.setStyleSheet("color: #64748b; border: none;")
        lu = QLabel(unit)
        lu.setFont(QFont("Consolas", 7, QFont.Bold))
        lu.setStyleSheet("color: #94a3b8; border: none;")
        hdr.addWidget(lt)
        hdr.addStretch()
        hdr.addWidget(lu)
        layout.addLayout(hdr)
        
        lv = QLabel(val)
        lv.setFont(QFont("Consolas", 15, QFont.Bold))
        lv.setStyleSheet(f"color: {color}; border: none;")
        lv.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lv)
        
        if note:
            ln = QLabel(note)
            ln.setFont(QFont("Segoe UI", 7))
            ln.setStyleSheet("color: #475569; border: none;")
            ln.setAlignment(Qt.AlignRight)
            layout.addWidget(ln)
            
        return {"frame": frame, "val_label": lv}

    def _set_status_style(self, status: str):
        self.status_pill.setText(status.upper())
        if "RUNNING" in status or "ACCEL" in status or "JOG" in status:
            self.status_pill.setStyleSheet("""
                color: #ffffff; background-color: #15803d; border-radius: 4px; letter-spacing: 0.5px;
            """)
        elif "TRIP" in status or "FAULT" in status:
            self.status_pill.setStyleSheet("""
                color: #ffffff; background-color: #b91c1c; border-radius: 4px; letter-spacing: 0.5px;
            """)
        elif "DECEL" in status:
            self.status_pill.setStyleSheet("""
                color: #ffffff; background-color: #b45309; border-radius: 4px; letter-spacing: 0.5px;
            """)
        else:
            self.status_pill.setStyleSheet("""
                color: #94a3b8; background-color: #1e293b; border-radius: 4px; letter-spacing: 0.5px;
            """)

    def update_telemetry(self, state: VFDState):
        self._set_status_style(state.status_text)
        dir_arrow = "▶" if state.direction == "FWD" else "◀"
        self.lbl_dir.setText(f"DIR: {state.direction} {dir_arrow}")
        
        # Frequency
        self.lbl_actual_freq.setText(f"{state.actual_frequency:.1f} Hz")
        freq_color = "#10b981" if ("RUNNING" in state.status_text or "ACCEL" in state.status_text or "JOG" in state.status_text) else ("#ef4444" if "TRIP" in state.status_text else "#f8fafc")
        self.lbl_actual_freq.setStyleSheet(f"color: {freq_color}; border: none;")
        self.freq_bar.setValueSmooth(state.actual_frequency * 10.0)
        
        delta = state.actual_frequency - state.set_frequency
        sign = "+" if delta > 0 else ""
        self.lbl_delta.setText(f"Δ: {sign}{delta:.1f} Hz")
        self.lbl_target_info.setText(f"SETPOINT: {state.set_frequency:.1f} Hz")
        
        # Speed & Load
        self.lbl_speed_val.setText(f"{state.motor_speed} RPM")
        load_int = int(state.load_percent)
        self.lbl_load_val.setText(f"{load_int} %")
        load_col = "#10b981" if load_int <= 80 else ("#f59e0b" if load_int <= 100 else "#ef4444")
        self.lbl_load_val.setStyleSheet(f"color: {load_col}; border: none;")
        self.load_bar.setValueSmooth(state.load_percent)
        
        # Electrical, Power & Motor Torque
        self.tile_curr["val_label"].setText(f"{state.output_current:.2f}")
        self.tile_volt["val_label"].setText(f"{int(state.output_voltage)}")
        self.tile_dcbus["val_label"].setText(f"{int(state.dc_bus_voltage)}")
        
        temp_color = "#10b981" if state.motor_temp < 70 else ("#f59e0b" if state.motor_temp < 85 else "#ef4444")
        self.tile_temp["val_label"].setText(f"{state.motor_temp:.1f}")
        self.tile_temp["val_label"].setStyleSheet(f"color: {temp_color}; border: none;")
        
        self.lbl_power.setText(f"POWER: {state.power_kw:.2f} kW | TORQUE: {state.shaft_torque_nm:.1f} N·m ({state.torque_percent:.0f}%) | SYNC: {state.sync_speed} RPM")

    def update_alarms_count(self, alarms_list):
        count = len(alarms_list)
        if count > 0:
            self.lbl_active_alarms.setText(f"{count} ACTIVE ALARM{'S' if count > 1 else ''}")
            self.lbl_active_alarms.setStyleSheet("""
                color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444; border-radius: 3px; padding: 1px 6px;
            """)
        else:
            self.lbl_active_alarms.setText("0 FAULTS")
            self.lbl_active_alarms.setStyleSheet("""
                color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                border-radius: 3px; padding: 1px 6px;
            """)

    def _on_rs485_updated(self, diag: dict):
        is_sim = diag.get("is_simulation", True)
        tx = diag.get("tx_count", 0)
        rx = diag.get("rx_count", 0)
        baud = diag.get("baudrate", 9600)
        port = diag.get("port", "COM3")
        crc_err = diag.get("crc_errors", 0)
        if is_sim:
            self.lbl_footer_status.setText(f"FUJI FRENIC-Mini C2 | Modbus RTU Virtual Bus @ {baud} | TX: {tx} RX: {rx} [SYNC OK]")
        elif crc_err > 0:
            self.lbl_footer_status.setText(f"RS-485 {port} | CRC Errors: {crc_err} | Timeouts: {diag.get('timeouts', 0)}")
        else:
            self.lbl_footer_status.setText(f"RS-485 {port} @ {baud} 8N1 | TX: {tx} RX: {rx} [HEALTHY]")
