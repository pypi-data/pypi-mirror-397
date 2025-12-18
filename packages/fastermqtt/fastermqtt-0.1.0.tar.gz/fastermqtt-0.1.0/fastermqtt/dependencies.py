"""
MQTT Dependency Injection Module

Provides MQTT-specific dependency injection functions for accessing MQTT context information in subscriber handlers.

Usage Example::

    from typing import Annotated
    from fastapi import Depends
    from fastmqtt.dependencies import (
        get_mqtt_message,
        get_mqtt_topic,
        get_topic_param,
        MqttMessageDep,
        MqttTopicDep,
    )

    @router.subscribe("client/+/control")
    async def handler(
        message: MqttMessageDep,  # Type alias usage
        topic: Annotated[str, Depends(get_mqtt_topic)],  # Explicit dependency
        client_id: Annotated[str, Depends(get_topic_param(1))],  # Extract topic segment
    ):
        print(message.topic, message.payload, client_id)
"""
from typing import Annotated, Any, Callable

from fastapi import Depends, Request

from .exceptions import MQTTTopicError
from .types import MQTTMessage


# TODO: Research MQTT scope structure, define MQTTScopeDict TypedDict
def _get_mqtt_scope(request: Request) -> dict[str, Any]:
    """
    Get MQTT scope from Request

    :param request: FastAPI Request object
    :return: MQTT scope dictionary
    :raises MQTTTopicError: If not in MQTT context
    """
    mqtt_scope = request.scope.get('mqtt')
    if mqtt_scope is None:
        raise MQTTTopicError("Not in MQTT context, cannot retrieve MQTT information")
    return mqtt_scope


def get_mqtt_message(request: Request) -> MQTTMessage:
    """
    Get current MQTT message

    :param request: FastAPI Request (contains scope['mqtt'])
    :return: MQTTMessage object
    :raises MQTTTopicError: If not in MQTT context

    Usage Example::

        @router.subscribe("client/+/control")
        async def handler(message: Annotated[MQTTMessage, Depends(get_mqtt_message)]):
            print(message.topic, message.payload)
    """
    mqtt_scope = _get_mqtt_scope(request)
    message: MQTTMessage | None = mqtt_scope.get('message')
    if message is None:
        raise MQTTTopicError("Missing message object in MQTT scope")
    return message


def get_mqtt_topic(request: Request) -> str:
    """
    Get current message's topic

    :param request: FastAPI Request (contains scope['mqtt'])
    :return: MQTT topic string
    :raises MQTTTopicError: If not in MQTT context

    Usage Example::

        @router.subscribe("client/+/control")
        async def handler(topic: Annotated[str, Depends(get_mqtt_topic)]):
            print(topic)
    """
    message = get_mqtt_message(request)
    return message.topic


def get_mqtt_payload(request: Request) -> bytes:
    """
    Get current message's raw payload

    :param request: FastAPI Request (contains scope['mqtt'])
    :return: Raw payload bytes
    :raises MQTTTopicError: If not in MQTT context

    Usage Example::

        @router.subscribe("client/+/control")
        async def handler(payload: Annotated[bytes, Depends(get_mqtt_payload)]):
            data = json.loads(payload)
    """
    message = get_mqtt_message(request)
    return message.payload


def get_mqtt_qos(request: Request) -> int:
    """
    Get current message's QoS level

    :param request: FastAPI Request (contains scope['mqtt'])
    :return: QoS level (0, 1, or 2)
    :raises MQTTTopicError: If not in MQTT context

    Usage Example::

        @router.subscribe("client/+/control")
        async def handler(qos: Annotated[int, Depends(get_mqtt_qos)]):
            print(f"QoS: {qos}")
    """
    message = get_mqtt_message(request)
    return message.qos


def get_topic_param(index: int) -> Callable[[Request], str]:
    """
    Create a dependency function to extract a specific segment from topic

    :param index: Segment index (position after splitting by /, starting from 0)
    :return: Dependency function that returns the topic segment at specified position

    Usage Example::

        @router.subscribe("+/status")
        async def handler(
            client_id: Annotated[str, Depends(get_topic_param(0))]  # Segment 0
        ):
            pass

        # For topic "abc123/status", client_id will be "abc123"
    """
    def _extract(request: Request) -> str:
        topic = get_mqtt_topic(request)
        parts = topic.split('/')
        if index < 0 or index >= len(parts):
            raise MQTTTopicError(
                f"Topic index {index} out of range, topic '{topic}' only has {len(parts)} segments",
                topic=topic,
            )
        return parts[index]
    return _extract


# ==================== Type Aliases ====================

MqttMessageDep = Annotated[MQTTMessage, Depends(get_mqtt_message)]
"""MQTT message dependency type alias"""

MqttTopicDep = Annotated[str, Depends(get_mqtt_topic)]
"""MQTT topic dependency type alias"""

MqttPayloadDep = Annotated[bytes, Depends(get_mqtt_payload)]
"""MQTT payload dependency type alias"""

MqttQosDep = Annotated[int, Depends(get_mqtt_qos)]
"""MQTT QoS dependency type alias"""
