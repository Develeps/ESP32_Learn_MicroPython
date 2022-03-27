from time import sleep
from machine import Pin, SoftI2C
import mlx90614

i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)
sensor = mlx90614.MLX90614(i2c)

while True:
    print((sensor.read_ambient_temp(), sensor.read_object_temp()))
    sleep(0.1)
