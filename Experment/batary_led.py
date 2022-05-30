from machine import Pin
import time

green_led = Pin(12, Pin.OUT)
red_led = Pin(13, Pin.OUT)

'''
green_led.value(1)
red_led.value(0)
time.sleep(1)
'''

for i in range(10):
    
    green_led.value(0)
    red_led.value(1)
    time.sleep(1)
    
    green_led.value(1)
    red_led.value(0)
    time.sleep(1)
    
    green_led.value(0)
    red_led.value(0)
    time.sleep(1)

    