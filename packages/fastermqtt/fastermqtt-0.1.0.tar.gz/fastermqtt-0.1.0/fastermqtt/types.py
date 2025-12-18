"""
FastMQTT Type Definitions

Provides core type definitions for the MQTT framework.

Types:
    MQTTMessage: MQTT message container
    SubscriptionInfo: Subscription metadata
    TopicParam: Topic parameter information
    PublishInfo: Publish operation information
    MQTTConfig: MQTT connection configuration
"""
from re import Pattern
from typing import Any, Awaitable, Callable

from pydantic import BaseModel, ConfigDict


class MQTTMessage(BaseModel):
    """
    MQTT Message Container

    Contains all information about a received MQTT message,
    including topic, payload, QoS level, and MQTT 5.0 properties.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    topic: str
    """Message topic"""

    payload: bytes
    """Message payload (raw bytes)"""

    qos: int = 0
    """QoS level (0, 1, or 2)"""

    properties: dict[str, Any] | None = None
    """MQTT 5.0 properties (optional)"""


class SubscriptionInfo(BaseModel):
    """
    Subscription Metadata

    Stores all information about a subscription, including topic pattern,
    handler function, QoS level, and parsed regex pattern.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    topic_pattern: str
    """Original topic pattern (e.g., "client/{client_id}/control")"""

    handler: Callable[..., Awaitable[Any]]
    """Handler function"""

    qos: int = 0
    """Subscribe QoS level"""

    topic_regex: Pattern[str] | None = None
    """Compiled regular expression for topic matching"""

    param_names: list[str] | None = None
    """List of parameter names extracted from topic pattern"""

    consumer_group: str | None = None
    """Shared subscription consumer group name (MQTT 5.0)"""


class TopicParam(BaseModel):
    """
    Topic Parameter Information

    Describes a single parameter extracted from topic pattern.
    """

    name: str
    """Parameter name"""

    index: int
    """Parameter position in topic (after splitting by /)"""


class PublishInfo(BaseModel):
    """
    Publish Operation Information

    Encapsulates all parameters for a publish operation.
    """

    topic: str
    """Target topic"""

    payload: bytes
    """Message content"""

    qos: int = 0
    """QoS level"""

    retain: bool = False
    """Whether to retain message"""


class MQTTConfig(BaseModel):
    """
    MQTT Connection Configuration

    Contains all parameters needed to establish an MQTT connection.
    """

    host: str
    """MQTT Broker address"""

    port: int = 1883
    """MQTT Broker port"""

    username: str | None = None
    """Authentication username"""

    password: str | None = None
    """Authentication password"""

    client_id: str | None = None
    """Client ID (auto-generated if not provided)"""

    keepalive: int = 60
    """Heartbeat interval (seconds)"""

    ssl_ca_cert: str | None = None
    """SSL CA certificate path (None means SSL disabled)"""

    clean_session: bool = True
    """Whether to clean session on connect"""

    default_consumer_group: str | None = None
    """Default shared subscription consumer group name"""
