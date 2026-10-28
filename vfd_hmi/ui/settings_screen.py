"""
Settings Screen for DLP KUMAR VFD HMI.
Displays hardware communication interfaces, network diagnostic parameters,
display brightness settings, and safe shutdown actions.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen
from core.system_state import NetworkState

class SettingsScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        
        # Grid of settings tiles
        from PyQt5.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(8)
        
        # 1. Communication Config
        card_comm = self._create_info_card(
            "COMMUNICATION CONFIGURATION",
            [
                ("Physical Layer", "RS-485 Half-Duplex (Isolated)"),
                ("Protocol", "Modbus RTU @ 9600 Baud"),
                ("Framing", "8 Data Bits, No Parity, 1 Stop Bit (8N1)"),
                ("Target Node ID", "Slave Address 0x01")
            ]
        )
        grid.addWidget(card_comm, 0, 0)
        
        # 2. Network Info
        self.card_net = self._create_info_card(
            "NETWORK & CONNECTIVITY",
            [
                ("Status", "Connected"),
                ("SSID", "DLP_INDUSTRIAL_WIFI"),
                ("IP Address", "192.168.1.100"),
                ("Hostname", "dlp-pi3a-hmi")
            ]
        )
        grid.addWidget(self.card_net, 0, 1)
        
        # 3. System Diagnostic & Mode
        card_sys = self._create_info_card(
            "SYSTEM DIAGNOSTICS",
            [
                ("Target Platform", "Raspberry Pi 3A+ (ARMv8 64-bit)"),
                ("Display Output", "5.0-inch HDMI TFT (800x480 native)"),
                ("Operating Mode", "SIMULATION ACTIVE (Dev Mode)"),
                ("HMI Software", "v1.1.0 (Production Core)")
            ]
        )
        grid.addWidget(card_sys, 1, 0)
        
        # 4. Display Brightness / Hardware Backlight Control
        card_disp = QFrame()
        card_disp.setStyleSheet("""
            QFrame {
                background-color: #121824;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        d_layout = QVBoxLayout(card_disp)
        d_layout.setContentsMargins(14, 10, 14, 10)
        
        lbl_disp_title = QLabel("DISPLAY BRIGHTNESS")
        lbl_disp_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_disp_title.setStyleSheet("color: #ff7a00; border: none;")
        d_layout.addWidget(lbl_disp_title)
        
        self.lbl_cur_b = QLabel("Current Level: 85 %")
        self.lbl_cur_b.setFont(QFont("Segoe UI", 9))
        self.lbl_cur_b.setStyleSheet("color: #94a3b8; border: none;")
        d_layout.addWidget(self.lbl_cur_b)
        
        b_presets = QHBoxLayout()
        for level in [25, 50, 75, 100]:
            btn_b = QPushButton(f"{level}%")
            btn_b.setFixedHeight(36)
            btn_b.setFont(QFont("Segoe UI", 9, QFont.Bold))
            btn_b.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b; color: #f8fafc;
                    border: 1px solid #334155; border-radius: 4px;
                }
                QPushButton:hover { background-color: #334155; color: #38bdf8; }
            """)
            btn_b.clicked.connect(lambda checked, l=level: self._set_brightness(l))
            b_presets.addWidget(btn_b)
        d_layout.addLayout(b_presets)
        d_layout.addStretch()
        
        grid.addWidget(card_disp, 1, 1)
        self.layout.addLayout(grid)
        
        # Bottom Actions
        act_row = QHBoxLayout()
        act_row.setSpacing(10)
        
        btn_reboot = QPushButton("⟳  RESTART APPLICATION")
        btn_reboot.setFixedHeight(48)
        btn_reboot.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_reboot.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #38bdf8;
                border: 1px solid #334155; border-radius: 6px;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        btn_reboot.clicked.connect(self._restart_app)
        
        btn_exit = QPushButton("✕  CLOSE HMI")
        btn_exit.setFixedHeight(48)
        btn_exit.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15); color: #ef4444;
                border: 1px solid #ef4444; border-radius: 6px;
            }
            QPushButton:hover { background-color: #ef4444; color: #ffffff; }
        """)
        btn_exit.clicked.connect(self._exit_app)
        
        act_row.addWidget(btn_reboot)
        act_row.addWidget(btn_exit)
        self.layout.addLayout(act_row)
        
        if self.controller:
            self.controller.network_updated.connect(self.update_network_info)

    def _create_info_card(self, title, items):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #121824;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(3)
        
        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_t.setStyleSheet("color: #ff7a00; border: none;")
        layout.addWidget(lbl_t)
        
        for k, v in items:
            row = QHBoxLayout()
            lbl_k = QLabel(k)
            lbl_k.setFont(QFont("Segoe UI", 8))
            lbl_k.setStyleSheet("color: #64748b; border: none;")
            
            lbl_v = QLabel(v)
            lbl_v.setFont(QFont("Segoe UI", 8, QFont.Bold))
            lbl_v.setStyleSheet("color: #f8fafc; border: none;")
            lbl_v.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            row.addWidget(lbl_k)
            row.addStretch()
            row.addWidget(lbl_v)
            layout.addLayout(row)
            
        layout.addStretch()
        return frame

    def _set_brightness(self, level):
        self.lbl_cur_b.setText(f"Current Level: {level} %")

    def _restart_app(self):
        # Cleanly trigger restart or reload
        if self.controller:
            self.controller._simulation_tick()

    def _exit_app(self):
        QApplication.quit()

    def update_network_info(self, net: NetworkState):
        pass
