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


class PWMTimerManager():
    TIMERPOOL = [True, True, True, True]    # True:Enable, False:Disable

    def __init__(self):
        pass

    def get_pwm_timer(self):
        for i, f in enumerate(PWMTimerManager.TIMERPOOL):
            if f:
                # print('Use Timer ID:{0}'.format(i))
                PWMTimerManager.TIMERPOOL[i] = False
                return i
        raise MemoryError('PWM Timer has depleted.')

    def rel_pwm_timer(self, i):
        PWMTimerManager.TIMERPOOL[i] = True


""" ---------------------------------------------------------------------- """
""" Pins ----------------------------------------------------------------- """


class StuduinoBitDigitalPinMixin(PWMTimerManager):
    def release_pwm(self):
        if self.pwm is not None:
            self.pwm.deinit()                       # stop pwm output.
            machine.Pin(self.pin, machine.Pin.OUT)  # initalize Pin
            self.pwm = None

    def write_digital(self, value):
        """Write a value to the pin that must be either 0, 1, True  or False.
        """
        self.release_pwm()
        p = machine.Pin(self.pin, machine.Pin.OUT)
        p.value(value)

    def read_digital(self):
        """Return the pin's value, which will be either 1 or 0.
        """
        self.release_pwm()
        p = machine.Pin(self.pin, machine.Pin.IN)
        return p.value()

    def write_analog(self, value):
        """Write a value to the pin that must be between 0 and 1023.
        """
        if self.pwm is None:
            self.duty = value
        else:
            self.duty = value
            self.pwm.duty(value)

    def set_analog_period(self, period, timer=-1):
        """Set the period of the PWM output of the pin in milliseconds.

        See https://en.wikipedia.org/wiki/Pulse-width_modulation.
        This is a null operation for the emulation.
        """
        freq = int(((1.0/period)*1000))
        self.set_analog_hz(freq, timer=timer)

    def set_analog_period_microseconds(self, period, timer=-1):
        """Set the period of the PWM output of the pin in microseconds.

        See https://en.wikipedia.org/wiki/Pulse-width_modulation)
        This is a null operation for the emulation.
        """
        freq = int(((1.0/period)*1000*1000))
        self.set_analog_hz(freq, timer=timer)

    def set_analog_hz(self, hz, timer=-1):
        if self.pwm is None:
            p = machine.Pin(self.pin, machine.Pin.OUT)
            if timer != -1:
                self.pwm = machine.PWM(p, hz, self.duty, timer=timer)
            else:
                self.pwm = machine.PWM(p, hz, self.duty)
        else:
            if timer != -1:
                self.pwm.init(freq=hz, duty=self.duty, timer=timer)
            else:
                self.pwm.freq(hz)

    def status(self):
        machine.PWM.list()


class StuduinoBitAnalogPinMixin():
    """Returns the pin's value, which will be between 0 and 1023
    """
    def read_analog(self, mv=False):
        if self.adc is None:
            self.adc = machine.ADC(self.pin)
            self.adc.atten(self.adc.ATTN_11DB)

        if mv:
            return self.adc.read()
        else:
            raw = self.adc.readraw()
            calib = self.adc.read()
            if (raw >= 150) and (raw <= 2450):
                val = calib / 3300 * 4095
            else:
                val = raw
            return val


class StuduinoBitDigitalPin(StuduinoBitDigitalPinMixin):
    def __init__(self, pin):
        self.pin = pin
        self.duty = 0
        self.pwm = None


class StuduinoBitAnalogPin(StuduinoBitAnalogPinMixin):
    def __init__(self, pin):
        self.pin = pin
        self.adc = None


class StuduinoBitAnalogDitialPin(StuduinoBitDigitalPinMixin,
                                 StuduinoBitAnalogPinMixin):
    def __init__(self, pin):
        self.pin = pin
        self.duty = 0
        self.pwm = None
        self.adc = None

    def write_digital(self, value):
        if self.adc is not None:
            self.adc.deinit()
            self.adc = None
        super().write_digital(value)

    def read_digital(self):
        if self.adc is not None:
            self.adc.deinit()
            self.adc = None
        return super().read_digital()

    def write_analog(self, value):
        if self.adc is not None:
            self.adc.deinit()
            self.adc = None
        super().write_analog(value)

    def set_analog_hz(self, hz, timer=-1):
        if self.adc is not None:
            self.adc.deinit()
            self.adc = None
        super().set_analog_hz(hz, timer)

    def read_analog(self, mv=False):
        if self.pwm is not None:
            self.pwm.deinit()
            self.pwm = None
        return super().read_analog(mv)

# for singleton pattern
# Implement used global value,
# maybe Micropython 'function' object can't have attribute...

__tpin = [None] * 21


def StuduinoBitTerminal(pin):
    global __tpin
    if pin == 'P0':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitAnalogDitialPin(32)
        return __tpin[i]

    elif pin == 'P1':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitAnalogDitialPin(33)
        return __tpin[i]

    elif pin == 'P2':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitAnalogDitialPin(36)
        return __tpin[i]

    elif pin == 'P3':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitAnalogDitialPin(39)
        return __tpin[i]

    elif pin == 'P4':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(25)
        return __tpin[i]

    elif pin == 'P5':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitAnalogDitialPin(15)
        return __tpin[i]

    elif pin == 'P6':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(26)
        return __tpin[i]

    elif pin == 'P7':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(5)
        return __tpin[i]

    elif pin == 'P8':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitAnalogDitialPin(14)
        return __tpin[i]

    elif pin == 'P9':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitAnalogDitialPin(12)
        return __tpin[i]

    elif pin == 'P10':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(0)
        return __tpin[i]

    elif pin == 'P11':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(27)
        return __tpin[i]

    elif pin == 'P12':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(4)
        return __tpin[i]

    elif pin == 'P13':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(18)
        return __tpin[i]

    elif pin == 'P14':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(19)
        return __tpin[i]

    elif pin == 'P15':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(23)
        return __tpin[i]

    elif pin == 'P16':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitAnalogDitialPin(13)
        return __tpin[i]

    elif pin == 'P19':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(22)
        return __tpin[i]

    elif pin == 'P20':
        i = int(pin[1:])
        if __tpin[i] is None:
            __tpin[i] = StuduinoBitDigitalPin(21)
        return __tpin[i]

    else:
        raise ValueError("pin must be 'P0'-'P16','P19','P20'")
