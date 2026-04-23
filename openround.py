from machine import I2C, PWM, Pin, time_pulse_us
import time

# =====================================================
# Pins
# =====================================================

SERVO_PIN = 14

PWMA_PIN = 16
AIN2_PIN = 17
AIN1_PIN = 18
STBY_PIN = 19

SDA_PIN = 4
SCL_PIN = 5

TRIG_PIN = 10
ECHO_PIN = 11


# =====================================================
# Settings
# =====================================================

SERVO_MIN = 30
SERVO_MAX = 100
SERVO_CENTER = 65

SERVO_REVERSE = True

# LEFT or RIGHT
CORNER_DIRECTION = "LEFT"

MOTOR_SPEED_STRAIGHT = 30
MOTOR_SPEED_TURN = 50

# No slowdown before turning. The robot switches directly into turning at this distance.
TURN_DISTANCE_CM = 40

TURN_ANGLE = 90
TURN_TOLERANCE = 5

# Stop after the 16th corner turn.
STOP_AFTER_TURNS = 16

# After the 16th turn, drive straight a little more before stopping.
# Increase to 900 / 1100 if it stops too early.
# Decrease to 500 if it goes too far.
STOP_AFTER_LAST_TURN_MS = 700

# Briefly ignore corners after a turn so the same wall is not counted again.
TURN_IGNORE_AFTER_TURN_MS = 350

KP = 1.8
KI = 0.00
KD = 0.25


# =====================================================
# Servo
# =====================================================

servo = PWM(Pin(SERVO_PIN))
servo.freq(50)


def set_servo_angle(angle):
    angle = max(SERVO_MIN, min(SERVO_MAX, angle))

    min_us = 500
    max_us = 2500
    pulse_us = min_us + (angle / 180) * (max_us - min_us)

    duty = int((pulse_us / 20000) * 65535)
    servo.duty_u16(duty)


def servo_full_left():
    set_servo_angle(SERVO_MAX)


def servo_full_right():
    set_servo_angle(SERVO_MIN)


def servo_center():
    set_servo_angle(SERVO_CENTER)


def set_servo_pid(correction):
    if SERVO_REVERSE:
        servo_angle = SERVO_CENTER - correction
    else:
        servo_angle = SERVO_CENTER + correction

    servo_angle = max(SERVO_MIN, min(SERVO_MAX, servo_angle))
    set_servo_angle(servo_angle)

    return servo_angle
