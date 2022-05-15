from hx711 import HX711
from utime import sleep_us, sleep


class Scales(HX711):
    def __init__(self, d_out, pd_sck):
        super(Scales, self).__init__(d_out, pd_sck)
        self.offset = 0

    def reset(self):
        self.power_off()
        self.power_on()

    def tare(self):
        self.offset = self.read()

    def raw_value(self):
        return self.read() - self.offset

    def stable_value(self, reads=10, delay_us=500):
        values = []
        for _ in range(reads):
            values.append(self.raw_value())
            sleep_us(delay_us)
        return self._stabilizer(values)

    @staticmethod
    def _stabilizer(values, deviation=4):
        weights = []
        for prev in values:
            weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]


scales = Scales(d_out=5, pd_sck=4)
scales.tare()
    
while True:
    try:
        val = scales.stable_value(reads=3)
        if val < 0:
            print("gram: ",0)
        else:  
            print("gram: ",val * 0.00283)
    except Exception:
        print(0)
scales.power_off()