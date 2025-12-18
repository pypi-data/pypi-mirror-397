"""
FastMQTT Middleware Module

Provides MQTT middleware infrastructure, supporting interception and processing
before and after message handling.

Architecture:
    BaseMQTTMiddleware: Middleware abstract base class
    MiddlewareChain: Middleware chain manager
    LoggingMiddleware: Logging middleware
    ErrorHandlingMiddleware: Error handling middleware
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable

from .types import MQTTMessage

logger = logging.getLogger("fastmqtt")


class BaseMQTTMiddleware(ABC):
    """
    MQTT Middleware Base Class

    Middleware can intercept message receiving and publishing processes, used for:
    - Logging
    - Authentication and authorization
    - Message transformation
    - Error handling
    - Performance monitoring

    Usage example::

        class LoggingMiddleware(BaseMQTTMiddleware):
            async def on_receive(
                self,
                message: MQTTMessage,
                call_next: Callable[[MQTTMessage], Awaitable[Any]]
            ) -> Any:
                logger.info(f"Received message: {message.topic}")
                result = await call_next(message)
                logger.info(f"Processing completed: {message.topic}")
                return result
    """

    @abstractmethod
    async def on_receive(
        self,
        message: MQTTMessage,
        call_next: Callable[[MQTTMessage], Awaitable[Any]],
    ) -> Any:
        """
        Message receive middleware

        :param message: Received MQTT message
        :param call_next: Call next middleware or final handler
        :return: Handler return value
        """
        pass

    async def on_publish(
        self,
        topic: str,
        payload: bytes,
        qos: int,
        retain: bool,
        call_next: Callable[[str, bytes, int, bool], Awaitable[None]],
    ) -> None:
        """
        Message publish middleware (optional override)

        :param topic: Target topic for publishing
        :param payload: Message content
        :param qos: QoS level
        :param retain: Whether to retain
        :param call_next: Call next middleware or actual publish
        """
        await call_next(topic, payload, qos, retain)


class MiddlewareChain:
    """
    Middleware Chain Manager

    Responsible for executing middlewares in order, forming a processing chain.
    Middlewares execute in the order they are added: first added executes first (onion model).
    """

    def __init__(self, middlewares: list[BaseMQTTMiddleware] | None = None):
        self._middlewares: list[BaseMQTTMiddleware] = middlewares or []

    def add(self, middleware: BaseMQTTMiddleware) -> None:
        """Add middleware to the end of the chain"""
        self._middlewares.append(middleware)

    def add_first(self, middleware: BaseMQTTMiddleware) -> None:
        """Add middleware to the beginning of the chain"""
        self._middlewares.insert(0, middleware)

    @property
    def middlewares(self) -> list[BaseMQTTMiddleware]:
        """Get middleware list (read-only)"""
        return self._middlewares.copy()

    def __len__(self) -> int:
        return len(self._middlewares)

    async def execute_receive(
        self,
        message: MQTTMessage,
        final_handler: Callable[[MQTTMessage], Awaitable[Any]],
    ) -> Any:
        """
        Execute receive middleware chain

        Build middleware chain: middleware1 -> middleware2 -> ... -> final_handler

        :param message: MQTT message
        :param final_handler: Final handler function (subscriber handler)
        :return: Handler return value
        """
        if not self._middlewares:
            return await final_handler(message)

        def build_chain(index: int) -> Callable[[MQTTMessage], Awaitable[Any]]:
            if index >= len(self._middlewares):
                return final_handler

            middleware = self._middlewares[index]
            next_handler = build_chain(index + 1)

            async def wrapped(msg: MQTTMessage) -> Any:
                return await middleware.on_receive(msg, next_handler)

            return wrapped

        chain = build_chain(0)
        return await chain(message)

    async def execute_publish(
        self,
        topic: str,
        payload: bytes,
        qos: int,
        retain: bool,
        final_publish: Callable[[str, bytes, int, bool], Awaitable[None]],
    ) -> None:
        """
        Execute publish middleware chain

        Build middleware chain: middleware1 -> middleware2 -> ... -> final_publish

        :param topic: Target topic
        :param payload: Message content
        :param qos: QoS level
        :param retain: Whether to retain
        :param final_publish: Final publish function
        """
        if not self._middlewares:
            await final_publish(topic, payload, qos, retain)
            return

        def build_chain(
            index: int,
        ) -> Callable[[str, bytes, int, bool], Awaitable[None]]:
            if index >= len(self._middlewares):
                return final_publish

            middleware = self._middlewares[index]
            next_publish = build_chain(index + 1)

            async def wrapped(t: str, p: bytes, q: int, r: bool) -> None:
                await middleware.on_publish(t, p, q, r, next_publish)

            return wrapped

        chain = build_chain(0)
        await chain(topic, payload, qos, retain)


# ==================== Built-in Middlewares ====================


class LoggingMiddleware(BaseMQTTMiddleware):
    """
    Logging Middleware

    Logs information about message receiving and processing for debugging and monitoring.
    """

    def __init__(self, log_payload: bool = False):
        """
        :param log_payload: Whether to log message content (may contain sensitive information)
        """
        self._log_payload = log_payload

    async def on_receive(
        self,
        message: MQTTMessage,
        call_next: Callable[[MQTTMessage], Awaitable[Any]],
    ) -> Any:
        """Log message receiving and processing"""
        payload_info = f", payload={message.payload[:100]!r}" if self._log_payload else ""
        logger.debug(
            f"[MQTT] Received message: topic={message.topic}, "
            f"qos={message.qos}, size={len(message.payload)}{payload_info}"
        )
        try:
            result = await call_next(message)
            logger.debug(f"[MQTT] Processing completed: topic={message.topic}")
            return result
        except Exception as e:
            logger.error(f"[MQTT] Processing failed: topic={message.topic}, error={e}")
            raise

    async def on_publish(
        self,
        topic: str,
        payload: bytes,
        qos: int,
        retain: bool,
        call_next: Callable[[str, bytes, int, bool], Awaitable[None]],
    ) -> None:
        """Log message publishing"""
        payload_info = f", payload={payload[:100]!r}" if self._log_payload else ""
        logger.debug(
            f"[MQTT] Publishing message: topic={topic}, "
            f"qos={qos}, retain={retain}, size={len(payload)}{payload_info}"
        )
        await call_next(topic, payload, qos, retain)
        logger.debug(f"[MQTT] Publishing completed: topic={topic}")


class ErrorHandlingMiddleware(BaseMQTTMiddleware):
    """
    Error Handling Middleware

    Captures and logs exceptions during message processing.
    """

    def __init__(self):
        """Error handling middleware, follows fail-fast principle"""
        pass

    async def on_receive(
        self,
        message: MQTTMessage,
        call_next: Callable[[MQTTMessage], Awaitable[Any]],
    ) -> Any:
        """Capture and log processing exceptions"""
        try:
            return await call_next(message)
        except Exception as e:
            logger.exception(f"[MQTT] Message processing exception: topic={message.topic}, error={e}")
            raise

    async def on_publish(
        self,
        topic: str,
        payload: bytes,
        qos: int,
        retain: bool,
        call_next: Callable[[str, bytes, int, bool], Awaitable[None]],
    ) -> None:
        """Capture and log publishing exceptions"""
        try:
            await call_next(topic, payload, qos, retain)
        except Exception as e:
            logger.exception(f"[MQTT] Message publishing exception: topic={topic}, error={e}")
            raise
