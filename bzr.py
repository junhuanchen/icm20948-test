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
from machine import Pin, PWM
from .terminal import StuduinoBitTerminal
import time


# for singleton pattern
# Implement used global value, maybe Micropython
# 'function' object can't have attribute...
__buzzer = None


def get_buzzer_object():
    global __buzzer
    from .bzr import __SBBuzzer

    if __buzzer is None:
        __buzzer = __SBBuzzer()
    return __buzzer


class StuduinoBitBuzzer():
    def __init__(self):
        self.__buzzer = get_buzzer_object()

    def on(self, sound, *, duration=None):
        self.__buzzer.on(sound, duration=duration)

    def off(self):
        self.__buzzer.off()

    def release(self):
        self.__buzzer.release()


class __SBBuzzer():
    def __init__(self):
        self._buzzer = StuduinoBitTerminal('P4')
        self.tid = self._buzzer.get_pwm_timer()

    def on(self, sound, *, duration=None):
        if type(sound) is str:
            if sound.isdigit():
                # MIDI noto number
                nn = int(sound)
                if nn < 48 or nn > 127:
                    raise ValueError("Note number must be '48'-'127'")
                tone = __SBBuzzer.NOTE_NUM[nn-48]
            else:
                # Letter notation
                tone = sound

            try:
                self._buzzer.set_analog_hz(__SBBuzzer.TONE_MAP[tone], self.tid)
            except KeyError as e:
                raise ValueError("Note must be 'C3'-'G9'")
        elif type(sound) is int:
            if sound < 0:
                raise ValueError("Frequency must be more than 0")
            self._buzzer.set_analog_hz(sound, self.tid)
        else:
            raise TypeError("sound type must be string or integer")

        self._buzzer.write_analog(10)

        if duration != None:
            if duration < 0:
                self.off()
                raise ValueError("duration must be more than 0 ms.")
            time.sleep_ms(duration)
            self.off()

    def off(self):
        self._buzzer.write_analog(0)

    def release(self):
        self._buzzer.write_analog(0)
        self._buzzer.rel_pwm_timer(self.tid)
        self._buzzer.release_pwm()


__SBBuzzer.TONE_MAP = {
    'C3': 131, 'CS3': 139, 'D3': 147, 'DS3': 156, 'E3': 165, 'F3': 175,
    'FS3': 185, 'G3': 196, 'GS3': 208, 'A3': 220, 'AS3': 233, 'B3': 247,
    'C4': 262, 'CS4': 277, 'D4': 294, 'DS4': 311, 'E4': 330, 'F4': 349,
    'FS4': 370, 'G4': 392, 'GS4': 415, 'A4': 440, 'AS4': 466, 'B4': 494,
    'C5': 523, 'CS5': 554, 'D5': 587, 'DS5': 622, 'E5': 659, 'F5': 699,
    'FS5': 740, 'G5': 784, 'GS5': 831, 'A5': 880, 'AS5': 932, 'B5': 988,
    'C6': 1047, 'CS6': 1109, 'D6': 1175, 'DS6': 1245, 'E6': 1319, 'F6': 1397,
    'FS6': 1480, 'G6': 1568, 'GS6': 1661, 'A6': 1760, 'AS6': 1865, 'B6': 1976,
    'C7': 2093, 'CS7': 2218, 'D7': 2349, 'DS7': 2489, 'E7': 2637, 'F7': 2794,
    'FS7': 2960, 'G7': 3136, 'GS7': 3322, 'A7': 3520, 'AS7': 3729, 'B7': 3951,
    'C8': 4186, 'CS8': 4435, 'D8': 4699, 'DS8': 4978, 'E8': 5274, 'F8': 5588,
    'FS8': 5920, 'G8': 6272, 'GS8': 6645, 'A8': 7040, 'AS8': 7459, 'B8': 7902,
    'C9': 8372, 'CS9': 8870, 'D9': 9397, 'DS9': 9956, 'E9': 10548, 'F9': 11175,
    'FS9': 11840, 'G9': 12544
}

__SBBuzzer.NOTE_NUM = [
    'C3', 'CS3', 'D3', 'DS3', 'E3', 'F3', 'FS3', 'G3', 'GS3', 'A3', 'AS3', 'B3',
    'C4', 'CS4', 'D4', 'DS4', 'E4', 'F4', 'FS4', 'G4', 'GS4', 'A4', 'AS4', 'B4',
    'C5', 'CS5', 'D5', 'DS5', 'E5', 'F5', 'FS5', 'G5', 'GS5', 'A5', 'AS5', 'B5',
    'C6', 'CS6', 'D6', 'DS6', 'E6', 'F6', 'FS6', 'G6', 'GS6', 'A6', 'AS6', 'B6',
    'C7', 'CS7', 'D7', 'DS7', 'E7', 'F7', 'FS7', 'G7', 'GS7', 'A7', 'AS7', 'B7',
    'C8', 'CS8', 'D8', 'DS8', 'E8', 'F8', 'FS8', 'G8', 'GS8', 'A8', 'AS8', 'B8',
    'C9', 'CS9', 'D9', 'DS9', 'E9', 'F9', 'FS9', 'G9'
]
