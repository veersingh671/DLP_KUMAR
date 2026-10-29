"""
Fuji Electric FRENIC-Mini (FRN-C2 Series) RS-485 Modbus Driver.
Implements the exact Fuji FRENIC-Mini C2 Modbus RTU register mapping,
including S-Group commands (S01, S05, S06, S07, S08),
M-Group monitors (M05, M06, M09, M11, M12, M13, M14, M16, M26, M44),
and parameter groups (F-Group, P-Group, H-Group, y-Group).
"""
from typing import Optional, Dict, Any, List, Tuple
from communication.modbus import ModbusRTUMaster

# Fuji FRENIC-Mini (FRN-C2 Series) Alarm Code Dictionary
FRENIC_FAULT_MAP = {
    1: ("OC1", "Overcurrent during acceleration", "Extend acceleration time (F07), inspect motor wiring and mechanical jamming."),
    2: ("OC2", "Overcurrent during deceleration", "Extend deceleration time (F08) or install braking resistor."),
    3: ("OC3", "Overcurrent during steady speed running", "Check for sudden load fluctuation or mechanical blockage."),
    5: ("EF",  "Ground fault detected", "Inspect motor insulation and motor leads for ground leakage."),
    6: ("OV1", "Overvoltage during acceleration", "Check for regenerative energy from high-inertia load or high AC supply voltage."),
    7: ("OV2", "Overvoltage during deceleration", "Extend deceleration time (F08) or check braking unit."),
    8: ("OV3", "Overvoltage during steady speed running", "Check AC input voltage stability; surge detected."),
    10: ("LU", "DC Undervoltage trip", "Main supply dropped below trip threshold; inspect L1/L2/L3 voltage."),
    11: ("OH1", "Heat sink overheating", "Check cabinet cooling fan, clear dust from heat sink fins, check ambient temp."),
    14: ("OL1", "Motor 1 Overload (Electronic thermal trip)", "Motor continuously overloaded; verify mechanical load and parameter F09."),
    16: ("OLU", "Inverter overload trip", "Continuous load exceeds inverter rating; downsize load or check duty cycle."),
    22: ("Er1", "Memory / EEPROM error", "Internal memory write failure; review parameter y97 RAM storage setting."),
    24: ("Er8", "RS-485 Communication error", "Check RS-485 wiring (DX+/DX-), terminator resistor (110 ohm), baud/parity mismatch."),
    25: ("Er1", "Memory / EEPROM error", "Internal memory write failure; review parameter y97 RAM storage setting.")
}

class FujiFrenicMiniDriver:
    """
    Dedicated RS-485 Modbus RTU Driver for Fuji Electric FRENIC-Mini (FRN-C2 Series).
    
    Register Address Calculation Formula:
        Hex Address = (Group Code << 8) | Item Number
        Decimal Address = (Group Code * 256) + Item Number
        Holding Register PLC Address = 40001 + Decimal Address
        
    Function Code Groups:
        - F: Fundamental Functions (0x00xx)
        - E: Extension Terminal Functions (0x01xx)
        - C: Control Functions (0x02xx)
        - P: Motor 1 Parameters (0x03xx)
        - H: High Performance Functions (0x04xx)
        - S: Command / Frequency Setting (0x07xx)
        - M: Monitor Data / Status (0x08xx)
        - y: Link Functions / RS-485 Comms (0x0Fxx, with 0x13xx aliases)
    """

    # Group S (0x07): Command Registers
    REG_S01_FREQ_RATIO = 0x0701  # Frequency ratio command (±20000 = ±100.00%, 0 allows S05)
    REG_S05_FREQ_HZ    = 0x0705  # Direct Frequency Reference (0.01 Hz resolution, 0-40000)
    REG_S06_OPERATION  = 0x0706  # Operation Command Word (Bit 0=FWD, 1=REV, 2=X1, 3=X2, 15=RST)
    REG_S07_UNIVERSAL_DO = 0x0707 # Universal Digital Output (Bit 0=Y1, Bit 1=30A/B/C)
    REG_S08_ACC_DEC_SW = 0x0708  # Accel/Decel selection switch

    # Group M (0x08): Monitor Registers
    REG_M05_REF_FREQ   = 0x0805  # Frequency Reference Setpoint (0.01 Hz)
    REG_M06_RAW_FREQ   = 0x0806  # Output frequency before slip compensation (0.01 Hz)
    REG_M09_ACT_FREQ   = 0x0809  # Final Output Frequency after slip comp (0.01 Hz)
    REG_M10_TORQUE_RAW = 0x080A  # Calculated Torque (%)
    REG_M11_ACT_CURR   = 0x080B  # Output Current (0.01 A)
    REG_M12_ACT_VOLT   = 0x080C  # Output Voltage (0.1 V)
    REG_M13_TORQUE_PCT = 0x080D  # Motor Calculated Output Torque (0.1%)
    REG_M14_STATUS     = 0x080E  # Operation Status Word
    REG_M16_ALARM_CODE = 0x0810  # Latest Alarm / Trip Code
    REG_M17_PAST_ALM1  = 0x0811  # Past Trip Record 1
    REG_M18_PAST_ALM2  = 0x0812  # Past Trip Record 2
    REG_M19_PAST_ALM3  = 0x0813  # Past Trip Record 3
    REG_M26_TEMP_C     = 0x081A  # Heat Sink Temperature (0.1 °C or 1 °C)
    REG_M41_RUN_HOURS  = 0x0829  # Cumulative Run Time (Hours)
    REG_M44_MOTOR_RPM  = 0x082C  # Motor Speed (RPM)

    # Group F (0x00): Fundamental Parameters
    REG_F01_FREQ_CMD_SRC = 0x0001  # 2 or 3 = RS-485 link
    REG_F02_RUN_CMD_SRC  = 0x0002  # 2 = RS-485 link
    REG_F03_MAX_FREQ     = 0x0003  # in 0.1 Hz (e.g. 500 = 50.0 Hz)
    REG_F04_BASE_FREQ    = 0x0004  # in 0.1 Hz (e.g. 500 = 50.0 Hz)
    REG_F05_RATED_VOLT   = 0x0005  # in 1 V (e.g. 380 V)
    REG_F07_ACCEL_TIME   = 0x0007  # in 0.1 s (e.g. 50 = 5.0 s)
    REG_F08_DECEL_TIME   = 0x0008  # in 0.1 s (e.g. 50 = 5.0 s)
    REG_F09_THERMAL_AMPS = 0x0009  # in 0.01 A (e.g. 750 = 7.50 A)
    REG_F10_THERMAL_TIME = 0x000A  # in 0.1 min (e.g. 50 = 5.0 min)
    REG_F11_THERMAL_TYPE = 0x000B  # 1: Standard motor, 2: Forced cooling
    REG_F15_FREQ_LIM_HI  = 0x000F  # in 0.1 Hz
    REG_F16_FREQ_LIM_LO  = 0x0010  # in 0.1 Hz (0 = 0.0 Hz)
    REG_F26_CARRIER_KHZ  = 0x001A  # in 0.1 kHz (e.g. 40 = 4.0 kHz)

    # Group P (0x03): Motor Parameters
    REG_P01_POLES        = 0x0301  # Motor Poles: 2, 4, 6, 8, 10, 12
    REG_P02_CAPACITY_KW  = 0x0302  # in 0.01 kW (e.g. 370 = 3.70 kW)
    REG_P03_RATED_CURRENT= 0x0303  # in 0.01 A (e.g. 750 = 7.50 A)
    REG_P04_AUTOTUNING   = 0x0304  # 0: Disabled, 1: Static, 2: Dynamic
    REG_P05_NO_LOAD_CURR = 0x0305  # in 0.01 A
    REG_P06_SLIP_COMP_HZ = 0x0306  # in 0.01 Hz (e.g. 150 = 1.50 Hz)
    REG_P07_R1_PERCENT   = 0x0307  # Primary resistance %
    REG_P08_X_PERCENT    = 0x0308  # Leakage reactance %

    # Group H (0x04): High-Performance Functions
    REG_H30_LINK_FUNCTION= 0x041E  # 3 = RS-485 Run Command & Freq Command priority

    # Group y (0x0F standard / 0x13 alias): RS-485 Communications Parameters
    REG_Y01_STATION_ADDR = 0x0F01  # Node 1 - 255
    REG_Y02_ERR_ACTION   = 0x0F02  # 0: Er8 trip, 1: Timeout trip, 2: Retry, 3: Continue
    REG_Y03_TIMEOUT_SEC  = 0x0F03  # in 0.1 s
    REG_Y04_BAUD_RATE    = 0x0F04  # 0:2400, 1:4800, 2:9600, 3:19200, 4:38400
    REG_Y05_DATA_LEN     = 0x0F05  # 0: 8-bit, 1: 7-bit
    REG_Y06_PARITY_BITS  = 0x0F06  # 0: 8N2, 1: 8E1, 2: 8O1, 3: 8N1
    REG_Y10_PROTOCOL     = 0x0F0A  # 0: Modbus RTU
    REG_Y97_SAVE_RAM     = 0x0F61  # 0: EEPROM, 1: RAM (preserve write endurance)
    REG_Y98_LINK_COMM    = 0x0F62  # Bus communication command source priority
    REG_Y99_LINK_ENABLE  = 0x0F63  # RS-485 link enable

    def __init__(self, master: ModbusRTUMaster, slave_id: int = 1):
        self.master = master
        self.slave_id = slave_id
        self.last_poll_successful = False
        self.comm_errors = 0
        self.motor_poles = 4
        self.motor_rated_kw = 3.7
        self.motor_rated_current = 7.5
        self.motor_slip_hz = 1.5

    # =========================================================================
    # Motor Calculations & Analytical Formulas
    # =========================================================================
    @staticmethod
    def calculate_sync_rpm(freq_hz: float, poles: int = 4) -> int:
        """
        Calculates synchronous speed in RPM: N_sync = (120 * f) / poles.
        """
        p = max(2, poles if poles in (2, 4, 6, 8, 10, 12) else 4)
        return int(round((120.0 * max(0.0, freq_hz)) / p))

    @staticmethod
    def calculate_shaft_rpm(actual_freq_hz: float, poles: int = 4, slip_hz: float = 1.5, load_factor: float = 0.8) -> int:
        """
        Calculates actual mechanical shaft speed in RPM taking into account motor slip.
        N_shaft = (120 * (f - effective_slip)) / poles.
        """
        if actual_freq_hz <= 0.1:
            return 0
        p = max(2, poles if poles in (2, 4, 6, 8, 10, 12) else 4)
        effective_slip = min(actual_freq_hz * 0.1, slip_hz * max(0.0, min(1.5, load_factor)))
        shaft_f = max(0.0, actual_freq_hz - effective_slip)
        return int(round((120.0 * shaft_f) / p))

    @staticmethod
    def calculate_motor_torque_nm(kw: float, rpm: int) -> float:
        """
        Calculates motor shaft torque in N*m: T = (9550 * P_kw) / RPM.
        """
        if rpm <= 10 or kw <= 0.0:
            return 0.0
        return round((9550.0 * kw) / rpm, 2)

    @staticmethod
    def calculate_thermal_load_pct(current: float, rated_current: float = 7.5, freq_hz: float = 50.0) -> float:
        """
        Calculates motor electronic thermal overload percentage according to Fuji F09 / F11.
        At frequencies below 20Hz, cooling is reduced for self-cooled motors, lowering FLA capability.
        """
        if rated_current <= 0.1:
            return 0.0
        cooling = 1.0
        if 0.1 < freq_hz < 20.0:
            cooling = 0.65 + 0.35 * (freq_hz / 20.0)
        effective_fla = rated_current * cooling
        return round(min(200.0, (current / effective_fla) * 100.0), 1)

    # =========================================================================
    # RS-485 Modbus RTU Command Transmission
    # =========================================================================
    def send_start(self, direction: str = "FWD") -> bool:
        """
        Sends Fuji FRENIC-Mini Operation Command (S06) to run motor.
        Bit 0 = FWD (0x0001), Bit 1 = REV (0x0002).
        """
        self.master.write_single_register(self.slave_id, self.REG_S01_FREQ_RATIO, 0x0000)
        s06_val = 0x0002 if direction == "REV" else 0x0001
        success = self.master.write_single_register(self.slave_id, self.REG_S06_OPERATION, s06_val)
        
        if success and self.master.is_simulation:
            self.master.virtual_holding_registers[self.REG_S06_OPERATION] = s06_val
            dir_bit = 0x0002 if direction == "REV" else 0x0001
            self.master.virtual_holding_registers[self.REG_M14_STATUS] = 0x1004 | dir_bit
            
        return success

    def send_stop(self) -> bool:
        """
        Sends Fuji FRENIC-Mini Stop Command (S06 = 0x0000).
        """
        s06_val = 0x0000
        success = self.master.write_single_register(self.slave_id, self.REG_S06_OPERATION, s06_val)
        
        if success and self.master.is_simulation:
            self.master.virtual_holding_registers[self.REG_S06_OPERATION] = s06_val
            self.master.virtual_holding_registers[self.REG_M14_STATUS] = 0x1000  # Keep RL bit
            
        return success

    def send_frequency(self, freq_hz: float) -> bool:
        """
        Sets target frequency setpoint on FRENIC-Mini via S05 (Units: 0.01 Hz).
        Range: 0.00 to 400.00 Hz (e.g. 50.00 Hz = 5000).
        """
        clamped_hz = max(0.0, min(400.0, freq_hz))
        reg_val = int(round(clamped_hz * 100))
        
        self.master.write_single_register(self.slave_id, self.REG_S01_FREQ_RATIO, 0x0000)
        success = self.master.write_single_register(self.slave_id, self.REG_S05_FREQ_HZ, reg_val)
        if success and self.master.is_simulation:
            self.master.virtual_holding_registers[self.REG_S05_FREQ_HZ] = reg_val
            
        return success

    def send_direction(self, direction: str) -> bool:
        """
        Switches rotation direction while maintaining run state on S06.
        """
        s06_val = 0x0002 if direction == "REV" else 0x0001
        success = self.master.write_single_register(self.slave_id, self.REG_S06_OPERATION, s06_val)
        if success and self.master.is_simulation:
            self.master.virtual_holding_registers[self.REG_S06_OPERATION] = s06_val
        return success

    def send_jog(self, direction: str = "FWD", jog_freq: float = 5.0) -> bool:
        """
        Executes motor jogging at low frequency (default 5.0 Hz).
        """
        self.send_frequency(jog_freq)
        return self.send_start(direction)

    def send_emergency_stop(self) -> bool:
        """
        Immediate coast stop: sets setpoint to 0.0 and commands S06 = 0x0000.
        """
        self.send_frequency(0.0)
        return self.send_stop()

    def send_fault_reset(self) -> bool:
        """
        Sends Fault Reset pulse via Bit 15 of S06 (0x8000).
        Fuji FRENIC requires Bit 15 high pulse to clear latched trips (OC1, LU, OH1, OL1, etc.).
        """
        success = self.master.write_single_register(self.slave_id, self.REG_S06_OPERATION, 0x8000)
        self.master.write_single_register(self.slave_id, self.REG_S06_OPERATION, 0x0000)
        
        if success and self.master.is_simulation:
            self.master.virtual_holding_registers[self.REG_M16_ALARM_CODE] = 0
            self.master.virtual_holding_registers[self.REG_M14_STATUS] &= ~0x0080
            
        return success

    # =========================================================================
    # Telemetry Polling & Monitor Decoding
    # =========================================================================
    def poll_telemetry(self) -> Optional[Dict[str, Any]]:
        """
        Polls Fuji FRENIC-Mini monitor registers:
        - M09 (0x0809): Output Frequency (0.01 Hz)
        - M11 (0x080B): Output Current (0.01 A)
        - M12 (0x080C): Output Voltage (0.1 V)
        - M13 (0x080D): Calculated Motor Torque (0.1%)
        - M14 (0x080E): Operation Status Word
        - M16 (0x0810): Latest Alarm Code
        - M26 (0x081A): Heat Sink Temperature (°C)
        - M44 (0x082C): Motor Speed (RPM)
        """
        regs = self.master.read_holding_registers(self.slave_id, self.REG_M09_ACT_FREQ, 8)
        if not regs or len(regs) < 8:
            self.comm_errors += 1
            self.last_poll_successful = False
            return None

        self.last_poll_successful = True
        
        raw_freq   = regs[0]  # M09: Output freq (0.01 Hz)
        raw_curr   = regs[2]  # M11: Output current (0.01 A)
        raw_volt   = regs[3]  # M12: Output voltage (0.1 V)
        raw_torque = regs[4]  # M13: Calculated motor torque (0.1%)
        m14_stat   = regs[5]  # M14: Status word
        alarm_num  = regs[7]  # M16: Alarm code

        # Optional read M26 for heat sink temp
        raw_temp = 380
        temp_regs = self.master.read_holding_registers(self.slave_id, self.REG_M26_TEMP_C, 1)
        if temp_regs and len(temp_regs) == 1:
            raw_temp = temp_regs[0]

        # Decode FRENIC M14 Status Bits:
        # Bit 0: FWD, Bit 1: REV, Bit 2: EXT (RUN), Bit 3: IL, Bit 4: LU, Bit 5: FAR, Bit 7: ALM, Bit 10: BRK, Bit 12: RL
        is_running  = bool(m14_stat & 0x0004) or bool(m14_stat & 0x0001) or bool(m14_stat & 0x0002)
        is_rev      = bool(m14_stat & 0x0002)
        is_fwd      = bool(m14_stat & 0x0001)
        curr_limit  = bool(m14_stat & 0x0008)  # IL (Bit 3)
        under_volt  = bool(m14_stat & 0x0010)  # LU (Bit 4)
        at_speed    = bool(m14_stat & 0x0020)  # FAR (Bit 5)
        is_tripped  = bool(m14_stat & 0x0080) or (alarm_num > 0)
        dc_braking  = bool(m14_stat & 0x0400)  # BRK (Bit 10)
        link_active = bool(m14_stat & 0x1000)  # RL (Bit 12)
        
        direction = "REV" if is_rev else "FWD"
        actual_freq = round(raw_freq / 100.0, 1)
        output_curr = round(raw_curr / 100.0, 2)
        output_volt = round(raw_volt / 10.0, 1)
        inv_temp    = round(raw_temp / 10.0, 1) if raw_temp > 200 else float(raw_temp)
        torque_pct  = round(raw_torque / 10.0, 1)

        # Synchronous and Shaft RPM
        sync_rpm = self.calculate_sync_rpm(actual_freq, self.motor_poles)
        load_fraction = output_curr / max(0.1, self.motor_rated_current)
        motor_speed = self.calculate_shaft_rpm(actual_freq, self.motor_poles, self.motor_slip_hz, load_fraction)

        # Electrical / Mechanical Power (kW)
        power_kw = round((1.732 * output_volt * output_curr * 0.85) / 1000.0, 2) if is_running else 0.0

        # Shaft Torque (N*m)
        shaft_torque_nm = self.calculate_motor_torque_nm(power_kw, motor_speed)

        # Motor Thermal Overload Load %
        thermal_load_pct = self.calculate_thermal_load_pct(output_curr, self.motor_rated_current, actual_freq)

        # DC Bus Voltage derivation
        dc_bus_voltage = round(output_volt * 1.414 if output_volt > 50 else 540.0, 1)

        # Lookup Fuji alarm
        fault_code_str = None
        fault_desc = None
        fault_remedy = None
        if is_tripped and alarm_num in FRENIC_FAULT_MAP:
            f_code, f_desc, f_rem = FRENIC_FAULT_MAP[alarm_num]
            fault_code_str = f"FUJI-{f_code}"
            fault_desc = f_desc
            fault_remedy = f_rem
        elif is_tripped:
            fault_code_str = f"FUJI-TRIP#{alarm_num}"
            fault_desc = "FRENIC Inverter Protective Trip"
            fault_remedy = "Inspect drive error logs and reset fault via RST command."

        if is_tripped:
            status_text = f"TRIP ({fault_code_str})"
        elif is_running:
            status_text = "AT SPEED" if at_speed else "RUNNING"
        else:
            status_text = "STOPPED"

        return {
            "status_word": m14_stat,
            "running": is_running,
            "direction": direction,
            "actual_frequency": actual_freq,
            "output_current": output_curr,
            "output_voltage": output_volt,
            "dc_bus_voltage": dc_bus_voltage,
            "motor_speed": motor_speed,
            "sync_speed": sync_rpm,
            "power_kw": power_kw,
            "shaft_torque_nm": shaft_torque_nm,
            "torque_percent": torque_pct,
            "thermal_load_percent": thermal_load_pct,
            "slip_hz": round(self.motor_slip_hz * load_fraction, 2),
            "motor_temp": inv_temp,
            "fault_code": fault_code_str,
            "fault_desc": fault_desc,
            "fault_remedy": fault_remedy,
            "status_text": status_text,
            "frenic_at_speed": at_speed,
            "frenic_current_limit": curr_limit,
            "frenic_link_ok": link_active,
            "frenic_dc_brake": dc_braking,
            "alarm_num": alarm_num
        }

    def read_fault_history(self) -> List[Dict[str, Any]]:
        """
        Reads trip records M16 (latest), M17 (1 trip ago), M18 (2 trips ago), M19 (3 trips ago).
        """
        regs = self.master.read_holding_registers(self.slave_id, self.REG_M16_ALARM_CODE, 4)
        history = []
        if regs:
            for idx, num in enumerate(regs):
                if num > 0 and num in FRENIC_FAULT_MAP:
                    code, desc, remedy = FRENIC_FAULT_MAP[num]
                    history.append({"trip_index": idx, "code": f"FUJI-{code}", "desc": desc, "remedy": remedy})
        return history

    def write_parameter(self, register_addr: int, value: float, data_type: str = "float") -> bool:
        """
        Writes parameter to Fuji FRENIC-Mini function code register.
        Supports F-group, P-group, H-group, and y-group.
        """
        if data_type == "float" or data_type == "scale10":
            int_val = int(round(value * 10))
        elif data_type == "scale100":
            int_val = int(round(value * 100))
        else:
            int_val = int(value)
        return self.master.write_single_register(self.slave_id, register_addr, int_val)

    def read_parameter(self, register_addr: int) -> Optional[int]:
        """
        Reads single holding register parameter from Fuji FRENIC-Mini.
        """
        regs = self.master.read_holding_registers(self.slave_id, register_addr, 1)
        if regs and len(regs) == 1:
            return regs[0]
        return None


# Backward-compatible alias for existing code
VFDModbusDriver = FujiFrenicMiniDriver
