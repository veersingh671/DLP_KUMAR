"""
Alarms Screen for DLP KUMAR VFD HMI.
ISA-101 High-Performance SCADA Alarm Annunciator & Diagnostic Suite.
Provides real-time event logging, single and global acknowledgement,
and animated drop-out root-cause diagnostic drawers.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
from ui.components import BaseScreen
from core.system_state import AlarmItem

class AlarmDropoutRowWidget(QFrame):
    """
    Industrial Alarm Card with smooth animated drop-out diagnostic drawer.
    Tapping '▼ DETAILS' expands the technical root-cause, RS-485 Modbus register, and remedy.
    """
    def __init__(self, alm: AlarmItem, ack_callback, parent=None):
        super().__init__(parent)
        self.alm = alm
        self.ack_callback = ack_callback
        self._is_open = False
        
        # Disciplined severity color coding
        if alm.severity == "CRITICAL":
            self.color = "#dc2626"
        elif alm.severity == "WARNING":
            self.color = "#d97706"
        else:
            self.color = "#2563eb"
            
        self.setStyleSheet(f"""
            AlarmDropoutRowWidget {{
                background-color: #131923;
                border: 1px solid #1e293b;
                border-left: 4px solid {self.color};
                border-radius: 5px;
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 6, 10, 6)
        main_layout.setSpacing(4)
        
        # 1. Top Summary Strip
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        lbl_code = QLabel(alm.code)
        lbl_code.setFont(QFont("Consolas", 10, QFont.Bold))
        lbl_code.setStyleSheet(f"color: {self.color}; border: none; min-width: 60px;")
        top_row.addWidget(lbl_code)
        
        msg_box = QVBoxLayout()
        msg_box.setSpacing(1)
        
        lbl_msg = QLabel(alm.message)
        lbl_msg.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_msg.setStyleSheet("color: #f1f5f9; border: none;")
        
        ack_text = "[ACKNOWLEDGED]" if alm.acknowledged else "[UNACKNOWLEDGED]"
        ack_col = "#10b981" if alm.acknowledged else "#ef4444"
        lbl_meta = QLabel(f"Timestamp: {alm.timestamp}  •  Severity: {alm.severity}  •  <span style='color:{ack_col};'>{ack_text}</span>")
        lbl_meta.setFont(QFont("Consolas", 7))
        lbl_meta.setStyleSheet("color: #64748b; border: none;")
        
        msg_box.addWidget(lbl_msg)
        msg_box.addWidget(lbl_meta)
        top_row.addLayout(msg_box)
        top_row.addStretch()
        
        # Toggle Details Button
        self.btn_toggle = QPushButton("▼ DETAILS")
        self.btn_toggle.setFixedSize(80, 26)
        self.btn_toggle.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: #1e293b; color: #cbd5e1;
                border: 1px solid #334155; border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: #334155; color: #ffffff; }}
        """)
        self.btn_toggle.clicked.connect(self._toggle_dropout)
        top_row.addWidget(self.btn_toggle)
        main_layout.addLayout(top_row)
        
        # 2. Animated Drop-out Drawer (hidden initially, height 0)
        self.dropout_drawer = QFrame()
        self.dropout_drawer.setMaximumHeight(0)
        self.dropout_drawer.setStyleSheet("""
            QFrame {
                background-color: #090d13;
                border: 1px solid #1e293b;
                border-radius: 4px;
            }
        """)
        dr_layout = QHBoxLayout(self.dropout_drawer)
        dr_layout.setContentsMargins(10, 6, 10, 6)
        dr_layout.setSpacing(10)
        
        detail_col = QVBoxLayout()
        detail_col.setSpacing(2)
        
        # Diagnostic metadata mapping
        reg_map = "Fuji M16 (0x0810 Trip Code)" if alm.severity == "CRITICAL" else "Modbus 0x3000 (Analog Limit)"
        lbl_source = QLabel(f"Signal Origin: {reg_map}")
        lbl_source.setFont(QFont("Consolas", 8, QFont.Bold))
        lbl_source.setStyleSheet("color: #93c5fd; border: none;")
        
        remedy_text = "Verify motor mechanical load, inspect cable insulation, extend accel time (F07), and reset via RST command." if "Overcurrent" in alm.message or "Trip" in alm.message else "Cooling airflow requires inspection. Clear filter pads and check fan rotation."
        lbl_remedy = QLabel(f"Recommended Action: {remedy_text}")
        lbl_remedy.setFont(QFont("Segoe UI", 8))
        lbl_remedy.setStyleSheet("color: #94a3b8; border: none;")
        lbl_remedy.setWordWrap(True)
        
        detail_col.addWidget(lbl_source)
        detail_col.addWidget(lbl_remedy)
        dr_layout.addLayout(detail_col)
        dr_layout.addStretch()
        
        if not alm.acknowledged:
            btn_ack_single = QPushButton("ACK FAULT")
            btn_ack_single.setFixedSize(86, 28)
            btn_ack_single.setFont(QFont("Segoe UI", 8, QFont.Bold))
            btn_ack_single.setStyleSheet("""
                QPushButton {
                    background-color: #15803d; color: #ffffff;
                    border: 1px solid #16a34a; border-radius: 4px;
                }
                QPushButton:hover { background-color: #16a34a; }
            """)
            btn_ack_single.clicked.connect(self._ack_single)
            dr_layout.addWidget(btn_ack_single)
            
        main_layout.addWidget(self.dropout_drawer)
        
        # Property animation for smooth drop-out height
        self._anim = QPropertyAnimation(self.dropout_drawer, b"maximumHeight")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def _toggle_dropout(self):
        if self._anim.state() == QPropertyAnimation.Running:
            self._anim.stop()
            
        if self._is_open:
            self._anim.setStartValue(self.dropout_drawer.maximumHeight())
            self._anim.setEndValue(0)
            self._is_open = False
            self.btn_toggle.setText("▼ DETAILS")
        else:
            self._anim.setStartValue(self.dropout_drawer.maximumHeight())
            self._anim.setEndValue(60)
            self._is_open = True
            self.btn_toggle.setText("▲ RETRACT")
            
        self._anim.start()

    def _ack_single(self):
        self.alm.acknowledged = True
        self.ack_callback()


class AlarmsScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        
        # 1. Header Row
        hdr = QHBoxLayout()
        lbl_title = QLabel("ALARM & EVENT LOG")
        lbl_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_title.setStyleSheet("color: #cbd5e1; border: none;")
        hdr.addWidget(lbl_title)
        hdr.addStretch()
        
        self.lbl_count = QLabel("0 ACTIVE")
        self.lbl_count.setFont(QFont("Segoe UI", 9, QFont.Bold))
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
        btn_layout.setSpacing(8)
        
        btn_ack = QPushButton("✓  ACKNOWLEDGE ALL")
        btn_ack.setFixedHeight(40)
        btn_ack.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn_ack.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #cbd5e1;
                border: 1px solid #334155; border-radius: 4px;
            }
            QPushButton:hover { background-color: #2563eb; color: #ffffff; border: 1px solid #3b82f6; }
        """)
        btn_ack.clicked.connect(self._on_ack)
        btn_layout.addWidget(btn_ack)
        
        btn_clear = QPushButton("✕  CLEAR RESOLVED")
        btn_clear.setFixedHeight(40)
        btn_clear.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #94a3b8;
                border: 1px solid #334155; border-radius: 4px;
            }
            QPushButton:hover { background-color: #334155; color: #f1f5f9; }
        """)
        btn_clear.clicked.connect(self._on_clear)
        btn_layout.addWidget(btn_clear)
        
        btn_sim_fault = QPushButton("⚡  TRIGGER TEST TRIP")
        btn_sim_fault.setFixedHeight(40)
        btn_sim_fault.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn_sim_fault.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #fca5a5;
                border: 1px solid #991b1b; border-radius: 4px;
            }
            QPushButton:hover { background-color: #991b1b; color: #ffffff; }
        """)
        btn_sim_fault.clicked.connect(self._on_test_fault)
        btn_layout.addWidget(btn_sim_fault)
        
        self.layout.addLayout(btn_layout)
        
        if self.controller:
            self.controller.alarms_updated.connect(self.populate_alarms)
            self.populate_alarms(self.controller.alarms)

    def populate_alarms(self, alarms_list):
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
            lbl_empty.setFont(QFont("Segoe UI", 10))
            lbl_empty.setStyleSheet("color: #64748b; padding: 40px;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(lbl_empty)
            return

        for alm in alarms_list:
            card = AlarmDropoutRowWidget(alm, ack_callback=self._on_single_ack)
            self.scroll_layout.addWidget(card)
            
        self.scroll_layout.addStretch()

    def _on_single_ack(self):
        if self.controller:
            self.controller.alarms_updated.emit(self.controller.alarms)

    def _on_ack(self):
        if self.controller:
            self.controller.acknowledge_alarms()

    def _on_clear(self):
        if self.controller:
            self.controller.clear_alarms()

    def _on_test_fault(self):
        if self.controller:
            self.controller.trigger_test_alarm("ERR-042", "Motor Overcurrent Instantaneous Trip", "CRITICAL")
