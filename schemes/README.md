# Electronics Schemes

This directory documents the electronics used in the WRO 2026 Future Engineers robot. It includes the main wiring scheme and reference photos for the controller, sensors, motor driver, power system, drive motor, and steering servo.

## Main Wiring Scheme

![Complete electronics wiring scheme](electronicsheme.jpeg)

The main scheme shows the robot electronics connected around a Raspberry Pi Pico 2 W H controller. The robot uses a separate ESP32-CAM for camera vision, a TB6612FNG motor driver for the DC drive motor, buck converters for voltage regulation, and I2C/UART-connected sensors for navigation.

## Component List

| Component | Image | Purpose |
| --- | --- | --- |
| Raspberry Pi Pico 2 W H | [`rpipico2wh.jpg`](rpipico2wh.jpg) | Main MicroPython controller for motor, servo, sensors, and navigation logic |
| ESP32-CAM | [`esp32cam.jpg`](esp32cam.jpg) | Vision module for red/green obstacle detection and UART output |
| TB6612FNG motor driver | [`tb6612fng.jpg`](tb6612fng.jpg) | Drives the 6 V DC motor from Pico PWM/direction signals |
| 6 V micro DC motor | [`6vmicrodc.jpg`](6vmicrodc.jpg) | Main drive motor for the rear/front drive system |
| HD-1440A servo | [`hd1440aservo.jpg`](hd1440aservo.jpg) | Steering actuator |
| US-100 ultrasonic sensor | [`us100.jpg`](us100.jpg) | Front distance sensor for wall/corner detection |
| MPU9250 IMU | [`mpu9250.jpg`](mpu9250.jpg) | Gyro yaw measurement for turns and heading correction |
| TCS34725 color sensor | [`tcs34725.jpg`](tcs34725.jpg) | Color sensing reference/backup module |
| LM2596 / RT3505 buck converter | [`rt3505.jpg`](rt3505.jpg) | Voltage regulation for logic and actuator rails |
| 6S 450 mAh LiPo battery | [`6s450mah40lipo.jpg`](6s450mah40lipo.jpg) | Main robot power source |
| On/off switch | [`switchonoff.jpg`](switchonoff.jpg) | Main power switching |

## Power Distribution

The battery feeds the power regulation stage through the main switch. Buck converters step the battery voltage down for the electronics and actuator rails. All modules share a common ground, which is required for stable PWM, I2C, UART, trigger/echo, and camera communication.

Important power notes:

- Keep motor/servo power separate from low-voltage logic where possible.
- Connect all grounds together at a common reference point.
- Confirm buck converter output voltage before connecting the Pico, ESP32-CAM, sensors, or servo.
- Use short, secure power wiring for motor and servo loads.

## Signal Connections

The software in `src/` expects the following main signal groups:

| Signal group | Connected modules |
| --- | --- |
| PWM steering | Pico 2 W H to HD-1440A servo |
| PWM/direction motor control | Pico 2 W H to TB6612FNG |
| I2C bus | Pico 2 W H to MPU9250 and TCS34725 |
| Ultrasonic distance | Pico 2 W H to US-100 trigger/echo |
| Camera UART | ESP32-CAM serial output to Pico UART input |

## Voltage Divider Notes

The scheme includes resistor dividers on signal paths that need level protection. In the drawing, 1 kOhm and 2 kOhm resistors are used near the camera and ultrasonic signal wiring. These are intended to reduce higher-voltage signals before they reach 3.3 V logic pins.

Before powering the robot:

1. Check every buck converter output with a multimeter.
2. Confirm that the ESP32-CAM and Pico share ground.
3. Confirm that UART TX/RX wiring is crossed correctly.
4. Confirm that US-100 echo voltage is safe for the Pico input.
5. Confirm motor polarity before running autonomous code.

## Development Photos

### Raspberry Pi Pico 2 W H

![Raspberry Pi Pico 2 W H](rpipico2wh.jpg)

### ESP32-CAM

![ESP32-CAM](esp32cam.jpg)

### Motor Driver

![TB6612FNG motor driver](tb6612fng.jpg)

### Sensors

![US-100 ultrasonic sensor](us100.jpg)

![MPU9250 IMU](mpu9250.jpg)

![TCS34725 color sensor](tcs34725.jpg)

### Actuators and Power

![6 V micro DC motor](6vmicrodc.jpg)

![HD-1440A steering servo](hd1440aservo.jpg)

![6S 450 mAh LiPo battery](6s450mah40lipo.jpg)

![On/off switch](switchonoff.jpg)

![Buck converter module](rt3505.jpg)

## Integration With Software

The electronics in this folder correspond to the source files in `src/`:

- `openround.py` uses the servo, motor driver, US-100, and MPU9250.
- `obstacleround.py` adds ESP32-CAM UART color data and obstacle-passing behavior.
- `servo_tune.py` is used to tune steering limits and gyro-assisted PID direction.
- `camera.cpp` runs on the ESP32-CAM and outputs color detections over serial.

## Checklist Before Testing

- Battery charged and physically secure.
- Buck converter outputs checked.
- Pico, ESP32-CAM, sensors, motor driver, and servo grounds connected together.
- Servo moves in the expected direction.
- Motor spins in the expected direction.
- US-100 distance readings are stable.
- MPU9250 is detected over I2C.
- ESP32-CAM sends valid UART messages.
- Switch can safely cut power.

This folder should be updated whenever the electronics layout, wiring, power system, or sensor placement changes.
