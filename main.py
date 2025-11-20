from machine import Pin, PWM
from time import sleep

# L298N motor control pins

# ---Left driver--- #
#motor 1 (front left)
IN1 = Pin(5, Pin.OUT)
IN2 = Pin(16, Pin.OUT)

#motor 2 (rear left)
IN3 = Pin(17, Pin.OUT)
IN4 = Pin(18, Pin.OUT)

lENA = PWM(Pin(25))
lENB = PWM(Pin(26))

# ---Right driver--- #
#motor 3 (front right)
IN5 = Pin(12, Pin.OUT)
IN6 = Pin(13, Pin.OUT)

#motor 4 (rear right)
IN7 = Pin(19, Pin.OUT)
IN8 = Pin(23, Pin.OUT)

rENA = PWM(Pin(27))
rENB = PWM(Pin(14))

# PWM for ENA/B pins 
lENA.freq(1000)  
rENA.freq(1000)  
lENB.freq(1000)  
rENB.freq(1000)  

def motor_forward(speed):
  
    IN1.value(1); IN2.value(0)
    IN3.value(1); IN4.value(0)
    IN5.value(1); IN6.value(0)
    IN7.value(1); IN8.value(0)
    lENA.duty(speed)
    rENA.duty(speed)
    lENB.duty(speed)
    rENB.duty(speed)

def motor_backward(speed):
   
    IN1.value(0); IN2.value(1)
    IN3.value(0); IN4.value(1)
    IN5.value(0); IN6.value(1)
    IN7.value(0); IN8.value(1)
    lENA.duty(speed)
    rENA.duty(speed)
    lENB.duty(speed)
    rENB.duty(speed)

def motor_stop():
    """Stop the motor."""
    IN1.value(0)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)
    IN5.value(0)
    IN6.value(0)
    IN7.value(0)
    IN8.value(0)
    lENA.duty(0)
    rENA.duty(0)
    lENB.duty(0)
    rENB.duty(0)
    
# Example demo loop
while True:
    print("Forward")
    motor_forward(600)  
    sleep(30)

    print("Stop")
    motor_stop()


