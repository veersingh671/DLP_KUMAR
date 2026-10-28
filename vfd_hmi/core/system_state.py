"""
System state models for DLP KUMAR VFD HMI.
Defines clean, structured data classes for telemetry, sensors, actuators, and alarms.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import time

@dataclass
class VFDState:
    online: bool = True
    running: bool = False
    direction: str = "FWD"           # FWD or REV
    set_frequency: float = 45.0      # Hz
    actual_frequency: float = 0.0    # Hz
    motor_speed: int = 0             # RPM
    output_current: float = 0.0      # Amperes
    output_voltage: float = 0.0      # Volts
    motor_temp: float = 38.0         # °C
    dc_bus_voltage: float = 540.0    # Volts
    power_kw: float = 0.0            # kW
    load_percent: float = 0.0        # %
    fault_code: Optional[str] = None
    status_text: str = "STOPPED"

@dataclass
class SensorItem:
    id: str
    name: str
    value: float
    unit: str
    min_val: float
    max_val: float
    warn_threshold: float
    crit_threshold: float
    status: str = "NORMAL"           # NORMAL, WARNING, CRITICAL

@dataclass
class ActuatorItem:
    id: str
    name: str
    equipment_type: str              # MOTOR, FAN, VALVE, BRAKE
    command_state: bool = False      # Desired target
    feedback_state: bool = False     # Verified physical feedback
    interlock_ok: bool = True

@dataclass
class AlarmItem:
    id: str
    code: str
    message: str
    severity: str                    # CRITICAL, WARNING, INFO
    timestamp: str = field(default_factory=lambda: time.strftime("%H:%M:%S"))
    acknowledged: bool = False
    cleared: bool = False

@dataclass
class NetworkState:
    connected: bool = True
    ssid: str = "DLP_INDUSTRIAL_WIFI"
    ip_address: str = "192.168.1.100"
    signal_strength: int = 86        # Percentage (0-100)
    hostname: str = "dlp-pi3a-hmi"
