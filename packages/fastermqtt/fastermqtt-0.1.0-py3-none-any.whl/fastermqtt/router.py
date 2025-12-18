"""
MqttRouter - MQTT Router (FastAPI Plugin Pattern)

Following FastStream's RedisRouter architecture:
- Inherits from APIRouter
- Manages Broker lifecycle via lifespan parameter
- Supports include_router() for hierarchical routing
- Root Router manages connections, sub-Routers share Broker

Architecture:
    MqttRouter: MQTT router that inherits from APIRouter
    _parse_topic_pattern(): Topic pattern parsing utility function

Features:
    - Prefix accumulation: Sub-router topics automatically prepend parent router prefix
    - Decorator-based subscription: @router.subscribe("topic/{param}")
    - Publish method: await router.publish("topic", payload)
    - Nested routing: router.include_router(sub_router)
    - Lifecycle management: Auto-integrates with FastAPI via lifespan
"""
import re
from collections.abc import Callable, Sequence
from contextlib import asynccontextmanager
from enum import Enum
from typing import TYPE_CHECKING, Any, Awaitable, ClassVar
from uuid import uuid4

from fastapi import APIRouter, FastAPI
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute

if TYPE_CHECKING:
    from fastapi import params

from .broker import MQTTBroker
from .exceptions import MQTTTopicError
from .serialization import encode_payload
from .types import MQTTConfig, SubscriptionInfo


def _parse_topic_pattern(pattern: str) -> tuple[str, re.Pattern[str], list[str]]:
    """
    Parse topic pattern, extract parameter names and generate regex expression

    MQTT protocol specifies: Single-level wildcard + must occupy the entire level.
    This function validates that {param} occupies an entire level, rejecting partial matches (e.g., prefix_{id}).

    :param pattern: Topic pattern, e.g., "client/{client_id}/control"
    :return: (mqtt_topic, regex, param_names)
        - mqtt_topic: MQTT subscription topic, e.g., "client/+/control"
        - regex: Regular expression for matching and extracting
        - param_names: List of parameter names, e.g., ["client_id"]
    :raises MQTTTopicError: If {param} does not occupy an entire level (e.g., prefix_{id})

    Example::

        # Valid: {param} occupies entire level
        pattern = "client/{client_id}/control"
        mqtt_topic = "client/+/control"

        # Invalid: Partial match, will raise MQTTTopicError
        pattern = "client/sensor_{id}/data"  # {id} does not occupy entire level
    """
    # 1. Validate: {param} must occupy entire level
    for level in pattern.split('/'):
        if '{' in level:
            # After removing all {param}, remaining content should be empty
            stripped = re.sub(r'\{[^}]+}', '', level)
            if stripped:
                raise MQTTTopicError(
                    f"Invalid topic pattern: Parameter in '{level}' does not occupy entire level. "
                    f"MQTT wildcard + must occupy the entire level, partial matches like 'prefix_{{id}}' are not supported.",
                    pattern=pattern,
                )

    # 2. Extract all {param} parameter names
    param_names = re.findall(r'\{([^}]+)}', pattern)

    # 3. Replace {param} with MQTT wildcard +
    mqtt_topic = re.sub(r'\{[^}]+}', '+', pattern)

    # 4. Build regular expression
    # 4.1 Use re.escape to fully escape all special characters
    regex_pattern = re.escape(pattern)
    # 4.2 re.escape will escape { and } to \{ and \}, need to restore and replace with named capture groups
    # First replace escaped \{param\} with named capture groups
    regex_pattern = re.sub(r'\\{([^}]+)\\}', r'(?P<\1>[^/]+)', regex_pattern)
    # 4.3 Compile regex
    topic_regex = re.compile(f'^{regex_pattern}$')

    return mqtt_topic, topic_regex, param_names


class MqttRouter(APIRouter):
    """
    MQTT Router (FastAPI Plugin Pattern)

    Following FastStream's RedisRouter design:
    - Inherits from APIRouter
    - Manages Broker lifecycle via lifespan parameter
    - Supports include_router() for hierarchical routing

    Usage example::

        # Root Router (with connection parameters)
        mqtt_router = MqttRouter(host="localhost", port=8883)

        # Sub Router (without connection parameters)
        client_router = MqttRouter(prefix="client/")

        # Subscribe
        @client_router.subscribe("{client_id}/control", qos=2)
        async def handler(client_id: str, payload: bytes):
            pass

        # Hierarchical aggregation
        mqtt_router.include_router(client_router)

        # FastAPI integration
        app.include_router(mqtt_router)  # Automatically manages lifecycle
    """

    # ==================== ClassVar Class-level Variables ====================
    broker_class: ClassVar[type[MQTTBroker]] = MQTTBroker
    """Broker class reference (for dependency injection and extension)"""

    broker: ClassVar[type[MQTTBroker]] = MQTTBroker
    """Broker class reference (for calling class methods)"""

    def __init__(
        self,
        host: str | None = None,
        port: int = 8883,
        username: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        keepalive: int = 60,
        ssl_ca_cert: str | None = None,
        clean_session: bool = True,
        default_consumer_group: str | None = None,
        prefix: str = "",
        **kwargs,
    ):
        """
        Create MQTT Router

        If host parameter is provided, this Router is a root Router, responsible for managing Broker lifecycle.
        If host is not provided (only prefix), this Router is a sub-Router, sharing the parent Router's Broker.

        :param host: MQTT Broker address (required for root Router)
        :param port: MQTT Broker port
        :param username: Username
        :param password: Password
        :param client_id: Client ID (auto-generated by default)
        :param keepalive: Heartbeat interval (seconds)
        :param ssl_ca_cert: SSL CA certificate path (None means SSL disabled)
        :param clean_session: Whether to clean session
        :param default_consumer_group: Default shared subscription consumer group name (global default)
        :param prefix: Topic prefix
        :param kwargs: Additional parameters passed to APIRouter
        """
        # Determine if this is a root Router
        self._is_root = host is not None

        # Save configuration (root Router only)
        if self._is_root:
            self._mqtt_config = MQTTConfig(
                host=host,
                port=port,
                username=username,
                password=password,
                client_id=client_id or f"fastmqtt-{uuid4().hex[:8]}",
                keepalive=keepalive,
                ssl_ca_cert=ssl_ca_cert,
                clean_session=clean_session,
                default_consumer_group=default_consumer_group,
            )
            self._default_consumer_group = default_consumer_group
        else:
            self._mqtt_config = None
            self._default_consumer_group = default_consumer_group

        # This Router's state
        self._prefix = prefix.rstrip('/')
        self._parent: 'MqttRouter | None' = None  # Parent Router reference (for dynamic full_prefix calculation)
        self._subscriptions: list[SubscriptionInfo] = []

        # Create lifespan (root Router only, must pass function object not call result)
        if self._is_root:
            self._mqtt_lifespan = self._create_lifespan()
        else:
            self._mqtt_lifespan = None

        # Initialize APIRouter (root Router injects lifespan)
        # Note: Don't pass prefix to APIRouter, because MQTT's prefix is topic prefix, not HTTP route prefix
        # APIRouter requires prefix to start with '/', while MQTT topics don't
        super().__init__(
            lifespan=self._mqtt_lifespan,
            **kwargs,
        )

    # ==================== Lifespan Management ====================

    def _create_lifespan(self):
        """
        Create lifespan context manager

        This method is only called in root Router, returns an asynccontextmanager,
        FastAPI will automatically recognize and call it during app startup/shutdown.
        """
        @asynccontextmanager
        async def mqtt_lifespan(app: FastAPI):
            # ==================== Startup ====================

            # 1. Start Broker
            await self.broker.start(self._mqtt_config)

            # 2. Register all subscribers
            self.register_to_broker()

            try:
                yield {"broker": self.broker}  # Expose to app.state
            finally:
                # ==================== Shutdown ====================
                await self.broker.stop()

        return mqtt_lifespan

    # ==================== Subscribe Decorator ====================

    def subscribe(
        self,
        topic: str,
        qos: int = 0,
        group: str | None = None,
    ) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
        """
        Subscribe decorator

        :param topic: Topic pattern, supports path parameter style: "{client_id}/control"
        :param qos: Subscribe QoS level
        :param group: Shared subscription consumer group name
                      - None: Use Router's default_consumer_group
                      - Non-empty string: Use specified consumer group
                      - Empty string "": Force no shared subscription

        Usage example::

            @router.subscribe("{client_id}/control", qos=2)
            async def handler(client_id: str, payload: bytes, session: SessionDep):
                pass

            # Use specified consumer group
            @router.subscribe("events", group="my-group")
            async def event_handler(payload: bytes):
                pass

            # Force no shared subscription
            @router.subscribe("broadcast", group="")
            async def broadcast_handler(payload: bytes):
                pass
        """
        def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            # 1. Calculate full topic (router prefix + subscribe topic)
            if self._prefix and topic:
                full_topic = f"{self._prefix}/{topic}"
            elif self._prefix:
                full_topic = self._prefix
            else:
                full_topic = topic

            # 2. Parse topic pattern
            mqtt_topic, topic_regex, param_names = _parse_topic_pattern(full_topic)

            # 3. Determine consumer group: group > self._default_consumer_group > None
            # Empty string "" means force no shared subscription
            if group is not None:
                consumer_group = group if group else None  # "" -> None
            else:
                consumer_group = self._default_consumer_group

            # 4. Create subscription info (topic_pattern already includes router prefix)
            subscription = SubscriptionInfo(
                topic_pattern=full_topic,
                handler=func,
                qos=qos,
                topic_regex=topic_regex,
                param_names=param_names,
                consumer_group=consumer_group,
            )

            # 5. Add to this Router
            self._subscriptions.append(subscription)

            return func
        return decorator

    # ==================== Nested Routing ====================

    def include_router(  # type: ignore[override]
        self,
        router: 'MqttRouter',
        *,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
        dependencies: 'Sequence[params.Depends] | None' = None,
        default_response_class: type[Response] = Default(JSONResponse),
        responses: dict[int | str, dict[str, Any]] | None = None,
        callbacks: list[BaseRoute] | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[APIRoute], str] = Default(generate_unique_id),
    ) -> None:
        """
        Include sub-Router (following FastStream's design)

        Merges sub-Router's subscriptions and accumulates topic prefix.
        Uses FastStream's _prefix_chain pattern to dynamically calculate full prefix.

        :param router: Sub-Router
        :param prefix: Additional prefix (optional)
        :param tags: OpenAPI tags (passed to APIRouter)
        :param dependencies: FastAPI dependencies (passed to APIRouter)
        :param default_response_class: Default response class (passed to APIRouter)
        :param responses: OpenAPI response definitions (passed to APIRouter)
        :param callbacks: OpenAPI callbacks (passed to APIRouter)
        :param deprecated: Whether marked as deprecated (passed to APIRouter)
        :param include_in_schema: Whether included in OpenAPI schema (passed to APIRouter)
        :param generate_unique_id_function: Function to generate unique ID (passed to APIRouter)

        Usage example::

            main_router = MqttRouter(host="localhost")
            client_router = MqttRouter(prefix="client/")
            main_router.include_router(client_router)
            # Subscription "control" in client_router becomes "client/control"
        """
        # 1. Set sub-Router's parent reference (FastStream pattern: dynamically calculate full_prefix)
        router._parent = self

        # 2. Calculate parent prefix (for merging subscriptions)
        parent_prefix = self.full_prefix
        if prefix:
            parent_prefix = f"{parent_prefix}/{prefix.rstrip('/')}" if parent_prefix else prefix.rstrip('/')

        # 3. Merge subscriptions (update topic_pattern)
        for sub in router._subscriptions:
            # Update topic (add parent Router's prefix)
            # Note: When sub.topic_pattern is empty, only use parent prefix
            if sub.topic_pattern:
                full_topic = f"{parent_prefix}/{sub.topic_pattern}" if parent_prefix else sub.topic_pattern
            else:
                full_topic = parent_prefix if parent_prefix else ""

            # Re-parse topic pattern
            mqtt_topic, topic_regex, param_names = _parse_topic_pattern(full_topic)

            # Determine consumer group: sub-Router's > parent Router's
            consumer_group = sub.consumer_group if sub.consumer_group is not None else self._default_consumer_group

            # Create new subscription info
            full_sub = SubscriptionInfo(
                topic_pattern=full_topic,
                handler=sub.handler,
                qos=sub.qos,
                topic_regex=topic_regex,
                param_names=param_names,
                consumer_group=consumer_group,
            )

            self._subscriptions.append(full_sub)

        # 4. Call FastAPI's include_router (pass all HTTP-related parameters)
        super().include_router(
            router=router,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
        )

    # ==================== Publish Message ====================

    async def publish(
        self,
        payload: bytes | str | BaseModel,
        qos: int = 0,
        retain: bool = False,
        **path_params: str,
    ) -> None:
        """
        Publish message

        Uses path_params to replace path parameter placeholders in prefix.

        Example::

            # prefix = "client/{client_id}/server_msg"
            await router.publish(payload, client_id="abc-123")
            # Publishes to: client/abc-123/server_msg

        :param payload: Message content
        :param qos: QoS level
        :param retain: Whether to retain
        :param path_params: Path parameters, used to replace {param} placeholders in prefix
        """
        # Use full_prefix property to dynamically calculate full topic (FastStream pattern)
        full_topic = self.full_prefix
        for key, value in path_params.items():
            full_topic = full_topic.replace(f"{{{key}}}", str(value))

        # Serialize payload
        encoded_payload = encode_payload(payload)

        # Publish to Broker
        await self.broker.publish(full_topic, encoded_payload, qos, retain)

    # ==================== Register to Broker ====================

    def register_to_broker(self) -> None:
        """
        Register all subscribers to Broker

        Called during root Router's lifespan startup.
        """
        for sub in self._subscriptions:
            self.broker.register_subscription(sub)

    # ==================== Helper Methods ====================

    @property
    def full_prefix(self) -> str:
        """
        Full prefix (dynamically concatenates parent Router's prefix chain + this Router's prefix)

        Follows FastStream's ConfigComposition.prefix implementation:
        Dynamically calculates via _parent reference chain, ensuring full prefix is available
        even when lower-level Router is included first.
        """
        if self._parent is not None:
            parent_prefix = self._parent.full_prefix
            if parent_prefix and self._prefix:
                return f"{parent_prefix}/{self._prefix}"
            return parent_prefix or self._prefix
        return self._prefix

    @property
    def subscriptions(self) -> list[SubscriptionInfo]:
        """Get this router's subscription list (read-only)"""
        return self._subscriptions.copy()

    def __repr__(self) -> str:
        return (
            f"MqttRouter("
            f"is_root={self._is_root}, "
            f"prefix={self._prefix!r}, "
            f"subscriptions={len(self._subscriptions)}"
            f")"
        )
