"""
FastMQTT Exception Hierarchy

Provides a complete exception hierarchy for the MQTT framework.

Exception Hierarchy:
    MQTTException (base)
    ├── MQTTConnectionError - Connection related errors
    ├── MQTTSubscriptionError - Subscription related errors
    ├── MQTTPublishError - Publish related errors
    ├── MQTTSerializationError - Serialization/deserialization errors
    ├── MQTTTopicError - Topic pattern related errors
    ├── MQTTMiddlewareError - Middleware related errors
    ├── MQTTRouterError - Router configuration errors
    └── MQTTNotInitializedError - Broker not initialized error
"""


class MQTTException(Exception):
    """
    MQTT Base Exception

    All MQTT-related exceptions inherit from this class.

    :param message: Error message
    """

    def __init__(self, message: str = "MQTT error occurred"):
        self.message = message
        super().__init__(self.message)


class MQTTConnectionError(MQTTException):
    """
    MQTT Connection Error

    Raised when connection to MQTT Broker fails.

    :param message: Error message
    :param host: Broker address
    :param port: Broker port
    """

    def __init__(
        self,
        message: str = "Failed to connect to MQTT Broker",
        host: str | None = None,
        port: int | None = None,
    ):
        self.host = host
        self.port = port
        if host and port:
            message = f"{message}: {host}:{port}"
        super().__init__(message)


class MQTTSubscriptionError(MQTTException):
    """
    MQTT Subscription Error

    Raised when subscription fails.

    :param message: Error message
    :param topic: Failed topic
    """

    def __init__(
        self,
        message: str = "Subscription failed",
        topic: str | None = None,
    ):
        self.topic = topic
        if topic:
            message = f"{message}: {topic}"
        super().__init__(message)


class MQTTPublishError(MQTTException):
    """
    MQTT Publish Error

    Raised when publishing a message fails.

    :param message: Error message
    :param topic: Target topic
    """

    def __init__(
        self,
        message: str = "Publish failed",
        topic: str | None = None,
    ):
        self.topic = topic
        if topic:
            message = f"{message}: {topic}"
        super().__init__(message)


class MQTTSerializationError(MQTTException):
    """
    MQTT Serialization Error

    Raised when message serialization or deserialization fails.

    :param message: Error message
    """

    def __init__(self, message: str = "Serialization failed"):
        super().__init__(message)


class MQTTTopicError(MQTTException):
    """
    MQTT Topic Error

    Raised when there's a topic pattern parsing or matching error.

    :param message: Error message
    :param topic: Related topic
    :param pattern: Related pattern
    """

    def __init__(
        self,
        message: str = "Topic error",
        topic: str | None = None,
        pattern: str | None = None,
    ):
        self.topic = topic
        self.pattern = pattern
        if pattern:
            message = f"{message}: pattern={pattern}"
        elif topic:
            message = f"{message}: topic={topic}"
        super().__init__(message)


class MQTTMiddlewareError(MQTTException):
    """
    MQTT Middleware Error

    Raised when an error occurs in middleware processing.

    :param message: Error message
    :param middleware_name: Middleware name
    """

    def __init__(
        self,
        message: str = "Middleware error",
        middleware_name: str | None = None,
    ):
        self.middleware_name = middleware_name
        if middleware_name:
            message = f"{message}: {middleware_name}"
        super().__init__(message)


class MQTTRouterError(MQTTException):
    """
    MQTT Router Error

    Raised when there's a router configuration or operation error.

    :param message: Error message
    """

    def __init__(self, message: str = "Router configuration error"):
        super().__init__(message)


class MQTTNotInitializedError(MQTTException):
    """
    MQTT Not Initialized Error

    Raised when trying to use MQTTBroker before initialization.
    """

    def __init__(self, message: str = "MQTTBroker not initialized, please call start() first"):
        super().__init__(message)
