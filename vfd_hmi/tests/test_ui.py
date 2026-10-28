"""
UI Unit Tests for DLP KUMAR VFD HMI.
Validates window geometry, touch targets, screen switching, and controller integration.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

class TestHMIUserInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.window = MainWindow()

    def tearDown(self):
        self.window.controller.sim_timer.stop()
        self.window.close()

    def test_window_resolution(self):
        # Strict requirement: Exactly 800x480 for 5-inch display
        self.assertEqual(self.window.width(), 800)
        self.assertEqual(self.window.height(), 480)

    def test_all_screens_loaded(self):
        self.assertEqual(self.window.stacked_widget.count(), 7)
        self.assertEqual(len(self.window.screen_names), 7)

    def test_screen_navigation(self):
        for idx, name in enumerate(self.window.screen_names):
            self.window.switch_screen(idx)
            self.assertEqual(self.window.stacked_widget.currentIndex(), idx)
            self.assertEqual(self.window.header.title_label.text(), name.upper())

    def test_header_telemetry_binding(self):
        # Trigger controller update
        self.window.controller.start_vfd()
        self.window.controller._simulation_tick()
        self.assertIn("VFD", self.window.header.vfd_pill.text())

if __name__ == "__main__":
    unittest.main()
