from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QFont

class Header(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Screen Title
        self.title_label = QLabel("DASHBOARD")
        self.title_label.setFont(QFont("Inter", 16, QFont.Bold))
        self.title_label.setStyleSheet("color: #ff6b00;")
        
        # Status
        self.vfd_status = QLabel("VFD: ONLINE")
        self.vfd_status.setStyleSheet("color: #8e8e93; font-weight: bold;")
        
        self.sys_status = QLabel("SYS: OK")
        self.sys_status.setStyleSheet("color: #8e8e93; font-weight: bold;")
        
        self.wifi_status = QLabel("WiFi ████ 82%")
        self.wifi_status.setStyleSheet("color: #8e8e93; font-weight: bold;")
        
        # Clock
        self.time_label = QLabel("00:00:00")
        self.time_label.setFont(QFont("Inter", 12, QFont.Bold))
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.vfd_status)
        layout.addSpacing(20)
        layout.addWidget(self.sys_status)
        layout.addSpacing(20)
        layout.addWidget(self.wifi_status)
        layout.addSpacing(20)
        layout.addWidget(self.time_label)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
    def update_time(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.time_label.setText(current_time)

    def set_title(self, title):
        self.title_label.setText(title.upper())

class NavigationBar(QWidget):
    def __init__(self, switch_callback, parent=None):
        super().__init__(parent)
        self.setFixedHeight(65)
        self.setStyleSheet("background-color: transparent;")
        self.switch_callback = switch_callback
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        self.buttons = []
        nav_items = ["HOME", "VFD", "SENSORS", "ACTUATORS", "ALARMS", "SETTINGS"]
        
        for idx, item in enumerate(nav_items):
            btn = QPushButton(item)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setFont(QFont("Inter", 12, QFont.Bold))
            btn.clicked.connect(lambda checked, index=idx: self.nav_clicked(index))
            layout.addWidget(btn)
            self.buttons.append(btn)
            
        if self.buttons:
            self.buttons[0].setChecked(True)
            
    def nav_clicked(self, index):
        for i, btn in enumerate(self.buttons):
            if i != index:
                btn.setChecked(False)
            else:
                btn.setChecked(True)
        self.switch_callback(index)

class BaseScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
