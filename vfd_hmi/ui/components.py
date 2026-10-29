"""
UI Components for DLP KUMAR VFD HMI.
Provides ISA-101 compliant, professional industrial-grade widgets with fluid animations
(animated drop-out drawers, smooth progress gauges, pulsing beacons).
Engineered with high-contrast, non-glare slate surfaces and disciplined status indicators.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QFrame, QProgressBar, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QTimer, QTime, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QColor

class PulsingStatusBeacon(QLabel):
    """
    Industrial tactile LED status beacon with gentle pulsing animation.
    """
    def __init__(self, color="#10b981", parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.base_color = color
        self._pulse_alpha = 1.0
        self._pulse_dir = -1
        
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick_pulse)
        self._timer.start(75)
        self._update_style()

    def set_color(self, color: str):
        self.base_color = color
        self._update_style()

    def _tick_pulse(self):
        self._pulse_alpha += self._pulse_dir * 0.05
        if self._pulse_alpha <= 0.40:
            self._pulse_alpha = 0.40
            self._pulse_dir = 1
        elif self._pulse_alpha >= 1.0:
            self._pulse_alpha = 1.0
            self._pulse_dir = -1
        self._update_style()

    def _update_style(self):
        r, g, b = 16, 185, 129
        if self.base_color == "#ef4444" or self.base_color == "#dc2626":
            r, g, b = 239, 68, 68
        elif self.base_color == "#38bdf8" or self.base_color == "#3b82f6":
            r, g, b = 59, 130, 246
        elif self.base_color == "#f59e0b" or self.base_color == "#d97706":
            r, g, b = 245, 158, 11
        elif self.base_color == "#94a3b8":
            r, g, b = 148, 163, 184
            
        self.setStyleSheet(f"""
            QLabel {{
                background-color: rgba({r}, {g}, {b}, {self._pulse_alpha:.2f});
                border: 2px solid rgba({r}, {g}, {b}, 0.95);
                border-radius: 6px;
            }}
        """)


class AnimatedProgressBar(QProgressBar):
    """
    Industrial gauge bar with smooth numerical interpolation animation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_val = float(self.value())
        self._anim = QPropertyAnimation(self, b"animatedVal")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_anim_val(self):
        return self._current_val

    def set_anim_val(self, val):
        self._current_val = val
        super().setValue(int(round(val)))

    animatedVal = pyqtProperty(float, get_anim_val, set_anim_val)

    def setValueSmooth(self, target_val: float):
        if self._anim.state() == QPropertyAnimation.Running:
            self._anim.stop()
        self._anim.setStartValue(self._current_val)
        self._anim.setEndValue(float(target_val))
        self._anim.start()


class DropoutDrawer(QFrame):
    """
    Industrial animated drop-out / slide-down drawer beneath the header.
    Features smooth height animation, real-time RS-485 packet stream, and quick emergency halt.
    """
    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setFixedHeight(0)
        self.setMaximumHeight(0)
        self._is_open = False
        
        self.setStyleSheet("""
            DropoutDrawer {
                background-color: #0c1017;
                border-bottom: 2px solid #2563eb;
                border-left: 1px solid #1e293b;
                border-right: 1px solid #1e293b;
            }
        """)
        
        self._anim = QPropertyAnimation(self, b"maximumHeight")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._sync_height)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)
        
        # 1. RS-485 Live Stream Box
        mb_box = QFrame()
        mb_box.setStyleSheet("background-color: #111722; border: 1px solid #1e293b; border-radius: 6px;")
        mb_l = QVBoxLayout(mb_box)
        mb_l.setContentsMargins(8, 4, 8, 4)
        mb_l.setSpacing(2)
        
        top_mb = QHBoxLayout()
        lbl_mb_title = QLabel("RS-485 MODBUS RTU BUS STREAM")
        lbl_mb_title.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_mb_title.setStyleSheet("color: #94a3b8; border: none;")
        self.lbl_mb_meta = QLabel("Baud: 9600 8N1 | CRC: VALID")
        self.lbl_mb_meta.setFont(QFont("Consolas", 8, QFont.Bold))
        self.lbl_mb_meta.setStyleSheet("color: #10b981; border: none;")
        top_mb.addWidget(lbl_mb_title)
        top_mb.addStretch()
        top_mb.addWidget(self.lbl_mb_meta)
        mb_l.addLayout(top_mb)
        
        self.lbl_mb_trace = QLabel("TX: [01 03 21 00 00 08 4E 3A] • RX: [01 03 10 00 01 11 ...]")
        self.lbl_mb_trace.setFont(QFont("Consolas", 8))
        self.lbl_mb_trace.setStyleSheet("color: #cbd5e1; border: none;")
        mb_l.addWidget(self.lbl_mb_trace)
        layout.addWidget(mb_box, 60)
        
        # 2. Drive Quick Envelope Box
        env_box = QFrame()
        env_box.setStyleSheet("background-color: #111722; border: 1px solid #1e293b; border-radius: 6px;")
        env_l = QHBoxLayout(env_box)
        env_l.setContentsMargins(8, 4, 8, 4)
        env_l.setSpacing(8)
        
        self.lbl_quick_curr = self._add_stat(env_l, "CURRENT", "0.00 A", "#f8fafc")
        self.lbl_quick_volt = self._add_stat(env_l, "DC BUS", "540 V", "#f8fafc")
        self.lbl_quick_temp = self._add_stat(env_l, "TEMP", "38.0 °C", "#10b981")
        layout.addWidget(env_box, 30)
        
        # 3. Fast Stop Button
        self.btn_estop = QPushButton("EMERGENCY\nSTOP")
        self.btn_estop.setFixedSize(92, 50)
        self.btn_estop.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.btn_estop.setCursor(Qt.PointingHandCursor)
        self.btn_estop.setStyleSheet("""
            QPushButton {
                background-color: #991b1b; color: #ffffff;
                border: 2px solid #b91c1c; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #b91c1c; }
            QPushButton:pressed { background-color: #7f1d1d; }
        """)
        self.btn_estop.clicked.connect(self._on_estop)
        layout.addWidget(self.btn_estop)

    def _sync_height(self, val):
        self.setFixedHeight(val)

    def _add_stat(self, layout, title, val, color):
        col = QVBoxLayout()
        col.setSpacing(1)
        lt = QLabel(title)
        lt.setFont(QFont("Segoe UI", 7, QFont.Bold))
        lt.setStyleSheet("color: #64748b; border: none;")
        lv = QLabel(val)
        lv.setFont(QFont("Consolas", 10, QFont.Bold))
        lv.setStyleSheet(f"color: {color}; border: none;")
        col.addWidget(lt)
        col.addWidget(lv)
        layout.addLayout(col)
        return lv

    def toggle(self, target_height: int = 68):
        if self._anim.state() == QPropertyAnimation.Running:
            self._anim.stop()
        if self._is_open:
            self._anim.setStartValue(self.height())
            self._anim.setEndValue(0)
            self._is_open = False
        else:
            self._anim.setStartValue(self.height())
            self._anim.setEndValue(target_height)
            self._is_open = True
        self._anim.start()

    def update_telemetry(self, vfd_state):
        self.lbl_quick_curr.setText(f"{vfd_state.output_current:.2f} A")
        self.lbl_quick_volt.setText(f"{int(vfd_state.dc_bus_voltage)} V")
        temp_col = "#10b981" if vfd_state.motor_temp < 70 else ("#f59e0b" if vfd_state.motor_temp < 85 else "#ef4444")
        self.lbl_quick_temp.setText(f"{vfd_state.motor_temp:.1f} °C")
        self.lbl_quick_temp.setStyleSheet(f"color: {temp_col}; border: none;")

    def update_rs485(self, diag: dict):
        tx = diag.get("tx_count", 0)
        rx = diag.get("rx_count", 0)
        baud = diag.get("baudrate", 9600)
        last_tx = diag.get("last_tx_hex", "")
        last_rx = diag.get("last_rx_hex", "")
        crc_err = diag.get("crc_errors", 0)
        
        tx_part = f"TX: [{last_tx[:18]}..]" if len(last_tx) > 18 else f"TX: [{last_tx}]"
        rx_part = f"RX: [{last_rx[:18]}..]" if len(last_rx) > 18 else f"RX: [{last_rx}]"
        self.lbl_mb_trace.setText(f"{tx_part} • {rx_part}")
        
        status_txt = "CRC OK" if crc_err == 0 else f"{crc_err} CRC ERR"
        status_col = "#10b981" if crc_err == 0 else "#ef4444"
        self.lbl_mb_meta.setText(f"Baud: {baud} | Status: {status_txt} | {tx} TX / {rx} RX")
        self.lbl_mb_meta.setStyleSheet(f"color: {status_col}; border: none;")

    def _on_estop(self):
        if self.controller:
            self.controller.stop_vfd()


class Header(QWidget):
    """
    Top status bar with screen title, pulsing status beacon,
    drop-out diagnostics drawer trigger, RS-485 pill, VFD pill, and clock.
    """
    def __init__(self, parent=None, close_callback=None, drawer_callback=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.drawer_callback = drawer_callback
        self.setStyleSheet("""
            QWidget {
                background-color: #0c1017;
                border-bottom: 1px solid #1e293b;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        
        # Pulsing Beacon & Screen Title
        self.beacon = PulsingStatusBeacon(color="#10b981")
        layout.addWidget(self.beacon)
        
        self.title_label = QLabel("DASHBOARD")
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #f1f5f9; border: none; letter-spacing: 0.5px;")
        layout.addWidget(self.title_label)
        
        # Drop-out Drawer Trigger Button
        if drawer_callback:
            self.btn_tray = QPushButton("▼ DIAGNOSTICS")
            self.btn_tray.setFixedHeight(26)
            self.btn_tray.setFont(QFont("Segoe UI", 8, QFont.Bold))
            self.btn_tray.setCursor(Qt.PointingHandCursor)
            self.btn_tray.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b; color: #cbd5e1;
                    border: 1px solid #334155; border-radius: 4px; padding: 0 8px;
                }
                QPushButton:hover { background-color: #2563eb; color: #ffffff; border: 1px solid #3b82f6; }
            """)
            self.btn_tray.clicked.connect(self._toggle_drawer)
            layout.addWidget(self.btn_tray)
        
        layout.addStretch()
        
        # Status Badges
        self.rs485_pill = QLabel("● RS485: SIM")
        self.rs485_pill.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.rs485_pill.setStyleSheet("""
            color: #93c5fd;
            background-color: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.35);
            border-radius: 5px;
            padding: 2px 7px;
        """)
        layout.addWidget(self.rs485_pill)

        self.vfd_pill = QLabel("● VFD: ONLINE")
        self.vfd_pill.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.vfd_pill.setStyleSheet("""
            color: #10b981;
            background-color: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-radius: 5px;
            padding: 2px 7px;
        """)
        layout.addWidget(self.vfd_pill)
        
        self.sys_pill = QLabel("SYS: NORMAL")
        self.sys_pill.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.sys_pill.setStyleSheet("""
            color: #94a3b8;
            background-color: rgba(148, 163, 184, 0.10);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 5px;
            padding: 2px 7px;
        """)
        layout.addWidget(self.sys_pill)
        
        # Clock
        self.time_label = QLabel("00:00:00")
        self.time_label.setFont(QFont("Consolas", 11, QFont.Bold))
        self.time_label.setStyleSheet("color: #e2e8f0; border: none; padding-left: 4px;")
        layout.addWidget(self.time_label)

        # Desktop Exit/Close button
        if close_callback:
            self.btn_close = QPushButton("✕")
            self.btn_close.setFixedSize(26, 26)
            self.btn_close.setCursor(Qt.PointingHandCursor)
            self.btn_close.setToolTip("Close HMI")
            self.btn_close.setStyleSheet("""
                QPushButton {
                    background: #1e293b; color: #94a3b8;
                    border: 1px solid #334155; border-radius: 4px;
                    font-weight: bold; font-size: 12px;
                }
                QPushButton:hover { background: #b91c1c; color: #ffffff; border: 1px solid #dc2626; }
            """)
            self.btn_close.clicked.connect(close_callback)
            layout.addWidget(self.btn_close)
        
        # Clock timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def _toggle_drawer(self):
        if self.drawer_callback:
            is_open = self.drawer_callback()
            self.btn_tray.setText("▲ RETRACT" if is_open else "▼ DIAGNOSTICS")
        
    def update_time(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.time_label.setText(current_time)

    def set_title(self, title):
        self.title_label.setText(title.upper())

    def update_vfd_status(self, is_online: bool, status_text: str = "ONLINE"):
        if is_online:
            self.vfd_pill.setText(f"● VFD: {status_text}")
            if "TRIP" in status_text or "FAULT" in status_text:
                self.vfd_pill.setStyleSheet("""
                    color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                    border: 1px solid #ef4444; border-radius: 5px; padding: 2px 7px;
                """)
                self.beacon.set_color("#ef4444")
            elif "RUNNING" in status_text or "ACCEL" in status_text or "JOG" in status_text:
                self.vfd_pill.setStyleSheet("""
                    color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                    border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 5px; padding: 2px 7px;
                """)
                self.beacon.set_color("#10b981")
            else:
                self.vfd_pill.setStyleSheet("""
                    color: #94a3b8; background-color: rgba(148, 163, 184, 0.1);
                    border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 5px; padding: 2px 7px;
                """)
                self.beacon.set_color("#94a3b8")
        else:
            self.vfd_pill.setText("○ VFD: OFFLINE")
            self.vfd_pill.setStyleSheet("""
                color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444; border-radius: 5px; padding: 2px 7px;
            """)
            self.beacon.set_color("#ef4444")

    def update_wifi(self, signal_pct: int, connected: bool = True):
        pass

    def update_sys_status(self, alarm_count: int):
        if alarm_count > 0:
            self.sys_pill.setText(f"SYS: {alarm_count} ALARMS")
            self.sys_pill.setStyleSheet("""
                color: #f59e0b; background-color: rgba(245, 158, 11, 0.15);
                border: 1px solid #f59e0b; border-radius: 5px; padding: 2px 7px;
            """)
        else:
            self.sys_pill.setText("SYS: NORMAL")
            self.sys_pill.setStyleSheet("""
                color: #94a3b8; background-color: rgba(148, 163, 184, 0.10);
                border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 5px; padding: 2px 7px;
            """)

    def update_rs485_status(self, diag: dict):
        is_sim = diag.get("is_simulation", True)
        is_conn = diag.get("is_connected", False)
        port = diag.get("port", "COM3")
        tx = diag.get("tx_count", 0)
        crc_err = diag.get("crc_errors", 0)

        if is_sim:
            self.rs485_pill.setText("◌ RS485: SIM")
            self.rs485_pill.setStyleSheet("""
                color: #93c5fd; background-color: rgba(59, 130, 246, 0.12);
                border: 1px solid rgba(59, 130, 246, 0.35); border-radius: 5px; padding: 2px 7px;
            """)
        elif is_conn and crc_err == 0:
            self.rs485_pill.setText(f"● {port} ({tx})")
            self.rs485_pill.setStyleSheet("""
                color: #10b981; background-color: rgba(16, 185, 129, 0.15);
                border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 5px; padding: 2px 7px;
            """)
        else:
            self.rs485_pill.setText(f"⚠ {port} ERR")
            self.rs485_pill.setStyleSheet("""
                color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444; border-radius: 5px; padding: 2px 7px;
            """)


class NavigationBar(QWidget):
    """
    Bottom persistent navigation bar (height: 52px).
    High-contrast industrial tab strip with 3px top active indicator.
    """
    def __init__(self, switch_callback, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QWidget {
                background-color: #0c1017;
                border-top: 1px solid #1e293b;
            }
        """)
        self.switch_callback = switch_callback
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(6)
        
        self.buttons = []
        nav_items = ["HOME", "VFD", "PARAMS", "SENSORS", "ACTUATORS", "ALARMS", "SETTINGS"]
        
        for idx, item in enumerate(nav_items):
            btn = QPushButton(item)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #131923;
                    color: #94a3b8;
                    border: 1px solid #1e293b;
                    border-radius: 4px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #1c2536;
                    border: 1px solid #334155;
                    color: #f8fafc;
                }
                QPushButton:checked {
                    background-color: #1a2333;
                    border: 1px solid #3b82f6;
                    border-top: 3px solid #3b82f6;
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(lambda checked, index=idx: self.nav_clicked(index))
            layout.addWidget(btn)
            self.buttons.append(btn)
            
        if self.buttons:
            self.buttons[0].setChecked(True)
            
    def nav_clicked(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.switch_callback(index)


class IndustrialCard(QFrame):
    """
    A dark industrial metric tile showing title, large value, and unit pill.
    """
    def __init__(self, label: str, value: str, unit: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #131923;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        
        # Header (Label + Unit)
        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_title = QLabel(label.upper())
        self.lbl_title.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #64748b; border: none;")
        
        self.lbl_unit = QLabel(unit)
        self.lbl_unit.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.lbl_unit.setStyleSheet("color: #94a3b8; border: none;")
        self.lbl_unit.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        hdr.addWidget(self.lbl_title)
        hdr.addStretch()
        hdr.addWidget(self.lbl_unit)
        layout.addLayout(hdr)
        
        # Main Value Readout
        self.lbl_val = QLabel(value)
        self.lbl_val.setFont(QFont("Consolas", 22, QFont.Bold))
        self.lbl_val.setStyleSheet("color: #f8fafc; border: none;")
        self.lbl_val.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(self.lbl_val)
        
    def set_value(self, val_str: str, color: str = "#f8fafc"):
        self.lbl_val.setText(val_str)
        self.lbl_val.setStyleSheet(f"color: {color}; border: none;")


class BaseScreen(QWidget):
    """
    Base container for HMI screens fitting 800 x 382 px viewport.
    """
    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)
        self.layout.setSpacing(6)
        self.setStyleSheet("background-color: #0c1017;")
