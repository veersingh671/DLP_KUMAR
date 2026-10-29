"""
Sensors Screen for DLP KUMAR VFD HMI.
ISA-101 High-Performance SCADA Telemetry Monitoring.
Structured instrument categorization, calibrated range gauges, and Modbus register mapping.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen, AnimatedProgressBar
from core.system_state import SensorItem

class SensorRowWidget(QFrame):
    """
    Structured sensor telemetry row with smooth animated gauge bar and threshold tags.
    """
    def __init__(self, sensor: SensorItem, parent=None):
        super().__init__(parent)
        self.sensor_id = sensor.id
        self.setFixedHeight(54)
        self.setStyleSheet("""
            SensorRowWidget {
                background-color: #131923;
                border: 1px solid #1e293b;
                border-radius: 5px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(12)
        
        # Name and Range Info
        name_col = QVBoxLayout()
        name_col.setSpacing(1)
        
        self.lbl_name = QLabel(sensor.name.upper())
        self.lbl_name.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_name.setStyleSheet("color: #f1f5f9; border: none;")
        
        modbus_addrs = {
            "S01": "0x3000 (M26 Analog)",
            "S02": "0x3001 (Line Volt)",
            "S03": "0x3002 (Motor Current)",
            "S04": "0x3003 (Pressure)",
            "S05": "0x3004 (Shaft Speed)"
        }
        addr = modbus_addrs.get(sensor.id, "0x3000")
        self.lbl_range = QLabel(f"Span: {sensor.min_val}..{sensor.max_val} {sensor.unit}  •  Modbus: {addr}")
        self.lbl_range.setFont(QFont("Consolas", 7))
        self.lbl_range.setStyleSheet("color: #64748b; border: none;")
        
        name_col.addWidget(self.lbl_name)
        name_col.addWidget(self.lbl_range)
        layout.addLayout(name_col, 35)
        
        # Smooth Animated Progress Bar
        self.bar = AnimatedProgressBar()
        self.bar.setRange(int(sensor.min_val * 10), int(sensor.max_val * 10))
        self.bar.setValue(int(sensor.value * 10))
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #090d13;
                border: 1px solid #1e293b;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.bar, 35)
        
        # Digital Value Readout
        self.lbl_val = QLabel(f"{sensor.value} {sensor.unit}")
        self.lbl_val.setFont(QFont("Consolas", 13, QFont.Bold))
        self.lbl_val.setStyleSheet("color: #f8fafc; border: none; min-width: 90px;")
        self.lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.lbl_val, 15)
        
        # Status Pill
        self.lbl_status = QLabel(sensor.status)
        self.lbl_status.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setFixedSize(74, 24)
        self._set_status_pill(sensor.status)
        layout.addWidget(self.lbl_status, 15)

    def _set_status_pill(self, status: str):
        self.lbl_status.setText(status)
        if status == "NORMAL":
            self.lbl_status.setStyleSheet("""
                color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 4px;
            """)
            self.bar.setStyleSheet("""
                QProgressBar { background-color: #090d13; border: 1px solid #1e293b; border-radius: 2px; }
                QProgressBar::chunk { background-color: #2563eb; border-radius: 2px; }
            """)
        elif status == "WARNING":
            self.lbl_status.setStyleSheet("""
                color: #f59e0b; background-color: rgba(245, 158, 11, 0.15);
                border: 1px solid #f59e0b; border-radius: 4px;
            """)
            self.bar.setStyleSheet("""
                QProgressBar { background-color: #090d13; border: 1px solid #1e293b; border-radius: 2px; }
                QProgressBar::chunk { background-color: #f59e0b; border-radius: 2px; }
            """)
        else:
            self.lbl_status.setStyleSheet("""
                color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444; border-radius: 4px;
            """)
            self.bar.setStyleSheet("""
                QProgressBar { background-color: #090d13; border: 1px solid #1e293b; border-radius: 2px; }
                QProgressBar::chunk { background-color: #ef4444; border-radius: 2px; }
            """)

    def update_data(self, sensor: SensorItem):
        self.bar.setValueSmooth(sensor.value * 10)
        self.lbl_val.setText(f"{sensor.value:.1f} {sensor.unit}")
        self._set_status_pill(sensor.status)


class SensorsScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        
        # Scroll area for sensor rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(6)
        
        scroll.setWidget(self.scroll_content)
        self.layout.addWidget(scroll)
        
        self.sensor_widgets = {}
        
        if self.controller:
            self.controller.sensors_updated.connect(self.update_sensors)
            self.build_sensors(self.controller.sensors)

    def build_sensors(self, sensors_list):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.sensor_widgets = {}
        for s in sensors_list:
            w = SensorRowWidget(s)
            self.scroll_layout.addWidget(w)
            self.sensor_widgets[s.id] = w
            
        self.scroll_layout.addStretch()

    def update_sensors(self, sensors_list):
        for s in sensors_list:
            if s.id in self.sensor_widgets:
                self.sensor_widgets[s.id].update_data(s)
