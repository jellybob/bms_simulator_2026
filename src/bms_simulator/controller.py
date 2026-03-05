import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Protocol, overload

import aiomqtt

from bms_simulator.cli import parse_broker_url

# Maps MQTT topic suffixes to State field names (where they differ)
_TOPIC_TO_FIELD = {
    "occupancy": "occupancy",
    "heat": "heat",
    "air_con": "air_con",
    "lights": "lights",
}

_BOOL_FIELDS = {"occupancy", "heat", "air_con", "lights"}

_FLOAT_FIELDS = {
    "time",
    "time_rate",
    "oat",
    "temperature",
    "exterior_light_level",
    "interior_light_level",
    "power_usage",
    "cumulative_power_usage",
}

_ALL_FIELDS = _BOOL_FIELDS | _FLOAT_FIELDS


class SetFn(Protocol):
    """Function to set actuator or sensor values."""

    @overload
    def __call__(self, topic: Literal["heat"], value: bool) -> None: ...

    @overload
    def __call__(self, topic: Literal["air_con"], value: bool) -> None: ...

    @overload
    def __call__(self, topic: Literal["lights"], value: bool) -> None: ...

    @overload
    def __call__(self, topic: Literal["occupancy"], value: bool) -> None: ...

    @overload
    def __call__(self, topic: Literal["time"], value: float | int) -> None: ...

    @overload
    def __call__(self, topic: Literal["time_rate"], value: float | int) -> None: ...

    @overload
    def __call__(self, topic: Literal["oat"], value: float | int) -> None: ...

    @overload
    def __call__(self, topic: Literal["temperature"], value: float | int) -> None: ...

    @overload
    def __call__(self, topic: Literal["exterior_light_level"], value: float | int) -> None: ...

    @overload
    def __call__(self, topic: Literal["interior_light_level"], value: float | int) -> None: ...

    def __call__(self, topic: str, value: bool | float | int) -> None:
        """Publish a value to the specified topic.

        Args:
            topic: The topic name (e.g., "lights", "heat", "temperature")
            value: The value to set (bool for actuators, float/int for sensors)
        """
        ...


@dataclass(frozen=True)
class State:
    """Immutable snapshot of the BMS simulation state."""

    time: float = 0.0
    time_rate: float = 1.0
    oat: float = 0.0
    temperature: float = 0.0
    occupancy: bool = False
    exterior_light_level: float = 0.0
    interior_light_level: float = 0.0
    heat: bool = False
    air_con: bool = False
    lights: bool = False
    power_usage: float = 0.0
    cumulative_power_usage: float = 0.0


def _parse_value(field: str, raw: str) -> float | bool:
    """Parse an MQTT string payload into the appropriate Python type."""
    if field in _BOOL_FIELDS:
        return raw.lower() == "true"
    return float(raw)


def _build_state(values: dict[str, str]) -> State:
    """Build a State from accumulated topic values."""
    kwargs = {}
    for field in _ALL_FIELDS:
        if field in values:
            kwargs[field] = _parse_value(field, values[field])
    return State(**kwargs)


def _format_value(value: object) -> str:
    """Convert a Python value to an MQTT payload string."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def run(
    callback: Callable[[State, State, SetFn], None],
    broker_url: str = "mqtt://broker/bms_sim",
):
    """Connect to the MQTT broker and call *callback* on each tick.

    The callback receives ``(state, previous_state, set)`` where *state* is the
    current :class:`State` snapshot, *previous_state* is the previous state,
    and *set* is a :class:`SetFn` that publishes values to topics.

    This function blocks until interrupted.

    Args:
        callback: Function called on each tick with (state, previous_state, set)
        broker_url: MQTT broker URL, e.g. "mqtt://broker/bms_sim"
    """
    host, port, base = parse_broker_url(broker_url)

    async def _run():
        async with aiomqtt.Client(host, port) as client:
            values: dict[str, str] = {}
            previous_state: State = State()

            async def set_value(topic: str, value: bool | float | int):
                payload = _format_value(value)
                await client.publish(f"{base}/{topic}/set", payload)

            def set_fn(topic: str, value: bool | float | int):
                asyncio.get_event_loop().create_task(set_value(topic, value))

            await client.subscribe(f"{base}/#")

            async for msg in client.messages:
                topic = str(msg.topic)
                prefix = f"{base}/"
                if not topic.startswith(prefix):
                    continue
                suffix = topic[len(prefix) :]

                # Only track top-level state topics, ignore /set, /overridden etc.
                if suffix not in _ALL_FIELDS:
                    continue

                payload = msg.payload.decode() if msg.payload else ""
                values[suffix] = payload

                # The server publishes time first after each tick — use it as
                # the trigger to call the user's callback with a full snapshot.
                if suffix == "time":
                    state = _build_state(values)
                    callback(state, previous_state, set_fn)
                    previous_state = state

    asyncio.run(_run())
