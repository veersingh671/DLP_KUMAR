"""
RS-485 Digital & Analog I/O Module Driver for DLP KUMAR VFD HMI.
Manages communication with remote RS-485 I/O expansion modules
(e.g., 8-channel relay output boards and 4-20mA / 0-10V analog input cards).
"""
from typing import List, Optional
from communication.modbus import ModbusRTUMaster

class IOModbusDriver:
    """
    Driver for RS-485 remote I/O modules:
    Coils 0x0000 - 0x0007: Digital Relay Outputs (Actuators)
    Input Regs 0x3000 - 0x3004: Analog Sensor Inputs (Sensors)
    """
    def __init__(self, master: ModbusRTUMaster, slave_id: int = 2):
        self.master = master
        self.slave_id = slave_id

    def set_relay(self, channel: int, state: bool) -> bool:
        """Sets relay coil output state (0-based channel index)."""
        return self.master.write_single_coil(self.slave_id, channel, state)

    def read_relays(self, count: int = 8) -> Optional[List[bool]]:
        """Reads status of digital relay coils."""
        return self.master.read_coils(self.slave_id, 0, count)

    def read_analog_inputs(self, count: int = 5) -> Optional[List[int]]:
        """Reads analog sensor input registers."""
        return self.master.read_holding_registers(self.slave_id, 0x3000, count)
