from bms_simulator.server import (
    LIGHT_PEAK_LUX,
    MINUTES_PER_DAY,
    OAT_AMPLITUDE,
    OAT_BASE,
    Server,
    compute_oat,
)


def make_server() -> Server:
    server = Server("localhost", 1883, "test")
    # Zero out jitter for deterministic tests
    server._occupancy_start_offset = 0.0
    server._occupancy_end_offset = 0.0
    server._light_start_offset = 0.0
    server._light_end_offset = 0.0
    return server


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


# --- OAT automation tests ---


def test_tick_updates_oat():
    server = make_server()
    server.tick()
    assert server.oat == compute_oat(server.time)


def test_oat_warmest_at_afternoon():
    server = make_server()
    server.time = 899.0
    server.time_overridden = True
    server.tick()
    assert server.oat > OAT_BASE + OAT_AMPLITUDE - 0.1


def test_oat_coldest_at_early_morning():
    server = make_server()
    server.time = 180.0
    server.time_overridden = True
    server.tick()
    # At 3am-ish, OAT should be near the minimum
    assert server.oat < OAT_BASE - OAT_AMPLITUDE + 1.0


def test_oat_respects_override():
    server = make_server()
    server.oat = 99.0
    server.oat_overridden = True
    server.tick()
    assert server.oat == 99.0


# --- Interior temperature automation tests ---


def test_temperature_drops_when_oat_lower():
    server = make_server()
    server.oat = 5.0
    server.oat_overridden = True
    server.temperature = 22.0
    initial = server.temperature
    server.tick()
    assert server.temperature < initial


def test_temperature_rises_when_oat_higher():
    server = make_server()
    server.oat = 35.0
    server.oat_overridden = True
    server.temperature = 22.0
    initial = server.temperature
    server.tick()
    assert server.temperature > initial


def test_temperature_respects_override():
    server = make_server()
    server.temperature = 22.0
    server.temperature_overridden = True
    server.tick()
    assert server.temperature == 22.0


# --- Occupancy automation tests ---


def test_occupied_during_business_hours():
    server = make_server()
    server.time = 720.0  # noon
    server.time_overridden = True
    server.tick()
    assert server.occupied is True


def test_unoccupied_before_business_hours():
    server = make_server()
    server.time = 300.0  # 5:00 AM
    server.time_overridden = True
    server.tick()
    assert server.occupied is False


def test_unoccupied_after_business_hours():
    server = make_server()
    server.time = 1200.0  # 8:00 PM
    server.time_overridden = True
    server.tick()
    assert server.occupied is False


def test_occupancy_respects_override():
    server = make_server()
    server.time = 0.0  # midnight
    server.time_overridden = True
    server.occupied = True
    server.occupancy_overridden = True
    server.tick()
    assert server.occupied is True


# --- Light level automation tests ---


def test_light_level_zero_at_night():
    server = make_server()
    server.time = 0.0  # midnight
    server.time_overridden = True
    server.tick()
    assert server.light_level == 0.0


def test_light_level_peaks_near_noon():
    server = make_server()
    # Midpoint of sunrise(360)..sunset(1200) = 780
    server.time = 779.0
    server.time_overridden = True
    server.tick()
    assert server.light_level > LIGHT_PEAK_LUX * 0.95


def test_light_level_respects_override():
    server = make_server()
    server.light_level = 42.0
    server.light_level_overridden = True
    server.tick()
    assert server.light_level == 42.0


# --- Day wrap randomization test ---


def test_midnight_wrap_randomizes_day():
    server = make_server()
    server.time = MINUTES_PER_DAY - 0.5
    server.time_rate = 1.0
    server._occupancy_start_offset = 0.0
    server._occupancy_end_offset = 0.0
    server._light_start_offset = 0.0
    server._light_end_offset = 0.0
    server.tick()
    # After wrapping past midnight, at least some offset should have changed
    # (with overwhelming probability given uniform random over ±30/±20)
    offsets = [
        server._occupancy_start_offset,
        server._occupancy_end_offset,
        server._light_start_offset,
        server._light_end_offset,
    ]
    assert any(o != 0.0 for o in offsets)
