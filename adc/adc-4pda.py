from time import sleep
from thermocouples_reference import thermocouples
import RPi.GPIO as GPIO

CS = 8
DOUT = 9
CLK = 11

round_pr=2
vc = 4.887
Tref=22.4
R1=471
R2=138 # 77.5
R2=R2 + 1013
coef = 1 + R2*1000.0/R1

print('coef=' + str(coef))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(CS, GPIO.OUT)
GPIO.setup(DOUT, GPIO.IN)
GPIO.setup(CLK, GPIO.OUT)

typeK = thermocouples['K']


while (True):
    GPIO.output(CS, True)
    GPIO.output(CLK, True)
    GPIO.output(CS, False)
    binData = 0
    i1 = 14

    while (i1 >= 0):
        GPIO.output(CLK, False)
        bitDOUT = GPIO.input(DOUT)
        GPIO.output(CLK, True)
        bitDOUT = bitDOUT << i1
        binData |= bitDOUT
        i1 -= 1

    GPIO.output(CS, True)
    binData &= 0xFFF 
    Vadc = vc * binData/4096.0
    Voltage = round(Vadc, round_pr)
    Vt = Vadc/coef
    T1 = round(typeK.inverse_CmV(Vt*1000, Tref=Tref-1), round_pr)
    T2 = round(typeK.inverse_CmV(Vt*1000, Tref=Tref), round_pr)
    T3 = round(typeK.inverse_CmV(Vt*1000, Tref=Tref+1), round_pr)
    T0 = round(typeK.inverse_CmV(Vt*1000), round_pr)
    print('Voltage=' + str(Voltage) + 'V, Vt=' + str(round((Vt)*1000,round_pr)) + 'mV, T= ' + str(T2) + 'C'+ ' T0= ' + str(T0) + 'C, T-T0='+ str(T2-T0) )
    #print 'T({0})={1}C, T({2})= {3}C, T({4})= {5}C, T0={6}' .format(Tref-1, T1, Tref, T2, Tref+1, T3, T2-T0) 
   
    sleep(1)
