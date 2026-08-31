from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt
from ui.components import Header, NavigationBar
from ui.dashboard import DashboardScreen
from ui.vfd_screen import VFDScreen
from ui.sensors_screen import SensorsScreen
from ui.actuators_screen import ActuatorsScreen
from ui.alarms_screen import AlarmsScreen
from ui.settings_screen import SettingsScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.header = Header()
        self.stacked_widget = QStackedWidget()
        self.nav_bar = NavigationBar(self.switch_screen)
        
        layout.addWidget(self.header)
        layout.addWidget(self.stacked_widget)
        layout.addWidget(self.nav_bar)
        
        self.screens = [
            DashboardScreen(),
            VFDScreen(),
            SensorsScreen(),
            ActuatorsScreen(),
            AlarmsScreen(),
            SettingsScreen()
        ]
        
        self.screen_names = [
            "DASHBOARD",
            "VFD CONTROL",
            "SENSORS",
            "ACTUATORS",
            "ALARMS",
            "SETTINGS"
        ]
        
        for screen in self.screens:
            self.stacked_widget.addWidget(screen)
            
        self.switch_screen(0)
        
    def switch_screen(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.header.set_title(self.screen_names[index])
