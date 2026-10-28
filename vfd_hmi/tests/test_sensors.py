"""
Unit tests for sensor limits and status evaluation.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.controller import HMIController
from core.system_state import SensorItem

class TestSensors(unittest.TestCase):
    def setUp(self):
        from PyQt5.QtWidgets import QApplication
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.controller = HMIController()

    def tearDown(self):
        self.controller.sim_timer.stop()

    def test_sensors_initialization(self):
        self.assertGreaterEqual(len(self.controller.sensors), 5)
        names = [s.name for s in self.controller.sensors]
        self.assertIn("Motor Temperature", names)
        self.assertIn("Supply Line Voltage", names)
        self.assertIn("Motor Current", names)

    def test_sensor_temperature_status(self):
        temp_sensor = self.controller.sensors[0]
        self.assertEqual(temp_sensor.name, "Motor Temperature")
        
        # Normal
        self.controller.vfd.motor_temp = 55.0
        self.controller._simulation_tick()
        self.assertEqual(self.controller.sensors[0].status, "NORMAL")
        
        # Warning (>= 70)
        self.controller.vfd.motor_temp = 72.0
        self.controller._simulation_tick()
        self.assertEqual(self.controller.sensors[0].status, "WARNING")
        
        # Critical (>= 85)
        self.controller.vfd.motor_temp = 88.0
        self.controller._simulation_tick()
        self.assertEqual(self.controller.sensors[0].status, "CRITICAL")

if __name__ == "__main__":
    unittest.main()
