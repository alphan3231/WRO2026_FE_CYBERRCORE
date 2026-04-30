# WRO 2026 Future Engineers Software Documentation

This folder contains the robot source code for Team CYBERRCORE's WRO 2026 Future Engineers vehicle. The software is split between an ESP32-CAM vision module written in Arduino C++ and MicroPython control utilities for drive, sensor, UART, and servo tuning. This documentation was last updated on April 30, 2026 at 18:52 +03.

## Software Architecture Overview

The current software is organized around two main roles:

- **ESP32-CAM vision module**: Captures low-resolution RGB565 frames, detects red and green objects, and sends compact serial messages.
- **MicroPython vehicle controller utilities**: Drive the steering servo, motor driver, ultrasonic distance sensor, and MPU9250 gyro for open-round navigation and calibration.
- **UART communication**: Vision output uses newline-terminated messages at 115200 baud, allowing another board to react to camera detections.

The system keeps the runtime logic simple and deterministic. The camera module only reports color and horizontal position, while the vehicle control code handles movement, turning, and tuning.

```text
ESP32-CAM camera.cpp
        |
        | Serial: COLOR,x,count
        v
MicroPython UART reader
        |
        v
LED debug / vehicle control integration

MicroPython openround.py
        |
        +-- TB6612FNG motor driver
        +-- Steering servo
        +-- US-100 ultrasonic distance sensor
        +-- MPU9250 gyro over I2C
```

## Programming Environment and Tools

### ESP32-CAM Vision Module

- **Language**: Arduino C++
- **Target board**: AI Thinker ESP32-CAM
- **Main library**: `esp_camera`
- **Camera format**: RGB565
- **Frame size**: QQVGA, 160x120
- **Output protocol**: Serial at 115200 baud

### MicroPython Controller Utilities

- **Language**: MicroPython
- **Hardware APIs**: `machine.Pin`, `machine.PWM`, `machine.I2C`, `machine.UART`
- **Actuators**: Steering servo and TB6612FNG motor driver
- **Sensors**: MPU9250 gyro and US-100 ultrasonic distance sensor
- **Debugging**: Console output and onboard LED blink feedback

## Core Software Components

| File | Language | Purpose |
| --- | --- | --- |
| [`camera.cpp`](camera.cpp) | Arduino C++ | ESP32-CAM color detection for red and green objects |
| [`camera_uart_blink.py`](camera_uart_blink.py) | MicroPython | UART receiver test that blinks LED on camera color messages |
| [`openround.py`](openround.py) | MicroPython | Open-round drive logic with gyro-assisted 90-degree corner turns |
| [`servo_tune.py`](servo_tune.py) | MicroPython | Servo center, direction, and PID steering tuning utility |

## Vision System

The ESP32-CAM code reads RGB565 frames at 160x120 resolution and scans the lower part of the image. Scanning starts at `ROI_Y_START = 30` and skips pixels with `STEP_X = 2` and `STEP_Y = 2` to reduce processing time.

### Color Detection Strategy

The camera converts each RGB565 pixel into RGB888 values and checks threshold rules:

- **Red**: high red channel, low green and blue channels, and red dominance over both other channels.
- **Green**: high green channel, limited red and blue channels, and green dominance over both other channels.
- **Minimum area**: detections must exceed `RED_MIN_AREA` or `GREEN_MIN_AREA`.

When both colors are visible, red is prioritized if it has at least as much detected area as green.

### Camera Output Format

The camera writes one line per frame:

```text
RED,<center_x>,<pixel_count>
GREEN,<center_x>,<pixel_count>
NONE
```

This compact format is easy to parse on a second microcontroller and avoids sending full images over UART.

## Open Round Navigation

`openround.py` implements a simple open-round strategy for repeated corner turns:

1. Center the servo and calibrate the gyro.
2. Drive straight with PID steering toward `target_yaw`.
3. Read front distance with the US-100 sensor.
4. If an obstacle or wall is closer than `TURN_DISTANCE_CM`, enter turn mode.
5. Hold full steering left or right until the gyro reports about 90 degrees of yaw change.
6. Reset yaw, briefly ignore corner detection, and continue.
7. After `STOP_AFTER_TURNS = 16`, drive straight briefly and stop.

### State Machine

```text
STRAIGHT
   |
   | distance < TURN_DISTANCE_CM
   v
TURN
   |
   | turned angle >= TURN_ANGLE - TURN_TOLERANCE
   v
STRAIGHT or FINAL_STRAIGHT_BEFORE_STOP
   |
   | final timer complete
   v
STOPPED
```

## Control System

The steering controller uses a basic PID loop:

```python
error = target_yaw - yaw
integral += error * dt
derivative = (error - last_error) / dt
output = (KP * error) + (KI * integral) + (KD * derivative)
```

The correction is applied around `SERVO_CENTER`. If `SERVO_REVERSE` is enabled, positive correction moves the servo in the opposite direction. This makes the same control code usable when the steering linkage orientation changes.

Current tuning values:

| Parameter | Value |
| --- | --- |
| `SERVO_MIN` | 30 |
| `SERVO_CENTER` | 65 |
| `SERVO_MAX` | 100 |
| `KP` | 1.8 |
| `KI` | 0.00 |
| `KD` | 0.25 |
| `MOTOR_SPEED_STRAIGHT` | 30 |
| `MOTOR_SPEED_TURN` | 50 |

## UART Test Utility

`camera_uart_blink.py` validates the camera serial output without needing the full vehicle logic. It reads UART lines and blinks the onboard LED:

- `RED` -> one blink
- `GREEN` -> two blinks
- `NONE` -> re-arms the detector

The script avoids repeated blinking while the same color remains visible. This makes it easier to confirm whether the camera is detecting new objects or continuously seeing the same object.

## Servo Tuning Utility

`servo_tune.py` helps tune steering limits and center position:

1. Center the servo.
2. Calibrate the MPU9250 gyro.
3. Hold straight using the PID controller for `PID_START_TIME_MS`.
4. Move to `TEST_SERVO_ANGLE`.
5. Keep the servo at that angle for mechanical inspection.

This is useful for checking whether `SERVO_MIN`, `SERVO_CENTER`, `SERVO_MAX`, and `SERVO_REVERSE` match the physical steering geometry.

## Hardware Pin Summary

### MicroPython Controller

| Signal | Pin |
| --- | --- |
| Servo PWM | 14 |
| Motor PWMA | 16 |
| Motor AIN2 | 17 |
| Motor AIN1 | 18 |
| Motor STBY | 19 |
| I2C SDA | 4 |
| I2C SCL | 5 |
| Ultrasonic TRIG | 10 |
| Ultrasonic ECHO | 11 |
| Camera UART TX | 0 |
| Camera UART RX | 1 |

### AI Thinker ESP32-CAM

The ESP32-CAM pin mapping follows the standard AI Thinker camera layout in `camera.cpp`, including XCLK on GPIO0, SCCB on GPIO26/GPIO27, and RGB data pins on GPIO5, GPIO18, GPIO19, GPIO21, GPIO34, GPIO35, GPIO36, and GPIO39.

## Testing and Validation

Recommended validation order:

1. Upload `camera.cpp` to the ESP32-CAM and confirm `ESP32_CAM_READY`.
2. Place red and green objects in view and confirm serial messages.
3. Run `camera_uart_blink.py` on the MicroPython controller and verify LED blink behavior.
4. Run `servo_tune.py` to confirm steering limits and PID direction.
5. Run `openround.py` on blocks or a safe test area to verify motor direction.
6. Test the full open-round behavior on the WRO track at low speed first.

## Deployment Instructions

### ESP32-CAM

1. Open `camera.cpp` in the Arduino IDE or compatible ESP32 build environment.
2. Select the AI Thinker ESP32-CAM board profile.
3. Build and upload the firmware.
4. Open the serial monitor at 115200 baud.
5. Confirm that `ESP32_CAM_READY` appears.

### MicroPython Controller

Copy the required `.py` file to the MicroPython board filesystem:

```bash
cp openround.py /path/to/micropython-board/
cp servo_tune.py /path/to/micropython-board/
cp camera_uart_blink.py /path/to/micropython-board/
```

Rename the active script to `main.py` if automatic startup is needed.

## Photo Documentation To Add

Photos can be added later to improve the documentation:

- Full robot wiring layout
- ESP32-CAM mount and field of view
- Servo linkage and center position
- MPU9250 and US-100 placement
- Open-round track testing setup

## Engineering Notes

- The camera intentionally uses a small frame size and pixel skipping for faster detection.
- The gyro is calibrated at startup, so the robot must stay still during calibration.
- `TURN_IGNORE_AFTER_TURN_MS` prevents the same wall from being counted as a new corner immediately after turning.
- The code favors simple thresholds and state machines so behavior can be tuned quickly during physical testing.

## Future Improvements

- Add a shared UART protocol between the camera and main driving script.
- Save tuning constants in a separate configuration file.
- Add separate test scripts for motor, ultrasonic sensor, gyro, and UART.
- Add lighting-condition calibration notes for red and green thresholds.
- Add photos and short videos linked from the documentation folders.

---

This source documentation is intended to make the WRO Future Engineers software understandable, testable, and easy to tune during robot development.
