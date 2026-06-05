from typing import Any

def strToInt[T](value: Any, default: T = -1) -> int | T:
    try:
        return int(float(value))
    except ValueError:
        return default
