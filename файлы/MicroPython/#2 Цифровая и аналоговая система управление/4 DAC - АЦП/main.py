from machine import Pin, DAC
from time import sleep



a = DAC(Pin(26))
a.write(255)
    

