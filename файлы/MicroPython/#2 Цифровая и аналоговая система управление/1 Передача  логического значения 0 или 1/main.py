from machine import Pin 
from time import sleep

#Указываем ряд светодиодов подключеных к ESP32
pin18 = Pin(18, Pin.OUT)
pin19 = Pin(19, Pin.OUT)
pin21 = Pin(21, Pin.OUT)
#Добавляем их в массив для удобства работы
pin = [pin18, pin19, pin21]
#Выполняем цикл программы 100
for i in range(100):
    #по очередно включаем светодиоды в промежутке времени 0.1 секунду
    for p in pin:
        p.value(1)
        sleep(0.1)
    #по очередно выключаем светодиоды в промежутке времени 0.1 секунду
    for p in pin:
        p.value(0)
        sleep(0.1)

