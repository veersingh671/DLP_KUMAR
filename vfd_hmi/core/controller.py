"""
HMI Controller for DLP KUMAR VFD HMI.
Acts as the central coordination layer between the UI, simulation physics,
and hardware drivers (RS-485 Modbus RTU / GPIO).
"""
import os
import json
import random
from typing import Dict, Any, List, Optional
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from core.system_state import VFDState, SensorItem, ActuatorItem, AlarmItem, NetworkState
from communication.modbus import ModbusRTUMaster
from communication.vfd import VFDModbusDriver
from communication.io import IOModbusDriver

class HMIController(QObject):
    # Signals for UI data-binding
    vfd_updated = pyqtSignal(object)       # Emits VFDState
    sensors_updated = pyqtSignal(list)      # Emits list of SensorItem
    actuators_updated = pyqtSignal(list)    # Emits list of ActuatorItem
    alarms_updated = pyqtSignal(list)       # Emits list of AlarmItem
    network_updated = pyqtSignal(object)    # Emits NetworkState
    parameters_updated = pyqtSignal(list)   # Emits list of parameter dicts
    rs485_updated = pyqtSignal(dict)        # Emits RS-485 bus diagnostics dictionary

    def __init__(self, base_dir=None, parent=None):
        super().__init__(parent)
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load configuration
        self.settings = self._load_json(os.path.join(self.base_dir, "config", "settings.json"), default={})
        self.parameters = self._load_json(os.path.join(self.base_dir, "config", "vfd_parameters.json"), default=[])
        
        # Communication Configuration
        comm_cfg = self.settings.get("communication", {})
        port = comm_cfg.get("port", "COM3")
        baud = comm_cfg.get("baudrate", 9600)
        parity = comm_cfg.get("parity", "N")
        slave_id = comm_cfg.get("slave_id", 1)
        
        # Initialize Modbus RTU Master & Drivers
        self.modbus = ModbusRTUMaster(port=port, baudrate=baud, parity=parity)
        self.vfd_driver = VFDModbusDriver(self.modbus, slave_id=slave_id)
        self.io_driver = IOModbusDriver(self.modbus, slave_id=2)
        
        # Open connection (defaults to virtual simulation if COM port absent)
        self.modbus.open_connection()

        # State instances
        self.vfd = VFDState()
        self.network = NetworkState()
        
        # Default Sensors (Analog 4-20mA / 0-10V inputs mapped to Modbus Regs 0x3000-0x3004)
        self.sensors = [
            SensorItem("S01", "Motor Temperature", 38.0, "°C", 0.0, 100.0, 70.0, 85.0),
            SensorItem("S02", "Supply Line Voltage", 382.0, "V", 300.0, 480.0, 420.0, 450.0),
            SensorItem("S03", "Motor Current", 0.0, "A", 0.0, 15.0, 10.0, 13.0),
            SensorItem("S04", "Hydraulic Pressure", 4.2, "bar", 0.0, 10.0, 7.5, 9.0),
            SensorItem("S05", "Shaft Speed", 0, "RPM", 0, 1800, 1600, 1750)
        ]
        
        # Default Actuators (Digital Relay outputs mapped to Modbus Coils 0x0000-0x0003)
        self.actuators = [
            ActuatorItem("A01", "Main Motor Drive", "MOTOR", False, False),
            ActuatorItem("A02", "Forced Cooling Fan", "FAN", True, True),
            ActuatorItem("A03", "Coolant Supply Valve", "VALVE", False, False),
            ActuatorItem("A04", "Holding Brake", "BRAKE", False, False)
        ]
        
        # Default Alarms
        self.alarms = [
            AlarmItem("ALM01", "WRN-102", "High ambient cabinet temperature", "WARNING"),
            AlarmItem("ALM02", "INF-001", "Modbus RTU Engine initialized", "INFO")
        ]
        
        # Ramp & simulation dynamics
        self.accel_rate = 10.0  # Hz per second
        self.decel_rate = 10.0  # Hz per second
        self._update_ramp_rates()
        
        # Main tick timer (100ms)
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._system_tick)
        self.sim_timer.start(100)
        
        self._diag_counter = 0

    def _load_json(self, path, default):
        try:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[Controller] Error loading {path}: {e}")
        return default

    def _update_ramp_rates(self):
        accel_sec = 5.0
        decel_sec = 5.0
        max_f = 50.0
        base_f = 50.0
        poles = 4
        rated_kw = 3.7
        rated_amps = 7.5
        slip_hz = 1.5

        for p in self.parameters:
            fcode = p.get("fuji_code", "")
            pid = p.get("id", "")
            val = float(p.get("value", 0.0))
            if fcode == "F03" or pid == "P01":
                max_f = max(1.0, val)
            elif fcode == "F04":
                base_f = max(1.0, val)
            elif fcode == "F07" or pid == "P03":
                accel_sec = max(0.1, val)
            elif fcode == "F08" or pid == "P04":
                decel_sec = max(0.1, val)
            elif fcode == "F09" or (pid == "P06" and "thermal" in p.get("name", "").lower()):
                rated_amps = max(0.1, val)
            elif fcode == "P01" or (pid == "P07" and "pole" in p.get("name", "").lower()):
                poles = int(val) if int(val) in (2, 4, 6, 8, 10, 12) else 4
            elif fcode == "P02":
                rated_kw = max(0.1, val)
            elif fcode == "P03":
                rated_amps = max(0.1, val)
            elif fcode == "P06":
                slip_hz = max(0.0, val)

        self.accel_rate = max_f / accel_sec
        self.decel_rate = max_f / decel_sec
        
        self.vfd.motor_poles = poles
        self.vfd.rated_kw = rated_kw
        self.vfd.rated_current = rated_amps
        self.vfd.base_frequency = base_f
        self.vfd.max_frequency = max_f
        self.vfd.slip_hz = slip_hz
        
        self.vfd_driver.motor_poles = poles
        self.vfd_driver.motor_rated_kw = rated_kw
        self.vfd_driver.motor_rated_current = rated_amps
        self.vfd_driver.motor_slip_hz = slip_hz

    # =========================================================================
    # VFD RS-485 Modbus Commands
    # =========================================================================
    def start_vfd(self):
        if self.vfd.fault_code:
            return False, "Cannot start while fault active. Reset fault first."
        self.vfd.running = True
        self.vfd.status_text = "ACCELERATING" if self.vfd.actual_frequency < self.vfd.set_frequency else "RUNNING"
        self.actuators[0].command_state = True
        
        # Send RS-485 Start Run Frame
        self.vfd_driver.send_start(self.vfd.direction)
        
        self.vfd_updated.emit(self.vfd)
        return True, "VFD Started via RS-485"

    def stop_vfd(self):
        self.vfd.running = False
        self.vfd.status_text = "DECELERATING" if self.vfd.actual_frequency > 0.0 else "STOPPED"
        self.actuators[0].command_state = False
        
        # Send RS-485 Stop Frame
        self.vfd_driver.send_stop()
        
        self.vfd_updated.emit(self.vfd)
        return True, "VFD Stopped via RS-485"

    def set_frequency(self, freq: float):
        max_f = 50.0
        min_f = 0.0
        for p in self.parameters:
            fcode = p.get("fuji_code", "")
            pid = p.get("id", "")
            pname = p.get("name", "").lower()
            if fcode == "F03" or pid == "P01":
                max_f = float(p.get("value", 50.0))
            elif fcode == "F16" or pid == "F16" or ("min" in pname and pid == "P02"):
                min_f = float(p.get("value", 0.0))
                
        clamped = max(min_f, min(max_f, round(freq, 1)))
        self.vfd.set_frequency = clamped
        
        # Send RS-485 Setpoint Frequency (S05: 0x0705 in 0.01 Hz)
        self.vfd_driver.send_frequency(clamped)
        
        self.vfd_updated.emit(self.vfd)
        return clamped

    def adjust_frequency(self, delta: float):
        return self.set_frequency(self.vfd.set_frequency + delta)

    def toggle_direction(self):
        self.vfd.direction = "REV" if self.vfd.direction == "FWD" else "FWD"
        self.vfd_driver.send_direction(self.vfd.direction)
        self.vfd_updated.emit(self.vfd)

    def reset_fault(self):
        self.vfd.fault_code = None
        self.vfd.status_text = "RUNNING" if self.vfd.running else "STOPPED"
        
        # Send RS-485 Fault Reset Pulse (0x0004)
        self.vfd_driver.send_fault_reset()
        
        self.vfd_updated.emit(self.vfd)
        return True

    # =========================================================================
    # Actuator & Coil Commands
    # =========================================================================
    def toggle_actuator(self, actuator_id: str):
        for idx, act in enumerate(self.actuators):
            if act.id == actuator_id:
                if act.id == "A01":
                    if self.vfd.running:
                        self.stop_vfd()
                    else:
                        self.start_vfd()
                    return
                act.command_state = not act.command_state
                act.feedback_state = act.command_state
                
                # Write to RS-485 remote relay coil
                self.io_driver.set_relay(idx, act.command_state)
                
                self.actuators_updated.emit(self.actuators)
                return

    # =========================================================================
    # Alarm Commands
    # =========================================================================
    def acknowledge_alarms(self):
        for alm in self.alarms:
            alm.acknowledged = True
        self.alarms_updated.emit(self.alarms)

    def clear_alarms(self):
        self.alarms = [alm for alm in self.alarms if not alm.acknowledged]
        self.alarms_updated.emit(self.alarms)

    def trigger_test_alarm(self, code="OC1", message="Fuji FRENIC: Motor Overcurrent Trip during Accel", severity="CRITICAL"):
        alm_id = f"ALM{len(self.alarms)+1:02d}"
        new_alm = AlarmItem(alm_id, code, message, severity)
        self.alarms.insert(0, new_alm)
        if severity == "CRITICAL":
            self.vfd.fault_code = code
            self.vfd.status_text = f"TRIP ({code})"
            self.vfd.running = False
            # Map code to Fuji M16 register
            code_num = 1 if "OC1" in code else (2 if "OC2" in code else (10 if "LU" in code else (11 if "OH" in code else (14 if "OL" in code else 1))))
            self.modbus.virtual_holding_registers[0x0810] = code_num
            self.modbus.virtual_holding_registers[0x080E] |= 0x0080  # Set Bit 7 ALM
            self.vfd_updated.emit(self.vfd)
        self.alarms_updated.emit(self.alarms)

    # =========================================================================
    # Parameter Management
    # =========================================================================
    def update_parameter(self, param_id: str, new_val: float):
        for p in self.parameters:
            if p.get("id") == param_id:
                p_min = p.get("min", 0.0)
                p_max = p.get("max", 100.0)
                if not (p_min <= new_val <= p_max):
                    return False, f"Value {new_val} out of range ({p_min} - {p_max})"
                p["value"] = new_val
                
                # Write through RS-485 register
                reg_addr = p.get("register", 2000)
                self.vfd_driver.write_parameter(reg_addr, new_val, p.get("data_type", "float"))
                
                self._update_ramp_rates()
                self._save_parameters()
                self.parameters_updated.emit(self.parameters)
                return True, "Parameter updated via RS-485"
        return False, "Parameter not found"

    def _save_parameters(self):
        path = os.path.join(self.base_dir, "config", "vfd_parameters.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.parameters, f, indent=2)
        except Exception as e:
            print(f"[Controller] Error saving parameters: {e}")

    # =========================================================================
    # RS-485 Bus Management & Diagnostics
    # =========================================================================
    def reconfigure_rs485(self, port: str, baudrate: int, parity: str, slave_id: int) -> bool:
        """Reconfigures RS-485 serial communication parameters."""
        self.vfd_driver.slave_id = slave_id
        self.modbus.parity = parity.upper()
        success = self.modbus.open_connection(port=port, baudrate=baudrate)
        self.rs485_updated.emit(self.modbus.get_diagnostics())
        return success

    def toggle_simulation_mode(self, force_sim: bool):
        """Forces or disables simulated RS-485 loopback mode."""
        self.modbus.is_simulation = force_sim
        if not force_sim:
            self.modbus.open_connection()
        self.rs485_updated.emit(self.modbus.get_diagnostics())

    def send_test_modbus_ping(self) -> Dict[str, Any]:
        """Sends an active poll frame to test RS-485 bus response."""
        res = self.vfd_driver.poll_telemetry()
        diag = self.modbus.get_diagnostics()
        diag["poll_result"] = "SUCCESS" if res is not None else "TIMEOUT/ERROR"
        self.rs485_updated.emit(diag)
        return diag

    def get_available_serial_ports(self):
        return ModbusRTUMaster.list_available_ports()

    def jog_vfd(self, direction: str = "FWD", jog_freq: float = 5.0):
        """Commands motor jogging at low frequency (default 5.0 Hz)."""
        if self.vfd.fault_code:
            return False, "Cannot jog while fault active. Reset fault first."
        self.vfd.running = True
        self.vfd.direction = direction
        self.vfd.set_frequency = jog_freq
        self.vfd.status_text = "JOGGING"
        self.actuators[0].command_state = True
        self.vfd_driver.send_jog(direction, jog_freq)
        self.vfd_updated.emit(self.vfd)
        return True, f"JOG {direction} ({jog_freq} Hz)"

    def emergency_stop_vfd(self):
        """Immediate coast stop: disables output inverter PWM immediately."""
        self.vfd.running = False
        self.vfd.actual_frequency = 0.0
        self.vfd.motor_speed = 0
        self.vfd.status_text = "EMERGENCY STOP"
        self.actuators[0].command_state = False
        self.vfd_driver.send_emergency_stop()
        self.vfd_updated.emit(self.vfd)
        return True, "Emergency Coast Stop activated"

    # =========================================================================
    # System Loop & Telemetry Synchronization
    # =========================================================================
    def _simulation_tick(self):
        """Backward-compatible alias for _system_tick."""
        self._system_tick()

    def _system_tick(self):
        dt = 0.1  # 100ms
        
        # If running on physical RS-485 bus, poll real drive holding registers
        if not self.modbus.is_simulation and self.modbus.is_connected:
            telemetry = self.vfd_driver.poll_telemetry()
            if telemetry:
                self.vfd.online = True
                self.vfd.running = telemetry["running"]
                self.vfd.direction = telemetry["direction"]
                self.vfd.actual_frequency = telemetry["actual_frequency"]
                self.vfd.output_current = telemetry["output_current"]
                self.vfd.output_voltage = telemetry["output_voltage"]
                self.vfd.dc_bus_voltage = telemetry["dc_bus_voltage"]
                self.vfd.motor_speed = telemetry["motor_speed"]
                self.vfd.sync_speed = telemetry.get("sync_speed", 1500)
                self.vfd.power_kw = telemetry.get("power_kw", 0.0)
                self.vfd.shaft_torque_nm = telemetry.get("shaft_torque_nm", 0.0)
                self.vfd.torque_percent = telemetry.get("torque_percent", 0.0)
                self.vfd.thermal_load_percent = telemetry.get("thermal_load_percent", 0.0)
                self.vfd.slip_hz = telemetry.get("slip_hz", 0.0)
                self.vfd.motor_temp = telemetry["motor_temp"]
                self.vfd.frenic_at_speed = telemetry.get("frenic_at_speed", False)
                self.vfd.frenic_current_limit = telemetry.get("frenic_current_limit", False)
                self.vfd.frenic_link_ok = telemetry.get("frenic_link_ok", True)
                self.vfd.frenic_dc_brake = telemetry.get("frenic_dc_brake", False)
                self.vfd.fault_code = telemetry["fault_code"]
                self.vfd.fault_desc = telemetry.get("fault_desc")
                self.vfd.fault_remedy = telemetry.get("fault_remedy")
                self.vfd.status_text = telemetry["status_text"]
                self.vfd.load_percent = round(min(100.0, (self.vfd.output_current / max(0.1, self.vfd.rated_current)) * 100.0), 1)
            else:
                self.vfd.online = False
                self.vfd.status_text = "RS485 COMM ERROR"
        else:
            # Simulation Physics Engine (Virtual Fuji FRENIC-Mini C2)
            target = self.vfd.set_frequency if (self.vfd.running and not self.vfd.fault_code) else 0.0
            
            if self.vfd.actual_frequency < target:
                self.vfd.actual_frequency = min(target, self.vfd.actual_frequency + self.accel_rate * dt)
                self.vfd.status_text = "ACCELERATING"
            elif self.vfd.actual_frequency > target:
                self.vfd.actual_frequency = max(target, self.vfd.actual_frequency - self.decel_rate * dt)
                self.vfd.status_text = "DECELERATING"
            else:
                if self.vfd.fault_code:
                    self.vfd.status_text = f"TRIP ({self.vfd.fault_code})"
                elif self.vfd.running:
                    self.vfd.status_text = "RUNNING"
                else:
                    self.vfd.status_text = "STOPPED"

            # Motor analytical physics calculations
            f = self.vfd.actual_frequency
            poles = max(2, self.vfd.motor_poles)
            base_f = max(10.0, self.vfd.base_frequency)
            rated_kw = max(0.1, self.vfd.rated_kw)
            rated_amps = max(0.1, self.vfd.rated_current)

            # Synchronous Speed N_sync = (120 * f) / poles
            sync_rpm = int(round((120.0 * f) / poles))
            self.vfd.sync_speed = sync_rpm

            # V/f curve with low-frequency voltage boost for breakaway torque
            nominal_v = 380.0
            if f > 0.1:
                v_ratio = min(1.0, f / base_f)
                boost = 12.0 * (1.0 - v_ratio) if v_ratio < 1.0 else 0.0
                self.vfd.output_voltage = round(nominal_v * v_ratio + boost + random.uniform(-0.5, 0.5), 1)
            else:
                self.vfd.output_voltage = 0.0

            # Current based on motor load curve + no-load magnetization current
            if f > 0.1:
                no_load_i = rated_amps * 0.35  # ~35% magnetization current
                f_load_factor = min(1.0, f / base_f)
                self.vfd.output_current = round(no_load_i + (rated_amps - no_load_i) * f_load_factor * 0.75 + random.uniform(-0.04, 0.04), 2)
                load_fraction = self.vfd.output_current / rated_amps
                self.vfd.load_percent = round(min(125.0, load_fraction * 100.0), 1)
            else:
                self.vfd.output_current = 0.0
                self.vfd.load_percent = 0.0
                load_fraction = 0.0

            # Slip and Shaft RPM: N_shaft = (120 * (f - slip)) / poles
            effective_slip = min(f * 0.08, self.vfd.slip_hz * load_fraction)
            self.vfd.slip_hz = round(effective_slip, 2)
            if f > 0.1:
                shaft_f = max(0.0, f - effective_slip * 0.5)  # slip compensation partially recovers speed
                self.vfd.motor_speed = int(round((120.0 * shaft_f) / poles))
            else:
                self.vfd.motor_speed = 0

            # Mechanical / Electrical Power: P = sqrt(3) * V * I * pf / 1000
            if self.vfd.output_voltage > 10.0 and self.vfd.output_current > 0.1:
                self.vfd.power_kw = round((1.732 * self.vfd.output_voltage * self.vfd.output_current * 0.85) / 1000.0, 2)
            else:
                self.vfd.power_kw = 0.0

            # Shaft Torque: T = (9550 * P_kw) / N_shaft
            if self.vfd.motor_speed > 10 and self.vfd.power_kw > 0.0:
                self.vfd.shaft_torque_nm = round((9550.0 * self.vfd.power_kw) / self.vfd.motor_speed, 2)
                base_sync_rpm = max(1, int((120.0 * base_f) / poles))
                t_rated = (9550.0 * rated_kw) / base_sync_rpm
                self.vfd.torque_percent = round(min(200.0, (self.vfd.shaft_torque_nm / t_rated) * 100.0), 1)
            else:
                self.vfd.shaft_torque_nm = 0.0
                self.vfd.torque_percent = 0.0

            # Motor Electronic Thermal Overload Accumulation (F09 / F11)
            cooling_derate = 1.0
            if 0.1 < f < 20.0:
                cooling_derate = 0.65 + 0.35 * (f / 20.0)
            eff_fla = rated_amps * cooling_derate
            self.vfd.thermal_load_percent = round(min(150.0, (self.vfd.output_current / eff_fla) * 100.0), 1) if f > 0.1 else 0.0

            # Heat Sink Temperature Model (M26)
            if self.vfd.running and f > 5.0:
                target_temp = 36.0 + (14.0 * load_fraction)
                self.vfd.motor_temp += (target_temp - self.vfd.motor_temp) * 0.005
            else:
                self.vfd.motor_temp += (30.0 - self.vfd.motor_temp) * 0.003
            self.vfd.motor_temp = round(self.vfd.motor_temp, 1)

            # Fuji Status Word (M14) bits:
            self.vfd.frenic_at_speed = bool(self.vfd.running and abs(f - self.vfd.set_frequency) < 0.2 and f > 0.1)
            self.vfd.frenic_current_limit = bool(self.vfd.load_percent > 115.0)
            self.vfd.frenic_link_ok = True
            self.vfd.frenic_dc_brake = False

            # Sync Virtual Modbus Registers (Legacy + Fuji FRENIC-Mini C2)
            self.modbus.virtual_holding_registers[0x2100] = 0x0001 if self.vfd.running else 0x0000
            self.modbus.virtual_holding_registers[0x2101] = int(self.vfd.actual_frequency * 100)
            self.modbus.virtual_holding_registers[0x2102] = int(self.vfd.output_current * 100)
            self.modbus.virtual_holding_registers[0x2103] = int(self.vfd.output_voltage * 10)
            self.modbus.virtual_holding_registers[0x2105] = self.vfd.motor_speed
            self.modbus.virtual_holding_registers[0x2106] = int(self.vfd.motor_temp * 10)

            # Fuji FRENIC-Mini (FRN-C2) S-Group & M-Group Registers
            self.modbus.virtual_holding_registers[0x0705] = int(self.vfd.set_frequency * 100)
            s06_val = 0
            if self.vfd.running:
                s06_val = 0x0002 if self.vfd.direction == "REV" else 0x0001
            self.modbus.virtual_holding_registers[0x0706] = s06_val
            self.modbus.virtual_holding_registers[0x0809] = int(self.vfd.actual_frequency * 100)
            self.modbus.virtual_holding_registers[0x080B] = int(self.vfd.output_current * 100)
            self.modbus.virtual_holding_registers[0x080C] = int(self.vfd.output_voltage * 10)
            self.modbus.virtual_holding_registers[0x080D] = int(self.vfd.torque_percent * 10)
            self.modbus.virtual_holding_registers[0x082C] = self.vfd.motor_speed
            
            m14 = 0x1000  # Bit 12: RL (Link Valid)
            if self.vfd.running:
                m14 |= 0x0004  # Bit 2: RUN
                m14 |= (0x0002 if self.vfd.direction == "REV" else 0x0001)
                if self.vfd.frenic_at_speed:
                    m14 |= 0x0020  # Bit 5: FAR (Frequency Arrival)
                if self.vfd.frenic_current_limit:
                    m14 |= 0x0008  # Bit 3: IL (Current Limiting)
            if self.vfd.fault_code:
                m14 |= 0x0080  # Bit 7: ALM (Alarm Trip)
            self.modbus.virtual_holding_registers[0x080E] = m14
            self.modbus.virtual_holding_registers[0x0810] = 1 if self.vfd.fault_code else 0
            self.modbus.virtual_holding_registers[0x081A] = int(self.vfd.motor_temp * 10)

        # Synchronize Sensors
        self.sensors[0].value = self.vfd.motor_temp
        self.sensors[0].status = "CRITICAL" if self.vfd.motor_temp >= 85 else ("WARNING" if self.vfd.motor_temp >= 70 else "NORMAL")
        self.sensors[1].value = round(382.0 + random.uniform(-1.5, 1.5), 1)
        self.sensors[2].value = self.vfd.output_current
        self.sensors[3].value = round(4.2 + (0.3 * (self.vfd.actual_frequency / 50.0)) + random.uniform(-0.03, 0.03), 2)
        self.sensors[4].value = self.vfd.motor_speed
        
        # Actuator feedback sync
        self.actuators[0].feedback_state = self.vfd.running and (self.vfd.actual_frequency > 0.0)

        # Network slight fluctuation
        if random.random() < 0.1:
            self.network.signal_strength = max(70, min(95, self.network.signal_strength + random.randint(-2, 2)))

        # Periodic RS-485 Diagnostics broadcast (every 500ms)
        self._diag_counter += 1
        if self._diag_counter >= 5:
            self._diag_counter = 0
            self.rs485_updated.emit(self.modbus.get_diagnostics())

        # Emit UI updates
        self.vfd_updated.emit(self.vfd)
        self.sensors_updated.emit(self.sensors)
        self.actuators_updated.emit(self.actuators)
        self.network_updated.emit(self.network)
