"""
Unit tests for VFD controller and physics simulation logic.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.controller import HMIController
from core.system_state import VFDState

class TestVFDController(unittest.TestCase):
    def setUp(self):
        from PyQt5.QtWidgets import QApplication
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.controller = HMIController()

    def tearDown(self):
        self.controller.sim_timer.stop()

    def test_vfd_start_stop(self):
        # Initial state should be stopped
        self.assertFalse(self.controller.vfd.running)
        
        # Start command
        ok, msg = self.controller.start_vfd()
        self.assertTrue(ok)
        self.assertTrue(self.controller.vfd.running)
        
        # Stop command
        ok, msg = self.controller.stop_vfd()
        self.assertTrue(ok)
        self.assertFalse(self.controller.vfd.running)

    def test_frequency_clamping(self):
        # P01 max is 50.0Hz, P02 min is 0.0Hz
        res = self.controller.set_frequency(75.0)
        self.assertEqual(res, 50.0)
        
        res = self.controller.set_frequency(-10.0)
        self.assertEqual(res, 0.0)
        
        res = self.controller.set_frequency(35.5)
        self.assertEqual(res, 35.5)

    def test_direction_toggle(self):
        self.assertEqual(self.controller.vfd.direction, "FWD")
        self.controller.toggle_direction()
        self.assertEqual(self.controller.vfd.direction, "REV")
        self.controller.toggle_direction()
        self.assertEqual(self.controller.vfd.direction, "FWD")

    def test_simulation_ramp(self):
        self.controller.set_frequency(50.0)
        self.controller.start_vfd()
        
        # Execute several simulation ticks
        for _ in range(10):
            self.controller._simulation_tick()
            
        # Frequency should have accelerated above 0
        self.assertGreater(self.controller.vfd.actual_frequency, 0.0)
        self.assertGreater(self.controller.vfd.motor_speed, 0)
        self.assertGreater(self.controller.vfd.output_current, 0.0)

    def test_fault_trip_and_reset(self):
        self.controller.trigger_test_alarm("ERR-010", "Inverter Overheat", "CRITICAL")
        self.assertEqual(self.controller.vfd.fault_code, "ERR-010")
        self.assertFalse(self.controller.vfd.running)
        
        # Starting with active fault should fail
        ok, _ = self.controller.start_vfd()
        self.assertFalse(ok)
        
        # Reset fault
        self.controller.reset_fault()
        self.assertIsNone(self.controller.vfd.fault_code)
        ok, _ = self.controller.start_vfd()
        self.assertTrue(ok)

if __name__ == "__main__":
    unittest.main()
