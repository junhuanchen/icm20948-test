"""
------------------------------------------------------------------------------
The MIT License (MIT)
Copyright (c) 2016 Newcastle University
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.import time
------------------------------------------------------------------------------
Author
Kenji Kawase, Artec Co., Ltd.
------------------------------------------------------------------------------
"""
import machine
import network
from esp import espnow
import io
import json
import time

# Use ESP-NOW
# https://www.espressif.com/sites/default/files/documentation/esp-now_user_guide_en.pdf

# StuduinoBitRadio is not High frequency 
# https://www.esp32.com/viewtopic.php?f=12&t=8754

class StuduinoBitRadio:
    BROADCAST_MAC_ADDRESS = b'\xFF' * 6

    WAIT_TIME = 1000  # msec

    def __nwled_on(self):
        self.nwpin.value(1)

    def __nwled_off(self):
        self.nwpin.value(0)

    def __recv_cb(self, dobj):
        # Group ID do not set yet.
        if self.__group == -1:
            return
        if dobj:
            data = dobj[1]
            if data[1] == self.__group:
                self.queue.append(data)

    def __init__(self):
        # Network LED OFF
        self.nwpin = machine.Pin(12, machine.Pin.OUT)
        self.nwpin.value(0)

        # Initialize StuduinoBitRadio information
        self.__group = -1
        self.queue = []
        self.is_on = False

    def on(self):
        # Wifi ON
        self.w = network.WLAN(network.STA_IF)
        self.w.active(True)
        self.w.config(protocol=network.MODE_LR)

        start = time.ticks_ms()
        while not self.w.active():
            if time.ticks_ms() - start > StuduinoBitRadio.WAIT_TIME:
                raise RuntimeError('Wifi was not started, try one more')

        # Network LED ON
        self.__nwled_on()
        self.is_on = True

    def off(self):
        # Wifi OFF
        self.w.active(False)

        start = time.ticks_ms()
        while self.w.active():
            if time.ticks_ms() - start > StuduinoBitRadio.WAIT_TIME:
                raise RuntimeError('Wifi was not stoped, try one more')

        # Network LED OFF
        self.__nwled_off()
        self.is_on = False

    def start(self, group):
        if not self.is_on:
            raise RuntimeError('Start Wifi before this method')

        try:
            # Intialize ESP-NOW and resiger coallback function.
            espnow.init()
            espnow.add_peer(StuduinoBitRadio.BROADCAST_MAC_ADDRESS)
            espnow.on_recv(self.__recv_cb)
        except OSError as e:
            print(e)

        self.__group = group

    def config(self, length=None, queue=None, channel=None, group=None):
        raise NotImplementedError

    def group(self, group=-1):
        if group < 0:
            raise ValueError("group must be 0 - 255")
        self.__group = group
        self.queue.clear()

    def __make_dal_header(self):
        dal_header = [1, self.__group, 1]
        return bytes(dal_header)

    def __make_pxt_header(self, type):
        pxt_header = [type, 0, 0, 0, 0]
        return bytes(pxt_header)

    def send_number(self, n):
        if not self.is_on:
            raise RuntimeError('Start Wifi before this method')

        hdal = self.__make_dal_header()
        hpxt = self.__make_pxt_header(0)
        dpxt_n = n.to_bytes(4, 'big')
        msg = hdal + hpxt + dpxt_n
        espnow.send(StuduinoBitRadio.BROADCAST_MAC_ADDRESS, msg)

    def send_value(self, s, n):
        if not self.is_on:
            raise RuntimeError('Start Wifi before this method')

        hdal = self.__make_dal_header()
        hpxt = self.__make_pxt_header(1)
        dpxt_n = n.to_bytes(4, 'big')
        dpxt_s = s.encode()
        msg = hdal + hpxt + dpxt_n + dpxt_s
        espnow.send(StuduinoBitRadio.BROADCAST_MAC_ADDRESS, msg)

    def send_string(self, s):
        if not self.is_on:
            raise RuntimeError('Start Wifi before this method')

        hdal = self.__make_dal_header()
        hpxt = self.__make_pxt_header(2)
        dpxt_s = s.encode()
        msg = hdal + hpxt + dpxt_s
        espnow.send(StuduinoBitRadio.BROADCAST_MAC_ADDRESS, msg)

    def send_buffer(self, buf):
        if not self.is_on:
            raise RuntimeError('Start Wifi before this method')

        hdal = self.__make_dal_header()
        hpxt = self.__make_pxt_header(3)
        dpxt_b = buf
        msg = hdal + hpxt + dpxt_b
        espnow.send(StuduinoBitRadio.BROADCAST_MAC_ADDRESS, msg)

    def recv(self):
        if not self.is_on:
            raise RuntimeError('Start Wifi before this method')

        try:
            data = self.queue.pop(0)
        except IndexError as e:
            return None

        if (data[3] == 0x00):   # Number
            num = data[8:12]
            num = int.from_bytes(num, 'big')
            return 0, num
        if (data[3] == 0x01):   # Value
            num = data[8:12]
            name = data[12:32]
            num = int.from_bytes(num, 'big')
            name = name.decode()
            return 1, (name, num)
        if (data[3] == 0x02):   # String
            name = data[8:32]
            name = name.decode()
            return 2, name
        if (data[3] == 0x03):   # Buffer
            buff = data[8:32]
            return 3, buff


class StuduinoBitBLE:

    def __init__(self):
        raise NotImplementedError


class StuduinoBitWiFiMixIn:
    def active(self, *args):
        return self._wlan.active(*args)

    def isconnected(self, *args):
        return self._wlan.isconnected(*args)

    def wifiactive(self):
        return self._wlan.wifiactive()

    def ifconfig(self, *args):
        return self._wlan.ifconfig(*args)

    def config(self, *args, **kwargs):
        return self._wlan.config(*args, **kwargs)


class StuduinoBitWiFiAP(StuduinoBitWiFiMixIn):
    def __init__(self):
        self._wlan = network.WLAN(network.AP_IF)

    def status(self, *args):
        self._wlan.status(*args)


class StuduinoBitWiFiSTA(StuduinoBitWiFiMixIn):
    def __init__(self):
        self._wlan = network.WLAN(network.STA_IF)

    def connect(self, *args):
        self._wlan.connect(*args)
        tmo = 50
        while not self._wlan.isconnected():
            time.sleep_ms(100)
            tmo -= 1
            if tmo == 0:
                return False
        return True

    def disconnect(self):
        self._wlan.disconnect()

    def scan(self):
        return self._wlan.scan()


def CreateWLAN(mode='STA'):
    if mode == 'STA':
        return StuduinoBitWiFiSTA()
    elif mode == 'AP':
        return StuduinoBitWiFiAP()
    else:
        raise TypeError('can\'t start WiFi {0} mode'.format(mode))
