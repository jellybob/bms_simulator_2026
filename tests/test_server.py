from bms_simulator.server import (
    AC_POWER_KW,
    HEATER_POWER_KW,
    LIGHT_PEAK_LUX,
    LIGHTS_LUX_CONTRIBUTION,
    LIGHTS_POWER_KW,
    MINUTES_PER_DAY,
    OAT_AMPLITUDE,
    OAT_BASE,
    WINDOW_TRANSMISSION_FACTOR,
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


def test_tick_at_zero_rate_does_not_advance_time_or_accumulate_power():
    server = make_server()
    server.time_rate = 0.0
    server.actuators["heat"].on = True
    initial_time = server.time
    initial_cumulative = server.cumulative_power_usage
    server.tick()
    assert server.time == initial_time
    assert server.cumulative_power_usage == initial_cumulative


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


def test_handle_exterior_light_level_set():
    server = make_server()
    server.handle_message("exterior_light_level/set", "500.0")
    assert server.exterior_light_level == 500.0
    assert server.exterior_light_level_overridden is True


def test_handle_exterior_light_level_override_clear():
    server = make_server()
    server.exterior_light_level_overridden = True
    server.handle_message("exterior_light_level/overridden/set", "false")
    assert server.exterior_light_level_overridden is False


def test_handle_interior_light_level_set():
    server = make_server()
    server.handle_message("interior_light_level/set", "500.0")
    assert server.interior_light_level == 500.0
    assert server.interior_light_level_overridden is True


def test_handle_interior_light_level_override_clear():
    server = make_server()
    server.interior_light_level_overridden = True
    server.handle_message("interior_light_level/overridden/set", "false")
    assert server.interior_light_level_overridden is False


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
    assert server.exterior_light_level == 0.0
    assert server.exterior_light_level_overridden is False
    assert server.interior_light_level == 0.0
    assert server.interior_light_level_overridden is False
    assert all(not a.on for a in server.actuators.values())
    assert server.power_usage == 0.0
    assert server.cumulative_power_usage == 0.0


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


def test_exterior_light_zero_at_night():
    server = make_server()
    server.time = 0.0  # midnight
    server.time_overridden = True
    server.tick()
    assert server.exterior_light_level == 0.0
    assert server.interior_light_level == 0.0


def test_exterior_light_peaks_near_noon():
    server = make_server()
    # Midpoint of sunrise(360)..sunset(1200) = 780
    server.time = 779.0
    server.time_overridden = True
    server.tick()
    assert server.exterior_light_level > LIGHT_PEAK_LUX * 0.95


def test_interior_light_is_attenuated_exterior():
    server = make_server()
    server.time = 779.0  # near midday peak
    server.time_overridden = True
    server.tick()
    expected = server.exterior_light_level * WINDOW_TRANSMISSION_FACTOR
    assert abs(server.interior_light_level - expected) < 0.01


def test_exterior_light_respects_override():
    server = make_server()
    server.exterior_light_level = 42.0
    server.exterior_light_level_overridden = True
    server.tick()
    assert server.exterior_light_level == 42.0


def test_interior_light_respects_override():
    server = make_server()
    server.interior_light_level = 42.0
    server.interior_light_level_overridden = True
    server.tick()
    assert server.interior_light_level == 42.0


def test_interior_light_uses_overridden_exterior():
    server = make_server()
    server.exterior_light_level = 100.0
    server.exterior_light_level_overridden = True
    server.tick()
    expected = 100.0 * WINDOW_TRANSMISSION_FACTOR
    assert abs(server.interior_light_level - expected) < 0.01


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


# --- Actuator control tests ---


def test_handle_heater_on():
    server = make_server()
    server.handle_message("heat/set", "true")
    assert server.actuators["heat"].on is True


def test_handle_heater_off():
    server = make_server()
    server.actuators["heat"].on = True
    server.handle_message("heat/set", "false")
    assert server.actuators["heat"].on is False


def test_handle_ac_on():
    server = make_server()
    server.handle_message("air_con/set", "true")
    assert server.actuators["air_con"].on is True


def test_handle_ac_off():
    server = make_server()
    server.actuators["air_con"].on = True
    server.handle_message("air_con/set", "false")
    assert server.actuators["air_con"].on is False


def test_handle_lights_on():
    server = make_server()
    server.handle_message("lights/set", "true")
    assert server.actuators["lights"].on is True


def test_handle_lights_off():
    server = make_server()
    server.actuators["lights"].on = True
    server.handle_message("lights/set", "false")
    assert server.actuators["lights"].on is False


def test_actuator_set_case_insensitive():
    server = make_server()
    server.handle_message("heat/set", "True")
    assert server.actuators["heat"].on is True
    server.handle_message("heat/set", "FALSE")
    assert server.actuators["heat"].on is False


# --- Heater effects on temperature ---


def test_heater_increases_temperature():
    server = make_server()
    server.temperature = 20.0
    server.oat = 20.0  # No OAT drift
    server.oat_overridden = True
    server.actuators["heat"].on = True
    server.tick()
    assert server.temperature > 20.0


def test_heater_respects_temperature_override():
    server = make_server()
    server.temperature = 20.0
    server.temperature_overridden = True
    server.actuators["heat"].on = True
    server.tick()
    assert server.temperature == 20.0


# --- AC effects on temperature ---


def test_ac_decreases_temperature():
    server = make_server()
    server.temperature = 25.0
    server.oat = 25.0  # No OAT drift
    server.oat_overridden = True
    server.actuators["air_con"].on = True
    server.tick()
    assert server.temperature < 25.0


def test_ac_respects_temperature_override():
    server = make_server()
    server.temperature = 25.0
    server.temperature_overridden = True
    server.actuators["air_con"].on = True
    server.tick()
    assert server.temperature == 25.0


def test_heater_and_ac_cancel_out():
    server = make_server()
    server.temperature = 22.0
    server.oat = 22.0  # No OAT drift
    server.oat_overridden = True
    server.actuators["heat"].on = True
    server.actuators["air_con"].on = True
    server.tick()
    assert abs(server.temperature - 22.0) < 0.001


# --- Lights effects on light level ---


def test_lights_add_lux_at_night():
    server = make_server()
    server.time = 0.0  # Midnight
    server.time_overridden = True
    server.actuators["lights"].on = True
    server.tick()
    assert server.exterior_light_level == 0.0
    assert server.interior_light_level == LIGHTS_LUX_CONTRIBUTION


def test_lights_add_to_ambient():
    server = make_server()
    server.time = 779.0  # Near midday peak
    server.time_overridden = True
    server.actuators["lights"].on = True
    server.tick()
    expected = server.exterior_light_level * WINDOW_TRANSMISSION_FACTOR + LIGHTS_LUX_CONTRIBUTION
    assert abs(server.interior_light_level - expected) < 0.01


def test_lights_respect_interior_light_level_override():
    server = make_server()
    server.interior_light_level = 100.0
    server.interior_light_level_overridden = True
    server.actuators["lights"].on = True
    server.tick()
    assert server.interior_light_level == 100.0


# --- Power usage tests ---


def test_power_usage_single_actuator():
    server = make_server()
    server.actuators["heat"].on = True
    server.tick()
    assert server.power_usage == HEATER_POWER_KW


def test_power_usage_multiple_actuators():
    server = make_server()
    server.actuators["heat"].on = True
    server.actuators["air_con"].on = True
    server.actuators["lights"].on = True
    server.tick()
    assert server.power_usage == HEATER_POWER_KW + AC_POWER_KW + LIGHTS_POWER_KW


def test_power_usage_zero_when_all_off():
    server = make_server()
    server.actuators["heat"].on = True
    server.tick()
    assert server.power_usage == HEATER_POWER_KW
    server.actuators["heat"].on = False
    server.tick()
    assert server.power_usage == 0.0


# --- Cumulative power usage tests ---


def test_cumulative_power_accumulates():
    server = make_server()
    server.time_rate = 1.0
    server.actuators["heat"].on = True
    server.tick()
    expected = HEATER_POWER_KW / 60.0
    assert abs(server.cumulative_power_usage - expected) < 0.001


def test_cumulative_power_scales_with_time_rate():
    server = make_server()
    server.time_rate = 60.0  # 1 hour per tick
    server.actuators["heat"].on = True
    server.tick()
    assert abs(server.cumulative_power_usage - HEATER_POWER_KW) < 0.001


def test_cumulative_power_resets_at_midnight():
    server = make_server()
    server.time = MINUTES_PER_DAY - 0.5
    server.time_rate = 1.0
    server.actuators["heat"].on = True
    server.tick()  # Wraps past midnight, resets cumulative then accumulates
    # Should only have the post-reset accumulation
    expected = HEATER_POWER_KW / 60.0
    assert abs(server.cumulative_power_usage - expected) < 0.001


def test_cumulative_power_accumulates_over_ticks():
    server = make_server()
    server.time_rate = 1.0
    server.actuators["heat"].on = True
    server.tick()
    first = server.cumulative_power_usage
    server.tick()
    assert abs(server.cumulative_power_usage - 2 * first) < 0.001
