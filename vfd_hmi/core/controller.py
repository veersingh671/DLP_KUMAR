"""
HMI Controller for DLP KUMAR VFD HMI.
Acts as the central coordination layer between the UI, simulation physics,
and hardware drivers (RS485 / Modbus / GPIO).
"""
import os
import json
import random
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from core.system_state import VFDState, SensorItem, ActuatorItem, AlarmItem, NetworkState

class HMIController(QObject):
    # Signals for UI data-binding
    vfd_updated = pyqtSignal(object)       # Emits VFDState
    sensors_updated = pyqtSignal(list)      # Emits list of SensorItem
    actuators_updated = pyqtSignal(list)    # Emits list of ActuatorItem
    alarms_updated = pyqtSignal(list)       # Emits list of AlarmItem
    network_updated = pyqtSignal(object)    # Emits NetworkState
    parameters_updated = pyqtSignal(list)   # Emits list of parameter dicts

    def __init__(self, base_dir=None, parent=None):
        super().__init__(parent)
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load configuration
        self.settings = self._load_json(os.path.join(self.base_dir, "config", "settings.json"), default={})
        self.parameters = self._load_json(os.path.join(self.base_dir, "config", "vfd_parameters.json"), default=[])
        
        # State instances
        self.vfd = VFDState()
        self.network = NetworkState()
        
        # Default Sensors
        self.sensors = [
            SensorItem("S01", "Motor Temperature", 38.0, "°C", 0.0, 100.0, 70.0, 85.0),
            SensorItem("S02", "Supply Line Voltage", 382.0, "V", 300.0, 480.0, 420.0, 450.0),
            SensorItem("S03", "Motor Current", 0.0, "A", 0.0, 15.0, 10.0, 13.0),
            SensorItem("S04", "Hydraulic / System Pressure", 4.2, "bar", 0.0, 10.0, 7.5, 9.0),
            SensorItem("S05", "Shaft Speed", 0, "RPM", 0, 1800, 1600, 1750)
        ]
        
        # Default Actuators
        self.actuators = [
            ActuatorItem("A01", "Main Motor Drive", "MOTOR", False, False),
            ActuatorItem("A02", "Forced Cooling Fan", "FAN", True, True),
            ActuatorItem("A03", "Coolant Supply Valve", "VALVE", False, False),
            ActuatorItem("A04", "Holding Brake", "BRAKE", False, False)
        ]
        
        # Default Alarms
        self.alarms = [
            AlarmItem("ALM01", "WRN-102", "High ambient cabinet temperature", "WARNING"),
            AlarmItem("ALM02", "INF-001", "System initialized in simulation mode", "INFO")
        ]
        
        # Ramp & simulation dynamics
        self.accel_rate = 10.0  # Hz per second
        self.decel_rate = 10.0  # Hz per second
        self._update_ramp_rates()
        
        # 100ms simulation timer
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._simulation_tick)
        self.sim_timer.start(100)

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
        for p in self.parameters:
            if p.get("id") == "P01":
                max_f = float(p.get("value", 50.0))
            elif p.get("id") == "P03":
                accel_sec = max(0.5, float(p.get("value", 5.0)))
            elif p.get("id") == "P04":
                decel_sec = max(0.5, float(p.get("value", 5.0)))
        
        self.accel_rate = max_f / accel_sec
        self.decel_rate = max_f / decel_sec

    # ==========================================
    # VFD Commands
    # ==========================================
    def start_vfd(self):
        if self.vfd.fault_code:
            return False, "Cannot start while fault active. Reset fault first."
        self.vfd.running = True
        self.vfd.status_text = "ACCELERATING" if self.vfd.actual_frequency < self.vfd.set_frequency else "RUNNING"
        self.actuators[0].command_state = True
        self.vfd_updated.emit(self.vfd)
        return True, "VFD Started"

    def stop_vfd(self):
        self.vfd.running = False
        self.vfd.status_text = "DECELERATING" if self.vfd.actual_frequency > 0.0 else "STOPPED"
        self.actuators[0].command_state = False
        self.vfd_updated.emit(self.vfd)
        return True, "VFD Stopped"

    def set_frequency(self, freq: float):
        max_f = 50.0
        min_f = 0.0
        for p in self.parameters:
            if p.get("id") == "P01":
                max_f = float(p.get("value", 50.0))
            elif p.get("id") == "P02":
                min_f = float(p.get("value", 0.0))
                
        clamped = max(min_f, min(max_f, round(freq, 1)))
        self.vfd.set_frequency = clamped
        self.vfd_updated.emit(self.vfd)
        return clamped

    def adjust_frequency(self, delta: float):
        return self.set_frequency(self.vfd.set_frequency + delta)

    def toggle_direction(self):
        self.vfd.direction = "REV" if self.vfd.direction == "FWD" else "FWD"
        self.vfd_updated.emit(self.vfd)

    def reset_fault(self):
        self.vfd.fault_code = None
        if self.vfd.running:
            self.vfd.status_text = "RUNNING"
        else:
            self.vfd.status_text = "STOPPED"
        self.vfd_updated.emit(self.vfd)
        return True

    # ==========================================
    # Actuator Commands
    # ==========================================
    def toggle_actuator(self, actuator_id: str):
        for act in self.actuators:
            if act.id == actuator_id:
                if act.id == "A01":
                    # Controlled via VFD
                    if self.vfd.running:
                        self.stop_vfd()
                    else:
                        self.start_vfd()
                    return
                act.command_state = not act.command_state
                act.feedback_state = act.command_state
                self.actuators_updated.emit(self.actuators)
                return

    # ==========================================
    # Alarm Commands
    # ==========================================
    def acknowledge_alarms(self):
        for alm in self.alarms:
            alm.acknowledged = True
        self.alarms_updated.emit(self.alarms)

    def clear_alarms(self):
        # Clears acknowledged alarms
        self.alarms = [alm for alm in self.alarms if not alm.acknowledged]
        self.alarms_updated.emit(self.alarms)

    def trigger_test_alarm(self, code="ERR-042", message="Motor Overcurrent Trip", severity="CRITICAL"):
        alm_id = f"ALM{len(self.alarms)+1:02d}"
        new_alm = AlarmItem(alm_id, code, message, severity)
        self.alarms.insert(0, new_alm)
        if severity == "CRITICAL":
            self.vfd.fault_code = code
            self.vfd.status_text = f"TRIP ({code})"
            self.vfd.running = False
            self.vfd_updated.emit(self.vfd)
        self.alarms_updated.emit(self.alarms)

    # ==========================================
    # Parameter Management
    # ==========================================
    def update_parameter(self, param_id: str, new_val: float):
        for p in self.parameters:
            if p.get("id") == param_id:
                p_min = p.get("min", 0.0)
                p_max = p.get("max", 100.0)
                if not (p_min <= new_val <= p_max):
                    return False, f"Value {new_val} out of range ({p_min} - {p_max})"
                p["value"] = new_val
                self._update_ramp_rates()
                self._save_parameters()
                self.parameters_updated.emit(self.parameters)
                return True, "Parameter updated"
        return False, "Parameter not found"

    def _save_parameters(self):
        path = os.path.join(self.base_dir, "config", "vfd_parameters.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.parameters, f, indent=2)
        except Exception as e:
            print(f"[Controller] Error saving parameters: {e}")

    # ==========================================
    # Simulation Physics Loop
    # ==========================================
    def _simulation_tick(self):
        dt = 0.1  # 100ms
        
        # 1. Frequency Ramp
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

        # 2. Electrical & Mechanical derivations
        f_ratio = self.vfd.actual_frequency / 50.0 if self.vfd.actual_frequency > 0 else 0.0
        
        # Motor Speed RPM (4-pole synchronous speed 1500 RPM @ 50Hz, 3.5% slip)
        self.vfd.motor_speed = int(self.vfd.actual_frequency * 29.0) if self.vfd.actual_frequency > 0.1 else 0
        
        # Output Voltage (V/f linear profile)
        nominal_v = 380.0
        self.vfd.output_voltage = round(min(nominal_v, nominal_v * f_ratio + (random.uniform(-0.8, 0.8) if f_ratio > 0 else 0.0)), 1)
        
        # Output Current (magnetizing base + torque component)
        if self.vfd.actual_frequency > 0.1:
            base_i = 1.2 + (2.1 * f_ratio)
            self.vfd.output_current = round(base_i + random.uniform(-0.05, 0.05), 2)
            self.vfd.load_percent = round(min(100.0, f_ratio * 75.0 + random.uniform(-1.0, 1.0)), 1)
        else:
            self.vfd.output_current = 0.0
            self.vfd.load_percent = 0.0

        # Output Power (kW)
        self.vfd.power_kw = round((1.732 * self.vfd.output_voltage * self.vfd.output_current * 0.85) / 1000.0, 2)
        
        # Motor Temperature (Thermal inertia)
        if self.vfd.running and self.vfd.actual_frequency > 5.0:
            target_temp = 36.0 + (12.0 * f_ratio)
            self.vfd.motor_temp += (target_temp - self.vfd.motor_temp) * 0.005
        else:
            self.vfd.motor_temp += (30.0 - self.vfd.motor_temp) * 0.003
        self.vfd.motor_temp = round(self.vfd.motor_temp, 1)

        # 3. Synchronize Sensors
        self.sensors[0].value = self.vfd.motor_temp
        self.sensors[0].status = "CRITICAL" if self.vfd.motor_temp >= 85 else ("WARNING" if self.vfd.motor_temp >= 70 else "NORMAL")
        
        self.sensors[1].value = round(382.0 + random.uniform(-1.5, 1.5), 1)
        self.sensors[2].value = self.vfd.output_current
        self.sensors[3].value = round(4.2 + (0.3 * f_ratio) + random.uniform(-0.03, 0.03), 2)
        self.sensors[4].value = self.vfd.motor_speed
        
        # Actuator feedback sync
        self.actuators[0].feedback_state = self.vfd.running and (self.vfd.actual_frequency > 0.0)

        # Network slight fluctuation
        if random.random() < 0.1:
            self.network.signal_strength = max(70, min(95, self.network.signal_strength + random.randint(-2, 2)))

        # Emit updates
        self.vfd_updated.emit(self.vfd)
        self.sensors_updated.emit(self.sensors)
        self.actuators_updated.emit(self.actuators)
        self.network_updated.emit(self.network)
