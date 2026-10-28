"""
UI Components for DLP KUMAR VFD HMI.
Provides industrial-grade, touch-optimized widgets for 800x480 resolution.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QFont, QColor

class Header(QWidget):
    """
    Top status bar (height: 46px) with screen title, VFD comms indicator,
    system health, Wi-Fi signal, and digital clock.
    """
    def __init__(self, parent=None, close_callback=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setStyleSheet("""
            QWidget {
                background-color: #0b0f19;
                border-bottom: 1px solid #1e293b;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)
        
        # Screen Title
        self.title_label = QLabel("DASHBOARD")
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.title_label.setStyleSheet("color: #ff7a00; border: none; letter-spacing: 1px;")
        
        # Status Badges
        self.vfd_pill = QLabel("● VFD: ONLINE")
        self.vfd_pill.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.vfd_pill.setStyleSheet("""
            color: #10b981;
            background-color: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 6px;
            padding: 3px 8px;
        """)
        
        self.sys_pill = QLabel("SYS: OK")
        self.sys_pill.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.sys_pill.setStyleSheet("""
            color: #38bdf8;
            background-color: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 6px;
            padding: 3px 8px;
        """)
        
        self.wifi_pill = QLabel("WiFi: 85%")
        self.wifi_pill.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.wifi_pill.setStyleSheet("""
            color: #94a3b8;
            background-color: rgba(148, 163, 184, 0.1);
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 6px;
            padding: 3px 8px;
        """)
        
        # Clock
        self.time_label = QLabel("00:00:00")
        self.time_label.setFont(QFont("Consolas", 12, QFont.Bold))
        self.time_label.setStyleSheet("color: #f8fafc; border: none; padding-left: 6px;")
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.vfd_pill)
        layout.addWidget(self.sys_pill)
        layout.addWidget(self.wifi_pill)
        layout.addWidget(self.time_label)

        # Desktop Exit/Close button
        if close_callback:
            self.btn_close = QPushButton("✕")
            self.btn_close.setFixedSize(26, 26)
            self.btn_close.setCursor(Qt.PointingHandCursor)
            self.btn_close.setToolTip("Close HMI")
            self.btn_close.setStyleSheet("""
                QPushButton {
                    background: #1e293b;
                    color: #94a3b8;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: #ef4444;
                    color: #ffffff;
                    border: 1px solid #ef4444;
                }
            """)
            self.btn_close.clicked.connect(close_callback)
            layout.addWidget(self.btn_close)
        
        # Clock timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
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
                    border: 1px solid #ef4444; border-radius: 6px; padding: 3px 8px;
                """)
            else:
                self.vfd_pill.setStyleSheet("""
                    color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                    border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 6px; padding: 3px 8px;
                """)
        else:
            self.vfd_pill.setText("○ VFD: OFFLINE")
            self.vfd_pill.setStyleSheet("""
                color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444; border-radius: 6px; padding: 3px 8px;
            """)

    def update_wifi(self, signal_pct: int, connected: bool = True):
        if connected:
            bars = "████" if signal_pct > 75 else ("███░" if signal_pct > 50 else "██░░")
            self.wifi_pill.setText(f"WiFi {bars} {signal_pct}%")
            self.wifi_pill.setStyleSheet("""
                color: #38bdf8; background-color: rgba(56, 189, 248, 0.12);
                border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 3px 8px;
            """)
        else:
            self.wifi_pill.setText("WiFi: OFFLINE")
            self.wifi_pill.setStyleSheet("""
                color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444; border-radius: 6px; padding: 3px 8px;
            """)

    def update_sys_status(self, alarm_count: int):
        if alarm_count > 0:
            self.sys_pill.setText(f"SYS: {alarm_count} ALARMS")
            self.sys_pill.setStyleSheet("""
                color: #f59e0b; background-color: rgba(245, 158, 11, 0.15);
                border: 1px solid #f59e0b; border-radius: 6px; padding: 3px 8px;
            """)
        else:
            self.sys_pill.setText("SYS: NORMAL")
            self.sys_pill.setStyleSheet("""
                color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 6px; padding: 3px 8px;
            """)


class NavigationBar(QWidget):
    """
    Bottom persistent navigation bar (height: 52px).
    Large touch targets (7 buttons, ~110px wide x 46px high).
    """
    def __init__(self, switch_callback, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet("""
            QWidget {
                background-color: #0b0f19;
                border-top: 1px solid #1e293b;
            }
        """)
        self.switch_callback = switch_callback
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)
        
        self.buttons = []
        nav_items = ["HOME", "VFD", "PARAMS", "SENSORS", "ACTUATORS", "ALARMS", "SETTINGS"]
        
        for idx, item in enumerate(nav_items):
            btn = QPushButton(item)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #121824;
                    color: #94a3b8;
                    border: 1px solid #1e293b;
                    border-radius: 6px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #1a2233;
                    border: 1px solid #334155;
                    color: #f8fafc;
                }
                QPushButton:checked {
                    background-color: #ff7a00;
                    border: 1px solid #ff7a00;
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
                background-color: #121824;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        
        # Header (Label + Unit)
        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_title = QLabel(label.upper())
        self.lbl_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #64748b; border: none;")
        
        self.lbl_unit = QLabel(unit)
        self.lbl_unit.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_unit.setStyleSheet("color: #ff7a00; border: none;")
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
        self.setStyleSheet("background-color: #070a12;")
