import RPi.GPIO as GPIO
from time import sleep

servoPIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

pwm = GPIO.PWM(servoPIN, 50) # GPIO 23 for PWM with 50Hz
pwm.start(0) # Initialization

def SetAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(23, True)
    pwm.ChangeDutyCycle(duty)
    sleep(0.55)
    GPIO.output(23, False)
    pwm.ChangeDutyCycle(0)
def on():
    SetAngle(15)
def off():
    SetAngle(60)

off()
# try:
#     while 1:
#         SetAngle(20)
#         sleep(3)
#         SetAngle(60)
#         sleep(3)
# except KeyboardInterrupt:
#     pwm.stop()
#     GPIO.cleanup()
