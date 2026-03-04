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

Here's a feature list. Checked boxes indicate features that exist, unchecked
boxes are stuff that doesn't exist.

- [x] A devcontainer that can be run Github Codespaces
- [x] An MQTT broker, configured for open access from containers
- [ ] A process which simulates being an office with a bunch of "sensors"
  - [ ] Time of day
    - [ ] Updates automatically
    - [ ] Has a configurable rate (defaulting to 1 minute per second)
  - [ ] Outside air temperature (OAT)
    - [ ] Updates automatically
    - [ ] Can be overridden to a specific temperature
  - [ ] Space temperature
    - [ ] Kind of simulated?
    - [ ] Drops if the OAT is lower than interior temp
    - [ ] Climbs if the OAT is higher than interior temp
    - [ ] That scales with the differential
  - [ ] Occupancy
    - [ ] Somewhat tied to time of day
    - [ ] Can be overridden
  - [ ] Light level
    - [ ] Somewhat tied to time of day
    - [ ] Can be overidden
- [ ] A web UI that shows/allows control of all that via an API

## The Client

The client is designed specifically for ease of use. It inentionally hides
many aspects of interacting with an MQTT broker behind a simple API focusing
on events from sensors.

An example program using it might look like this (it doesn't yet, because I
haven't yet written it):

```python
from bms_simulator import controller

def time_updated(payload):
    print(f"The time is now {payload.value}")
    if time.value >= 900 and time.value <= 540:
        controller.send("lights/set", 1.0)
 
controller.on_event("time", time_updated)
controler.run()
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
disabled. Writing `false` to `bms_sim/<topic>/overridden` will re-enable automatic adjustments, taking
the current sensor value as the new start point.

### Time management

- `bms_sim/time/rate`: The rate at which time advances in minutes per second. Default is 1.0.
