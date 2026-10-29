"""
Industrial Modbus RTU / RS-485 Protocol Engine for DLP KUMAR VFD HMI.
Provides pure-Python CRC16 Modbus computation, frame packing/unpacking,
serial bus management, port enumeration, and virtual drive loopback simulation.
"""
import time
import struct
import threading
from typing import List, Optional, Tuple, Dict, Any

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


def crc16_modbus(data: bytes) -> bytes:
    """
    Computes 16-bit Modbus CRC (Polynomial: 0xA001, Init: 0xFFFF).
    Returns 2 bytes in Little-Endian order (LSB first, MSB second).
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack("<H", crc)


def verify_crc(frame: bytes) -> bool:
    """Verifies if the trailing 2 bytes of the frame match the calculated CRC16."""
    if len(frame) < 3:
        return False
    payload = frame[:-2]
    expected_crc = frame[-2:]
    return crc16_modbus(payload) == expected_crc


class ModbusException(Exception):
    """Base Modbus Protocol Exception."""
    pass


class ModbusRTUMaster:
    """
    Industrial RS-485 Modbus RTU Master.
    Handles frame generation, serial communication, CRC validation,
    and automatic virtual simulation fallback if no hardware port is available.
    """
    def __init__(self, port: str = "COM3", baudrate: int = 9600, parity: str = "N",
                 databits: int = 8, stopbits: int = 1, timeout: float = 0.5):
        self.port_name = port
        self.baudrate = baudrate
        self.parity = parity.upper()
        self.databits = databits
        self.stopbits = stopbits
        self.timeout = timeout
        
        self.serial_port: Optional[Any] = None
        self.is_connected = False
        self.is_simulation = True
        self.lock = threading.Lock()
        
        # Diagnostics & Traffic metrics
        self.tx_count = 0
        self.rx_count = 0
        self.crc_errors = 0
        self.timeouts = 0
        self.last_tx_hex = ""
        self.last_rx_hex = ""
        self.last_error = ""

        # Virtual simulated drive memory map (when physical RS-485 is not plugged in)
        # Includes exact Fuji Electric FRENIC-Mini (C2 Series) register mapping
        self.virtual_holding_registers: Dict[int, int] = {
            # --- Fuji FRENIC-Mini Command Registers (Group S: 0x07) ---
            0x0701: 0,       # S01: Frequency ratio command (0 allows S05)
            0x0705: 4500,    # S05: Frequency Reference (0.01 Hz) = 45.00 Hz
            0x0706: 0x0000,  # S06: Operation Command (Bit 0=FWD, Bit 1=REV, Bit 15=RST)
            
            # --- Fuji FRENIC-Mini Monitor Registers (Group M: 0x08) ---
            0x0809: 0,       # M09: Output Frequency (0.01 Hz)
            0x080A: 0,       # M10: Calculated Torque (%)
            0x080B: 0,       # M11: Output Current (0.01 A)
            0x080C: 0,       # M12: Output Voltage (0.1 V)
            0x080D: 0,       # M13: Calculated Motor Torque (0.1%)
            0x080E: 0x1000,  # M14: Status Word (Bit 0=FWD, 1=REV, 2=RUN, 7=ALM, 12=RL)
            0x0810: 0,       # M16: Latest Alarm Code (1=OC1, 10=LU, 11=OH1, 14=OL1)
            0x081A: 380,     # M26: Heat Sink Temp (0.1 °C) = 38.0 °C
            0x082C: 0,       # M44: Motor Speed (RPM)
            
            # --- Fuji FRENIC-Mini Fundamental Parameters (Group F: 0x00) ---
            0x0001: 3,       # F01: Frequency source (3 = RS-485)
            0x0002: 2,       # F02: Operation source (2 = RS-485)
            0x0003: 500,     # F03: Maximum Frequency (0.1 Hz) = 50.0 Hz
            0x0004: 500,     # F04: Base Frequency (0.1 Hz) = 50.0 Hz
            0x0005: 380,     # F05: Rated Voltage (1 V) = 380 V
            0x0007: 50,      # F07: Accel Time 1 (0.1 s) = 5.0 s
            0x0008: 50,      # F08: Decel Time 1 (0.1 s) = 5.0 s
            0x0009: 750,     # F09: Motor 1 Thermal Overload (0.01 A) = 7.50 A
            0x0010: 0,       # F16: Low Frequency Limiter (0.1 Hz) = 0.0 Hz
            0x001A: 40,      # F26: Carrier Frequency (0.1 kHz) = 4.0 kHz
            
            # --- Fuji FRENIC-Mini Motor Parameters (Group P: 0x03) ---
            0x0301: 4,       # P01: Motor Poles (4 poles)
            0x0302: 370,     # P02: Motor Capacity (0.01 kW) = 3.7 kW
            0x0303: 750,     # P03: Motor Rated Current (0.01 A) = 7.50 A
            0x0306: 15,      # P06: Slip Compensation (0.1 Hz) = 1.5 Hz
            
            # --- Fuji FRENIC-Mini Communication Settings (Group y: 0x0F Standard & 0x13 Aliases) ---
            0x041E: 3,       # H30: Link Function Priority (3 = RS-485 Run + Freq)
            0x0F01: 1,       # y01: Station Address = 1
            0x0F03: 2,       # y03: Baud Rate (2 = 9600 bps)
            0x0F04: 2,       # y04: Baud Rate (2 = 9600 bps)
            0x0F06: 3,       # y06: Parity (3 = 8N1)
            0x0F0A: 0,       # y10: Protocol (0 = Modbus RTU)
            0x0F61: 1,       # y97: Data Save Mode (1 = RAM to protect EEPROM)
            # Legacy/Alternate Aliases
            0x1301: 1,       # y01 alias
            0x1303: 2,       # y03 alias
            0x1304: 3,       # y04 alias
            0x130A: 0,       # y10 alias
            0x1361: 1,       # y97 alias
            
            # --- Legacy / Standard Modbus Holding Registers Aliases ---
            0x2000: 0x0000,  # Control word
            0x2001: 4500,    # Target Freq
            0x2002: 50,      # Accel time
            0x2003: 50,      # Decel time
            0x2100: 0x0000,  # Status word
            0x2101: 0,       # Actual Freq
            0x2102: 0,       # Actual Current
            0x2103: 0,       # Output Voltage
            0x2104: 5400,    # DC Bus Voltage
            0x2105: 0,       # Motor RPM
            0x2106: 380,     # Inverter Temperature
            0x2107: 0,       # Fault Code
        }
        self.virtual_coils: Dict[int, bool] = {
            0: False, 1: True, 2: False, 3: False
        }

    @staticmethod
    def list_available_ports() -> List[Dict[str, str]]:
        """Lists all physical COM / serial ports detected on the host system."""
        ports_list = []
        if SERIAL_AVAILABLE:
            try:
                for p in serial.tools.list_ports.comports():
                    ports_list.append({
                        "device": p.device,
                        "description": p.description,
                        "hwid": p.hwid
                    })
            except Exception as e:
                print(f"[RS485] Error enumerating ports: {e}")
        return ports_list

    def open_connection(self, port: Optional[str] = None, baudrate: Optional[int] = None) -> bool:
        """Opens physical serial port connection or configures simulation mode."""
        with self.lock:
            if port:
                self.port_name = port
            if baudrate:
                self.baudrate = baudrate

            # Close existing
            if self.serial_port and self.serial_port.is_open:
                try:
                    self.serial_port.close()
                except Exception:
                    pass

            self.is_connected = False
            self.last_error = ""

            if not SERIAL_AVAILABLE:
                self.is_simulation = True
                self.is_connected = True
                self.last_error = "PySerial not available; simulation mode."
                return True

            try:
                # Map parity
                parity_map = {
                    "N": serial.PARITY_NONE,
                    "E": serial.PARITY_EVEN,
                    "O": serial.PARITY_ODD
                }
                ser_parity = parity_map.get(self.parity, serial.PARITY_NONE)

                self.serial_port = serial.Serial(
                    port=self.port_name,
                    baudrate=self.baudrate,
                    bytesize=self.databits,
                    parity=ser_parity,
                    stopbits=self.stopbits,
                    timeout=self.timeout,
                    write_timeout=self.timeout
                )
                self.is_connected = True
                self.is_simulation = False
                return True
            except Exception as e:
                self.last_error = str(e)
                # Graceful fallback to virtual simulation
                self.is_connected = True
                self.is_simulation = True
                return False

    def close_connection(self):
        """Closes the active serial connection."""
        with self.lock:
            if self.serial_port and self.serial_port.is_open:
                try:
                    self.serial_port.close()
                except Exception:
                    pass
            self.is_connected = False

    # =========================================================================
    # Modbus Frame Execution
    # =========================================================================
    def _execute_frame(self, request_frame: bytes, expected_resp_len: int) -> Optional[bytes]:
        """Transmits request frame over RS-485 (or simulation) and captures response."""
        self.tx_count += 1
        self.last_tx_hex = " ".join(f"{b:02X}" for b in request_frame)

        if self.is_simulation or not (self.serial_port and self.serial_port.is_open):
            # Virtual Loopback Engine
            return self._virtual_device_respond(request_frame)

        with self.lock:
            try:
                # Modbus 3.5-char silent frame spacing
                time.sleep(3.5 * 11 / self.baudrate)
                self.serial_port.reset_input_buffer()
                self.serial_port.write(request_frame)
                self.serial_port.flush()

                # Read response
                response = self.serial_port.read(expected_resp_len)
                if not response:
                    self.timeouts += 1
                    self.last_error = f"RS-485 Timeout on {self.port_name}"
                    return None

                self.rx_count += 1
                self.last_rx_hex = " ".join(f"{b:02X}" for b in response)

                if not verify_crc(response):
                    self.crc_errors += 1
                    self.last_error = "RS-485 CRC Checksum Mismatch"
                    return None

                return response
            except Exception as e:
                self.last_error = f"RS-485 Comms Error: {e}"
                self.timeouts += 1
                return None

    def read_holding_registers(self, slave_id: int, address: int, count: int) -> Optional[List[int]]:
        """
        Function 0x03: Read Holding Registers.
        Request: [Slave ID, 0x03, Addr Hi, Addr Lo, Count Hi, Count Lo, CRC Lo, CRC Hi]
        """
        req = struct.pack(">BBHH", slave_id, 0x03, address, count)
        req += crc16_modbus(req)
        
        # Expected response: Slave + Func + ByteCount(1) + (count * 2) + CRC(2)
        expected_len = 1 + 1 + 1 + (count * 2) + 2
        resp = self._execute_frame(req, expected_len)
        
        if not resp or len(resp) < 5:
            return None
            
        if resp[0] != slave_id or resp[1] != 0x03:
            return None
            
        byte_count = resp[2]
        if len(resp) != 3 + byte_count + 2:
            return None
            
        values = []
        for i in range(count):
            val = struct.unpack(">H", resp[3 + i * 2: 5 + i * 2])[0]
            values.append(val)
        return values

    def write_single_register(self, slave_id: int, address: int, value: int) -> bool:
        """
        Function 0x06: Write Single Holding Register.
        Request: [Slave ID, 0x06, Addr Hi, Addr Lo, Val Hi, Val Lo, CRC Lo, CRC Hi]
        """
        req = struct.pack(">BBHH", slave_id, 0x06, address, value & 0xFFFF)
        req += crc16_modbus(req)
        
        expected_len = 8
        resp = self._execute_frame(req, expected_len)
        if not resp or len(resp) != 8:
            return False
            
        return resp[:6] == req[:6]

    def write_multiple_registers(self, slave_id: int, address: int, values: List[int]) -> bool:
        """
        Function 0x10: Write Multiple Holding Registers.
        """
        count = len(values)
        byte_count = count * 2
        req = struct.pack(">BBHHB", slave_id, 0x10, address, count, byte_count)
        for v in values:
            req += struct.pack(">H", v & 0xFFFF)
        req += crc16_modbus(req)
        
        expected_len = 8
        resp = self._execute_frame(req, expected_len)
        if not resp or len(resp) != 8:
            return False
        return resp[0] == slave_id and resp[1] == 0x10

    def read_coils(self, slave_id: int, address: int, count: int) -> Optional[List[bool]]:
        """Function 0x01: Read Coils."""
        req = struct.pack(">BBHH", slave_id, 0x01, address, count)
        req += crc16_modbus(req)
        
        byte_count = (count + 7) // 8
        expected_len = 3 + byte_count + 2
        resp = self._execute_frame(req, expected_len)
        if not resp or len(resp) < 5 or resp[1] != 0x01:
            return None
            
        coils = []
        for i in range(count):
            byte_idx = 3 + (i // 8)
            bit_idx = i % 8
            coils.append(bool((resp[byte_idx] >> bit_idx) & 1))
        return coils

    def write_single_coil(self, slave_id: int, address: int, state: bool) -> bool:
        """Function 0x05: Write Single Coil (0xFF00 for ON, 0x0000 for OFF)."""
        val = 0xFF00 if state else 0x0000
        req = struct.pack(">BBHH", slave_id, 0x05, address, val)
        req += crc16_modbus(req)
        
        resp = self._execute_frame(req, 8)
        if not resp or len(resp) != 8:
            return False
        return resp[:6] == req[:6]

    # =========================================================================
    # Virtual Loopback Responder (Simulation Physics)
    # =========================================================================
    def _virtual_device_respond(self, req: bytes) -> Optional[bytes]:
        """Provides instant Modbus RTU response for simulation and test benches."""
        if len(req) < 4:
            return None
            
        slave_id = req[0]
        func = req[1]
        self.rx_count += 1

        if func == 0x03:  # Read Holding Registers
            addr, count = struct.unpack(">HH", req[2:6])
            byte_count = count * 2
            resp = struct.pack(">BBB", slave_id, 0x03, byte_count)
            for i in range(count):
                reg_val = self.virtual_holding_registers.get(addr + i, 0)
                resp += struct.pack(">H", reg_val)
            resp += crc16_modbus(resp)
            self.last_rx_hex = " ".join(f"{b:02X}" for b in resp)
            return resp

        elif func == 0x06:  # Write Single Register
            addr, val = struct.unpack(">HH", req[2:6])
            self.virtual_holding_registers[addr] = val
            resp = req[:6] + crc16_modbus(req[:6])
            self.last_rx_hex = " ".join(f"{b:02X}" for b in resp)
            return resp

        elif func == 0x10:  # Write Multiple Registers
            addr, count, byte_count = struct.unpack(">HHB", req[2:7])
            for i in range(count):
                val = struct.unpack(">H", req[7 + i * 2: 9 + i * 2])[0]
                self.virtual_holding_registers[addr + i] = val
            resp = struct.pack(">BBHH", slave_id, 0x10, addr, count)
            resp += crc16_modbus(resp)
            self.last_rx_hex = " ".join(f"{b:02X}" for b in resp)
            return resp

        elif func == 0x01:  # Read Coils
            addr, count = struct.unpack(">HH", req[2:6])
            byte_count = (count + 7) // 8
            resp = struct.pack(">BBB", slave_id, 0x01, byte_count)
            bytes_data = [0] * byte_count
            for i in range(count):
                val = self.virtual_coils.get(addr + i, False)
                if val:
                    bytes_data[i // 8] |= (1 << (i % 8))
            resp += bytes(bytes_data) + crc16_modbus(resp + bytes(bytes_data))
            self.last_rx_hex = " ".join(f"{b:02X}" for b in resp)
            return resp

        elif func == 0x05:  # Write Single Coil
            addr, val = struct.unpack(">HH", req[2:6])
            self.virtual_coils[addr] = (val == 0xFF00)
            resp = req[:6] + crc16_modbus(req[:6])
            self.last_rx_hex = " ".join(f"{b:02X}" for b in resp)
            return resp

        return None

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns live diagnostic statistics of the RS-485 bus."""
        return {
            "port": self.port_name,
            "baudrate": self.baudrate,
            "parity": self.parity,
            "is_connected": self.is_connected,
            "is_simulation": self.is_simulation,
            "tx_count": self.tx_count,
            "rx_count": self.rx_count,
            "crc_errors": self.crc_errors,
            "timeouts": self.timeouts,
            "last_tx_hex": self.last_tx_hex,
            "last_rx_hex": self.last_rx_hex,
            "last_error": self.last_error
        }
