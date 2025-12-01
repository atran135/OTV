from enes100 import enes100
from machine import Pin, PWM
from time import sleep
import math

# ============================
#  MOTOR SETUP (Your hardware)
# ============================

# ---Left driver--- #
IN1 = Pin(5, Pin.OUT)
IN2 = Pin(16, Pin.OUT)
IN3 = Pin(17, Pin.OUT)
IN4 = Pin(18, Pin.OUT)
lENA = PWM(Pin(26))
lENB = PWM(Pin(27))

# ---Right driver--- #
IN5 = Pin(12, Pin.OUT)
IN6 = Pin(13, Pin.OUT)
IN7 = Pin(19, Pin.OUT)
IN8 = Pin(23, Pin.OUT)
rENA = PWM(Pin(25))
rENB = PWM(Pin(14))

lENA.freq(1000)
lENB.freq(1000)
rENA.freq(1000)
rENB.freq(1000)

# --- MOTOR CONTROL ---
def left_motor(speed):     # speed: -65535 to +65535
    if speed > 0:          # forward
        IN1.value(1)
        IN2.value(0)
        IN3.value(1)
        IN4.value(0)
        lENA.duty_u16(speed)
        lENB.duty_u16(speed)
    elif speed < 0:        # backward
        IN1.value(0)
        IN2.value(1)
        IN3.value(0)
        IN4.value(1)
        lENA.duty_u16(-speed)
        lENB.duty_u16(-speed)
    else:
        IN1.value(0); IN2.value(0)
        IN3.value(0); IN4.value(0)
        lENA.duty_u16(0)
        lENB.duty_u16(0)

def right_motor(speed):    # speed: -65535 to +65535
    if speed > 0:          # forward
        IN5.value(1)
        IN6.value(0)
        IN7.value(1)
        IN8.value(0)
        rENA.duty_u16(speed)
        rENB.duty_u16(speed)
    elif speed < 0:        # backward
        IN5.value(0)
        IN6.value(1)
        IN7.value(0)
        IN8.value(1)
        rENA.duty_u16(-speed)
        rENB.duty_u16(-speed)
    else:
        IN5.value(0); IN6.value(0)
        IN7.value(0); IN8.value(0)
        rENA.duty_u16(0)
        rENB.duty_u16(0)
        
def left_shift(speed):
        #front left
        IN1.value(0)
        IN2.value(1)
        #rear left
        IN3.value(1)
        IN4.value(0)
        lENA.duty_u16(speed)
        lENB.duty_u16(speed)
        #front right
        IN5.value(1)
        IN6.value(0)
        #rear right
        IN7.value(0)
        IN8.value(1)
        rENA.duty_u16(speed)
        rENB.duty_u16(speed)

def right_shift(speed):
        #front left
        IN1.value(1)
        IN2.value(0)
        #rear left
        IN3.value(0)
        IN4.value(1)
        lENA.duty_u16(speed)
        lENB.duty_u16(speed)
        #front right
        IN5.value(0)
        IN6.value(1)
        #rear right
        IN7.value(1)
        IN8.value(0)
        rENA.duty_u16(speed)
        rENB.duty_u16(speed)

def drive(left_speed, right_speed):
    left_motor(left_speed)
    right_motor(right_speed)

def stop():
    left_motor(0)
    right_motor(0)

# ============================
#   ENES100 SETUP
# ============================

enes100.begin("towmaters", "seed", 345, 1116)
sleep(0.5)

yStart = enes100.y
# Tolerances
POSITION_TOL = 0.015
HEADING_TOL = 0.05

# ============================
#   NAVIGATION LOOP
# ============================
if(enes100.y > 0.75):
    desired_initial_heading = 0   
    # Target destination (meters)
    x_target = 0.5
    y_target = 0.5

else:
    desired_initial_heading = 0
    # Target destination (meters)
    x_target = 0.5
    y_target = 1.5
    
# =============================
#   PHASE 1: TURN TO HEADING
# =============================

while True:
    heading = enes100.theta

    # compute wrapped angle error
    error = desired_initial_heading - heading
    if error > math.pi: error -= 2*math.pi
    if error < -math.pi: error += 2*math.pi

    print("Heading:", heading, "Error:", error)

    if abs(error) < HEADING_TOL:
        stop()
        #print("Aligned! Starting navigation...")
        sleep(0.5)
        break

    turn_speed = 25000

    if error > 0:
        drive(-turn_speed, turn_speed)   # turn left
    else:
        drive(turn_speed, -turn_speed)   # turn right

    sleep(0.1)


# =============================
#   PHASE 2: DRIVE TO TARGET
# =============================


while True:
    x = enes100.x #Sets x to aruco markers reading
    y = enes100.y #Sets y to aruco markers reading
    
    heading = enes100.theta

    dx = x_target - x
    dy = y_target - y
    distance = math.sqrt(dx*dx + dy*dy)

    if distance < POSITION_TOL:
        stop()
        #print("Arrived at target!")
        enes100.print("Arrived at target!")
        break

    desired_heading = 0
    error = desired_heading - heading

    # wrap error
    if error > math.pi: error -= 2*math.pi
    if error < -math.pi: error += 2*math.pi

    if abs(error) > HEADING_TOL:
        # turn to correct heading
        turn_speed = 25000
        if error > 0:
            drive(-turn_speed, turn_speed)
        else:
            drive(turn_speed, -turn_speed)
    else:
        if(yStart > 0.75):
            right_shift(40000)
        else:
            left_shift(40000)

    sleep(1)

# =================================
#   PHASE 3: DRIVE TO SIDE WALL
# =================================

x_target2 = 0.5 #End target of x
y_target2 = 0.125 #End target of y

while True:
    x = enes100.x #Sets x to aruco markers reading
    y = enes100.y #Sets y to aruco markers reading
    
    heading = enes100.theta

    dx = x_target2 - x
    dy = y_target2 - y
    distance = math.sqrt(dx*dx + dy*dy)

    if distance < POSITION_TOL:
        stop()
        #print("Arrived at wall!")
        enes100.print("Arrived at wall!")
        break

    desired_heading = 0
    error = desired_heading - heading

    # wrap error
    if error > math.pi: error -= 2*math.pi
    if error < -math.pi: error += 2*math.pi

    if abs(error) > HEADING_TOL:
        # turn to correct heading
        turn_speed = 25000
        if error > 0:
            drive(-turn_speed, turn_speed)
        else:
            drive(turn_speed, -turn_speed)
    else:
            right_shift(40000)

    sleep(1)

# =================================
#   PHASE 4: DRIVE ALONG SIDE WALL
# =================================

x_target3 = 3.75 #End target of x
y_target3 = 0.125 #End target of y

while True:
    x = enes100.x #Sets x to aruco markers reading
    y = enes100.y #Sets y to aruco markers reading
    
    heading = enes100.theta

    dx = x_target3 - x
    dy = y_target3 - y
    distance = math.sqrt(dx*dx + dy*dy)

    if distance < POSITION_TOL:
        stop()
        print("Arrived at finish!")
        enes100.print("Arrived at finish!")
        break

    desired_heading = 0
    error = desired_heading - heading

    # wrap error
    if error > math.pi: error -= 2*math.pi
    if error < -math.pi: error += 2*math.pi

    if abs(error) > HEADING_TOL:
        # turn to correct heading
        turn_speed = 25000
        if error > 0:
            drive(-turn_speed, turn_speed)
        else:
            drive(turn_speed, -turn_speed)
    else:
            drive(40000)

    sleep(1)
