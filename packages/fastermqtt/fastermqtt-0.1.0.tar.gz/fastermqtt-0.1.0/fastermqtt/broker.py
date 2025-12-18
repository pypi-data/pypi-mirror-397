"""
MQTTBroker Singleton Manager

MQTT client manager based on gmqtt, implemented as global singleton using pure classmethod pattern.
Integrated with FastAPI lifecycle, supports dynamic subscription and message dispatching.

Features:
- FastAPI-style dependency injection (using solve_dependencies)
- MQTT topic parameter extraction (e.g., client/{client_id}/control)
"""
import asyncio
import logging
import re
import ssl
import uuid
from contextlib import AsyncExitStack
from typing import Any, ClassVar

from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from gmqtt import Client
from gmqtt.mqtt.constants import MQTTv311
from starlette.requests import Request

from .exceptions import (
    MQTTConnectionError,
    MQTTNotInitializedError,
    MQTTPublishError,
)
from .types import MQTTConfig, MQTTMessage, SubscriptionInfo

logger = logging.getLogger("fastmqtt")


class MQTTRequest(Request):
    """
    MQTT message Request wrapper (for FastAPI dependency injection)

    Inherits from starlette.requests.Request but does not call super().__init__(),
    avoiding Request's scope["type"] assertion check (only allows http/websocket).

    Reference: FastStream's StreamMessage implementation:
    https://github.com/airtai/faststream/blob/main/faststream/_internal/fastapi/route.py

    Key implementation:
    - _query_params contains all non-dependency parameters to inject (MQTT params + topic path params)
    - FastAPI's solve_dependencies retrieves parameter values from _query_params
    """

    scope: dict[str, Any]
    _cookies: dict[str, Any]
    _headers: dict[str, Any]
    _body: bytes
    _query_params: dict[str, Any]

    def __init__(
            self,
            *,
            body: bytes,
            headers: dict[str, Any],
            query_params: dict[str, Any],
            async_exit_stack: AsyncExitStack,
    ) -> None:
        """
        Initialize MQTTRequest

        :param body: Message body (payload)
        :param headers: Request headers (MQTT messages typically have none, pass empty dict)
        :param query_params: Query parameters (MQTT params + topic path params, for dependency injection)
        :param async_exit_stack: AsyncExitStack required by FastAPI dependency injection
        """
        # Don't call super().__init__(), set attributes directly
        self._headers = headers
        self._body = body
        # _query_params contains all parameters to inject (FastAPI retrieves values from here)
        self._query_params = query_params
        self.scope = {
            "path_params": query_params,
            # FastAPI 0.112.4+ requires these two AsyncExitStacks
            "fastapi_inner_astack": async_exit_stack,
            "fastapi_function_astack": async_exit_stack,
        }
        self._cookies = {}


class MQTTBroker:
    """
    MQTT Broker Singleton Manager (pure classmethod pattern)

    Responsibilities:
    - Manage gmqtt client connection
    - Dispatch messages to subscribers
    - Lifecycle management (integrated with FastAPI)

    Usage example::

        # Called by MqttRouter's lifespan
        await MQTTBroker.start(config)
        await MQTTBroker.publish("topic", payload, qos=1)
        await MQTTBroker.stop()

    Note: This class is never instantiated, all methods are @classmethod
    """

    # ==================== ClassVar Configuration Constants ====================

    RECONNECT_INTERVAL: ClassVar[int] = 5
    """Reconnection interval (seconds)"""

    # ==================== ClassVar State Variables ====================

    _client: ClassVar[Client | None] = None
    """gmqtt client instance"""

    _config: ClassVar[MQTTConfig | None] = None
    """MQTT configuration"""

    _subscriptions: ClassVar[dict[str, SubscriptionInfo]] = {}
    """Subscription information: topic_pattern -> SubscriptionInfo"""

    _is_connected: ClassVar[bool] = False
    """Connection status"""

    _dependants: ClassVar[dict[str, Dependant]] = {}
    """Store analyzed handler dependency information: handler_name -> Dependant"""

    # ==================== Lifecycle Management ====================

    @classmethod
    async def start(cls, config: MQTTConfig) -> None:
        """
        Start Broker (called by MqttRouter's lifespan)

        :param config: MQTT connection configuration
        :raises MQTTConnectionError: If connection fails
        """
        if cls._is_connected:
            logger.warning("MqttBroker already connected, skipping duplicate startup")
            return

        # Save configuration
        cls._config = config

        # Create gmqtt client
        cls._client = Client(config.client_id or f"fastmqtt-{uuid.uuid4().hex[:8]}")

        # Set authentication
        password_display = '*' * len(config.password) if config.password else None
        logger.debug(f"MQTT authentication config: username={config.username!r}, password={password_display!r}")
        if config.username:
            cls._client.set_auth_credentials(config.username, config.password)
            logger.debug("MQTT authentication credentials set")

        # Set callbacks
        cls._client.on_connect = cls._on_connect
        cls._client.on_message = cls._on_message
        cls._client.on_disconnect = cls._on_disconnect

        # Create SSL context
        ssl_context: ssl.SSLContext | None = None
        if config.ssl_ca_cert:
            # TODO: Add certificate file existence check and error handling
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(cafile=config.ssl_ca_cert)

        # Connect to Broker
        try:
            await cls._client.connect(
                host=config.host,
                port=config.port,
                keepalive=config.keepalive,
                version=MQTTv311,
                ssl=ssl_context,
            )
        except (OSError, asyncio.TimeoutError, ConnectionError) as e:
            raise MQTTConnectionError(f"Failed to connect to MQTT Broker: {e}") from e

        cls._is_connected = True
        logger.info(f"MqttBroker connected: {config.host}:{config.port}")

    @classmethod
    async def stop(cls) -> None:
        """
        Stop Broker (called by MqttRouter's lifespan)

        Graceful shutdown:
        - Disconnect MQTT connection
        - Clean up all state
        """
        # 1. Disconnect
        if cls._client:
            try:
                await cls._client.disconnect()
            except (OSError, asyncio.TimeoutError, RuntimeError) as e:
                logger.warning(f"Exception occurred while disconnecting MQTT: {e}")
            cls._client = None

        # 2. Clean up state
        cls._is_connected = False
        cls._subscriptions.clear()
        cls._dependants.clear()
        cls._config = None

        logger.info("MqttBroker disconnected")

    # ==================== Callback Functions ====================

    @classmethod
    def _on_connect(
            cls,
            client: Client,
            flags: int,
            rc: int,
            # TODO: Research gmqtt's properties specific type, define PropertiesDict TypedDict
            properties: dict[str, Any],
    ) -> None:
        """
        gmqtt connection success callback

        Subscribe to all registered topics after connection succeeds.
        """
        cls._is_connected = True
        logger.info(f"MQTT connected successfully, flags={flags}, rc={rc}")

        # Subscribe to all registered topics
        for topic_pattern, subscription in cls._subscriptions.items():
            mqtt_topic = cls._pattern_to_mqtt_topic(topic_pattern, subscription.consumer_group)
            client.subscribe(mqtt_topic, qos=subscription.qos)
            logger.debug(f"Subscribed to topic: {mqtt_topic} (pattern: {topic_pattern})")

    @classmethod
    def _on_message(
            cls,
            client: Client,
            topic: str,
            payload: bytes,
            qos: int,
            # TODO: Research gmqtt's properties specific type, define PropertiesDict TypedDict
            properties: dict[str, Any],
    ) -> int:
        """
        gmqtt message callback

        Directly start async task to process message.
        Return 0 indicates message has been processed.
        """
        message = MQTTMessage(
            topic=topic,
            payload=payload,
            qos=qos,
            properties=properties,
        )

        # Directly start async task for processing
        asyncio.create_task(cls._dispatch_message(message))

        return 0

    @classmethod
    # TODO: Research gmqtt's packet parameter specific type
    def _on_disconnect(cls, client: Client, packet: Any, exc: Exception | None = None) -> None:
        """gmqtt disconnect callback"""
        cls._is_connected = False
        if exc:
            logger.warning(f"MQTT connection disconnected: {exc}")
        else:
            logger.info("MQTT connection disconnected")

    # ==================== Subscription Management ====================

    @classmethod
    def register_subscription(cls, subscription: SubscriptionInfo) -> None:
        """
        Register subscription

        Called by MQTTRouter. If already connected, subscribe immediately; otherwise delay until connection.
        Also analyze handler's dependency information for subsequent dependency injection.

        :param subscription: Subscription information
        """
        topic_pattern = subscription.topic_pattern
        cls._subscriptions[topic_pattern] = subscription

        # Analyze handler dependencies
        handler = subscription.handler
        handler_name = f"{handler.__module__}.{handler.__name__}"
        dependant = get_dependant(path="", call=handler)
        cls._dependants[handler_name] = dependant

        logger.debug(f"Registered subscription: {topic_pattern}, handler: {handler_name}")

        # If already connected, subscribe immediately
        if cls._is_connected and cls._client:
            mqtt_topic = cls._pattern_to_mqtt_topic(topic_pattern, subscription.consumer_group)
            cls._client.subscribe(mqtt_topic, qos=subscription.qos)
            logger.debug(f"Subscribed to topic: {mqtt_topic}")

    @classmethod
    def _pattern_to_mqtt_topic(cls, pattern: str, consumer_group: str | None = None) -> str:
        """
        Convert topic pattern to MQTT topic

        Supports MQTT 5.0 shared subscription format: $share/{group}/{topic}

        Examples::

            # Regular subscription
            pattern = 'client/{client_id}/control'
            mqtt_topic = 'client/+/control'

            # Shared subscription
            pattern = 'client/{client_id}/control', consumer_group = 'workers'
            mqtt_topic = '$share/workers/client/+/control'

        :param pattern: topic pattern
        :param consumer_group: Shared subscription consumer group name, None for regular subscription
        :return: MQTT topic (possibly with $share prefix)
        """
        mqtt_topic = re.sub(r'\{[^}]+\}', '+', pattern)
        if consumer_group:
            mqtt_topic = f"$share/{consumer_group}/{mqtt_topic}"
        return mqtt_topic

    @classmethod
    def _pattern_to_regex(cls, pattern: str) -> re.Pattern[str]:
        """
        Convert topic pattern to regular expression

        Example: 'client/{client_id}/control' -> r'client/(?P<client_id>[^/]+)/control'

        :param pattern: topic pattern
        :return: Compiled regular expression
        """
        regex_pattern = pattern
        # Escape regex special characters (but keep { and })
        regex_pattern = re.sub(r'([.^$*?[\]\\|()])', r'\\\\\\1', regex_pattern)
        # Replace {param} with named capture group
        regex_pattern = re.sub(r'\{([^}]+)\}', r'(?P<\\1>[^/]+)', regex_pattern)
        return re.compile(f'^{regex_pattern}$')

    # ==================== Message Processing ====================

    @classmethod
    async def _dispatch_message(cls, message: MQTTMessage) -> None:
        """
        Dispatch message to matching subscribers

        Supports FastAPI-style dependency injection.

        Process:
        1. Match subscribed topic pattern
        2. Extract topic parameters
        3. Create fake Request object for dependency resolution
        4. Resolve handler dependencies
        5. Call handler

        :param message: MQTT message
        """
        for topic_pattern, subscription in cls._subscriptions.items():
            # Compile regex (if not compiled yet)
            if subscription.topic_regex is None:
                subscription.topic_regex = cls._pattern_to_regex(topic_pattern)

            # Match topic
            match = subscription.topic_regex.match(message.topic)
            if not match:
                continue

            # Extract topic parameters
            topic_params = match.groupdict()

            # Get handler and dependency information
            handler = subscription.handler
            handler_name = f"{handler.__module__}.{handler.__name__}"
            dependant = cls._dependants.get(handler_name)

            if dependant is None:
                logger.error(f"Handler dependency information not found: {handler_name}")
                continue

            # Call handler
            try:
                await cls._call_handler(
                    message=message,
                    handler=handler,
                    topic_params=topic_params,
                    dependant=dependant,
                )
            except Exception as e:
                # Catch all exceptions to prevent single message processing failure from crashing the entire message loop
                # This is a common message queue pattern to ensure system robustness
                logger.exception(
                    f"Message processing exception: topic={message.topic}, "
                    f"pattern={topic_pattern}, error={e}"
                )

    @classmethod
    async def _call_handler(
            cls,
            message: MQTTMessage,
            handler: Any,
            topic_params: dict[str, str],
            dependant: Dependant,
    ) -> None:
        """
        Call handler (via dependency injection)

        All parameters (MQTT native params, topic path params, dependency injection params) are
        resolved uniformly through FastAPI's solve_dependencies, directly call handler using solved.values.

        :param message: MQTT message
        :param handler: Original handler function
        :param topic_params: Parameters extracted from topic
        :param dependant: FastAPI dependency information
        """
        async with AsyncExitStack() as async_exit_stack:
            request = cls._create_fake_request(message, topic_params, async_exit_stack)

            # FastAPI >= 0.112.4 requires body and embed_body_fields parameters
            solved = await solve_dependencies(
                request=request,
                dependant=dependant,
                async_exit_stack=async_exit_stack,
                body=request._body,
                embed_body_fields=False,
            )

            if solved.errors:
                logger.error(f"Dependency resolution failed: topic={message.topic}, errors={solved.errors}")
                return

            # All parameters have been resolved to solved.values through solve_dependencies
            await handler(**solved.values)

    @classmethod
    def _create_fake_request(
            cls,
            message: MQTTMessage,
            path_params: dict[str, str],
            async_exit_stack: AsyncExitStack,
    ) -> MQTTRequest:
        """
        Create fake Request object (for FastAPI dependency injection)

        Uses MQTTRequest class to bypass starlette.Request's scope["type"] assertion check.

        Reference: FastStream implementation: merge all non-dependency parameters (MQTT params + topic path params)
        into query_params, FastAPI's solve_dependencies retrieves parameter values from it.

        :param message: MQTT message
        :param path_params: Path parameters extracted from topic
        :param async_exit_stack: AsyncExitStack required by FastAPI dependency injection
        :return: MQTTRequest object
        """
        # Merge MQTT parameters and topic path parameters
        # FastAPI's solve_dependencies retrieves parameter values from _query_params
        query_params: dict[str, Any] = {
            # MQTT native parameters
            'message': message,
            'topic': message.topic,
            'payload': message.payload,
            'qos': message.qos,
            'properties': message.properties,
            # topic path parameters
            **path_params,
        }

        return MQTTRequest(
            body=message.payload,
            headers={},
            query_params=query_params,
            async_exit_stack=async_exit_stack,
        )

    # ==================== Public Interface ====================

    @classmethod
    async def publish(
            cls,
            topic: str,
            payload: bytes | str,
            qos: int = 0,
            retain: bool = False,
    ) -> None:
        """
        Publish message

        :param topic: Target topic
        :param payload: Message content
        :param qos: Quality of Service level (0, 1, 2)
        :param retain: Whether to retain message
        :raises MQTTNotInitializedError: If not initialized
        :raises MQTTPublishError: If publish fails
        """
        if cls._client is None:
            raise MQTTNotInitializedError()

        if not cls._is_connected:
            raise MQTTPublishError("MQTT not connected", topic=topic)

        # Convert payload to bytes
        if isinstance(payload, str):
            payload_bytes = payload.encode('utf-8')
        else:
            payload_bytes = payload

        try:
            cls._client.publish(topic, payload_bytes, qos=qos, retain=retain)
            logger.debug(f"Published message: topic={topic}, qos={qos}, retain={retain}")
        except (OSError, RuntimeError, ValueError) as e:
            raise MQTTPublishError(f"Failed to publish message: {e}", topic=topic) from e

    @classmethod
    def is_connected(cls) -> bool:
        """
        Check if connected

        :return: Connection status
        """
        return cls._is_connected

    @classmethod
    def is_initialized(cls) -> bool:
        """
        Check if initialized

        :return: Initialization status
        """
        return cls._config is not None
