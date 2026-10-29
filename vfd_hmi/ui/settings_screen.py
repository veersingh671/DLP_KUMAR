"""
Settings and RS-485 Diagnostics Screen for DLP KUMAR VFD HMI.
ISA-101 Industrial Serial Bus Diagnostic Suite for Fuji FRENIC-Mini C2.
Provides serial port configuration, baud rate selection, live packet sniffer,
CRC validation counters, and system controls.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QComboBox, QSpinBox, QApplication, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen

class SettingsScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        
        # Connect to controller RS-485 updates
        if self.controller:
            self.controller.rs485_updated.connect(self._on_rs485_updated)
            
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(4, 2, 4, 2)
        main_layout.setSpacing(8)
        
        # =====================================================================
        # LEFT PANEL: RS-485 Bus Configuration & Live Traffic Sniffer
        # =====================================================================
        left_card = QFrame()
        left_card.setStyleSheet("""
            QFrame {
                background-color: #131923;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(12, 8, 12, 8)
        left_layout.setSpacing(6)
        
        lbl_rs_title = QLabel("FUJI FRENIC-Mini (C2) RS-485 MODBUS")
        lbl_rs_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_rs_title.setStyleSheet("color: #cbd5e1; border: none;")
        left_layout.addWidget(lbl_rs_title)
        
        # Row 1: COM Port selector + Refresh
        row_port = QHBoxLayout()
        row_port.setSpacing(6)
        lbl_p = QLabel("Serial Port:")
        lbl_p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_p.setStyleSheet("color: #94a3b8; border: none; min-width: 75px;")
        
        self.combo_ports = QComboBox()
        self.combo_ports.setFixedHeight(28)
        self.combo_ports.setStyleSheet("""
            QComboBox {
                background-color: #1e293b; color: #f1f5f9;
                border: 1px solid #334155; border-radius: 4px; padding: 2px 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e293b; color: #f1f5f9;
                selection-background-color: #2563eb;
            }
        """)
        
        btn_scan = QPushButton("↻ SCAN")
        btn_scan.setFixedSize(65, 28)
        btn_scan.setFont(QFont("Segoe UI", 8, QFont.Bold))
        btn_scan.setCursor(Qt.PointingHandCursor)
        btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #cbd5e1;
                border: 1px solid #334155; border-radius: 4px;
            }
            QPushButton:hover { background-color: #2563eb; color: #ffffff; border: 1px solid #3b82f6; }
        """)
        btn_scan.clicked.connect(self._scan_ports)
        
        row_port.addWidget(lbl_p)
        row_port.addWidget(self.combo_ports, 1)
        row_port.addWidget(btn_scan)
        left_layout.addLayout(row_port)
        
        # Row 2: Baud Rate & Parity
        row_params = QHBoxLayout()
        row_params.setSpacing(6)
        
        lbl_b = QLabel("Baud Rate:")
        lbl_b.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_b.setStyleSheet("color: #94a3b8; border: none;")
        
        self.combo_baud = QComboBox()
        self.combo_baud.setFixedHeight(28)
        self.combo_baud.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.combo_baud.setStyleSheet("""
            QComboBox {
                background-color: #1e293b; color: #f1f5f9;
                border: 1px solid #334155; border-radius: 4px; padding: 2px 6px;
            }
        """)
        
        lbl_parity = QLabel("Parity:")
        lbl_parity.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_parity.setStyleSheet("color: #94a3b8; border: none;")
        
        self.combo_parity = QComboBox()
        self.combo_parity.setFixedHeight(28)
        self.combo_parity.addItems(["None (8N1)", "Even (8E1)", "Odd (8O1)"])
        self.combo_parity.setStyleSheet("""
            QComboBox {
                background-color: #1e293b; color: #f1f5f9;
                border: 1px solid #334155; border-radius: 4px; padding: 2px 6px;
            }
        """)
        
        row_params.addWidget(lbl_b)
        row_params.addWidget(self.combo_baud, 1)
        row_params.addWidget(lbl_parity)
        row_params.addWidget(self.combo_parity, 1)
        left_layout.addLayout(row_params)
        
        # Row 3: Slave Node ID & Action Buttons
        row_actions = QHBoxLayout()
        row_actions.setSpacing(6)
        
        lbl_slave = QLabel("Slave ID:")
        lbl_slave.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_slave.setStyleSheet("color: #94a3b8; border: none;")
        
        self.spin_slave = QSpinBox()
        self.spin_slave.setRange(1, 247)
        self.spin_slave.setValue(1)
        self.spin_slave.setFixedHeight(28)
        self.spin_slave.setFixedWidth(55)
        self.spin_slave.setStyleSheet("""
            QSpinBox {
                background-color: #1e293b; color: #f1f5f9;
                border: 1px solid #334155; border-radius: 4px; padding: 2px 4px;
            }
        """)
        
        self.btn_apply = QPushButton("CONNECT")
        self.btn_apply.setFixedHeight(28)
        self.btn_apply.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #15803d; color: #ffffff;
                border: 1px solid #16a34a; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #16a34a; }
        """)
        self.btn_apply.clicked.connect(self._apply_rs485)
        
        self.btn_mode = QPushButton("SIMULATION: ON")
        self.btn_mode.setFixedHeight(28)
        self.btn_mode.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.btn_mode.setCursor(Qt.PointingHandCursor)
        self.btn_mode.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #cbd5e1;
                border: 1px solid #334155; border-radius: 4px;
            }
            QPushButton:hover { background-color: #334155; color: #ffffff; }
        """)
        self.btn_mode.clicked.connect(self._toggle_mode)
        
        row_actions.addWidget(lbl_slave)
        row_actions.addWidget(self.spin_slave)
        row_actions.addWidget(self.btn_apply, 1)
        row_actions.addWidget(self.btn_mode, 1)
        left_layout.addLayout(row_actions)
        
        # RS-485 Hex Packet Sniffer Frame
        sniffer_frame = QFrame()
        sniffer_frame.setStyleSheet("""
            QFrame {
                background-color: #090d13;
                border: 1px solid #1e293b;
                border-radius: 5px;
            }
        """)
        sn_layout = QVBoxLayout(sniffer_frame)
        sn_layout.setContentsMargins(8, 6, 8, 6)
        sn_layout.setSpacing(3)
        
        sn_header = QHBoxLayout()
        lbl_sn = QLabel("LIVE MODBUS TRAFFIC MONITOR")
        lbl_sn.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_sn.setStyleSheet("color: #64748b; border: none;")
        
        self.lbl_packet_stats = QLabel("TX: 0 | RX: 0 | CRC ERR: 0")
        self.lbl_packet_stats.setFont(QFont("Consolas", 8, QFont.Bold))
        self.lbl_packet_stats.setStyleSheet("color: #10b981; border: none;")
        
        sn_header.addWidget(lbl_sn)
        sn_header.addStretch()
        sn_header.addWidget(self.lbl_packet_stats)
        sn_layout.addLayout(sn_header)
        
        self.lbl_tx_hex = QLabel("TX: [WAITING FOR TRANSMISSION]")
        self.lbl_tx_hex.setFont(QFont("Consolas", 8))
        self.lbl_tx_hex.setStyleSheet("color: #cbd5e1; border: none;")
        sn_layout.addWidget(self.lbl_tx_hex)
        
        self.lbl_rx_hex = QLabel("RX: [WAITING FOR RESPONSE]")
        self.lbl_rx_hex.setFont(QFont("Consolas", 8))
        self.lbl_rx_hex.setStyleSheet("color: #10b981; border: none;")
        sn_layout.addWidget(self.lbl_rx_hex)
        
        row_ping = QHBoxLayout()
        self.lbl_last_err = QLabel("Bus Status: READY")
        self.lbl_last_err.setFont(QFont("Segoe UI", 7))
        self.lbl_last_err.setStyleSheet("color: #64748b; border: none;")
        
        btn_ping = QPushButton("PING BUS")
        btn_ping.setFixedSize(80, 24)
        btn_ping.setFont(QFont("Segoe UI", 8, QFont.Bold))
        btn_ping.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #cbd5e1;
                border: 1px solid #334155; border-radius: 4px;
            }
            QPushButton:hover { background-color: #2563eb; color: #ffffff; border: 1px solid #3b82f6; }
        """)
        btn_ping.clicked.connect(self._ping_bus)
        
        row_ping.addWidget(self.lbl_last_err, 1)
        row_ping.addWidget(btn_ping)
        sn_layout.addLayout(row_ping)
        
        left_layout.addWidget(sniffer_frame)
        main_layout.addWidget(left_card, 55)
        
        # =====================================================================
        # RIGHT PANEL: System Diagnostics, Brightness & Actions
        # =====================================================================
        right_card = QFrame()
        right_card.setStyleSheet("""
            QFrame {
                background-color: #131923;
                border: 1px solid #1e293b;
                border-radius: 6px;
            }
        """)
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(12, 8, 12, 8)
        right_layout.setSpacing(6)
        
        lbl_sys_title = QLabel("SYSTEM & DISPLAY CONTROL")
        lbl_sys_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_sys_title.setStyleSheet("color: #cbd5e1; border: none;")
        right_layout.addWidget(lbl_sys_title)
        
        # Hardware Info Grid
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame { background-color: #090d13; border: 1px solid #1e293b; border-radius: 5px; }
        """)
        inf_layout = QGridLayout(info_frame)
        inf_layout.setContentsMargins(8, 6, 8, 6)
        inf_layout.setSpacing(3)
        
        def _add_kv(grid, r, k, v):
            lk = QLabel(k)
            lk.setFont(QFont("Segoe UI", 7, QFont.Bold))
            lk.setStyleSheet("color: #64748b; border: none;")
            lv = QLabel(v)
            lv.setFont(QFont("Consolas", 7))
            lv.setStyleSheet("color: #f1f5f9; border: none;")
            grid.addWidget(lk, r, 0)
            grid.addWidget(lv, r, 1)
            
        _add_kv(inf_layout, 0, "Target Drive:", "Fuji FRENIC-Mini (FRN-C2)")
        _add_kv(inf_layout, 1, "RS-485 Port:", "Modbus RTU (Pins 4 DX+ / 5 DX-)")
        _add_kv(inf_layout, 2, "Cmd Registers:", "S06 (0x0706) / S05 (0x0705)")
        _add_kv(inf_layout, 3, "Mon Registers:", "M09, M11, M12, M13, M14, M16")
        _add_kv(inf_layout, 4, "Link Setting:", "H30=3 (RS-485 Run & Freq priority)")
        right_layout.addWidget(info_frame)
        
        # Brightness Selector
        lbl_b_title = QLabel("DISPLAY BRIGHTNESS")
        lbl_b_title.setFont(QFont("Segoe UI", 7, QFont.Bold))
        lbl_b_title.setStyleSheet("color: #64748b; border: none; margin-top: 2px;")
        right_layout.addWidget(lbl_b_title)
        
        b_presets = QHBoxLayout()
        b_presets.setSpacing(6)
        for level in [25, 50, 75, 100]:
            btn_b = QPushButton(f"{level}%")
            btn_b.setFixedHeight(26)
            btn_b.setFont(QFont("Consolas", 8, QFont.Bold))
            btn_b.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b; color: #cbd5e1;
                    border: 1px solid #334155; border-radius: 4px;
                }
                QPushButton:hover { background-color: #2563eb; color: #ffffff; border: 1px solid #3b82f6; }
            """)
            btn_b.clicked.connect(lambda ch, l=level: self._set_brightness(l))
            b_presets.addWidget(btn_b)
        right_layout.addLayout(b_presets)
        
        right_layout.addStretch()
        
        # App Exit Button
        btn_exit = QPushButton("✕  CLOSE HMI APPLICATION")
        btn_exit.setFixedHeight(34)
        btn_exit.setFont(QFont("Segoe UI", 8, QFont.Bold))
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #fca5a5;
                border: 1px solid #991b1b; border-radius: 4px;
            }
            QPushButton:hover { background-color: #991b1b; color: #ffffff; }
        """)
        btn_exit.clicked.connect(QApplication.quit)
        right_layout.addWidget(btn_exit)
        
        main_layout.addWidget(right_card, 45)
        self.layout.addLayout(main_layout)
        
        self._scan_ports()

    def _scan_ports(self):
        self.combo_ports.clear()
        if self.controller:
            ports = self.controller.get_available_serial_ports()
            for p in ports:
                self.combo_ports.addItem(f"{p['device']} ({p['description']})", p['device'])
        
        self.combo_ports.addItem("Virtual Loopback Bus (Simulation)", "VIRTUAL")
        
        if self.controller:
            current_port = self.controller.modbus.port_name
            for i in range(self.combo_ports.count()):
                if self.combo_ports.itemData(i) == current_port:
                    self.combo_ports.setCurrentIndex(i)
                    break

    def _apply_rs485(self):
        port = self.combo_ports.currentData() or "COM3"
        baud = int(self.combo_baud.currentText())
        parity_txt = self.combo_parity.currentText()
        parity = "N" if "None" in parity_txt else ("E" if "Even" in parity_txt else "O")
        slave_id = self.spin_slave.value()
        
        if self.controller:
            success = self.controller.reconfigure_rs485(port, baud, parity, slave_id)
            if success:
                self.btn_apply.setText("CONNECTED")
                self.btn_apply.setStyleSheet("""
                    QPushButton { background-color: #15803d; color: #ffffff; border: 1px solid #16a34a; border-radius: 4px; }
                """)
            else:
                self.btn_apply.setText("RETRY")
                self.btn_apply.setStyleSheet("""
                    QPushButton { background-color: #b91c1c; color: #ffffff; border: 1px solid #dc2626; border-radius: 4px; }
                """)

    def _toggle_mode(self):
        if not self.controller:
            return
        current_sim = self.controller.modbus.is_simulation
        new_sim = not current_sim
        self.controller.toggle_simulation_mode(new_sim)
        
        if new_sim:
            self.btn_mode.setText("SIMULATION: ON")
            self.btn_mode.setStyleSheet("""
                QPushButton { background-color: #1e293b; color: #cbd5e1; border: 1px solid #334155; border-radius: 4px; }
            """)
        else:
            self.btn_mode.setText("PHYSICAL BUS: ACTIVE")
            self.btn_mode.setStyleSheet("""
                QPushButton { background-color: #15803d; color: #ffffff; border: 1px solid #16a34a; border-radius: 4px; }
            """)

    def _ping_bus(self):
        if self.controller:
            res = self.controller.send_test_modbus_ping()
            stat = res.get("poll_result", "UNKNOWN")
            self.lbl_last_err.setText(f"Ping: {stat}")
            self.lbl_last_err.setStyleSheet("color: #10b981;" if "SUCCESS" in stat else "color: #ef4444;")

    def _set_brightness(self, level: int):
        pass

    def _on_rs485_updated(self, diag: dict):
        tx = diag.get("tx_count", 0)
        rx = diag.get("rx_count", 0)
        crc = diag.get("crc_errors", 0)
        last_tx = diag.get("last_tx_hex", "NONE")
        last_rx = diag.get("last_rx_hex", "NONE")
        
        self.lbl_packet_stats.setText(f"TX: {tx} | RX: {rx} | CRC ERR: {crc}")
        self.lbl_packet_stats.setStyleSheet("color: #10b981;" if crc == 0 else "color: #ef4444;")
        
        self.lbl_tx_hex.setText(f"TX: [{last_tx}]")
        self.lbl_rx_hex.setText(f"RX: [{last_rx}]")
