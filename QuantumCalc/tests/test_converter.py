from core.converter import convert


def test_length_conversion():
    assert convert("Length", 1, "km", "m") == 1000


def test_temperature_conversion():
    assert convert("Temperature", 0, "°C", "°F") == 32
