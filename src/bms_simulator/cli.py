import asyncio
import logging
from urllib.parse import urlparse

import click

from bms_simulator.server import Server


def parse_broker_url(url: str) -> tuple[str, int, str]:
    """Parse an MQTT broker URL into (host, port, base_topic).

    Expected format: mqtt://host[:port][/base_topic]
    """
    parsed = urlparse(url)
    if parsed.scheme != "mqtt":
        raise click.BadParameter(f"Expected mqtt:// scheme, got {parsed.scheme}://")

    host = parsed.hostname
    if not host:
        raise click.BadParameter("No hostname in broker URL")

    port = parsed.port or 1883
    base_topic = parsed.path.lstrip("/")

    return host, port, base_topic


@click.command()
@click.argument("broker_url")
def main(broker_url: str):
    """Run the BMS simulator server.

    BROKER_URL: MQTT broker URL, e.g. mqtt://broker/base_topic
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    host, port, base_topic = parse_broker_url(broker_url)
    click.echo(f"Connecting to {host}:{port}, base topic: {base_topic!r}")

    server = Server(host, port, base_topic)
    asyncio.run(server.run())
