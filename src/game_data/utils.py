import json
from typing import Any
import functools

def strToInt[T](value: Any, default: T = -1) -> int | T:
    try:
        return int(float(value))
    except ValueError, TypeError:
        return default

def strToFloat(value: Any, default = 0.0):
    try:
        return float(value)
    except:
        return default

def strToBool(value: Any):
    return str(value).lower() in ['1', 't', 'true', '1', 'y', 'yes']

json_dumps_compact = functools.partial(json.dumps, ensure_ascii = False, separators=(",", ":"))
