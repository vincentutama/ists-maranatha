# Perbaiki mekanisme servo
# perbaiki diplay oled
# perbaiki timing programdelay
# 

import time
import datetime
# from i2cRead import i2cRead
import RPi.GPIO as GPIO
import oled
import Adafruit_ADS1x15

# =======PinOut========
pvVoltageCH = 0
pvCurrentCH = 1
BattVoltageCH = 2
BattCurrentCH = 3
autoButton =4 #pilih mode
manualButton = 17 #pilih PLN atau INV
PLN=24
INV=22

#Variable
x=0
status="PLN"
programDelay=0.01

#mode
defaultATS="PLN"
availMode=[0,1,2,3,4]
defaultMode = 0 
subMode = 0 #Manual 0 PLN 1 INV || Auto 2 Max 3 Normal 4 Backup 
#max->use PV as posible ,save->keep batery over 85% ,backup-> charge when grid available, 
# manual selector->pln/inv

#GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(autoButton, GPIO.IN) #Auto Mode 1
GPIO.setup(manualButton, GPIO.IN) #Manual Mode 0
GPIO.setup(24, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)

#i2c 
#i2c setup
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
def i2cRead(channelSelect):
    # time.sleep(1)
    return(0.000124219*adc.read_adc(channelSelect,gain=GAIN))

#module ATS
class TransferSwitch:
    PLN=24
    INV=22
    switchingTime=0.009 #for test use 2s
    def __init__(self):
        print("ATS initiated")
    def SwitchTo(self, Target) :
        if Target == "PLN" :
            if (GPIO.input(self.PLN)==0 and GPIO.input(self.PLN)==0) :
                GPIO.output(self.INV,0)
                GPIO.output(self.INV,0)

                time.sleep(self.switchingTime)

                GPIO.output(self.PLN,1)
                GPIO.output(self.PLN,1)
                self.State = "PLN"
                print("Status : ",self.State)
        elif Target == "INV" :
            if (GPIO.input(self.INV)==0 and GPIO.input(self.INV)==0):
                GPIO.output(self.PLN,0)
                GPIO.output(self.PLN,0)
                # print("A")
                # Delay change to uninteruptable
                time.sleep(self.switchingTime)

                GPIO.output(self.INV,1)
                GPIO.output(self.INV,1)
                self.State = "INV"
                print("Status : ",self.State)
        else:
            print("not PLN or INV ERROR !!")
    def SwitchStat(self):
        # print("Status After Switch : ", GPIO.input(PLN),GPIO.input(PLN),GPIO.input(INV),GPIO.input(INV))
        if (GPIO.input(self.PLN)==0 and GPIO.input(self.PLN)==0) and (GPIO.input(self.INV)==1 and GPIO.input(self.INV)==1) : 
            Status = "INV"
        elif (GPIO.input(self.PLN)==1 and GPIO.input(self.PLN)==1) and (GPIO.input(self.INV)==0 and GPIO.input(self.INV)==0):
            Status = "PLN"
        else :
            Status = "Undefined"
        return(Status)

#Servo
servoPIN = 23
GPIO.setup(servoPIN, GPIO.OUT)
class Servo:
    def __init__(self):
        print("Servo initiated")
        self.pwm = GPIO.PWM(servoPIN, 50) # GPIO 23 for PWM with 50Hz
        self.pwm.start(0) # Initialization

    def SetAngle(self,angle):
        duty = angle / 18 + 2
        GPIO.output(23, True)
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(0.55)
        GPIO.output(23, False)
        self.pwm.ChangeDutyCycle(0)
    def on(self):
        # self.SetAngle(15)
        print("servo on")
    def off(self):
        # self.SetAngle(60)
        print("servo off")

# time Setup
now = datetime.datetime.now()

# Class
class Battery:
    capacity=0 #in Ah
    SOC=0 #in %
    def __init__(self,batteryVoltage,PVCurrent,INVCurrent,realBatteryCapacity):
        self.refresh(batteryVoltage,PVCurrent,INVCurrent,realBatteryCapacity)
        
    def refresh(self,batteryVoltage,PVCurrent,INVCurrent,realBatteryCapacity):
        if (PVCurrent<0.5 and INVCurrent < 0.5):
            self.SOC=self.StateOfCharge(batteryVoltage)
            self.capacity=realBatteryCapacity*self.SOC/100
            print("executed Capacity : ",self.capacity)
            
    def StateOfCharge(self,batteryVoltage):
        if batteryVoltage>=13 :
            SOC = 100
                
        elif batteryVoltage<13 and batteryVoltage>=12.75:
            SOC = 90

        elif batteryVoltage<12.75 and batteryVoltage>=12.5:
            SOC = 80

        elif batteryVoltage<12.5 and batteryVoltage>=12.3:
            SOC = 70

        elif batteryVoltage<12.3 and batteryVoltage>=12.15:
            SOC = 60

        elif batteryVoltage<12.15 and batteryVoltage>=12.05:
            SOC = 50
        
        elif batteryVoltage<12.05 and batteryVoltage>=11.95:
            SOC = 40

        elif batteryVoltage<11.95 and batteryVoltage>=11.81:
            SOC = 30

        elif batteryVoltage<11.81 and batteryVoltage>=11.66:
            SOC = 20

        elif batteryVoltage<11.66 and batteryVoltage>=11.51:
            SOC = 10

        elif batteryVoltage<11.51 :
            SOC = 0

        else:
            print("ERROR!! \nBattery Voltage detect : ", batteryVoltage)
        return SOC
    def Discharge(self,INVCurrent):#per hour, so divide Current with 60 Minute and 60 second for 1s refresh rate
        self.capacity-=INVCurrent
    def Charge(self,PVCurrent):
        self.capacity+=PVCurrent

def Current(channelSelect):
    voltageRare=i2cRead(channelSelect)
    Resistance=0.25455#0.0015
    if channelSelect==1:#penyesuaian current PV
        current = voltageRare/Resistance#Bila perlu kalibrasi
    elif channelSelect==3:#penyesuaian current Batt
        current = voltageRare/Resistance#Bila perlu kalibrasi
    return current
def Voltage(channelSelect):
    voltageRare=i2cRead(channelSelect)
    VoltageDivPV=6.599597586
    VoltageDivBatt=6.599597586
    if channelSelect==0:#penyesuaian voltage divider PV
        voltage = voltageRare*VoltageDivPV#Bila perlu kalibrasi
    elif channelSelect==2:#penyesuaian voltage divider Batt
        voltage = (voltageRare*VoltageDivBatt)#Bila perlu kalibrasi
    return voltage

class loop:
    # message="n/a"
    servo=0#off
    mode=0
    lowMode=0
    # Status="null"
    count=0
    x=0
    timerVoltage=0
    ATS=TransferSwitch()
    servo = Servo()
    def __init__(self):
        mode=0
        x=0
    def pln(self):
        self.ATS.SwitchTo("PLN")
        self.Status = "PLN"
        # self.servo.off()
        self.servo=0
    def inv(self):
        # self.servo.on()
        time.sleep(5)
        self.ATS.SwitchTo("INV")
        self.Status = "INV"
        self.servo=1
    def Check(self):
        self.BattCurrent=Current(BattCurrentCH)
        self.BattVoltage=Voltage(BattVoltageCH)
        self.PVVoltage=Voltage(pvVoltageCH)
        if (GPIO.input(manualButton)==1 and self.x==0):
            if self.mode!= 0 :
                self.mode = 0
                self.x=1
                print("Mode change to manual PLN")
                self.pln()
                # ATS.SwitchTo("PLN")
                # self.Status = "PLN"
                # servo.off()
            elif self.mode == 0 and self.x==0:
                self.mode = 1
                self.x=1
                print("Mode change to manual INV")
                self.inv()
                # servo.on()
                # time.sleep(5)
                # ATS.SwitchTo("INV")
                # self.Status = "INV"
        elif (GPIO.input(autoButton)==1):
            if (self.mode < 2 or self.mode ==4) and self.x==0:
                self.mode = 2
                self.x=1
                print("Mode change to Auto Max")   
                self.message= "Mode change to Auto Max"
                self.MaximumMode()
            elif self.mode < 3 and self.x==0:
                self.mode = 3
                self.x=1
                print("Mode change to Auto Normal")
                self.message= "Mode change to Auto Normal"
                self.NormalMode()
            elif self.mode == 3 and self.x==0:
                self.mode = 4
                self.x=1
                print("Mode change to Smart Auto")
                self.message= "Mode change to Smart Auto"
        elif(GPIO.input(autoButton)==0 and GPIO.input(manualButton)==0):
            self.x=0
        if (GPIO.input(PLN)==0 and GPIO.input(PLN)==0) and (GPIO.input(INV)==1 and GPIO.input(INV)==1) : 
            self.Status = "INV"
        elif (GPIO.input(PLN)==1 and GPIO.input(PLN)==1) and (GPIO.input(INV)==0 and GPIO.input(INV)==0):
            self.Status = "PLN"
        else :
            self.Status = "Undefined"
        self.count+=1
        # if(Current(BattCurrentCH)<=1 and self.PVVoltage<=5 and self.count>30*4/programDelay):#selama 30 menit
            # battery.refresh(12.2,0.2,0.2,75)#Ganti dengan parameter asli
            # self.count=0
    def getMode(self):
        return(self.mode)
    def MaximumMode(self):
        if self.PVVoltage<=12.9:
            battReconnect=12.75
            battDisconnect=11.8
        else:
            battReconnect=14
            battDisconnect=12.65
        if self.BattVoltage>=battReconnect:
            self.ATS.SwitchTo("INV")
            self.Status = "INV"
            self.timerVoltage=0
            self.lowMode=0
        elif self.BattVoltage<=battDisconnect:
            self.lowMode=1
            self.timerVoltage+=1
            if (self.timerVoltage>=2/programDelay):#timer selama 4 detik
                self.ATS.SwitchTo("PLN")
                # print("low Voltage")
                self.message="low Voltage"
                self.Status = "PLN"
                if self.servo==1:
                    self.servo.off() #harus 1x aja
                    self.servo=0
        elif self.BattVoltage<battReconnect and self.BattVoltage>battDisconnect and self.lowMode==0:
            self.ATS.SwitchTo("INV")
            self.Status = "INV"
        elif self.BattVoltage>(battReconnect-0.2) and self.lowMode==1:
            if self.servo==0:
                self.servo.on() #harus 1x aja
                self.servo=1
            
    def NormalMode(self):
        if now.hour>=18 or now.hour<7:
           self.MaximumMode()
        else:
            self.pln()

    def SavingMode(self):
        if self.PVVoltage<=12.9:
            battReconnect=12.75
            battDisconnect=12.3
        else:
            battReconnect=14
            battDisconnect=12.8
        if self.BattVoltage>=battReconnect:
            self.ATS.SwitchTo("INV")
            self.Status = "INV"
            self.timerVoltage=0
            self.lowMode=0
        elif self.BattVoltage<=battDisconnect:
            self.lowMode=1
            self.timerVoltage+=1
            if (self.timerVoltage>=2/programDelay):#timer selama 4 detik
                self.ATS.SwitchTo("PLN")
                # print("low Voltage")
                self.message="low Voltage"
                self.Status = "PLN"
                if self.servo==1:
                    self.servo.off() #harus 1x aja
                    self.servo=0
        elif self.BattVoltage<battReconnect and self.BattVoltage>battDisconnect and self.lowMode==0:
            self.ATS.SwitchTo("INV")
            self.Status = "INV"
        elif self.BattVoltage>(battReconnect-0.2) and self.lowMode==1:
            if self.servo==0:
                self.servo.on() #harus 1x aja
                self.servo=1

    def ModeSelector(self,modeSelect):
        if modeSelect==2:
            self.MaximumMode()#pake banyak
        elif modeSelect==3:
            self.NormalMode()#pake malem aja
        elif modeSelect==4:
            self.SavingMode()#pake dikit

class Data:
    def __init__(self):
        print("Data logger initiated")
    def Logging(self,current):
        battery.Discharge(current)

#===Start Program===
def runProgram():
    print("program started")
    battery = Battery(Voltage(BattVoltageCH),0.2,0.2,75) #input parameter battre
    infLoop = loop()
    ATS = TransferSwitch()
    ATS.SwitchTo(defaultATS)
    data=Data()
    arrayMode=["PLN","INV","Max","Night","Saving"]
    print(Voltage(BattVoltageCH))
    print(i2cRead(3))
    print(Current(BattCurrentCH))
    # Loop
    try:
        while 1:
            infLoop.Check()
            infLoop.ModeSelector(infLoop.getMode())
            # print('mode.....', mode())
            # data.Logging(5)
            # if (i<(1/programDelay)):
            localmode=arrayMode[infLoop.getMode()]
            l1="   Mode    : "+localmode
            statusATS = ATS.SwitchStat()
            l2="   Status  : "+statusATS
            l3="   Battery : "+str(battery.StateOfCharge(infLoop.BattVoltage))+'%'
            # else:
            #     l1=str(now.strftime("%a, %b %d %Y "))
            #     l2="PV Voltage : "+str(Voltage(pvVoltageCH))+" V"
            #     l3="Daya : "#+str(Voltage(BattVoltageCH)*Current(BattCurrentCH))+"W"
            #     if (i>2/programDelay):
            #         i=0
            #         # print(Current(BattCurrentCH))
            # print(infLoop.BattVoltage)
            oled.print(l1,l2,l3)
            # i+=1
            time.sleep(programDelay)
    except KeyboardInterrupt:
        GPIO.cleanup()
        oled.clear()


runProgram()