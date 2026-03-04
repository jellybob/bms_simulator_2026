import asyncio
import logging

import aiomqtt

log = logging.getLogger(__name__)

MINUTES_PER_DAY = 1440


class Server:
    def __init__(self, host: str, port: int, base_topic: str):
        self.host = host
        self.port = port
        self.base = base_topic

        # Time state
        self.time: float = 480.0  # 8:00 AM
        self.time_rate: float = 1.0  # minutes per second
        self.time_overridden: bool = False

        # Placeholder sensor values (no automatic behavior yet)
        self.oat: float = 15.0
        self.oat_overridden: bool = False
        self.temperature: float = 22.0
        self.temperature_overridden: bool = False
        self.occupied: bool = False
        self.occupancy_overridden: bool = False
        self.light_level: float = 0.0
        self.light_level_overridden: bool = False

    def tick(self):
        """Advance simulation by one second. Called once per second."""
        if not self.time_overridden:
            self.time = (self.time + self.time_rate) % MINUTES_PER_DAY

    def handle_message(self, topic_suffix: str, payload: str):
        """Process an incoming MQTT message. topic_suffix is relative to base_topic."""
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
            await self._publish_time()

    async def _message_loop(self):
        async for msg in self._client.messages:
            topic = str(msg.topic)
            payload = msg.payload.decode() if msg.payload else ""

            # Strip base topic prefix to get the suffix
            prefix = f"{self.base}/"
            if topic.startswith(prefix):
                suffix = topic[len(prefix):]
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
