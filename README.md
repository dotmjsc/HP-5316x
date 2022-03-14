# HP5316x
HP 5316x universal counter driver for Python (HP 5316a, HP 5316b)

Needs the following non-standard packages:
* pyvisa
* enum

Usage example:

```python
instrument = HP5316X("GPIB1::20::INSTR")

# set measurement mode to period channel A
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
