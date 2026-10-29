"""
Unit tests for Fuji Electric FRENIC-Mini (FRN-C2 Series) RS-485 Modbus RTU communication engine.
Validates CRC-16 Modbus algorithms, S-group commands (S01, S05, S06), M-group monitor registers
(M09, M11, M12, M14, M16), motor parameters (P01, P02, P03), and fault code decoding (OC1, LU, OH1, OL1).
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication.modbus import crc16_modbus, verify_crc, ModbusRTUMaster
from communication.vfd import FujiFrenicMiniDriver, VFDModbusDriver, FRENIC_FAULT_MAP
from communication.io import IOModbusDriver

class TestFujiFrenicMiniRS485(unittest.TestCase):
    def setUp(self):
        self.master = ModbusRTUMaster(port="COM3", baudrate=9600)
        self.master.is_simulation = True
        self.master.is_connected = True
        self.driver = FujiFrenicMiniDriver(self.master, slave_id=1)

    def test_crc16_known_vector(self):
        # Frame payload: 01 03 00 00 00 0A
        # Expected CRC: CD C5 (little-endian b'\xc5\xcd')
        payload = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x0A])
        crc = crc16_modbus(payload)
        self.assertEqual(crc, b'\xc5\xcd')
        self.assertTrue(verify_crc(payload + crc))

    def test_frenic_s06_operation_start_stop(self):
        # Test Forward Start: S06 = 0x0001 (Bit 0)
        ok = self.driver.send_start(direction="FWD")
        self.assertTrue(ok)
        self.assertEqual(self.master.virtual_holding_registers[0x0706], 0x0001)

        # Test Reverse Start: S06 = 0x0002 (Bit 1)
        ok = self.driver.send_start(direction="REV")
        self.assertTrue(ok)
        self.assertEqual(self.master.virtual_holding_registers[0x0706], 0x0002)

        # Test Stop: S06 = 0x0000
        ok = self.driver.send_stop()
        self.assertTrue(ok)
        self.assertEqual(self.master.virtual_holding_registers[0x0706], 0x0000)

    def test_frenic_s05_frequency_reference(self):
        # 50.00 Hz on S05 -> 5000 (0.01 Hz units)
        ok = self.driver.send_frequency(50.0)
        self.assertTrue(ok)
        self.assertEqual(self.master.virtual_holding_registers[0x0705], 5000)
        # S01 relative frequency must be cleared (0) to ensure S05 priority
        self.assertEqual(self.master.virtual_holding_registers[0x0701], 0)

        # 25.50 Hz on S05 -> 2550
        ok = self.driver.send_frequency(25.5)
        self.assertTrue(ok)
        self.assertEqual(self.master.virtual_holding_registers[0x0705], 2550)

    def test_frenic_s06_fault_reset_pulse(self):
        # Set alarm active in virtual registers
        self.master.virtual_holding_registers[0x0810] = 1       # OC1 active
        self.master.virtual_holding_registers[0x080E] |= 0x0080  # ALM bit 7 active

        ok = self.driver.send_fault_reset()
        self.assertTrue(ok)
        # Alarm code in M16 should be cleared
        self.assertEqual(self.master.virtual_holding_registers[0x0810], 0)
        # ALM bit 7 in M14 should be cleared
        self.assertFalse(bool(self.master.virtual_holding_registers[0x080E] & 0x0080))

    def test_frenic_telemetry_polling_and_status_decoding(self):
        # Simulate active running motor at 45.00 Hz, 6.20 A, 380 V
        self.master.virtual_holding_registers[0x0809] = 4500     # M09: 45.00 Hz
        self.master.virtual_holding_registers[0x080B] = 620      # M11: 6.20 A
        self.master.virtual_holding_registers[0x080C] = 3800     # M12: 380.0 V
        self.master.virtual_holding_registers[0x080E] = 0x1005   # M14: RL (0x1000) + RUN (0x0004) + FWD (0x0001)
        self.master.virtual_holding_registers[0x0810] = 0        # M16: No fault

        telemetry = self.driver.poll_telemetry()
        self.assertIsNotNone(telemetry)
        self.assertTrue(telemetry["running"])
        self.assertEqual(telemetry["direction"], "FWD")
        self.assertEqual(telemetry["actual_frequency"], 45.0)
        self.assertEqual(telemetry["output_current"], 6.20)
        self.assertEqual(telemetry["output_voltage"], 380.0)
        self.assertEqual(telemetry["status_text"], "RUNNING")
        self.assertIsNone(telemetry["fault_code"])

    def test_frenic_alarm_code_mapping(self):
        # Simulate Overcurrent trip during acceleration (Code 1 = OC1)
        self.master.virtual_holding_registers[0x080E] = 0x1080   # ALM bit active
        self.master.virtual_holding_registers[0x0810] = 1        # Code 1 = OC1

        telemetry = self.driver.poll_telemetry()
        self.assertIsNotNone(telemetry)
        self.assertEqual(telemetry["fault_code"], "FUJI-OC1")
        self.assertIn("Overcurrent", telemetry["fault_desc"])
        self.assertIn("F07", telemetry["fault_remedy"])

        # Check Undervoltage (Code 10 = LU)
        self.master.virtual_holding_registers[0x0810] = 10
        telemetry = self.driver.poll_telemetry()
        self.assertEqual(telemetry["fault_code"], "FUJI-LU")

        # Check Motor Overload (Code 14 = OL1)
        self.master.virtual_holding_registers[0x0810] = 14
        telemetry = self.driver.poll_telemetry()
        self.assertEqual(telemetry["fault_code"], "FUJI-OL1")

    def test_motor_pole_synchronous_speed_calculation(self):
        # 4-pole motor: Ns = 120 * 50 / 4 = 1500 RPM, with ~3.5% slip = ~1447 RPM
        self.driver.motor_poles = 4
        self.master.virtual_holding_registers[0x0809] = 5000  # 50.00 Hz
        self.master.virtual_holding_registers[0x080E] = 0x1005  # RUN
        telemetry = self.driver.poll_telemetry()
        self.assertGreater(telemetry["motor_speed"], 1400)
        self.assertLessEqual(telemetry["motor_speed"], 1500)

        # 2-pole motor: Ns = 120 * 50 / 2 = 3000 RPM, with ~3.5% slip = ~2895 RPM
        self.driver.motor_poles = 2
        telemetry = self.driver.poll_telemetry()
        self.assertGreater(telemetry["motor_speed"], 2800)
        self.assertLessEqual(telemetry["motor_speed"], 3000)

    def test_frenic_motor_parameter_write(self):
        # Write F03 Maximum Frequency = 60.0 Hz (Register 0x0003, scale10 -> 600)
        ok = self.driver.write_parameter(0x0003, 60.0, data_type="scale10")
        self.assertTrue(ok)
        self.assertEqual(self.master.virtual_holding_registers[0x0003], 600)

        # Write P01 Motor Poles = 4 (Register 0x0301, int -> 4)
        ok = self.driver.write_parameter(0x0301, 4, data_type="int")
        self.assertTrue(ok)
        self.assertEqual(self.master.virtual_holding_registers[0x0301], 4)

    def test_legacy_holding_registers_backward_compatibility(self):
        # Write to legacy holding register 0x2001
        ok = self.master.write_single_register(slave_id=1, address=0x2001, value=4850)
        self.assertTrue(ok)
        regs = self.master.read_holding_registers(slave_id=1, address=0x2001, count=1)
        self.assertEqual(regs[0], 4850)

    def test_motor_analytical_calculations(self):
        # Synchronous speed formula: N = 120 * f / P
        self.assertEqual(FujiFrenicMiniDriver.calculate_sync_rpm(50.0, 4), 1500)
        self.assertEqual(FujiFrenicMiniDriver.calculate_sync_rpm(60.0, 4), 1800)
        self.assertEqual(FujiFrenicMiniDriver.calculate_sync_rpm(50.0, 2), 3000)
        self.assertEqual(FujiFrenicMiniDriver.calculate_sync_rpm(50.0, 6), 1000)

        # Shaft torque formula: T = (9550 * P_kW) / RPM
        t_nm = FujiFrenicMiniDriver.calculate_motor_torque_nm(3.7, 1450)
        self.assertAlmostEqual(t_nm, 24.37, delta=0.1)

        # Thermal overload at nominal frequency (50Hz) and nominal current (7.5A)
        th_50 = FujiFrenicMiniDriver.calculate_thermal_load_pct(7.5, 7.5, 50.0)
        self.assertEqual(th_50, 100.0)

        # Thermal overload at low frequency (10Hz) with reduced self-cooling
        th_10 = FujiFrenicMiniDriver.calculate_thermal_load_pct(7.5, 7.5, 10.0)
        self.assertGreater(th_10, 100.0)

    def test_frenic_jog_and_emergency_stop(self):
        # Test JOG command
        ok = self.driver.send_jog(direction="REV", jog_freq=5.0)
        self.assertTrue(ok)
        self.assertEqual(self.master.virtual_holding_registers[0x0705], 500)   # 5.00 Hz
        self.assertEqual(self.master.virtual_holding_registers[0x0706], 0x0002) # REV

        # Test Emergency Stop command
        ok = self.driver.send_emergency_stop()
        self.assertTrue(ok)
        self.assertEqual(self.master.virtual_holding_registers[0x0705], 0)      # 0.00 Hz
        self.assertEqual(self.master.virtual_holding_registers[0x0706], 0x0000) # STOP

    def test_frenic_fault_history_reading(self):
        # Simulate trip history: M16=1 (OC1), M17=10 (LU), M18=11 (OH1), M19=14 (OL1)
        self.master.virtual_holding_registers[0x0810] = 1   # Latest
        self.master.virtual_holding_registers[0x0811] = 10  # 1 trip ago
        self.master.virtual_holding_registers[0x0812] = 11  # 2 trips ago
        self.master.virtual_holding_registers[0x0813] = 14  # 3 trips ago

        history = self.driver.read_fault_history()
        self.assertEqual(len(history), 4)
        self.assertEqual(history[0]["code"], "FUJI-OC1")
        self.assertEqual(history[1]["code"], "FUJI-LU")
        self.assertEqual(history[2]["code"], "FUJI-OH1")
        self.assertEqual(history[3]["code"], "FUJI-OL1")

    def test_io_relay_coils(self):
        io_drv = IOModbusDriver(self.master, slave_id=2)
        ok = io_drv.set_relay(channel=1, state=True)
        self.assertTrue(ok)
        relays = io_drv.read_relays(count=4)
        self.assertIsNotNone(relays)
        self.assertTrue(relays[1])

if __name__ == "__main__":
    unittest.main()
