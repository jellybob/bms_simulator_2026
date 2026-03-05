from bms_simulator.controller import State, _build_state, _format_value, _parse_value


class TestParseValue:
    def test_bool_true(self):
        assert _parse_value("occupancy", "true") is True

    def test_bool_false(self):
        assert _parse_value("lights", "false") is False

    def test_bool_case_insensitive(self):
        assert _parse_value("heat", "True") is True
        assert _parse_value("air_con", "FALSE") is False

    def test_float(self):
        assert _parse_value("time", "480.0") == 480.0

    def test_float_temperature(self):
        assert _parse_value("temperature", "22.5") == 22.5


class TestFormatValue:
    def test_bool_true(self):
        assert _format_value(True) == "true"

    def test_bool_false(self):
        assert _format_value(False) == "false"

    def test_float(self):
        assert _format_value(22.5) == "22.5"

    def test_int(self):
        assert _format_value(480) == "480"

    def test_string_passthrough(self):
        assert _format_value("hello") == "hello"


class TestBuildState:
    def test_empty_gives_defaults(self):
        state = _build_state({})
        assert state == State()

    def test_partial_values(self):
        state = _build_state({"time": "600.0", "occupancy": "true"})
        assert state.time == 600.0
        assert state.occupancy is True
        assert state.temperature == 0.0  # default

    def test_full_state(self):
        values = {
            "time": "480.0",
            "time_rate": "2.0",
            "oat": "18.5",
            "temperature": "22.0",
            "occupancy": "true",
            "exterior_light_level": "1500.0",
            "interior_light_level": "1450.0",
            "heat": "false",
            "air_con": "true",
            "lights": "true",
            "power_usage": "1080.0",
            "cumulative_power_usage": "540.0",
        }
        state = _build_state(values)
        assert state.time == 480.0
        assert state.time_rate == 2.0
        assert state.oat == 18.5
        assert state.temperature == 22.0
        assert state.occupancy is True
        assert state.exterior_light_level == 1500.0
        assert state.interior_light_level == 1450.0
        assert state.heat is False
        assert state.air_con is True
        assert state.lights is True
        assert state.power_usage == 1080.0
        assert state.cumulative_power_usage == 540.0

    def test_ignores_unknown_fields(self):
        state = _build_state({"time": "100.0", "unknown_field": "42"})
        assert state.time == 100.0

    def test_state_is_frozen(self):
        import pytest

        state = _build_state({"time": "100.0"})
        with pytest.raises(AttributeError):
            state.time = 200.0
