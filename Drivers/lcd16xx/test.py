from time import sleep_ms, ticks_ms
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd
import time


i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)

s = ""
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.show_cursor()
lcd.blink_cursor_on()
'''   
for i in "Hello Word \nIt's working!":
    s = s + i
    print(s)
    lcd.putstr(s)
    time.sleep(0.5)
    lcd.clear()
'''
time.sleep(1)
lcd.putchar('1') 
for i in range(10):
    lcd.move_to(i, 0)
    time.sleep(1)