import pytest
from click import BadParameter

from bms_simulator.cli import parse_broker_url


def test_parse_basic_url():
    host, port, base = parse_broker_url("mqtt://broker/base_topic")
    assert host == "broker"
    assert port == 1883
    assert base == "base_topic"


def test_parse_url_with_port():
    host, port, base = parse_broker_url("mqtt://broker:1884/topic")
    assert host == "broker"
    assert port == 1884
    assert base == "topic"


def test_parse_url_no_topic():
    host, port, base = parse_broker_url("mqtt://broker")
    assert host == "broker"
    assert port == 1883
    assert base == ""


def test_parse_url_nested_topic():
    host, port, base = parse_broker_url("mqtt://broker/floor/1")
    assert host == "broker"
    assert port == 1883
    assert base == "floor/1"


def test_parse_url_bad_scheme():
    with pytest.raises(BadParameter, match="mqtt://"):
        parse_broker_url("http://broker/topic")


def test_parse_url_no_host():
    with pytest.raises(BadParameter, match="hostname"):
        parse_broker_url("mqtt:///topic")
