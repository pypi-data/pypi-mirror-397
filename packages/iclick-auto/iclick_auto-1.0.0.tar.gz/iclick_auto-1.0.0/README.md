# iclick-auto

![PyPI version](https://img.shields.io/pypi/v/iclick-auto.svg)
![PyPI license](https://img.shields.io/pypi/l/iclick-auto.svg)

[English](README.en.md) | 中文

用于iOS免越狱自动化的 Python SDK。除了 API 调用功能外，还实现了断线重连和事件监听机制。

官方网站: https://iosclick.com/

## 安装

```bash
pip install iclick-auto
```

## 快速开始

```python
from iclick import client as iclient

# 创建客户端实例
client = iclient()

# 监听设备事件
client.on('device:online', lambda data: print('设备上线:', data))
client.on('device:offline', lambda data: print('设备下线:', data))

# 连接服务器
client.connect()

# 调用 API
result = client.invoke('getDevices', {'deviceId': 'P60904DC8D3F'})

print('结果:', result)
```

## API 文档

### `client(options)`

创建客户端实例。

**参数：**

| 参数 | 类型 | 可选 | 说明 | 默认值 |
|------|------|------|------|--------|
| `options.host` | str | 是 | WebSocket 服务器地址 | `127.0.0.1` |
| `options.port` | int | 是 | WebSocket 服务器端口 | `23188` |
| `options.autoReconnect` | bool | 是 | 是否启用自动重连 | `True` |
| `options.reconnectDelay` | int | 是 | 重连延迟（秒） | `3` |
| `options.maxReconnectAttempts` | int | 是 | 最大重连次数，0表示无限 | `8` |

**示例：**

```python
from iclick import client as iclient

client = iclient({
    'host': '192.168.31.15',
    'port': 23188,
    'autoReconnect': True,
    'reconnectDelay': 5
})
```

### `client.connect()`

连接到 WebSocket 服务器。

**示例：**

```python
try:
    client.connect()
    print('连接成功')
except Exception as error:
    print('连接失败:', error)
```

### `client.invoke(type, params, timeout)`

调用 API 方法。

**参数：**

- `type` (str): API 类型
- `params` (dict, 可选): 请求参数，默认 `{}`
- `timeout` (int, 可选): 超时时间（秒），默认 `18`

**返回：** 响应数据

**示例：**

```python
# 发送按键
result = client.invoke('sendKey', {
    'deviceId': 'P60904DC8D3F',
    'key': 'h',
    'fnkey': 'COMMAND'
})

# 自定义超时时间
result = client.invoke('someType', {'param': 'value'}, 30)
```

### `client.on(event_name, callback)`

注册事件监听器。

**参数：**

- `event_name` (str): 事件名称
- `callback` (callable): 回调函数，接收事件数据作为参数

**示例：**

```python
client.on('device:online', lambda data: print('设备上线:', data))
client.on('device:offline', lambda data: print('设备下线:', data))
```

### `client.off(event_name, callback)`

移除事件监听器。

**参数：**

- `event_name` (str): 事件名称
- `callback` (callable, 可选): 要移除的回调函数。如果不提供，将移除该事件的所有监听器

**示例：**

```python
def handler(data):
    print('收到事件:', data)

# 注册监听器
client.on('someEvent', handler)

# 移除特定监听器
client.off('someEvent', handler)

# 移除事件的所有监听器
client.off('someEvent')
```

### `client.destroy()`

销毁客户端，断开连接并清理所有资源。

**示例：**

```python
client.destroy()
print('客户端已销毁')
```

## License

MIT

## 相关链接

- API参考: https://iosclick.com/zh/api/index.html
- 事件通知: https://iosclick.com/zh/api/notify.html
- PyPI 包: https://pypi.org/project/iclick-auto/

## 问题反馈

如有问题，请在 [Issues](https://github.com/Undefined-Token/iclick-python/issues) 中反馈。
