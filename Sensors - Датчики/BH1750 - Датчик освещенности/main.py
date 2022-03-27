from time import sleep
from BH1750 import BH1750
from machine import Pin, SoftI2C

i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)

s = BH1750(i2c)

while True:
    print(s.luminance(BH1750.CONT_LOWRES))