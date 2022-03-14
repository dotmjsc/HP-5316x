'''
HP5316x GPIB driver
2020 MJSC
'''

import pyvisa
import enum
import time

class Measurement:
    def __init__(self):
        self.raw = ""
        self.value = 0.0
        self.overflow = False
        self.unit = "NONE"


# Command for Gates
GATEMODES_LIST = (
    'GA0',
    'GA1',
    'GA2',
    'GA3',
    )

# Command for Trigger Level Modes
TRIGGERLEVELMODES_LIST = (
    'TR0',
    'TR1',
    )

# Command for Trigger Slopes A
TRIGGERSLOPES_A_LIST = (
    'AS0',
    'AS1',
    )

# Command for Trigger Slopes B
TRIGGERSLOPES_B_LIST = (
    'BS0',
    'BS1',
    )

# Command for Meas Modes
MEASMODES_LIST = (
    'FN0',
    'FN1',
    'FN2',
    'FN3',
    'FN4',
    'FN5',
    'FN6',
    'FN7',
    'FN8',
    'FN9',
    'FN10',
    'FN11',
    'FN12',
    'FN13',
    'FN14',
    )


def get_available_devices():
    rm = pyvisa.ResourceManager()
    devices = rm.list_resources()
    rm.close()
    return devices


def _decode(rawdata):
    measurement = Measurement()
    measurement.raw = rawdata
    measurement.value = float(rawdata[1:20])

    if rawdata[0] == "O":
        measurement.overflow = True
    elif rawdata[0] == "F":
        measurement.unit = "HZ"
    elif rawdata[0] == "T":
        measurement.unit = "SEC"
    elif rawdata[0] == "X":
        measurement.unit = "ERROR"
    elif rawdata[0] == " ":
        measurement.unit = "NONE"
    return measurement


class HP5316X(object):

    class TriggerLevelModes(enum.Enum):
        FRONT_CONTROL = 0
        SET_LEVEL = 1

    class TriggerSlopes(enum.Enum):
        POSITIVE = 0
        NEGATIVE = 1

    class GateModes(enum.Enum):
        LONG_FRONT = 0
        SHORT_FRONT = 1
        LONG_REAR = 2
        SHORT_REAR = 3

    class MeasModes(enum.Enum):
        DISPLAY_TEST = 0
        FREQ_A = 1
        INT_A_TO_B = 2
        INT_DELAY = 3
        RATIO_AB = 4
        FREQ_C = 5
        TOTALIZE_STOP = 6
        PERIOD_A = 7
        INT_AVG_A_TO_B = 8
        CHECK_10MHZ = 9
        A_GATED_BY_B = 10
        GATE_TIME = 11
        TOTALIZE_START = 12
        FREQ_A_ARMED_BY_B_POS = 13
        FREQ_A_ARMED_BY_B_NEG = 14


    def __init__(self, address, settle_time = 0.2):
        self._address = address
        self._rm = pyvisa.ResourceManager()
        self._inst = self._rm.open_resource(address)
        self._inst.write_termination = "\r\n"
        self._inst.read_termination = "\r\n"
        self._settle_time = settle_time
        self._inst.clear()
        self._init_settings()

    def __del__(self):
        self._rm.close()

    def _init_settings(self):
        # set wait mode to single
        self._inst.write('WA1')

        # default settings
        self.gatemode = self.GateModes.LONG_FRONT
        self.measmode = self.MeasModes.FREQ_A
        self.triggerlevelmode = self.TriggerLevelModes.FRONT_CONTROL
        self.triggerslope_a = self.TriggerSlopes.POSITIVE
        self.triggerslope_b = self.TriggerSlopes.POSITIVE
        self.triggerlevel_a = 0
        self.triggerlevel_b = 0
        self.timeout = 2

    def get_measurement(self):
        self._inst.clear()
        try:
            result = self._inst.read()
        except:
            return None
        return _decode(result)

    def reset(self):
        self._inst.write('RE')
        time.sleep(self._settle_time)

    def initialize(self):
        self._inst.write('IN')
        self._init_settings()
        time.sleep(self._settle_time)

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        if not isinstance(timeout, int):
            raise TypeError('timeout must be an integer')
        self._timeout = timeout
        self._inst.timeout = timeout

    @property
    def triggerlevelmode(self):
        return self._triggerlevelmode

    @triggerlevelmode.setter
    def triggerlevelmode(self, mode):
        if not isinstance(mode, self.TriggerLevelModes):
            raise TypeError('mode must be an instance of TriggerLevelModes Enum')
        self._triggerlevelmode = mode
        self._inst.write(TRIGGERLEVELMODES_LIST[self._triggerlevelmode.value])
        time.sleep(self._settle_time)

    @property
    def triggerslope_a(self):
        return self._triggerslope_A

    @triggerslope_a.setter
    def triggerslope_a(self, slope):
        if not isinstance(slope, self.TriggerSlopes):
            raise TypeError('slope must be an instance of TriggerSlopes Enum')
        self._triggerslope_A = slope
        self._inst.write(TRIGGERSLOPES_A_LIST[self._triggerslope_A.value])
        time.sleep(self._settle_time)

    @property
    def triggerslope_b(self):
        return self._triggerslope_B

    @triggerslope_b.setter
    def triggerslope_b(self, slope):
        if not isinstance(slope, self.TriggerSlopes):
            raise TypeError('slope must be an instance of TriggerSlopes Enum')
        self._triggerslope_B = slope
        self._inst.write(TRIGGERSLOPES_B_LIST[self._triggerslope_B.value])
        time.sleep(self._settle_time)

    @property
    def triggerlevel_a(self):
        return self.triggerlevel_A

    @triggerlevel_a.setter
    def triggerlevel_a(self, level):
        if isinstance(level, int):
            level = float(level)
        if not isinstance(level, float):
            raise TypeError('level must be a float')
        if level < -2.5 or level > 2.5:
            raise ValueError('level must be between -2.5 and 2.5')
        self._triggerlevel_A = level
        levelstring = 'AT{0:+.2f}'.format(level)
        self._inst.write(levelstring)
        time.sleep(self._settle_time)

    @property
    def triggerlevel_b(self):
        return self.triggerlevel_B

    @triggerlevel_b.setter
    def triggerlevel_b(self, level):
        if isinstance(level, int):
            level = float(level)
        if not isinstance(level, float):
            raise TypeError('level must be a float')
        if level < -2.5 or level > 2.5:
            raise ValueError('level must be between -2.5 and 2.5')
        self._triggerlevel_B = level
        levelstring = 'BT{0:+.2f}'.format(level)
        self._inst.write(levelstring)
        time.sleep(self._settle_time)

    @property
    def measmode(self):
        return self._measmode

    @measmode.setter
    def measmode(self, mode):
        if not isinstance(mode, self.MeasModes):
            raise TypeError('mode must be an instance of GateModes Enum')
        self._measmode = mode
        self._inst.write(MEASMODES_LIST[self._measmode.value])
        time.sleep(self._settle_time)

    @property
    def measmode(self):
        return self._measmode

    @measmode.setter
    def measmode(self, mode):
        if not isinstance(mode, self.MeasModes):
            raise TypeError('mode must be an instance of GateModes Enum')
        self._measmode = mode
        self._inst.write(MEASMODES_LIST[self._measmode.value])
        time.sleep(self._settle_time)

if __name__ == '__main__':
    instrument = HP5316X("GPIB1::20::INSTR")

    # set measurment mode to period channel A
    instrument.measmode = instrument.MeasModes.PERIOD_A

    # set gatemode to long with front control
    instrument.gatemode = instrument.GateModes.LONG_FRONT

    # set mode to manual level set
    instrument.triggerlevelmode = instrument.TriggerLevelModes.SET_LEVEL

    # set manual trigger level
    instrument.triggerlevel_a = 0.01

    # set positive trigger slopes
    instrument.triggerslope_a = instrument.TriggerSlopes.POSITIVE

    for i in range(3):
        # get one measurement
        meas = instrument.get_measurement()

        if meas is not None:
            print("raw answer: " + meas.raw)
            print("value: " + str(meas.value))
            print("unit: " + meas.unit)
            print("overflow: " + str(meas.overflow))

    del instrument
