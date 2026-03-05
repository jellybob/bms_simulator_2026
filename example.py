from bms_simulator import controller
from bms_simulator.controller import SetFn, State


def update(state: State, previous_state: State, set: SetFn):
    print(f"The time is now {state.time}")
    if state.occupancy:
        if not state.lights:
            print("Turning on the lights")
            set("lights", True)

        heat_required = False
        aircon_required = False
        if state.temperature < 20:
            heat_required = True
        elif state.temperature > 25:
            aircon_required = True

        if state.heat != heat_required:
            set("heat", heat_required)
        if state.air_con != aircon_required:
            set("air_con", aircon_required)

    else:
        if state.lights:
            print("Turning off the lights")
            set("lights", False)


controller.run(update)
