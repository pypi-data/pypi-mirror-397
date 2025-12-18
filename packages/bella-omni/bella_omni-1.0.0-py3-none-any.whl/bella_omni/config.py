"""
Bella Omni 配置模块
"""
from dataclasses import dataclass, field
from typing import Optional, List
import os


@dataclass
class OmniConfig:
    """
    Omni 插件配置
    
    Attributes:
        api_key: DashScope API 密钥，默认从环境变量读取
        model: 模型名称
        default_voice: 默认语音
        available_voices: 可用语音列表
        enable_image: 是否启用图片输入
        enable_video: 是否启用视频输入
        route_prefix: 路由前缀
        enable_turn_detection: 是否启用 VAD 自动检测（False=按住说话模式）
    """
    api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("DASHSCOPE_API_KEY")
    )
    model: str = "qwen3-omni-flash-realtime-2025-12-01"
    default_voice: str = "Cherry"
    available_voices: List[str] = field(default_factory=lambda: [
        "Cherry",      # 女声-活泼
        "Serena",      # 女声-温柔
        "Ethan",       # 男声-沉稳
        "Chelsie",     # 女声-甜美
    ])
    enable_image: bool = True
    enable_video: bool = True
    route_prefix: str = "/api/realtime"
    enable_turn_detection: bool = False  # 按住说话模式
    
    def validate(self) -> None:
        """验证配置"""
        if not self.api_key:
            raise ValueError(
                "API Key 未配置，请设置 DASHSCOPE_API_KEY 环境变量或传入 api_key 参数"
            )
    
    @classmethod
    def from_env(cls) -> "OmniConfig":
        """从环境变量创建配置"""
        return cls(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model=os.getenv("OMNI_MODEL", "qwen3-omni-flash-realtime-2025-12-01"),
            default_voice=os.getenv("OMNI_DEFAULT_VOICE", "Cherry"),
        )
