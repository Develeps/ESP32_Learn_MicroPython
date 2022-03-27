
from max6675 import MAX6675
from time import sleep

m = MAX6675(so_pin=21, cs_pin=22, sck_pin=23)

while True:
    print("F:",m.readFahrenheit(),"C:",m.readCelsius() )
    sleep(1)