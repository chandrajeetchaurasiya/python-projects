import math


def format_result(value):
    if isinstance(value, int):
        return f"{value:,}"
    value = float(value)
    if math.isclose(value, round(value), rel_tol=0, abs_tol=1e-12):
        return f"{int(round(value)):,}"
    if abs(value) >= 1e12 or (value != 0 and abs(value) < 1e-8):
        return f"{value:.10g}"
    return f"{value:.12g}"
