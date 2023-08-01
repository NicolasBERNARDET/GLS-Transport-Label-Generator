from functools import wraps
from typing import Any, Callable

from flask import request, jsonify
from marshmallow import ValidationError


def required_params(schema: Any) -> Callable[..., Any]:
    def decorator(fn: Any) -> Callable[..., Any]:

        @wraps(fn)
        def wrapper(*args: tuple[Any, ...], **kwargs: [str, Any]) -> Any:
            try:
                schema.load(request.get_json())
            except ValidationError as err:
                error = {
                    "status": "error",
                    "messages": err.messages
                }
                return jsonify(error), 400
            return fn(*args, **kwargs)

        return wrapper

    return decorator
