"""
Main Window for DLP KUMAR VFD HMI.
Manages the fixed 800x480 frameless viewport, animated drop-out diagnostics drawer,
fluid screen switching transitions, and wires the HMIController to the UI views.
"""
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from ui.components import Header, NavigationBar, DropoutDrawer
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
        
        # 1. Slide-down Animated Dropout Drawer
        self.drawer = DropoutDrawer(self.controller)
        
        # 2. Header (46px) with close button & drawer trigger
        self.header = Header(
            close_callback=self.close,
            drawer_callback=self.drawer.toggle
        )
        layout.addWidget(self.header)
        layout.addWidget(self.drawer)
        
        # 3. Main Content Stack
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # 4. Bottom Action / Navigation Bar (52px)
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
            
        # Wire controller to header status & drawer telemetry
        self.controller.vfd_updated.connect(
            lambda v: self.header.update_vfd_status(v.online, v.status_text)
        )
        self.controller.vfd_updated.connect(self.drawer.update_telemetry)
        
        self.controller.network_updated.connect(
            lambda n: self.header.update_wifi(n.signal_strength, n.connected)
        )
        self.controller.alarms_updated.connect(
            lambda alms: self.header.update_sys_status(len(alms))
        )
        self.controller.rs485_updated.connect(
            self.header.update_rs485_status
        )
        self.controller.rs485_updated.connect(self.drawer.update_rs485)
        
        self._screen_anim = None
        
        # Start at Dashboard
        self.switch_screen(0)
        
    def switch_screen(self, index: int):
        if 0 <= index < len(self.screens):
            current_screen = self.screens[index]
            self.stacked_widget.setCurrentIndex(index)
            self.header.set_title(self.screen_names[index])
            
            # Smooth screen fade animation
            eff = QGraphicsOpacityEffect(current_screen)
            current_screen.setGraphicsEffect(eff)
            self._screen_anim = QPropertyAnimation(eff, b"opacity")
            self._screen_anim.setDuration(160)
            self._screen_anim.setStartValue(0.3)
            self._screen_anim.setEndValue(1.0)
            self._screen_anim.setEasingCurve(QEasingCurve.OutQuad)
            self._screen_anim.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
