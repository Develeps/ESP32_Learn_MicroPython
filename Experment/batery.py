from machine import Pin, ADC
import time

adc = ADC(Pin(34))
adc.atten(ADC.ATTN_6DB)

max_battery = 0.973
min_battery = 0.836

baterry = max_battery-min_battery

green_led = Pin(12, Pin.OUT)
red_led = Pin(13, Pin.OUT)


while True:
    a = []
    for i in range(100):
        a.append(adc.read_u16()*1.95/65535)
        time.sleep(0.01)
    b1 = sum(a)/100
    b = round(sum(a)/100-min_battery, 3)
    b_proc = round(b*100/baterry)
    if b_proc > 100:
        b_proc = 100
        
    if b_proc > 21:
        green_led.value(1)
        red_led.value(0)
    else:
        green_led.value(0)
        red_led.value(1)

    print("%"+str(b_proc), "volte:",round(b1/(1/(4.3)), 3))


