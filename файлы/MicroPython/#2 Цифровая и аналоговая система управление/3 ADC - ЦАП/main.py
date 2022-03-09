from machine import Pin, ADC
from time import sleep

while True:
    sleep(1)
    a = ADC(Pin(34))
    a.atten(ADC.ATTN_11DB) 
    val = a.read()
    print(val*3.3/4095)
    
