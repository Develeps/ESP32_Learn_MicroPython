import time
from BH1750 import BH1750
from machine import Pin, SoftI2C

i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)

s = BH1750(i2c)
s.on()
print(s.luminance(True))