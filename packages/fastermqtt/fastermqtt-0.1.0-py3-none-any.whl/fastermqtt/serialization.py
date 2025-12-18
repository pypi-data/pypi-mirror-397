"""
fastmqtt message serialization module

Provides serialization and deserialization functionality for MQTT messages,
with automatic conversion support for Pydantic models.

Features:
    - encode_payload(): Encode bytes/str/Pydantic models to bytes
    - decode_payload(): Decode bytes to target type
    - is_pydantic_model(): Check if an object is a Pydantic model instance
    - is_pydantic_model_type(): Check if a type is a Pydantic model class
"""
import logging
from typing import Any, TypeVar

import orjson
from pydantic import BaseModel

from .exceptions import MQTTSerializationError

logger = logging.getLogger("fastmqtt")

T = TypeVar('T')


def is_pydantic_model(obj: Any) -> bool:
    """
    Check if an object is a Pydantic model instance

    :param obj: Object to check
    :return: True if the object is a Pydantic model instance
    """
    return isinstance(obj, BaseModel)


def is_pydantic_model_type(cls: type) -> bool:
    """
    Check if a type is a Pydantic model class

    :param cls: Type to check
    :return: True if the type is a Pydantic model class
    """
    try:
        return isinstance(cls, type) and issubclass(cls, BaseModel)
    except TypeError:
        return False


def encode_payload(payload: bytes | str | BaseModel) -> bytes:
    """
    Encode payload to bytes

    :param payload: Original content
        - bytes: Return directly
        - str: UTF-8 encode
        - Pydantic model: Call model_dump_json() then encode
    :return: Encoded bytes
    :raises MQTTSerializationError: If encoding fails

    Usage example::

        payload = encode_payload(DeviceControl(action="start"))
        # Returns: b'{"action":"start"}'

        payload = encode_payload("hello")
        # Returns: b'hello'

        payload = encode_payload(b'raw bytes')
        # Returns: b'raw bytes'
    """
    try:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, str):
            return payload.encode()
        if is_pydantic_model(payload):
            return payload.model_dump_json().encode()
        raise MQTTSerializationError(f"Unsupported payload type: {type(payload)}")
    except MQTTSerializationError:
        raise
    except (TypeError, ValueError, UnicodeEncodeError) as e:
        logger.error(f"Encoding failed: payload_type={type(payload)}, error={e}")
        raise MQTTSerializationError(f"Encoding failed: {e}") from e


def decode_payload(
        payload: bytes,
        target_type: type[T] | None = None,
) -> T | bytes | str | dict[str, Any]:
    """
    Decode bytes to target type

    :param payload: Original bytes
    :param target_type: Target type
        - None: Try JSON parsing, fallback to str on failure, then bytes
        - bytes: Return directly
        - str: UTF-8 decode
        - dict: JSON parse
        - Pydantic model: Parse and validate
    :return: Decoded object
    :raises MQTTSerializationError: If decoding fails

    Usage example::

        # Auto decode (no target type)
        data = decode_payload(b'{"action":"start"}')
        # Returns: {"action": "start"}

        # Specify Pydantic model type
        control = decode_payload(b'{"action":"start"}', DeviceControl)
        # Returns: DeviceControl(action="start")

        # Specify str type
        text = decode_payload(b'hello', str)
        # Returns: "hello"

        # Specify bytes type
        raw = decode_payload(b'raw bytes', bytes)
        # Returns: b'raw bytes'
    """
    try:
        # If no type specified, try smart decoding
        if target_type is None:
            try:
                return orjson.loads(payload)
            except (orjson.JSONDecodeError, TypeError):
                try:
                    return payload.decode()
                except UnicodeDecodeError:
                    return payload

        # bytes type: return directly
        if target_type is bytes:
            return payload

        # str type: decode
        if target_type is str:
            return payload.decode()

        # dict type: JSON parse
        if target_type is dict:
            return orjson.loads(payload)

        # Pydantic model
        if is_pydantic_model_type(target_type):
            data = orjson.loads(payload)
            return target_type.model_validate(data)

        raise MQTTSerializationError(f"Unsupported target type: {target_type}")
    except MQTTSerializationError:
        raise
    except (TypeError, ValueError, UnicodeDecodeError, orjson.JSONDecodeError) as e:
        logger.error(f"Decoding failed: payload_length={len(payload)}, target_type={target_type}, error={e}")
        raise MQTTSerializationError(f"Decoding failed: {e}") from e
