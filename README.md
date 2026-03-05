# BMS Simulator 2026

This tool is designed to teach the basics of interacting with
environmental control systems via MQTT in Python. It originates
from my son's school running a take your child to work day, which
is a concept that was never designed for the modern world. I needed
something to give him a taste of what the work of interacting with
building management systems looks like.

## What is it?

There's two components to this project. The server, which is responsible
for pretending to be a floor of an office building, exposing various
"device" states to an MQTT broker. The client provides a simple Python
interface for interacting with the broker to read sensor state and write
to device states.

None of this is fancy, or even neccessarily functional, I'm writing it one
day before its needed, so everything is rough.

## The Server

The server runs a simulation loop, calling the `tick` method once a second
which is then responsible for updating the environment's state based on
conditions. Over the course of a day various aspects of the office are updated
such as temperature and occupancy.

The following devices exist, which are matched here with the MQTT topic.

### Sensors

Report environmental state:

- Time of day in minutes since midnight: `time`
  - Has an attached simulation rate setting how many minutes advance in each second
    of realtime. `time/rate`
- Outside Air Temperature (OAT) in degrees celsius: `oat`
  - Varies over the course of a day
- Occupancy, which is a simple boolean: `occupancy`
- Light level in lux `light_level`
  - Varies with time of day
- Power usage in KW `power_usage`
  - The sum of all actuators currently drawing power
- Daily cumulative power usage in KWh `cumulative_power_usage`
  - Tracks how much power has been drawn over the course of the day
  - Resets to 0 daily

### Acctuators

Influence the environment by contributing something, such as heat or light. All of
these require power to run, which will be tracked.

- Heater: `heat`
  - Draws 800KW while on
  - Contributes heat into the environment, similar to outside air temperature
  - When on provides 10 celsius of heat
- Air conditioner: `air_con`
  - Draws 1000KW while on
  - Removes heat from the environment, the opposite of a heater
  - When on removes 10 celsius of heat
- Lights: `lights`
  - Draws 80KW while on
  - Adds 400 lux of ambient light

## The Client

The client is designed specifically for ease of use. It inentionally hides
many aspects of interacting with an MQTT broker behind a simple API focusing
on events from sensors.

An example program using it might look like this (it doesn't yet, because I
haven't yet written it):

```python
from bms_simulator import controller
from bms_simulator.controller import State, SetFn

def update(state: State, previous: State, set: SetFn):
    print(f"The time is now {state.time}")
    if state.time >= 900 and state.time <= 540:
        set("lights", True)
 
controler.run(update)
```

## MQTT topics

The server process runs with a configurable base topic (defaulting to the empty
string ""), and publishes to topics below that. As an example if the base were
`bms_sim` then the following topics will contain sensor data:

- `bms_sim/time`: The current time in minutes since midnight.
- `bms_sim/oat`: The outside air temperature in degrees Celsius.
- `bms_sim/temperature`: The interior temperature in degrees Celsius.
- `bms_sim/occupancy`: Whether the space is occupied or not. "true" or "false"
- `bms_sim/light_level`: The light level in lux.

To set a value write to `bms_sim/<topic>/set` where `<topic>` is one of the topics listed above.

This will cause `bms_sim/<topic>/overridden` to be set to `true`, and automatic adjustments to be
disabled. Writing `false` to `bms_sim/<topic>/overridden/set` will re-enable automatic adjustments, taking
the current sensor value as the new start point.

### Time management

- `bms_sim/time/rate`: The rate at which time advances in minutes per second. Default is 1.0.
  - To change the rate, write to `bms_sim/time/rate/set`.
