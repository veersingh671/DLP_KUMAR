# DLP KUMAR - Raspberry Pi VFD HMI

## 1. PROJECT OVERVIEW

This project is a dedicated industrial-style HMI/control application running on a Raspberry Pi 3A+.

The Raspberry Pi is the main processing and control unit.

The user interface is displayed on a 5-inch HDMI touchscreen display.

The HMI must allow the operator to:

- Monitor VFD parameters in real time.
- Read VFD operating parameters.
- Write permitted VFD parameters.
- Start and stop the VFD.
- Set VFD frequency.
- Reset VFD faults.
- Monitor motor voltage.
- Monitor motor current.
- Monitor motor speed.
- Monitor motor temperature.
- Monitor DC bus voltage if available from the VFD.
- Monitor additional sensors.
- Control actuators.
- Monitor actuator states.
- Display alarms and faults.
- Display communication status.
- Display Wi-Fi connection strength.
- Display system status.
- Store selected operating data and alarms.

The application must be designed specifically for a small 5-inch 800x480 touchscreen.

This is NOT a desktop application.

It must look and behave like a dedicated industrial HMI.

---

# 2. HARDWARE

## Main controller

Raspberry Pi 3A+

The Raspberry Pi performs:

- HMI processing
- UI rendering
- VFD communication
- Sensor processing
- Actuator control
- Alarm processing
- Data logging
- Network monitoring

---

## Display

5-inch HDMI TFT touchscreen.

Target display:

- Size: 5 inch
- Resolution: 800 x 480 pixels
- Orientation: Landscape
- HDMI video input
- USB touchscreen interface
- USB power/touch connection
- Target application resolution: 800 x 480

The application MUST be designed for exactly:

800 x 480 pixels

Do not design the UI for 1080p and scale it down.

The UI must be designed directly around the 800x480 layout.

---

# 3. DISPLAY DESIGN RULES

These rules are mandatory.

## Resolution

Use:

800 x 480

Landscape orientation.

---

## No desktop-style UI

Do NOT create:

- Desktop windows
- Window decorations
- Title bars
- OS-style menus
- Small desktop buttons
- Tiny text
- Unnecessary scrollbars

The application should run fullscreen.

---

## Touch-first design

The HMI is operated primarily by touchscreen.

All buttons must be large enough for reliable finger operation.

Recommended minimum touch target:

44 x 44 pixels

Preferred:

50-70 pixels

Important controls such as START, STOP, RESET, APPLY and WRITE should be even larger.

Never create tiny clickable text.

---

# 4. UI LAYOUT

Use a consistent layout throughout the application.

Recommended screen structure:

+------------------------------------------------+
| HEADER / STATUS BAR                            |
+------------------------------------------------+
|                                                |
|                                                |
|              MAIN CONTENT AREA                 |
|                                                |
|                                                |
|                                                |
+------------------------------------------------+
| NAVIGATION / ACTION BAR                        |
+------------------------------------------------+

Target dimensions:

Header:
approximately 45-55 px

Bottom navigation:
approximately 55-70 px

Main content:
remaining area

---

# 5. HEADER

The header should appear on all major screens.

It should show:

- Current screen name
- VFD communication status
- System status
- Wi-Fi signal
- Current time

Example:

------------------------------------------------
| DASHBOARD | VFD: ONLINE | SYS: OK | WiFi ████ |
------------------------------------------------

Do not make the header too large.

The main data must remain visible.

---

# 6. WIFI STATUS

Wi-Fi status must be visible in the header.

Example:

WiFi ████████ 82%

or:

WiFi: 82%

The application should obtain the actual Wi-Fi signal strength from the Raspberry Pi.

Do not use a fake fixed value in production.

If Wi-Fi is disconnected:

WiFi: OFFLINE

The Wi-Fi indicator should update automatically.

---

# 7. MAIN SCREEN / DASHBOARD

The dashboard is the first screen after application startup.

The dashboard must provide the most important real-time information without requiring scrolling.

Recommended values:

- VFD status
- Motor frequency
- Motor speed
- Motor current
- Motor voltage
- Motor power if available
- Motor temperature
- DC bus voltage if available
- Important sensor values
- Active alarm count
- Communication status

Example conceptual layout:

+------------------------------------------------+
| DASHBOARD              VFD ONLINE   WiFi ████ |
+------------------------------------------------+
|                                                |
| VFD STATUS              RUNNING                |
|                                                |
| FREQUENCY              45.0 Hz                 |
| SPEED                  1450 RPM                |
|                                                |
| CURRENT                 3.20 A                 |
| VOLTAGE               380.0 V                  |
|                                                |
| TEMPERATURE             42.5 °C                |
| DC BUS                 540 V                   |
|                                                |
+------------------------------------------------+
| VFD | SENSORS | ACTUATORS | ALARMS | SETTINGS |
+------------------------------------------------+

The exact dashboard layout can be improved as development progresses.

Do not overcrowd the dashboard.

---

# 8. VFD CONTROL SCREEN

Create a dedicated VFD control screen.

The screen must provide:

## READ VALUES

At minimum, if supported by the VFD:

- Running status
- Frequency
- Set frequency
- Output current
- Output voltage
- Motor speed
- Motor power
- Motor temperature
- DC bus voltage
- Fault code
- Warning status
- Direction
- Operating mode

The actual available parameters depend on the VFD.

Do not invent VFD registers.

---

## WRITE CONTROLS

The operator should be able to control:

- Start
- Stop
- Frequency setpoint
- Direction if supported
- Fault reset

Example:

+------------------------------------------------+
| VFD CONTROL                                    |
+------------------------------------------------+
| STATUS        RUNNING                          |
| FREQUENCY     45.0 Hz                          |
| CURRENT        3.2 A                           |
| VOLTAGE      380 V                             |
| SPEED        1450 RPM                          |
+------------------------------------------------+
|                                                |
| FREQUENCY                                      |
|                                                |
|       [ - ]      45.0 Hz       [ + ]           |
|                                                |
|              [ APPLY ]                         |
|                                                |
|       [ START ]       [ STOP ]                 |
|                                                |
|              [ RESET FAULT ]                   |
+------------------------------------------------+

Important commands must require appropriate confirmation where necessary.

---

# 9. VFD PARAMETER SCREEN

Create a separate parameter management screen.

The operator must be able to:

- Read supported parameters.
- View parameter name.
- View parameter number/register.
- View current value.
- Edit writable parameters.
- Write values to the VFD.
- Validate values before writing.

Example:

+------------------------------------------------+
| VFD PARAMETERS                                 |
+------------------------------------------------+
| Parameter        Value       Status            |
|------------------------------------------------|
| Max Frequency    50.0 Hz     [EDIT]            |
| Min Frequency     0.0 Hz     [EDIT]            |
| Acceleration      5.0 sec    [EDIT]            |
| Deceleration      5.0 sec    [EDIT]            |
| Motor Voltage   380 V        [EDIT]            |
+------------------------------------------------+
| [ READ ]                         [ WRITE ]     |
+------------------------------------------------+

Do not allow arbitrary register writes from the normal operator interface.

Each parameter must have metadata.

Example:

{
    "name": "Maximum Frequency",
    "register": 2001,
    "data_type": "uint16",
    "scale": 0.1,
    "unit": "Hz",
    "readable": true,
    "writable": true,
    "minimum": 0,
    "maximum": 50
}

The actual register addresses must come from the VFD manual.

Never guess register addresses.

---

# 10. SENSOR SCREEN

Create a dedicated sensor monitoring screen.

The screen should support multiple sensors.

Possible parameters include:

- Temperature
- Voltage
- Current
- Pressure
- Flow
- Level
- Speed
- Humidity
- Digital inputs
- Other project-specific sensors

Example:

+------------------------------------------------+
| SENSORS                                        |
+------------------------------------------------+
| TEMPERATURE              42.5 °C               |
|                                                |
| VOLTAGE                  380.2 V               |
|                                                |
| CURRENT                    3.21 A               |
|                                                |
| PRESSURE                   4.2 bar              |
|                                                |
| SPEED                   1450 RPM               |
+------------------------------------------------+

Each sensor should have:

- Name
- Value
- Unit
- Status
- Valid/invalid state
- Communication state if applicable
- Alarm limits if configured

---

# 11. ACTUATOR SCREEN

Create a dedicated actuator control screen.

Possible actuators:

- Motor
- Pump
- Fan
- Valve
- Relay
- Brake
- Solenoid
- Other project-specific actuators

Each actuator should display:

- Name
- Current state
- Command state
- Feedback state if available

Example:

+------------------------------------------------+
| ACTUATORS                                      |
+------------------------------------------------+
| MOTOR          RUNNING                         |
|                                                |
| FAN            OFF                             |
|                                                |
| VALVE          OPEN                            |
|                                                |
| BRAKE          OFF                             |
+------------------------------------------------+
|        [ CONTROL ACTUATORS ]                  |
+------------------------------------------------+

Never display an actuator as ON unless the software has valid feedback or the design explicitly defines the state as command-only.

---

# 12. ALARM SCREEN

Create a dedicated alarm screen.

The alarm system must support:

- Active alarms
- Warnings
- Faults
- Acknowledgement
- Alarm clearing
- Timestamp
- Alarm source
- Current value
- Limit value where appropriate

Example:

+------------------------------------------------+
| ALARMS                                         |
+------------------------------------------------+
| ACTIVE ALARMS                                  |
|                                                |
| [HIGH] MOTOR TEMPERATURE                       |
| 72 °C / Limit 70 °C                            |
|                                                |
| [FAULT] VFD OVERCURRENT                        |
|                                                |
| [WARN] SENSOR COMMUNICATION LOST               |
+------------------------------------------------+
| [ ACKNOWLEDGE ]              [ CLEAR ]         |
+------------------------------------------------+

Use clear visual states for:

- Normal
- Warning
- Fault
- Communication failure

Do not rely only on color.

Use text/icons as well.

---

# 13. SETTINGS SCREEN

Create a settings screen for configuration.

Possible settings:

- VFD communication settings
- Modbus address
- Baud rate
- Parity
- Stop bits
- Sensor configuration
- Alarm thresholds
- Engineering units
- Network information
- Display settings
- Logging settings

Avoid exposing dangerous low-level settings to normal operators.

Separate operator settings and engineering settings if necessary.

---

# 14. NETWORK SCREEN

Create a simple network information screen.

Show:

- Wi-Fi connected/disconnected
- SSID
- IP address
- Signal strength
- Connection state
- Hostname

Example:

+------------------------------------------------+
| NETWORK                                        |
+------------------------------------------------+
| STATUS       CONNECTED                         |
| SSID         DLP_NETWORK                       |
| IP ADDRESS   192.168.1.100                     |
| SIGNAL       82%                               |
| HOSTNAME     raspberrypi                       |
+------------------------------------------------+

---

# 15. NAVIGATION

Use simple persistent navigation.

Recommended:

[HOME] [VFD] [SENSORS] [ACTUATORS] [ALARMS]

Settings can be accessed separately.

Navigation must be easy to operate with one finger.

Do not use complicated menus.

Avoid deep navigation trees.

The operator should reach important screens in one tap.

---

# 16. SOFTWARE ARCHITECTURE

Use a modular architecture.

Do NOT put everything inside main.py.

Recommended structure:

vfd_hmi/
|
|-- main.py
|
|-- config/
|   |-- settings.json
|   |-- vfd_parameters.json
|
|-- ui/
|   |-- __init__.py
|   |-- main_window.py
|   |-- dashboard.py
|   |-- vfd_screen.py
|   |-- parameters_screen.py
|   |-- sensors_screen.py
|   |-- actuators_screen.py
|   |-- alarms_screen.py
|   |-- settings_screen.py
|
|-- communication/
|   |-- __init__.py
|   |-- modbus.py
|   |-- vfd.py
|   |-- io.py
|
|-- hardware/
|   |-- __init__.py
|   |-- sensors.py
|   |-- actuators.py
|
|-- core/
|   |-- __init__.py
|   |-- controller.py
|   |-- data_manager.py
|   |-- alarm_manager.py
|   |-- system_state.py
|
|-- utils/
|   |-- __init__.py
|   |-- logger.py
|   |-- helpers.py
|
|-- data/
|   |-- logs/
|
|-- tests/
|   |-- test_vfd.py
|   |-- test_sensors.py
|   |-- test_ui.py
|
|-- requirements.txt
|-- README.md
|-- .gitignore

---

# 17. SOFTWARE LAYERS

Use the following architecture:

UI
 |
 v
Controller / Application Logic
 |
 +-------------------+
 |         |         |
 VFD     Sensors   Actuators
 Manager  Manager   Manager
 |
 v
Communication / Hardware Layer

The UI must NOT directly control GPIO or Modbus.

For example:

BAD:

button -> write Modbus register directly

GOOD:

button
  ->
controller
  ->
vfd_manager
  ->
modbus
  ->
VFD

This separation is mandatory.

---

# 18. VFD COMMUNICATION

Use Modbus RTU over RS485 if the selected VFD supports it.

Communication must be isolated inside:

communication/modbus.py

and:

communication/vfd.py

The VFD module should expose high-level functions such as:

read_status()
read_frequency()
read_current()
read_voltage()
read_speed()
read_temperature()
read_fault()
set_frequency()
start()
stop()
reset_fault()
read_parameter()
write_parameter()

The UI must not know Modbus register details.

---

# 19. REAL-TIME DATA

Real-time values should update automatically.

Do not freeze the UI while waiting for Modbus.

Communication must run asynchronously or in worker threads/timers.

The UI must remain responsive even if:

- VFD is disconnected.
- RS485 communication fails.
- Sensor is disconnected.
- Network is disconnected.

Communication failures must not crash the application.

---

# 20. COMMUNICATION FAILURE

If the VFD becomes disconnected:

Show:

VFD: OFFLINE

Do not display stale values as if they are current.

Each data value should have a validity state.

Example:

frequency:
    value = 45.0
    valid = true
    timestamp = ...

If communication fails:

frequency:
    value = null
    valid = false

The UI should clearly show the value as unavailable.

---

# 21. DATA MODEL

Use structured data models.

Example:

VFD state:

{
    "online": true,
    "running": true,
    "frequency": 45.0,
    "current": 3.2,
    "voltage": 380.0,
    "speed": 1450,
    "temperature": 42.5,
    "fault": null
}

Sensor:

{
    "name": "Motor Temperature",
    "value": 42.5,
    "unit": "°C",
    "valid": true
}

---

# 22. SAFETY

This is a control application.

Do not blindly send commands to hardware.

Before writing a parameter:

1. Validate data type.
2. Validate range.
3. Validate writable permission.
4. Confirm communication state.
5. Send command.
6. Check response.
7. Update UI only after successful confirmation.

For example:

Operator enters:

100 Hz

If maximum frequency is:

50 Hz

The application must reject it.

Never silently clamp unsafe values.

---

# 23. START / STOP SAFETY

START and STOP must be clearly separated.

Do not place START and STOP next to each other without clear visual distinction.

Important commands should have confirmation where appropriate.

Example:

START

"Start VFD?"

[ CANCEL ] [ START ]

The exact safety policy can be configured later.

---

# 24. UI STYLE

Use a clean industrial HMI appearance.

Requirements:

- Dark or neutral background.
- High contrast.
- Large values.
- Clear labels.
- Large buttons.
- Minimal decoration.
- Consistent spacing.
- Consistent icons.
- No unnecessary animation.
- No gradients unless they improve readability.
- No excessive shadows.
- No tiny text.

The design should look professional and functional rather than like a web dashboard.

---

# 25. COLORS

Use a consistent semantic color system.

Normal:
neutral/green status

Warning:
yellow/orange

Fault:
red

Offline:
gray/dark neutral

Important controls should remain readable even if color is unavailable.

Never communicate status using color alone.

---

# 26. TYPOGRAPHY

Because the display is only 800x480:

Prioritize readability.

Recommended approximate sizes:

Header:
18-22 px

Navigation:
16-20 px

Normal labels:
16-18 px

Important values:
24-36 px

Critical values:
30-42 px

Do not use very small fonts.

Adjust based on actual testing on the physical 5-inch display.

---

# 27. TOUCH INTERACTION

The touchscreen is the primary operator input.

All important controls should have large touch areas.

Recommended:

Normal button:
minimum 50x45 px

Important action:
minimum 70x50 px

Avoid buttons smaller than 44x44 px.

Use visual feedback when a button is pressed.

---

# 28. KEYBOARD / MOUSE

The final HMI must not require a keyboard or mouse.

Keyboard and mouse may be used during development only.

All normal operation must be possible using the touchscreen.

---

# 29. DEVELOPMENT MODE

The project must support a development/simulation mode.

This is extremely important.

When developing on the laptop, the application must be able to run without the actual VFD and sensors.

Example:

SIMULATION_MODE = true

In simulation mode:

VFD values are generated locally.

Example:

Frequency:
45.0 Hz

Current:
3.2 A

Voltage:
380 V

Temperature:
42.5 °C

This allows UI development without hardware.

---

# 30. PRODUCTION MODE

Production mode runs on the Raspberry Pi.

Example:

SIMULATION_MODE = false

The application then communicates with the real:

- VFD
- Sensors
- Actuators
- Network

---

# 31. LAPTOP DEVELOPMENT

The main development environment is the user's Windows laptop.

Use:

- VS Code
- Antigravity
- Codex
- Git if available

The laptop is used for:

- UI design
- Code development
- Simulation
- Testing
- Debugging

The Raspberry Pi is the final runtime target.

---

# 32. RASPBERRY PI DEPLOYMENT

The final application runs on:

Raspberry Pi 3A+

The Raspberry Pi must:

- Boot Linux.
- Start the HMI automatically.
- Run fullscreen.
- Display at 800x480.
- Connect to the touchscreen.
- Communicate with the VFD.
- Read sensors.
- Control actuators.
- Log data.
- Recover from communication errors.

---

# 33. FULLSCREEN

The final HMI must run fullscreen.

No:

- Window border
- Desktop panel
- Mouse cursor if possible
- Terminal
- Desktop icons

The operator should see only the HMI.

---

# 34. STARTUP

After Raspberry Pi boot:

1. Linux starts.
2. Network initializes.
3. HMI application starts automatically.
4. HMI enters fullscreen mode.
5. Communication services start.
6. Dashboard appears.

The operator should not need to manually launch the application.

---

# 35. LOGGING

Create application logs.

Log:

- Application startup
- Application shutdown
- VFD connection
- VFD disconnection
- Communication errors
- Parameter writes
- Start/stop commands
- Alarm events
- Sensor failures

Do not log passwords or sensitive credentials.

---

# 36. DATA LOGGING

Support optional logging of:

- Timestamp
- Frequency
- Current
- Voltage
- Temperature
- Speed
- Sensor values
- Alarm state

Keep logging lightweight because the Raspberry Pi 3A+ has limited resources.

Do not introduce a heavy database unless required.

---

# 37. PERFORMANCE

The Raspberry Pi 3A+ is the production target.

Therefore:

- Keep the UI lightweight.
- Avoid unnecessary animations.
- Avoid excessive CPU usage.
- Avoid memory-heavy frameworks where possible.
- Do not continuously recreate widgets.
- Update only values that changed.
- Use timers/workers appropriately.
- Keep background polling controlled.

Target a responsive touchscreen experience.

---

# 38. ERROR HANDLING

The application must never crash because of a temporary hardware communication failure.

Examples:

VFD disconnected:

Show:

VFD OFFLINE

Sensor disconnected:

Show:

SENSOR ERROR

Wi-Fi disconnected:

Show:

WiFi OFFLINE

The application should continue running.

---

# 39. TESTING

Test each layer independently.

Tests must eventually cover:

1. UI startup.
2. Navigation.
3. Simulation mode.
4. VFD communication.
5. VFD read functions.
6. VFD write functions.
7. Parameter validation.
8. Sensor handling.
9. Actuator handling.
10. Alarm handling.
11. Network status.
12. Logging.
13. Communication failure recovery.

---

# 40. DEVELOPMENT ORDER

Do NOT implement everything at once.

Follow this exact development order:

PHASE 1:
Project structure

PHASE 2:
Basic application startup

PHASE 3:
800x480 fullscreen window

PHASE 4:
Main HMI layout

PHASE 5:
Dashboard

PHASE 6:
Navigation

PHASE 7:
Simulation data

PHASE 8:
VFD screen

PHASE 9:
VFD parameter screen

PHASE 10:
Sensor screen

PHASE 11:
Actuator screen

PHASE 12:
Alarm screen

PHASE 13:
Network/Wi-Fi status

PHASE 14:
Real VFD communication

PHASE 15:
Real sensors

PHASE 16:
Real actuators

PHASE 17:
Data logging

PHASE 18:
Automatic startup

PHASE 19:
Hardware testing

PHASE 20:
Final optimization for Raspberry Pi 3A+

---

# 41. IMPORTANT DEVELOPMENT RULE

Do not make assumptions about hardware.

If a VFD parameter/register is unknown:

DO NOT INVENT IT.

Use a configuration placeholder until the VFD manual is provided.

If a sensor interface is unknown:

DO NOT assume GPIO, ADC, RS485, I2C, or SPI.

Wait until the actual sensor/interface is defined.

---

# 42. UI DEVELOPMENT PRIORITY

The first goal is NOT VFD communication.

The first goal is:

A beautiful, responsive, functional 800x480 HMI.

Use simulation data first.

The UI must be completely usable before connecting the real VFD.

---

# 43. FIRST IMPLEMENTATION TASK

Start by creating:

1. main.py
2. MainWindow
3. 800x480 fullscreen HMI
4. Header
5. Dashboard
6. Bottom navigation
7. Simulation data
8. Wi-Fi status placeholder/real status
9. VFD status indicator
10. Sensor cards
11. Navigation between screens

Do not implement real Modbus yet.

Do not implement real GPIO yet.

Do not implement real actuator control yet.

First make the HMI functional using simulated data.

---

# 44. DESIGN TARGET

The final HMI should feel similar to a professional industrial machine control panel.

The operator should be able to understand the system within a few seconds.

The most important information should always be visible.

Avoid unnecessary complexity.

Use large numbers for important measurements.

Example:

45.0
Hz

3.20
A

380
V

42.5
°C

1450
RPM

---

# 45. FINAL GOAL

The final system should behave like this:

                  5" TOUCHSCREEN
                         |
                         v
                 RASPBERRY PI 3A+
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
         VFD          SENSORS       ACTUATORS
          |
          v
    READ + WRITE
    PARAMETERS

The HMI must provide:

READ:
- VFD status
- Frequency
- Speed
- Voltage
- Current
- Temperature
- Power
- DC bus voltage
- Faults
- Warnings
- Sensor values
- Actuator status
- Wi-Fi status
- System status

WRITE:
- Frequency
- Start
- Stop
- Reset
- Direction if supported
- Permitted VFD parameters
- Actuator commands
- Configuration parameters

The application must be modular, safe, responsive, lightweight, and optimized for the Raspberry Pi 3A+ and 800x480 5-inch touchscreen.

---

# 46. INSTRUCTIONS FOR CODEX / ANTIGRAVITY

You are working on an industrial HMI project.

Follow this README as the project specification.

Before changing architecture, inspect the existing project.

Do not unnecessarily rewrite working code.

Do not create unnecessary files.

Keep modules separated according to the architecture described above.

Do not invent hardware protocols or VFD registers.

Use simulation mode until real hardware specifications are provided.

Always maintain compatibility with:

- Raspberry Pi 3A+
- 800x480 display
- Touchscreen operation
- Fullscreen HMI
- Low-resource hardware

When implementing UI, test at exactly:

800x480

Do not optimize only for the laptop screen.

The physical 5-inch screen is the final UI target.

When implementing a new feature:

1. Keep the existing application working.
2. Add the feature modularly.
3. Test it in simulation mode.
4. Check 800x480 layout.
5. Check touchscreen usability.
6. Check Raspberry Pi 3A+ resource usage.
7. Only then move to the next feature.

Never sacrifice UI readability for adding more information.

The HMI must prioritize:

SAFETY
READABILITY
RELIABILITY
RESPONSIVENESS
SIMPLICITY
MAINTAINABILITY