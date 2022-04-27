from time import sleep_ms, ticks_ms
from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd

i2c = I2C(scl=Pin(14), sda=Pin(12), freq=400000)

lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.putstr("Hello ernitron\nIt's working!")

lcd.show_cursor()
lcd.blink_cursor_on()
