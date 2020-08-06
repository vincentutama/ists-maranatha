def StateOfCharge(batteryVoltage):
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