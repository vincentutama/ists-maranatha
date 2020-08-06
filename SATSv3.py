# import
import time
import datetime
import RPi.GPIO as GPIO
import Adafruit_ADS1x15

#import module
import oled
import bat

# ================PinOut==================
#ATS
PLN=24
INV=22
#Data
pvVoltageCH = 0
pvCurrentCH = 1
BattVoltageCH = 2
BattCurrentCH = 3
#Button
autoButton =4 #pilih mode
manualButton = 17 #pilih PLN atau INV
#Servo
servoPIN = 23
#=========================================

#Variable
x=0
status="PLN"
programDelay=0.01
switchTime=0.009

#mode
defaultATS="PLN"
availMode=[0,1,2,3,4]
defaultMode = 0 
subMode = 0 

#GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(autoButton, GPIO.IN) #Auto Mode 1
GPIO.setup(manualButton, GPIO.IN) #Manual Mode 0
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(24, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)

#i2c setup
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
def i2cRead(channelSelect):
    # time.sleep(1)
    return(0.000124219*adc.read_adc(channelSelect,gain=GAIN))

#Function Tegangan
def Voltage(channelSelect):
    voltageRare=i2cRead(channelSelect)
    VoltageDiv=6.599597586
    voltage = voltageRare*VoltageDiv#Bila perlu kalibrasi
    return voltage

#function Arus
def Current(channelSelect):
    voltageRare=i2cRead(channelSelect)
    Resistance=0.25455#0.0015
    current = voltageRare/Resistance#Bila perlu kalibrasi
    return current

#Class

#ATS
class TransferSwitch:
    PLN=24
    INV=22
    switchingTime=0.009 #for test use 2s
    def __init__(self,switchTime):
        self.switchingTime=switchTime
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
                
                time.sleep(self.switchingTime)

                GPIO.output(self.INV,1)
                GPIO.output(self.INV,1)
                self.State = "INV"
                print("Status : ",self.State)
        else:
            print("not PLN or INV ERROR !!")

    def SwitchStat(self):
        if (GPIO.input(self.PLN)==0 and GPIO.input(self.PLN)==0) and (GPIO.input(self.INV)==1 and GPIO.input(self.INV)==1) : 
            Status = "INV"
        elif (GPIO.input(self.PLN)==1 and GPIO.input(self.PLN)==1) and (GPIO.input(self.INV)==0 and GPIO.input(self.INV)==0):
            Status = "PLN"
        else :
            Status = "Undefined"
        return(Status)

#Servo

class Servo:
    def __init__(self):
        self.pwm = GPIO.PWM(servoPIN, 50) # GPIO 23 for PWM with 50Hz
        self.pwm.start(0) # Initialization
        print("Servo initiated")

    def SetAngle(self,angle):
        duty = angle / 18 + 2
        GPIO.output(23, True)
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(0.55)
        GPIO.output(23, False)
        self.pwm.ChangeDutyCycle(0)

    def on(self):
        self.SetAngle(15)
        print("servo on")

    def off(self):
        self.SetAngle(60)
        print("servo off")

#Battery
class Battery:
    capacity=0 #in Ah
    SOC=0 #in %
    def __init__(self,batteryVoltage,PVCurrent,INVCurrent,realBatteryCapacity):
        self.refresh(batteryVoltage,PVCurrent,INVCurrent,realBatteryCapacity)
    
    def refresh(self,batteryVoltage,PVCurrent,INVCurrent,realBatteryCapacity):
        if (PVCurrent<0.5 and INVCurrent < 0.5):
            self.SOC=bat.StateOfCharge(batteryVoltage)
            self.capacity=realBatteryCapacity*self.SOC/100
            print("executed Capacity : ",self.capacity)

    def Discharge(self,INVCurrent):#per hour, so divide Current with 60 Minute and 60 second for 1s refresh rate
        self.capacity-=INVCurrent

    def Charge(self,PVCurrent):
        self.capacity+=PVCurrent

# time Setup
now = datetime.datetime.now()

#loop
class loop:
    servo=0#off
    mode=0
    lowMode=0    
    count=0
    x=0
    timerVoltage=0
    ATS=TransferSwitch(switchTime)
    servo = Servo()
    t = datetime.datetime.now()

    def __init__(self):
        mode=0
        x=0

    def pln(self):
        self.ATS.SwitchTo("PLN")
        self.Status = "PLN"
        if self.servo==1:
            self.servo.off()
            self.servo=0

    def inv(self):
        if self.servo==0:
            self.servo.on()
            self.servo=1
            time.sleep(5)
        self.ATS.SwitchTo("INV")
        self.Status = "INV"

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

            elif self.mode == 0 and self.x==0:
                self.mode = 1
                self.x=1
                print("Mode change to manual INV")
                self.inv()

        elif (GPIO.input(autoButton)==1):
            if (self.mode < 2 or self.mode ==4) and self.x==0:
                self.mode = 2
                self.x=1
                self.message= "Mode change to Auto Max"
                self.MaximumMode()

            elif self.mode < 3 and self.x==0:
                self.mode = 3
                self.x=1
                self.message= "Mode change to Auto Normal"
                self.NormalMode()
            elif self.mode == 3 and self.x==0:
                self.mode = 4
                self.x=1
                self.message= "Mode change to Smart Auto"
            print(self.message)
        elif(GPIO.input(autoButton)==0 and GPIO.input(manualButton)==0):
            self.x=0
        if (GPIO.input(PLN)==0 and GPIO.input(PLN)==0) and (GPIO.input(INV)==1 and GPIO.input(INV)==1) : 
            self.Status = "INV"
        elif (GPIO.input(PLN)==1 and GPIO.input(PLN)==1) and (GPIO.input(INV)==0 and GPIO.input(INV)==0):
            self.Status = "PLN"
        else :
            self.Status = "Undefined"
        self.count+=1
        if(Current(BattCurrentCH)<=1 and self.PVVoltage<=5 and self.count>30*4/programDelay):#selama 30 menit
            battery.refresh(12.2,0.2,0.2,75)#Ganti dengan parameter asli
            self.count=0

    def getMode(self):
        return(self.mode)
    
    def MainMode(self,BRNight,BDNight,BRDay,BDDay):
        if self.PVVoltage<=12.9:
            battReconnect=BRNight#12.75
            battDisconnect=BDNight#11.8
        else:
            battReconnect=BRDay#14
            battDisconnect=BDDay#12.65

        if self.BattVoltage>=battReconnect:
            self.inv()
            self.Status = "INV"
            self.timerVoltage=0
            self.lowMode=0

        elif self.BattVoltage<=battDisconnect:
            self.lowMode=1
            self.timerVoltage+=1
            if (self.timerVoltage>=4/programDelay):#timer selama 4 detik
                self.pln()
                self.message="low Voltage"
                self.Status = "PLN"

        elif self.BattVoltage<battReconnect and self.BattVoltage>battDisconnect and self.lowMode==0:
            self.inv()
            self.Status = "INV"

        elif self.BattVoltage>battDisconnect and self.lowMode==1:
            self.timerVoltage=0

    def MaximumMode(self):
        battReconnectNight=12.75
        battDisconnectNight=11.8
        battReconnectDay=14
        battDisconnectDay=2.65
        self.MainMode(battReconnectNight,battDisconnectNight,battReconnectDay,battDisconnectDay)
            
    def NormalMode(self):
        if now.hour>=18 or now.hour<7:
           self.MaximumMode()
        else:
            self.pln()

    def SavingMode(self):
        battReconnectNight=12.75
        battDisconnectNight=12.3
        battReconnectDay=14
        battDisconnectDay=12.8
        self.MainMode(battReconnectNight,battDisconnectNight,battReconnectDay,battDisconnectDay)
   
    def ModeSelector(self,modeSelect):
        if modeSelect==2:
            self.MaximumMode()#pake banyak
        elif modeSelect==3:
            self.NormalMode()#pake malem aja
        elif modeSelect==4:
            self.SavingMode()#pake dikit

#in Development           
class Data:
    def __init__(self):
        print("Data logger initiated")
    def Logging(self,current):
        battery.Discharge(current)

def runProgram():
    print("program started")
    infLoop = loop()
    battery = Battery(Voltage(BattVoltageCH),0,infLoop.BattCurrent,200) #input parameter battre
    ATS = TransferSwitch()
    ATS.SwitchTo(defaultATS)
    data=Data()
    arrayMode=["PLN","INV","Max","Night","Saving"]
    print("Battery Voltage: "+Voltage(BattVoltageCH))
    print(i2cRead(3))
    print("Battery Current: "+Current(BattCurrentCH))

    # Loop
    try:
        while 1:
            infLoop.Check()
            infLoop.ModeSelector(infLoop.getMode())
            if (i<(1/programDelay)):
                localmode=arrayMode[infLoop.getMode()]
                l1="   Mode    : "+localmode
                statusATS = ATS.SwitchStat()
                l2="   Status  : "+statusATS
                l3="   Battery : "+str(battery.StateOfCharge(infLoop.BattVoltage))+'%'
            else:
                l1=str(now.strftime("%a, %b %d %Y "))
                l2="PV Voltage : "+str(Voltage(pvVoltageCH))+" V"
                l3="Daya : "#+str(Voltage(BattVoltageCH)*Current(BattCurrentCH))+"W"
                if (i>2/programDelay):
                    i=0
            print(infLoop.BattVoltage)
            oled.print(l1,l2,l3)
            # i+=1
            time.sleep(programDelay)
    except KeyboardInterrupt:
        GPIO.cleanup()
        oled.clear()
