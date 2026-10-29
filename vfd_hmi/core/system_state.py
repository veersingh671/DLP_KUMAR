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
    set_frequency: float = 45.0      # Hz (S05)
    actual_frequency: float = 0.0    # Hz (M09)
    motor_speed: int = 0             # RPM (M44 / shaft speed)
    sync_speed: int = 1500           # RPM (Synchronous speed: 120*f/P)
    output_current: float = 0.0      # Amperes (M11)
    output_voltage: float = 0.0      # Volts (M12)
    motor_temp: float = 38.0         # °C (M26 / heatsink & thermal model)
    dc_bus_voltage: float = 540.0    # Volts (Derived DC bus)
    power_kw: float = 0.0            # kW (Mechanical / electrical power)
    shaft_torque_nm: float = 0.0     # Motor torque in N·m
    torque_percent: float = 0.0      # Motor torque % (M13)
    thermal_load_percent: float = 0.0# Motor thermal accumulation vs F09 limit
    slip_hz: float = 0.0             # Motor slip frequency (Hz)
    motor_poles: int = 4             # P01: Motor poles (2, 4, 6, 8)
    rated_kw: float = 3.7            # P02: Motor rated kW
    rated_current: float = 7.5       # P03 / F09: Motor rated FLA (A)
    base_frequency: float = 50.0     # F04: Base frequency (Hz)
    max_frequency: float = 50.0      # F03: Max frequency (Hz)
    frenic_at_speed: bool = False    # M14 Bit 5: FAR (Frequency arrival)
    frenic_current_limit: bool = False # M14 Bit 3: IL (Current limit active)
    frenic_link_ok: bool = True      # M14 Bit 12: RL (RS-485 link priority active)
    frenic_dc_brake: bool = False    # M14 Bit 10: BRK (DC braking active)
    load_percent: float = 0.0        # %
    fault_code: Optional[str] = None
    fault_desc: Optional[str] = None
    fault_remedy: Optional[str] = None
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
