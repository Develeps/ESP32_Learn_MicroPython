from machine import Pin
from machine import Timer
from time import sleep_ms
import ubluetooth

import usys
import ustruct as struct
import utime
from machine import Pin, SPI, reset
from nrf24l01 import NRF24L01
from micropython import const
import sys

# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)

if usys.platform == "pyboard":
    cfg = {"spi": 2, "miso": "Y7", "mosi": "Y8", "sck": "Y6", "csn": "Y5", "ce": "Y4"}
elif usys.platform == "esp8266":  # Hardware SPI
    cfg = {"spi": 1, "miso": 12, "mosi": 13, "sck": 14, "csn": 4, "ce": 5}
elif usys.platform == "esp32":  # Software SPI
    cfg = {"spi": -1, "miso": 32, "mosi": 14, "sck": 32, "csn": 27, "ce": 12}
else:
    raise ValueError("Unsupported platform {}".format(usys.platform))

# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")


class ESP32_BLE():
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        global is_ble_connected
        is_ble_connected = True
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):
        global is_ble_connected
        is_ble_connected = False
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    def ble_irq(self, event, data):
        global ble_msg
        
        if event == 1: #_IRQ_CENTRAL_CONNECT:
                       # A central has connected to this peripheral
            self.connected()

        elif event == 2: #_IRQ_CENTRAL_DISCONNECT:
                         # A central has disconnected from this peripheral.
            self.advertiser()
            self.disconnected()
        
        elif event == 3: #_IRQ_GATTS_WRITE:
                         # A client has written to this characteristic or descriptor.          
            buffer = self.ble.gatts_read(self.rx)
            ble_msg = buffer.decode('UTF-8').strip()
            
    def register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("\r\n")



#NRF
def master():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    if cfg["spi"] == -1:
        spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
        nrf = NRF24L01(spi, csn, ce, payload_size=8)
    else:
        nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=8)

    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(1, pipes[1])
    nrf.start_listening()

    num_needed = 16
    num_successes = 0
    num_failures = 0
    led_state = 0

    print("NRF24L01 master mode, sending %d packets..." % num_needed)
    ble.send("NRF24L01 master mode, sending %d packets... " + str(num_needed))

    while num_successes < num_needed and num_failures < num_needed:
        if ble_msg == "NRF SLAVE":
            break
        if ble_msg == "NRF STOP":
            break
        # stop listening and send packet
        nrf.stop_listening()
        millis = utime.ticks_ms()
        led_state = max(1, (led_state << 1) & 0x0F)
        print("sending:", millis, led_state)
        ble.send("sending: " + str(millis) + " " + str(led_state))
        
        try:
            nrf.send(struct.pack("ii", millis, led_state))
        except OSError:
            pass

        # start listening again
        nrf.start_listening()

        # wait for response, with 250ms timeout
        start_time = utime.ticks_ms()
        timeout = False
        while not nrf.any() and not timeout:
            if utime.ticks_diff(utime.ticks_ms(), start_time) > 250:
                timeout = True

        if timeout:
            
            print("failed, response timed out")
            ble.send("failed, response timed out")
            
            num_failures += 1

        else:
            # recv packet
            (got_millis,) = struct.unpack("i", nrf.recv())

            # print response and round-trip delay
            print(
                "got response:",
                got_millis,
                "(delay",
                utime.ticks_diff(utime.ticks_ms(), got_millis),
                "ms)",
            )
            ble.send("got response: " +
                str(got_millis) + 
                " (delay" + 
                str(utime.ticks_diff(utime.ticks_ms(), got_millis)) + 
                " ms)",
            )
            
            num_successes += 1

        # delay then loop
        utime.sleep_ms(250)

    print("master finished sending; successes=%d, failures=%d" % (num_successes, num_failures))
    ble.send("master finished sending; successes=%d, failures=%d" % (num_successes, num_failures))



def slave():
    
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    if cfg["spi"] == -1:
        spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
        nrf = NRF24L01(spi, csn, ce, payload_size=8)
    else:
        nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=8)

    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.start_listening()

    print("NRF24L01 slave mode, waiting for packets... (ctrl-C to stop)")
    ble.send("NRF24L01 slave mode, waiting for packets...")
    
    while True:
        if ble_msg == "NRF MASTER":
            break
        if ble_msg == "NRF STOP":
            break
        if nrf.any():
            while nrf.any():
                buf = nrf.recv()
                millis, led_state = struct.unpack("ii", buf)
                
                #print("received:", millis, led_state)
                ble.send("received: " + str(millis) + " " + str(led_state))
                
                utime.sleep_ms(_RX_POLL_DELAY)

            # Give master time to get into receive mode.
            utime.sleep_ms(_SLAVE_SEND_DELAY)
            nrf.stop_listening()
            try:
                nrf.send(struct.pack("i", millis))
            except OSError:
                pass
            
            print("sent response")
            ble.send("sent response")
            
            nrf.start_listening()






ble = ESP32_BLE("ESP32BLE")

ble_msg = ""
is_ble_connected = False

led = Pin(2, Pin.OUT)
but = Pin(0, Pin.IN)

while True:
    if is_ble_connected:      #???????????????????????? ??????????????????????
        if ble_msg:           #?????????????????? ??????????????????
            print(ble_msg)    #?????????????? ??????????????????
            
            if ble_msg == "NRF MASTER":
                master()
            if ble_msg == "NRF SLAVE":
                slave()
            if ble_msg == "DEV RESET":
                reset()
            if ble_msg == "DEV EXIT":
                sys.exit()
            ble_msg = ""
        '''
            print(data)
            ble.send(data) #???????????????????? ??????????
        '''
    sleep_ms(10)


