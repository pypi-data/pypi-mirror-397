# FasterMQTT

一个受 [FastStream](https://github.com/airtai/faststream) 架构启发的 FastAPI 风格 MQTT 框架。

FasterMQTT 将 FastAPI 优雅的路由模式带入 MQTT，实现了简洁的订阅管理，支持依赖注入、主题路径参数和层级路由。

## 特性

- **FastAPI 集成**：通过 lifespan 管理与 FastAPI 无缝集成
- **装饰器订阅**：使用 `@router.subscribe("topic/{param}")` 定义处理器
- **主题路径参数**：自动提取，如 `client/{client_id}/control` → `client_id="abc123"`
- **依赖注入**：在 MQTT 处理器中完整支持 FastAPI `Depends()`
- **层级路由**：通过 `include_router()` 实现嵌套路由和前缀累加
- **共享订阅**：MQTT 5.0 `$share/{group}/{topic}` 消费者组
- **中间件系统**：洋葱模型中间件，用于消息拦截
- **Pydantic/SQLModel 支持**：自动序列化/反序列化消息负载
- **类型安全**：全代码库完整类型注解

## 安装

```bash
pip install fastermqtt
```



## 快速开始

### 基本用法

```python
from fastapi import FastAPI
from fastermqtt import MqttRouter

# 创建带 MQTT 连接配置的根路由
mqtt_router = MqttRouter(
    host="localhost",
    port=1883,
    username="user",
    password="password",
)

# 订阅主题
@mqtt_router.subscribe("sensors/temperature")
async def handle_temperature(payload: bytes):
    temperature = float(payload.decode())
    print(f"温度: {temperature}")

# 与 FastAPI 集成
app = FastAPI()
app.include_router(mqtt_router)
```

### 主题路径参数

自动从主题段中提取值：

```python
@mqtt_router.subscribe("client/{client_id}/control")
async def handle_control(client_id: str, payload: bytes):
    print(f"客户端 {client_id} 的命令: {payload}")
```

### 层级路由

使用嵌套路由组织订阅：

```python
# 根路由（管理 MQTT 连接）
mqtt_router = MqttRouter(host="localhost", port=1883)

# 子路由（无连接配置，共享父路由的 broker）
client_router = MqttRouter(prefix="client")

@client_router.subscribe("{client_id}/status")
async def handle_status(client_id: str, payload: bytes):
    # 订阅: client/{client_id}/status
    pass

# 包含子路由
mqtt_router.include_router(client_router)
```

### 依赖注入

在 MQTT 处理器中使用 FastAPI 的依赖注入：

```python
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@mqtt_router.subscribe("events/{event_type}")
async def handle_event(
    event_type: str,
    payload: bytes,
    session: SessionDep,
):
    # 保存事件到数据库
    event = Event(type=event_type, data=payload.decode())
    session.add(event)
    await session.commit()
```

### 发布消息

```python
# 从路由发布（使用路由的前缀）
client_router = MqttRouter(prefix="client/{client_id}/response")

await client_router.publish(
    payload=b"OK",
    client_id="abc123",  # 替换 {client_id}
    qos=1,
)
# 发布到: client/abc123/response

# 直接通过 broker 发布
from fastermqtt import MQTTBroker

await MQTTBroker.publish(
    topic="notifications/alert",
    payload=b"系统警报!",
    qos=2,
    retain=True,
)
```

### 共享订阅（消费者组）

在多个服务实例间分发消息：

```python
# 全局默认消费者组
mqtt_router = MqttRouter(
    host="localhost",
    port=1883,
    default_consumer_group="workers",  # 所有订阅使用此组
)

# 单个订阅的消费者组
@mqtt_router.subscribe("tasks/heavy", group="heavy-workers")
async def handle_heavy_task(payload: bytes):
    # "heavy-workers" 组中只有一个实例接收每条消息
    pass

# 强制不使用共享订阅（覆盖默认值）
@mqtt_router.subscribe("broadcast/all", group="")
async def handle_broadcast(payload: bytes):
    # 所有实例都接收每条消息
    pass
```

### Pydantic 模型序列化

```python
from pydantic import BaseModel
from fastermqtt import encode_payload, decode_payload

class SensorData(BaseModel):
    sensor_id: str
    value: float
    timestamp: int

# 编码用于发布
data = SensorData(sensor_id="temp-1", value=23.5, timestamp=1234567890)
payload = encode_payload(data)  # 返回 JSON 字节

# 在处理器中解码
@mqtt_router.subscribe("sensors/data")
async def handle_sensor_data(payload: bytes):
    data = decode_payload(payload, SensorData)
    print(f"传感器 {data.sensor_id}: {data.value}")
```

### 中间件

添加横切关注点，如日志和错误处理：

```python
from fastermqtt import (
    BaseMQTTMiddleware,
    MiddlewareChain,
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    MQTTMessage,
)

class MetricsMiddleware(BaseMQTTMiddleware):
    async def on_receive(self, message: MQTTMessage, call_next):
        start = time.time()
        result = await call_next(message)
        duration = time.time() - start
        metrics.record("mqtt_message_duration", duration)
        return result

# 构建中间件链
chain = MiddlewareChain()
chain.add(ErrorHandlingMiddleware())
chain.add(LoggingMiddleware(log_payload=True))
chain.add(MetricsMiddleware())
```

## API 参考

### MqttRouter

继承自 FastAPI `APIRouter` 的主路由类。

```python
MqttRouter(
    host: str | None = None,          # MQTT broker 地址（仅根路由）
    port: int = 8883,                  # MQTT broker 端口
    username: str | None = None,      # 认证用户名
    password: str | None = None,      # 认证密码
    client_id: str | None = None,     # 客户端 ID（未提供则自动生成）
    keepalive: int = 60,              # 心跳间隔（秒）
    ssl_ca_cert: str | None = None,   # SSL CA 证书路径
    clean_session: bool = True,       # 连接时是否清除会话
    default_consumer_group: str | None = None,  # 默认共享订阅组
    prefix: str = "",                 # 主题前缀
)
```

#### 方法

- `subscribe(topic, qos=0, group=None)` - 注册订阅处理器的装饰器
- `publish(payload, qos=0, retain=False, **path_params)` - 发布消息
- `include_router(router, prefix="", ...)` - 包含子路由

### MQTTBroker

MQTT 连接的单例管理器（纯 classmethod 模式）。

```python
# 生命周期（由 MqttRouter 自动调用）
await MQTTBroker.start(config)
await MQTTBroker.stop()

# 发布
await MQTTBroker.publish(topic, payload, qos=0, retain=False)

# 状态
MQTTBroker.is_connected()  # bool
MQTTBroker.is_initialized()  # bool
```

### 依赖函数

```python
from fastermqtt import (
    get_mqtt_message,   # 获取 MQTTMessage 对象
    get_mqtt_topic,     # 获取主题字符串
    get_mqtt_payload,   # 获取原始负载字节
    get_mqtt_qos,       # 获取 QoS 级别
    get_topic_param,    # 按索引提取主题段
)

# 便捷类型别名
from fastermqtt import (
    MqttMessageDep,  # Annotated[MQTTMessage, Depends(get_mqtt_message)]
    MqttTopicDep,    # Annotated[str, Depends(get_mqtt_topic)]
    MqttPayloadDep,  # Annotated[bytes, Depends(get_mqtt_payload)]
    MqttQosDep,      # Annotated[int, Depends(get_mqtt_qos)]
)
```

### 类型

```python
from fastermqtt import (
    MQTTMessage,       # 消息容器（topic, payload, qos, properties）
    SubscriptionInfo,  # 订阅元数据
    MQTTConfig,        # 连接配置
)
```

### 异常

```python
from fastermqtt import (
    MQTTException,           # 基础异常
    MQTTConnectionError,     # 连接失败
    MQTTSubscriptionError,   # 订阅失败
    MQTTPublishError,        # 发布失败
    MQTTSerializationError,  # 序列化/反序列化错误
    MQTTTopicError,          # 主题模式错误
    MQTTMiddlewareError,     # 中间件错误
    MQTTRouterError,         # 路由配置错误
    MQTTNotInitializedError, # Broker 未初始化
)
```

## 架构

FasterMQTT 遵循 [FastStream](https://github.com/airtai/faststream) 的架构：

```
MqttRouter（继承 APIRouter）
    ├── 通过 lifespan 管理 MQTTBroker 生命周期
    ├── 支持 include_router() 实现层级路由
    ├── 前缀累加：子路由主题自动添加父路由前缀
    └── 所有路由共享 broker

MQTTBroker（单例，纯 classmethod）
    ├── 管理 gmqtt Client 连接
    ├── 分发消息给订阅者
    ├── 通过 solve_dependencies 实现 FastAPI 风格依赖注入
    └── 通过正则表达式提取主题参数
```

## 配置

### SSL/TLS

```python
mqtt_router = MqttRouter(
    host="mqtt.example.com",
    port=8883,
    ssl_ca_cert="/path/to/ca.crt",
)
```

### 清除会话

```python
mqtt_router = MqttRouter(
    host="localhost",
    port=1883,
    clean_session=False,  # 重连时保留订阅
)
```

## 依赖

- Python 3.10+
- FastAPI
- gmqtt
- pydantic
- orjson（用于 JSON 序列化）

## 许可证

MIT License

## 致谢

- [FastStream](https://github.com/airtai/faststream) - 路由模式架构的灵感来源
- [FastAPI](https://github.com/tiangolo/fastapi) - 依赖注入和路由模式
- [gmqtt](https://github.com/wialon/gmqtt) - 底层 MQTT 客户端
