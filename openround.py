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


# =====================================================
# Motor - TB6612FNG
# =====================================================

pwma = PWM(Pin(PWMA_PIN))
pwma.freq(1000)

ain2 = Pin(AIN2_PIN, Pin.OUT)
ain1 = Pin(AIN1_PIN, Pin.OUT)
stby = Pin(STBY_PIN, Pin.OUT)


def motor_forward(speed):
    speed = max(0, min(100, speed))

    stby.value(1)
    ain1.value(1)
    ain2.value(0)

    duty = int((speed / 100) * 65535)
    pwma.duty_u16(duty)


def motor_stop():
    pwma.duty_u16(0)
    ain1.value(0)
    ain2.value(0)
    stby.value(0)


# =====================================================
# US-100 distance sensor
# =====================================================

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

trig.value(0)
time.sleep(0.05)


def read_distance_once():
    trig.value(0)
    time.sleep_us(2)

    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    try:
        duration = time_pulse_us(echo, 1, 30000)
    except OSError:
        return None

    if duration <= 0:
        return None

    distance_cm = duration / 58.0

    if distance_cm < 2 or distance_cm > 450:
        return None

    return distance_cm


def read_distance_cm(samples=2):
    values = []

    for _ in range(samples):
        d = read_distance_once()

        if d is not None:
            values.append(d)

        time.sleep(0.005)

    if len(values) == 0:
        return None

    values.sort()
    return values[len(values) // 2]


# =====================================================
# MPU9250
# =====================================================

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=400000)

devices = i2c.scan()
print("I2C devices:", devices)

MPU_ADDR = 0x68

if MPU_ADDR not in devices:
    print("0x68 not found, trying 0x69...")
    MPU_ADDR = 0x69

if MPU_ADDR not in devices:
    print("MPU9250 not found. Check the wiring.")

    while True:
        motor_stop()
        servo_center()
        time.sleep(1)

i2c.writeto_mem(MPU_ADDR, 0x6B, b"\x00")
time.sleep(0.05)

# Gyro +-250 dps
i2c.writeto_mem(MPU_ADDR, 0x1B, b"\x00")

# Accel +-2g
i2c.writeto_mem(MPU_ADDR, 0x1C, b"\x00")


def read_word(reg):
    high = i2c.readfrom_mem(MPU_ADDR, reg, 1)[0]
    low = i2c.readfrom_mem(MPU_ADDR, reg + 1, 1)[0]

    value = (high << 8) | low

    if value > 32767:
        value -= 65536

    return value


def read_gyro():
    gx_raw = read_word(0x43)
    gy_raw = read_word(0x45)
    gz_raw = read_word(0x47)

    gx = gx_raw / 131.0
    gy = gy_raw / 131.0
    gz = gz_raw / 131.0

    return gx, gy, gz


def calibrate_gyro(samples=400):
    print("Gyro calibration starting. Keep the robot still...")

    gx_sum = 0
    gy_sum = 0
    gz_sum = 0

    for _ in range(samples):
        gx, gy, gz = read_gyro()

        gx_sum += gx
        gy_sum += gy
        gz_sum += gz

        time.sleep(0.004)

    print("Calibration complete.")

    return gx_sum / samples, gy_sum / samples, gz_sum / samples
