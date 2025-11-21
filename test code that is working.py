from machine import Pin, PWM
import time

# ===== PWM Frequency =====
FREQ = 1000

# ===== Motor Driver 1 (Motors 1 & 2) =====
IN1 = Pin(12, Pin.OUT)  # Motor 1
IN2 = Pin(13, Pin.OUT)

IN3 = Pin(16, Pin.OUT)  # Motor 2
IN4 = Pin(17, Pin.OUT)

ENA = PWM(Pin(14))
ENB = PWM(Pin(25))
ENA.freq(FREQ)
ENB.freq(FREQ)

# ===== Motor Driver 2 (Motors 3 & 4) =====
IN5 = Pin(18, Pin.OUT)  # Motor 3
IN6 = Pin(19, Pin.OUT)

IN7 = Pin(23, Pin.OUT)  # Motor 4
IN8 = Pin(5, Pin.OUT)

ENC = PWM(Pin(26))
END = PWM(Pin(27))
ENC.freq(FREQ)
END.freq(FREQ)

# ===== Helper to set PWM duty =====
def set_speed(pwm, duty):
    pwm.duty(int(duty * 1023))   # duty from 0.0–1.0

# ===== STOP all motors =====
def stop():
    IN1.value(0); IN2.value(0)
    IN3.value(0); IN4.value(0)
    IN5.value(0); IN6.value(0)
    IN7.value(0); IN8.value(0)
    set_speed(ENA, 0);  set_speed(ENB, 0)
    set_speed(ENC, 0);  set_speed(END, 0)

# ===== FORWARD test =====
def forward(speed=0.6):

    # ===== Motor 1 (Front Left) — REVERSED FIXED =====
    IN1.value(0)
    IN2.value(1)

    # ===== Motor 2 (Front Right) =====
    IN3.value(1)
    IN4.value(0)

    # ===== Motor 3 (Back Left) =====
    IN5.value(1)
    IN6.value(0)

    # ===== Motor 4 (Back Right) =====
    IN7.value(1)
    IN8.value(0)

    # Set PWM speed (0.0 – 1.0)
    set_speed(ENA, speed)
    set_speed(ENB, speed)
    set_speed(ENC, speed)
    set_speed(END, speed)

# ===== MAIN TEST =====
print("Forward test: running motors for 2 seconds...")
forward(0.6)
time.sleep(2)

print("Stopping motors.")
stop()

