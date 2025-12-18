"""
FastMQTT - FastAPI-style MQTT Framework

A framework inspired by FastStream architecture, bringing FastAPI's elegant patterns to MQTT:
- Decorator-based subscriptions
- Dependency injection support
- Topic path parameters
- Hierarchical routing

Usage example::

    from fastapi import FastAPI
    from fastmqtt import MqttRouter

    mqtt_router = MqttRouter(host="localhost", port=1883)

    @mqtt_router.subscribe("sensors/{sensor_id}/data")
    async def handle_sensor(sensor_id: str, payload: bytes):
        print(f"Sensor {sensor_id}: {payload}")

    app = FastAPI()
    app.include_router(mqtt_router)
"""

# ==================== Core Classes ====================

from .router import MqttRouter
from .broker import MQTTBroker

# ==================== Type Definitions ====================

from .types import (
    MQTTMessage,
    SubscriptionInfo,
    TopicParam,
    PublishInfo,
    MQTTConfig,
)

# ==================== Dependency Injection ====================

from .dependencies import (
    get_mqtt_message,
    get_mqtt_topic,
    get_mqtt_payload,
    get_mqtt_qos,
    get_topic_param,
    # Type aliases
    MqttMessageDep,
    MqttTopicDep,
    MqttPayloadDep,
    MqttQosDep,
)

# ==================== Serialization ====================

from .serialization import (
    encode_payload,
    decode_payload,
)

# ==================== Exceptions ====================

from .exceptions import (
    MQTTException,
    MQTTConnectionError,
    MQTTSubscriptionError,
    MQTTPublishError,
    MQTTSerializationError,
    MQTTTopicError,
    MQTTMiddlewareError,
    MQTTRouterError,
    MQTTNotInitializedError,
)

# ==================== Middleware ====================

from .middleware import (
    BaseMQTTMiddleware,
    MiddlewareChain,
    LoggingMiddleware,
    ErrorHandlingMiddleware,
)

__version__ = "0.1.0"
__all__ = [
    # Core
    "MqttRouter",
    "MQTTBroker",
    # Types
    "MQTTMessage",
    "SubscriptionInfo",
    "TopicParam",
    "PublishInfo",
    "MQTTConfig",
    # Dependencies
    "get_mqtt_message",
    "get_mqtt_topic",
    "get_mqtt_payload",
    "get_mqtt_qos",
    "get_topic_param",
    "MqttMessageDep",
    "MqttTopicDep",
    "MqttPayloadDep",
    "MqttQosDep",
    # Serialization
    "encode_payload",
    "decode_payload",
    # Exceptions
    "MQTTException",
    "MQTTConnectionError",
    "MQTTSubscriptionError",
    "MQTTPublishError",
    "MQTTSerializationError",
    "MQTTTopicError",
    "MQTTMiddlewareError",
    "MQTTRouterError",
    "MQTTNotInitializedError",
    # Middleware
    "BaseMQTTMiddleware",
    "MiddlewareChain",
    "LoggingMiddleware",
    "ErrorHandlingMiddleware",
]
