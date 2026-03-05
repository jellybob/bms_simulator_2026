from bms_simulator import controller
from bms_simulator.controller import SetFn, State


def update(state: State, _previous: State, set: SetFn) -> None:
    """Handle updates as they arrive."""

    # Split the time (minutes since midnight) into hour and minute.
    time = state.time
    hour = time // 60
    minute = time % 60

    # Print that to the console.
    print(f"The time is {hour:02.0f}:{minute:02.0f}")


controller.run(update)
