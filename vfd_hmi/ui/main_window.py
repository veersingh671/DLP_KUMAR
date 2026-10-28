"""
Main Window for DLP KUMAR VFD HMI.
Manages the fixed 800x480 frameless viewport, screen switching,
and wires the HMIController to the UI views.
"""
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from ui.components import Header, NavigationBar
from ui.dashboard import DashboardScreen
from ui.vfd_screen import VFDScreen
from ui.parameters_screen import ParametersScreen
from ui.sensors_screen import SensorsScreen
from ui.actuators_screen import ActuatorsScreen
from ui.alarms_screen import AlarmsScreen
from ui.settings_screen import SettingsScreen
from core.controller import HMIController

class MainWindow(QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        # Strict 800x480 resolution for 5-inch TFT touch screen
        self.setFixedSize(800, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("DLP KUMAR - Industrial VFD HMI")
        
        # Central Controller
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.controller = controller or HMIController(base_dir=base_dir)
        
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            #CentralWidget {
                background-color: #070a12;
            }
        """)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Header (46px) with close button
        self.header = Header(close_callback=self.close)
        layout.addWidget(self.header)
        
        # 2. Main Content Stack (382px)
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # 3. Bottom Action / Navigation Bar (52px)
        self.nav_bar = NavigationBar(self.switch_screen)
        layout.addWidget(self.nav_bar)
        
        # Instantiate All Screens with Controller
        self.screens = [
            DashboardScreen(self.controller),
            VFDScreen(self.controller),
            ParametersScreen(self.controller),
            SensorsScreen(self.controller),
            ActuatorsScreen(self.controller),
            AlarmsScreen(self.controller),
            SettingsScreen(self.controller)
        ]
        
        self.screen_names = [
            "DASHBOARD",
            "VFD CONTROL",
            "VFD PARAMETERS",
            "SENSORS MONITOR",
            "ACTUATORS CONTROL",
            "ALARMS & EVENTS",
            "SYSTEM SETTINGS"
        ]
        
        for screen in self.screens:
            self.stacked_widget.addWidget(screen)
            
        # Wire controller to header status
        self.controller.vfd_updated.connect(
            lambda v: self.header.update_vfd_status(v.online, v.status_text)
        )
        self.controller.network_updated.connect(
            lambda n: self.header.update_wifi(n.signal_strength, n.connected)
        )
        self.controller.alarms_updated.connect(
            lambda alms: self.header.update_sys_status(len(alms))
        )
        
        # Start at Dashboard
        self.switch_screen(0)
        
    def switch_screen(self, index: int):
        if 0 <= index < len(self.screens):
            self.stacked_widget.setCurrentIndex(index)
            self.header.set_title(self.screen_names[index])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
