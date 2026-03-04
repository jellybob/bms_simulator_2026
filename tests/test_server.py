from bms_simulator.server import MINUTES_PER_DAY, Server


def make_server() -> Server:
    return Server("localhost", 1883, "test")


def test_tick_advances_time():
    server = make_server()
    initial = server.time
    server.tick()
    assert server.time == initial + server.time_rate


def test_tick_wraps_at_midnight():
    server = make_server()
    server.time = MINUTES_PER_DAY - 0.5
    server.time_rate = 1.0
    server.tick()
    assert server.time == 0.5


def test_tick_respects_override():
    server = make_server()
    server.time_overridden = True
    initial = server.time
    server.tick()
    assert server.time == initial


def test_tick_rate_change():
    server = make_server()
    server.time_rate = 5.0
    initial = server.time
    server.tick()
    assert server.time == initial + 5.0


def test_handle_time_set():
    server = make_server()
    server.handle_message("time/set", "720")
    assert server.time == 720.0
    assert server.time_overridden is True


def test_handle_override_clear():
    server = make_server()
    server.time_overridden = True
    server.handle_message("time/overridden/set", "false")
    assert server.time_overridden is False


def test_handle_override_clear_is_case_insensitive():
    server = make_server()
    server.time_overridden = True
    server.handle_message("time/overridden/set", "False")
    assert server.time_overridden is False


def test_handle_rate_change():
    server = make_server()
    server.handle_message("time/rate/set", "10.0")
    assert server.time_rate == 10.0


def test_handle_oat_set():
    server = make_server()
    server.handle_message("oat/set", "25.5")
    assert server.oat == 25.5
    assert server.oat_overridden is True


def test_handle_oat_override_clear():
    server = make_server()
    server.oat_overridden = True
    server.handle_message("oat/overridden/set", "false")
    assert server.oat_overridden is False


def test_handle_temperature_set():
    server = make_server()
    server.handle_message("temperature/set", "18.0")
    assert server.temperature == 18.0
    assert server.temperature_overridden is True


def test_handle_temperature_override_clear():
    server = make_server()
    server.temperature_overridden = True
    server.handle_message("temperature/overridden/set", "false")
    assert server.temperature_overridden is False


def test_handle_occupancy_set_true():
    server = make_server()
    server.handle_message("occupancy/set", "true")
    assert server.occupied is True
    assert server.occupancy_overridden is True


def test_handle_occupancy_set_false():
    server = make_server()
    server.occupied = True
    server.handle_message("occupancy/set", "false")
    assert server.occupied is False
    assert server.occupancy_overridden is True


def test_handle_occupancy_override_clear():
    server = make_server()
    server.occupancy_overridden = True
    server.handle_message("occupancy/overridden/set", "false")
    assert server.occupancy_overridden is False


def test_handle_light_level_set():
    server = make_server()
    server.handle_message("light_level/set", "500.0")
    assert server.light_level == 500.0
    assert server.light_level_overridden is True


def test_handle_light_level_override_clear():
    server = make_server()
    server.light_level_overridden = True
    server.handle_message("light_level/overridden/set", "false")
    assert server.light_level_overridden is False


def test_initial_state():
    server = make_server()
    assert server.time == 480.0
    assert server.time_rate == 1.0
    assert server.time_overridden is False
    assert server.oat == 15.0
    assert server.oat_overridden is False
    assert server.temperature == 22.0
    assert server.temperature_overridden is False
    assert not server.occupied
    assert server.occupancy_overridden is False
    assert server.light_level == 0.0
    assert server.light_level_overridden is False
