import asyncio
import logging
import math
import random
from dataclasses import dataclass

import aiomqtt

log = logging.getLogger(__name__)

MINUTES_PER_DAY = 1440

# Outside air temperature: cosine curve across the day
OAT_BASE = 15.0
OAT_AMPLITUDE = 5.0
OAT_PEAK_MINUTE = 900  # 3:00 PM — hottest point

# Interior temperature drift rate
THERMAL_RATE = 0.01  # °C per minute per degree of differential

# Light level: half-sine from sunrise to sunset
SUNRISE = 360  # 6:00 AM
SUNSET = 1200  # 8:00 PM
LIGHT_PEAK_LUX = 500.0

# Occupancy: business hours
BUSINESS_START = 480  # 8:00 AM
BUSINESS_END = 1080  # 6:00 PM

# Daily randomness
OCCUPANCY_JITTER = 30  # ±30 min
LIGHT_JITTER = 20  # ±20 min

# Actuator specifications
HEATER_POWER_KW = 800
HEATER_HEAT_CONTRIBUTION = 10.0  # °C
AC_POWER_KW = 1000
AC_HEAT_REMOVAL = 10.0  # °C
LIGHTS_POWER_KW = 80
LIGHTS_LUX_CONTRIBUTION = 400.0


def compute_oat(time: float) -> float:
    """Compute outside air temperature from a daily cosine curve."""
    angle = 2 * math.pi * (time - OAT_PEAK_MINUTE) / MINUTES_PER_DAY
    return OAT_BASE + OAT_AMPLITUDE * math.cos(angle)


def compute_light_level(time: float, start_offset: float = 0.0, end_offset: float = 0.0) -> float:
    """Compute light level as a half-sine between sunrise and sunset."""
    sunrise = SUNRISE + start_offset
    sunset = SUNSET + end_offset
    if time < sunrise or time >= sunset:
        return 0.0
    progress = (time - sunrise) / (sunset - sunrise)
    return LIGHT_PEAK_LUX * math.sin(progress * math.pi)


@dataclass
class Actuator:
    """A controllable device that draws power and influences the environment."""

    name: str
    topic: str
    on: bool = False
    power_kw: float = 0.0


class Server:
    def __init__(self, host: str, port: int, base_topic: str):
        self.host = host
        self.port = port
        self.base = base_topic

        # Time state
        self.time: float = 480.0  # 8:00 AM
        self.time_rate: float = 1.0  # minutes per second
        self.time_overridden: bool = False

        # Sensor values
        self.oat: float = 15.0
        self.oat_overridden: bool = False
        self.temperature: float = 22.0
        self.temperature_overridden: bool = False
        self.occupied: bool = False
        self.occupancy_overridden: bool = False
        self.light_level: float = 0.0
        self.light_level_overridden: bool = False

        # Actuators
        self.actuators: dict[str, Actuator] = {
            "heat": Actuator("Heater", "heat", power_kw=HEATER_POWER_KW),
            "air_con": Actuator("Air Conditioner", "air_con", power_kw=AC_POWER_KW),
            "lights": Actuator("Lights", "lights", power_kw=LIGHTS_POWER_KW),
        }

        # Power tracking
        self.power_usage: float = 0.0
        self.cumulative_power_usage: float = 0.0

        # Daily jitter offsets (re-randomized each simulated day)
        self._occupancy_start_offset: float = 0.0
        self._occupancy_end_offset: float = 0.0
        self._light_start_offset: float = 0.0
        self._light_end_offset: float = 0.0
        self._randomize_day()

    def _randomize_day(self):
        """Pick fresh random offsets for the new simulated day."""
        self._occupancy_start_offset = random.uniform(-OCCUPANCY_JITTER, OCCUPANCY_JITTER)
        self._occupancy_end_offset = random.uniform(-OCCUPANCY_JITTER, OCCUPANCY_JITTER)
        self._light_start_offset = random.uniform(-LIGHT_JITTER, LIGHT_JITTER)
        self._light_end_offset = random.uniform(-LIGHT_JITTER, LIGHT_JITTER)

    def tick(self):
        """Advance simulation by one second. Called once per second."""
        prev_time = self.time
        if not self.time_overridden:
            self.time = (self.time + self.time_rate) % MINUTES_PER_DAY
            if self.time < prev_time:
                self._randomize_day()
                self.cumulative_power_usage = 0.0

        if not self.oat_overridden:
            self.oat = compute_oat(self.time)

        if not self.temperature_overridden:
            diff = self.oat - self.temperature
            self.temperature += diff * THERMAL_RATE * self.time_rate
            if self.actuators["heat"].on:
                self.temperature += THERMAL_RATE * HEATER_HEAT_CONTRIBUTION * self.time_rate
            if self.actuators["air_con"].on:
                self.temperature -= THERMAL_RATE * AC_HEAT_REMOVAL * self.time_rate

        if not self.occupancy_overridden:
            start = BUSINESS_START + self._occupancy_start_offset
            end = BUSINESS_END + self._occupancy_end_offset
            self.occupied = start <= self.time < end

        if not self.light_level_overridden:
            self.light_level = compute_light_level(
                self.time, self._light_start_offset, self._light_end_offset
            )
            if self.actuators["lights"].on:
                self.light_level += LIGHTS_LUX_CONTRIBUTION

        self.power_usage = sum(a.power_kw for a in self.actuators.values() if a.on)
        self.cumulative_power_usage += self.power_usage * (self.time_rate / 60.0)

    def handle_message(self, topic_suffix: str, payload: str):
        """Process an incoming MQTT message. topic_suffix is relative to base_topic."""
        # Check for actuator control messages
        if topic_suffix.endswith("/set"):
            actuator_topic = topic_suffix[:-4]
            if actuator_topic in self.actuators:
                self.actuators[actuator_topic].on = payload.lower() == "true"
                return

        match topic_suffix:
            case "time/set":
                self.time = float(payload)
                self.time_overridden = True
            case "time/overridden/set":
                if payload.lower() == "false":
                    self.time_overridden = False
            case "time/rate/set":
                self.time_rate = float(payload)
            case "oat/set":
                self.oat = float(payload)
                self.oat_overridden = True
            case "oat/overridden/set":
                if payload.lower() == "false":
                    self.oat_overridden = False
            case "temperature/set":
                self.temperature = float(payload)
                self.temperature_overridden = True
            case "temperature/overridden/set":
                if payload.lower() == "false":
                    self.temperature_overridden = False
            case "occupancy/set":
                self.occupied = payload.lower() == "true"
                self.occupancy_overridden = True
            case "occupancy/overridden/set":
                if payload.lower() == "false":
                    self.occupancy_overridden = False
            case "light_level/set":
                self.light_level = float(payload)
                self.light_level_overridden = True
            case "light_level/overridden/set":
                if payload.lower() == "false":
                    self.light_level_overridden = False

    async def run(self):
        async with aiomqtt.Client(self.host, self.port) as client:
            self._client = client

            # Subscribe to control topics
            await client.subscribe(f"{self.base}/+/set")
            await client.subscribe(f"{self.base}/+/+/set")

            # Publish initial state
            await self._publish_all()

            async with asyncio.TaskGroup() as tg:
                tg.create_task(self._tick_loop())
                tg.create_task(self._message_loop())

    async def _tick_loop(self):
        while True:
            await asyncio.sleep(1)
            self.tick()
            await self._publish_all()

    async def _message_loop(self):
        async for msg in self._client.messages:
            topic = str(msg.topic)
            payload = msg.payload.decode() if msg.payload else ""

            # Strip base topic prefix to get the suffix
            prefix = f"{self.base}/"
            if topic.startswith(prefix):
                suffix = topic[len(prefix) :]
                log.info("Received %s = %s", suffix, payload)
                self.handle_message(suffix, payload)

                # Publish updated state after handling
                await self._publish_all()

    async def _publish_time(self):
        await self._client.publish(f"{self.base}/time", str(self.time), retain=True)

    async def _publish_all(self):
        client = self._client
        base = self.base
        await client.publish(f"{base}/time", str(self.time), retain=True)
        await client.publish(f"{base}/time/rate", str(self.time_rate), retain=True)
        overridden = str(self.time_overridden).lower()
        await client.publish(f"{base}/time/overridden", overridden, retain=True)
        await client.publish(f"{base}/oat", str(self.oat), retain=True)
        await client.publish(
            f"{base}/oat/overridden", str(self.oat_overridden).lower(), retain=True
        )
        await client.publish(f"{base}/temperature", str(self.temperature), retain=True)
        await client.publish(
            f"{base}/temperature/overridden",
            str(self.temperature_overridden).lower(),
            retain=True,
        )
        await client.publish(f"{base}/occupancy", "true" if self.occupied else "false", retain=True)
        await client.publish(
            f"{base}/occupancy/overridden",
            str(self.occupancy_overridden).lower(),
            retain=True,
        )
        await client.publish(f"{base}/light_level", str(self.light_level), retain=True)
        await client.publish(
            f"{base}/light_level/overridden",
            str(self.light_level_overridden).lower(),
            retain=True,
        )
        for topic, actuator in self.actuators.items():
            state = "true" if actuator.on else "false"
            await client.publish(f"{base}/{topic}", state, retain=True)
        await client.publish(f"{base}/power_usage", str(self.power_usage), retain=True)
        await client.publish(
            f"{base}/cumulative_power_usage",
            str(self.cumulative_power_usage),
            retain=True,
        )
