"""
Sensors Screen for DLP KUMAR VFD HMI.
Provides real-time analog and digital sensor monitoring with graphical range gauges.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen
from core.system_state import SensorItem

class SensorRowWidget(QFrame):
    def __init__(self, sensor: SensorItem, parent=None):
        super().__init__(parent)
        self.sensor_id = sensor.id
        self.setFixedHeight(58)
        self.setStyleSheet("""
            QFrame {
                background-color: #121824;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(14)
        
        # Name and Range Info
        name_col = QVBoxLayout()
        name_col.setSpacing(2)
        
        self.lbl_name = QLabel(sensor.name.upper())
        self.lbl_name.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_name.setStyleSheet("color: #f8fafc; border: none;")
        
        self.lbl_range = QLabel(f"Span: {sensor.min_val}..{sensor.max_val} {sensor.unit}")
        self.lbl_range.setFont(QFont("Segoe UI", 8))
        self.lbl_range.setStyleSheet("color: #64748b; border: none;")
        
        name_col.addWidget(self.lbl_name)
        name_col.addWidget(self.lbl_range)
        layout.addLayout(name_col)
        
        # Visual Progress / Range Bar
        self.bar = QProgressBar()
        self.bar.setRange(int(sensor.min_val), int(sensor.max_val))
        self.bar.setValue(int(sensor.value))
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(12)
        self.bar.setMinimumWidth(160)
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #0b0f19;
                border: 1px solid #334155;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #38bdf8;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.bar)
        
        # Digital Value Readout
        self.lbl_val = QLabel(f"{sensor.value} {sensor.unit}")
        self.lbl_val.setFont(QFont("Consolas", 14, QFont.Bold))
        self.lbl_val.setStyleSheet("color: #f8fafc; border: none; min-width: 90px;")
        self.lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.lbl_val)
        
        # Status Pill
        self.lbl_status = QLabel(sensor.status)
        self.lbl_status.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setFixedSize(80, 26)
        self._set_status_pill(sensor.status)
        layout.addWidget(self.lbl_status)

    def _set_status_pill(self, status: str):
        self.lbl_status.setText(status)
        if status == "NORMAL":
            self.lbl_status.setStyleSheet("""
                color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 4px;
            """)
        elif status == "WARNING":
            self.lbl_status.setStyleSheet("""
                color: #f59e0b; background-color: rgba(245, 158, 11, 0.15);
                border: 1px solid #f59e0b; border-radius: 4px;
            """)
        else:
            self.lbl_status.setStyleSheet("""
                color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444; border-radius: 4px;
            """)

    def update_data(self, sensor: SensorItem):
        self.bar.setValue(int(sensor.value))
        if isinstance(sensor.value, float):
            self.lbl_val.setText(f"{sensor.value:.1f} {sensor.unit}")
        else:
            self.lbl_val.setText(f"{sensor.value} {sensor.unit}")
        self._set_status_pill(sensor.status)


class SensorsScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        self.sensor_rows = {}
        
        if self.controller:
            for s in self.controller.sensors:
                row = SensorRowWidget(s)
                self.sensor_rows[s.id] = row
                self.layout.addWidget(row)
                
            self.layout.addStretch()
            self.controller.sensors_updated.connect(self.on_sensors_updated)
            
    def on_sensors_updated(self, sensors_list):
        for s in sensors_list:
            if s.id in self.sensor_rows:
                self.sensor_rows[s.id].update_data(s)
