from machine import Pin, PWM, UART
import time

# robot state
mission_check = 0
mission_phase = 0

x_coord = 0.0
y_coord = 0.0
angle = 0.0

# timing
last_aruco = 0
aruco_int = 5000

# arena
ARENA_X = 4.0
ARENA_Y = 2.0

# motor pins
IN1 = Pin(5, Pin.OUT)
IN2 = Pin(16, Pin.OUT)
IN3 = Pin(17, Pin.OUT)
IN4 = Pin(18, Pin.OUT)

IN5 = Pin(19, Pin.OUT)
IN6 = Pin(23, Pin.OUT)
IN7 = Pin(12, Pin.OUT)
IN8 = Pin(13, Pin.OUT)

ENA = PWM(Pin(14), freq=20000)
ENB = PWM(Pin(25), freq=20000)
ENC = PWM(Pin(26), freq=20000)
END = PWM(Pin(27), freq=20000)

uart = UART(1, baudrate=115200, tx=4, rx=2)

def pwm_set(p, v):
    duty = int(abs(v) * 1023)
    p.duty(duty)

def set_motor(a, b, pwm, v):
    if v >= 0:
        a.value(1)
        b.value(0)
    else:
        a.value(0)
        b.value(1)
    pwm_set(pwm, v)

def mecanum(vx, vy, w):
    FL = vx - vy - w
    FR = vx + vy + w
    RL = vx + vy - w
    RR = vx - vy + w

    set_motor(IN1, IN2, ENA, FL)
    set_motor(IN5, IN6, ENC, FR)
    set_motor(IN3, IN4, ENB, RL)
    set_motor(IN7, IN8, END, RR)

def stop():
    mecanum(0, 0, 0)

def readAruco():
    global x_coord, y_coord, angle, mission_check
    if uart.any():
        line = uart.readline().decode().strip()
        parts = line.split()

        if len(parts) >= 3:
            x_coord = float(parts[0])
            y_coord = float(parts[1])
            angle = float(parts[2])
            if len(parts) == 4:
                mission_check = int(parts[3])
        elif "START" in line:
            mission_check = 1
        elif "STOP" in line:
            mission_check = 0

def at_pos(tx, ty, tol):
    return abs(x_coord - tx) < tol and abs(y_coord - ty) < tol

def orient():
    if angle > 0.2:
        mecanum(0, 0, -0.2)
    elif angle < -0.2:
        mecanum(0, 0, 0.2)

def wall_follow():
    if y_coord < ARENA_Y / 2:
        mecanum(0.1, 0, 0)
    else:
        mecanum(-0.1, 0, 0)

def cross_log():
    mecanum(0.2, 0, 0)

mission_y = 0
goal_y = 0

stop()

while True:
    if mission_check != 1:
        readAruco()
        continue

    if mission_phase == 0:
        if y_coord > ARENA_Y * 0.75:
            mission_y = ARENA_Y * 0.25
            goal_y = ARENA_Y * 0.90
        else:
            mission_y = ARENA_Y * 0.75
            goal_y = ARENA_Y * 0.10
        mission_phase = 1

    now = time.ticks_ms()
    if time.ticks_diff(now, last_aruco) >= aruco_int:
        readAruco()
        last_aruco = now

    if mission_phase == 1:
        orient()
        wall_follow()

        if 3.0 < x_coord < 3.4:
            cross_log()

        dx = 2.0 - x_coord
        dy = mission_y - y_coord
        mecanum(dx * 0.3, dy * 0.3, 0)

        if at_pos(2.0, mission_y, 0.15):
            stop()
            time.sleep(2)
            mission_phase = 2

    if mission_phase == 2:
        time.sleep(3)
        mission_phase = 3

    if mission_phase == 3:
        orient()
        dx = 2.0 - x_coord
        dy = goal_y - y_coord
        mecanum(dx * 0.3, dy * 0.3, 0)

        if at_pos(2.0, goal_y, 0.15):
            stop()
            break

    readAruco()
