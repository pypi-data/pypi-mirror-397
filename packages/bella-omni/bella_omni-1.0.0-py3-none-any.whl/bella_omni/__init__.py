"""
Bella Omni Backend Plugin

可热插拔的 FastAPI 路由模块，支持 Qwen Omni 全模态实时对话

使用方式:
```python
from fastapi import FastAPI
from bella_omni import create_omni_router, OmniConfig

app = FastAPI()

# 方式1: 使用默认配置
app.include_router(create_omni_router())

# 方式2: 自定义配置
config = OmniConfig(
    api_key="your-api-key",
    model="qwen3-omni-flash-realtime-2025-12-01",
    default_voice="Cherry",
)
app.include_router(create_omni_router(config))
```
"""

from .config import OmniConfig
from .router import create_omni_router
from .session import OmniSession

__version__ = "1.0.0"
__all__ = ["OmniConfig", "create_omni_router", "OmniSession"]
