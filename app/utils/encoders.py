from typing import Any

from _decimal import Decimal


def json_encoder_default(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    return obj.__dict__
