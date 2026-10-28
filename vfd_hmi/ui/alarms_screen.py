"""
Alarms Screen for DLP KUMAR VFD HMI.
Provides real-time alarm annunciator, acknowledgement, clearing, and test fault simulation.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen
from core.system_state import AlarmItem

class AlarmsScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        
        # 1. Header Row
        hdr = QHBoxLayout()
        lbl_title = QLabel("ALARM & EVENT LOG")
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_title.setStyleSheet("color: #ff7a00; border: none;")
        hdr.addWidget(lbl_title)
        hdr.addStretch()
        
        self.lbl_count = QLabel("0 ACTIVE")
        self.lbl_count.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_count.setStyleSheet("""
            color: #10b981; background-color: rgba(16, 185, 129, 0.12);
            border-radius: 4px; padding: 2px 10px;
        """)
        hdr.addWidget(self.lbl_count)
        self.layout.addLayout(hdr)
        
        # 2. Scrollable Alarm List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(6)
        
        scroll.setWidget(self.scroll_content)
        self.layout.addWidget(scroll)
        
        # 3. Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_ack = QPushButton("✓  ACKNOWLEDGE ALL")
        btn_ack.setFixedHeight(48)
        btn_ack.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_ack.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #38bdf8;
                border: 1px solid #334155; border-radius: 6px;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        btn_ack.clicked.connect(self._on_ack)
        btn_layout.addWidget(btn_ack)
        
        btn_clear = QPushButton("✕  CLEAR RESOLVED")
        btn_clear.setFixedHeight(48)
        btn_clear.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #94a3b8;
                border: 1px solid #334155; border-radius: 6px;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        btn_clear.clicked.connect(self._on_clear)
        btn_layout.addWidget(btn_clear)
        
        btn_sim_fault = QPushButton("⚡  TRIGGER TEST TRIP")
        btn_sim_fault.setFixedHeight(48)
        btn_sim_fault.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_sim_fault.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15); color: #ef4444;
                border: 1px solid #ef4444; border-radius: 6px;
            }
            QPushButton:hover { background-color: #ef4444; color: #ffffff; }
        """)
        btn_sim_fault.clicked.connect(self._on_test_fault)
        btn_layout.addWidget(btn_sim_fault)
        
        self.layout.addLayout(btn_layout)
        
        if self.controller:
            self.controller.alarms_updated.connect(self.populate_alarms)
            self.populate_alarms(self.controller.alarms)

    def populate_alarms(self, alarms_list):
        # Clear existing
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        active_count = len(alarms_list)
        if active_count > 0:
            self.lbl_count.setText(f"{active_count} ACTIVE")
            self.lbl_count.setStyleSheet("""
                color: #ef4444; background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #ef4444; border-radius: 4px; padding: 2px 10px;
            """)
        else:
            self.lbl_count.setText("0 FAULTS")
            self.lbl_count.setStyleSheet("""
                color: #10b981; background-color: rgba(16, 185, 129, 0.12);
                border-radius: 4px; padding: 2px 10px;
            """)
            
        if not alarms_list:
            lbl_empty = QLabel("No active alarms or warnings. System operating normally.")
            lbl_empty.setFont(QFont("Segoe UI", 11))
            lbl_empty.setStyleSheet("color: #64748b; padding: 40px;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(lbl_empty)
            return

        for alm in alarms_list:
            card = QFrame()
            card.setFixedHeight(58)
            
            # Severity color
            if alm.severity == "CRITICAL":
                color = "#ef4444"
            elif alm.severity == "WARNING":
                color = "#f59e0b"
            else:
                color = "#38bdf8"
                
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #121824;
                    border: 1px solid #1e293b;
                    border-left: 4px solid {color};
                    border-radius: 6px;
                }}
            """)
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(14, 4, 14, 4)
            c_layout.setSpacing(12)
            
            # Code badge
            lbl_code = QLabel(alm.code)
            lbl_code.setFont(QFont("Consolas", 10, QFont.Bold))
            lbl_code.setStyleSheet(f"color: {color}; border: none; min-width: 60px;")
            
            # Message and Timestamp
            msg_box = QVBoxLayout()
            msg_box.setSpacing(1)
            
            lbl_msg = QLabel(alm.message)
            lbl_msg.setFont(QFont("Segoe UI", 10, QFont.Bold))
            lbl_msg.setStyleSheet("color: #f8fafc; border: none;")
            
            ack_text = "[ACKNOWLEDGED]" if alm.acknowledged else "[UNACKNOWLEDGED]"
            lbl_time = QLabel(f"Time: {alm.timestamp}  |  Severity: {alm.severity}  |  {ack_text}")
            lbl_time.setFont(QFont("Segoe UI", 8))
            lbl_time.setStyleSheet("color: #64748b; border: none;")
            
            msg_box.addWidget(lbl_msg)
            msg_box.addWidget(lbl_time)
            
            c_layout.addWidget(lbl_code)
            c_layout.addLayout(msg_box)
            c_layout.addStretch()
            
            self.scroll_layout.addWidget(card)
            
        self.scroll_layout.addStretch()

    def _on_ack(self):
        if self.controller:
            self.controller.acknowledge_alarms()

    def _on_clear(self):
        if self.controller:
            self.controller.clear_alarms()

    def _on_test_fault(self):
        if self.controller:
            self.controller.trigger_test_alarm("ERR-042", "Motor Overcurrent Instantaneous Trip", "CRITICAL")
