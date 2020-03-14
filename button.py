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
We used the script below as reference
https://github.com/casnortheast/microbit_stub/
------------------------------------------------------------------------------
"""
from machine import Pin
import utime

# for singleton pattern
# Implement used global value,
# maybe Micropython 'function' object can't have attribute...
__button = [None] * 2


def get_button_object(ab):
    global __button

    from .button import __SBButton

    b = __SBButton(ab)   # Type error check
    i = 0
    if ab == 'A':
        i = 0
    elif ab == 'B':
        i = 1

    if __button[i] is None:
        __button[i] = b
    return __button[i]


class StuduinoBitButton:
    def __init__(self, ab):
        self.__button = get_button_object(ab)

    def get_value(self):
        return self.__button.get_value()

    def is_pressed(self):
        """If the button is pressed down, is_pressed() is True, else False.
        """
        return self.__button.is_pressed()

    def was_pressed(self):
        """True if the button was pressed since the last time was_pressed()
        was called, else False.
        """
        return self.__button.was_pressed()

    def get_presses(self):
        """Returns the running total of button presses.
        """
        return self.__button.get_presses()


""" ---------------------------------------------------------------------- """
""" Buttons -------------------------------------------------------------- """


class __SBButton:
    """Button class represents buttons A and B.
       There are 2 buttons:
       button_a
       button_b
       with methods to test whether a button has been pressed and
       how many times
    """

    def __init__(self, ab):
        self._count = 0
        self._was_pressed = False
        if ab == 'A':
            pin = 15
        elif ab == 'B':
            pin = 27
        else:
            raise ValueError("ab must be 'A' or 'B'")

        self._button = Pin(pin, Pin.IN)
        self._button.irq(handler=self.__button_pushed,
                         trigger=Pin.IRQ_FALLING)

        self.prev_time = utime.ticks_ms()

    def get_value(self):
        return self._button.value()

    def is_pressed(self):
        """If the button is pressed down, is_pressed() is True, else False.
        """
        if self._button.value() == 1:
            flag = False
        else:
            flag = True
        return flag

    def was_pressed(self):
        """True if the button was pressed since the last time was_pressed()
        was called, else False.
        """
        flag = self._was_pressed
        self._was_pressed = False
        return flag

    def get_presses(self):
        """Returns the running total of button presses.
        """
        count = self._count
        self._count = 0
        return count

    def __button_pushed(self, p):
        cur_time = utime.ticks_ms()
        if cur_time < self.prev_time + 150:
            return

        self.prev_time = cur_time

        self._was_pressed = True
        self._count += 1
        return
