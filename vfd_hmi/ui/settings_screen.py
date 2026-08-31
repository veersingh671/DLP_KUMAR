from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.components import BaseScreen

class SettingsScreen(BaseScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        settings_items = [
            ("VFD COMMUNICATION", "Modbus RTU / 9600 / 8N1"),
            ("NETWORK", "WiFi Connected: DLP_NETWORK"),
            ("DISPLAY", "Brightness: 80%"),
            ("SYSTEM", "Version 1.0.0")
        ]
        
        for title, desc in settings_items:
            frame = QFrame()
            frame.setStyleSheet("background-color: #333; border-radius: 5px;")
            frame.setFixedHeight(70)
            
            f_layout = QVBoxLayout(frame)
            f_layout.setContentsMargins(10, 5, 10, 5)
            
            lbl_title = QLabel(title)
            lbl_title.setFont(QFont("Arial", 12, QFont.Bold))
            lbl_title.setStyleSheet("color: #007acc;")
            
            lbl_desc = QLabel(desc)
            lbl_desc.setFont(QFont("Arial", 12))
            
            f_layout.addWidget(lbl_title)
            f_layout.addWidget(lbl_desc)
            
            self.layout.addWidget(frame)
            
        self.layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_reboot = QPushButton("REBOOT SYSTEM")
        btn_reboot.setStyleSheet("background-color: #f44336; color: white;")
        btn_reboot.setFixedHeight(50)
        
        btn_exit = QPushButton("EXIT APP")
        btn_exit.setFixedHeight(50)
        btn_exit.clicked.connect(self.exit_app)
        
        btn_layout.addWidget(btn_reboot)
        btn_layout.addWidget(btn_exit)
        self.layout.addLayout(btn_layout)
        
    def exit_app(self):
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()
