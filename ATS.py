import RPi.GPIO as GPIO
import threading
import logging
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)
# GPIO.setup(23, GPIO.OUT, initial=GPIO.LOW)
# GPIO.setup(24, GPIO.OUT, initial=GPIO.LOW)

# event = threading.Event
# thread = threading.Thread(target=SwitchTo, args=(switchingTime))
# thread_two = threading.Thread(target=SwitchTo, args=(switchingTime))
# thread.start()
# thread_two.start()
# Parameter
PLN=24
INV=22
# print("GPIO PIN  : ",INV[0],INV[1])
switchingTime=0.009 #for test use 2s

def SwitchTo(Target) :
    # print("Status Before Switch : ", GPIO.input(PLN[0]),GPIO.input(PLN[1]),GPIO.input(INV[0]),GPIO.input(INV[1]))
    # print("Target : ", Target)
    if Target == "PLN" :
        # print ("TF PLN execute")
        if (GPIO.input(PLN)==0 and GPIO.input(PLN)==0) :
            # print ("TF PLN Switching")
            GPIO.output(INV,0)
            GPIO.output(INV,0)

            # Delay change to uninteruptable
            time.sleep(switchingTime)

            GPIO.output(PLN,1)
            GPIO.output(PLN,1)
            State = "PLN"
            print("Status : ",State)
        # elif (GPIO.input(PLN)==1 and GPIO.input(PLN)==1) :
        #     print("Already PLN ")
    elif Target == "INV" :
        # print("B")
        # print(GPIO.input(INV),GPIO.input(INV))
        if (GPIO.input(INV)==0 and GPIO.input(INV)==0):
            GPIO.output(PLN,0)
            GPIO.output(PLN,0)
            # print("A")
            # Delay change to uninteruptable
            time.sleep(switchingTime)

            GPIO.output(INV,1)
            GPIO.output(INV,1)
            State = "INV"
            print("Status : ",State)
        # elif (GPIO.input(INV)==1 and GPIO.input(INV)==1) :
        #     print("Already INV ")
    else:
        print("not PLN or INV ERROR !!")
def SwitchStat():
    # print("Status After Switch : ", GPIO.input(PLN),GPIO.input(PLN),GPIO.input(INV),GPIO.input(INV))
    if (GPIO.input(PLN)==0 and GPIO.input(PLN)==0) and (GPIO.input(INV)==1 and GPIO.input(INV)==1) : 
        Status = "INV"
    elif (GPIO.input(PLN)==1 and GPIO.input(PLN)==1) and (GPIO.input(INV)==0 and GPIO.input(INV)==0):
        Status = "PLN"
    else :
        Status = "Undefined"
    return(Status)
# SwitchTo("PLN")