import time
import ATS
import RPi.GPIO as GPIO
import oled
import servo

# =======PinOut========
pvVoltageCH = 0
pvCurrentCH = 1
BattVoltageCH = 2
BattCurrentCH = 3
autoButton =4 #pilih mode
manualButton = 17 #pilih PLN atau INV
PLN=21
INV=22

#Variable
x=0
status="PLN"
programDelay=0.05

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

# Class

class loop:
    # message="n/a"
    mode=0
    lowMode=0
    # Status="null"
    count=0
    x=0
    timerVoltage=0
    def __init__(self):
        mode=0
        x=0
    def Check(self):
        if (GPIO.input(manualButton)==1 and self.x==0):
            if self.mode!= 0 :
                self.mode = 0
                self.x=1
                print("Mode change to manual PLN")
                ATS.SwitchTo("PLN")
                self.Status = "PLN"
                servo.off()
            elif self.mode == 0 and self.x==0:
                self.mode = 1
                self.x=1
                print("Mode change to manual INV")
                servo.on()
                time.sleep(5)
                ATS.SwitchTo("INV")
                self.Status = "INV"
        else:
            self.x=0
    def getMode(self):
        return(self.mode)
        

#===Start Program===
def runProgram():
    print("program started")
    infLoop = loop()
    ATS.SwitchTo(defaultATS)
    arrayMode=["PLN","INV","A1","A2","A3"]
    # Loop
    try:
        while 1:
            infLoop.Check()
            localmode=arrayMode[infLoop.getMode()]
            mode="   Mode    : "+localmode
            statusATS = ATS.SwitchStat()
            stat="   Status  : "+statusATS
            mssg="   Battery : "+str('NA')
            oled.print(mode,stat,mssg)
            time.sleep(programDelay)
    except KeyboardInterrupt:
        GPIO.cleanup()
        oled.clear()