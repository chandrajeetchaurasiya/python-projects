"""Offline unit conversion helpers."""
FACTORS = {
    "Length": {"mm": 0.001, "cm": 0.01, "m": 1, "km": 1000, "inch": 0.0254, "ft": 0.3048, "mile": 1609.344},
    "Mass": {"mg": 1e-6, "g": 0.001, "kg": 1, "tonne": 1000, "lb": 0.45359237},
    "Area": {"m²": 1, "km²": 1_000_000, "acre": 4046.8564224, "hectare": 10_000},
    "Volume": {"mL": 0.001, "L": 1, "m³": 1000, "US gallon": 3.785411784},
}


def convert(category, value, source, target):
    value = float(value)
    if category == "Temperature":
        celsius = {"°C": value, "°F": (value - 32) * 5 / 9, "K": value - 273.15}[source]
        return {"°C": celsius, "°F": celsius * 9 / 5 + 32, "K": celsius + 273.15}[target]
    factors = FACTORS[category]
    return value * factors[source] / factors[target]
