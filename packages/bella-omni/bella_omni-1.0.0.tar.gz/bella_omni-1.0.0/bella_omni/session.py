# -*- coding: utf-8 -*-
"""
Bella Omni - 会话管理模块

支持 Qwen Omni 全模态实时对话
"""
import asyncio
from dataclasses import dataclass, field
from typing import Literal, Callable, Optional
from enum import Enum

import dashscope
from dashscope.audio.qwen_omni import (
    OmniRealtimeConversation,
    OmniRealtimeCallback,
    MultiModality,
    AudioFormat,
)

from .config import OmniConfig


# ============================================================================
# ADT 类型定义
# ============================================================================

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass(frozen=True)
class TranscriptEvent:
    """转写事件"""
    text: str
    is_final: bool
    is_user: bool
    tag: Literal["transcript"] = "transcript"


@dataclass(frozen=True)
class AudioEvent:
    """音频事件"""
    data: str  # base64 encoded
    tag: Literal["audio"] = "audio"


@dataclass(frozen=True)
class StateEvent:
    """状态事件"""
    state: str
    message: str
    tag: Literal["state"] = "state"


# 事件联合类型
OmniEvent = TranscriptEvent | AudioEvent | StateEvent

# 事件处理器类型
EventHandler = Callable[[dict], None]


# ============================================================================
# 会话管理器
# ============================================================================

@dataclass
class OmniSession:
    """
    Omni 实时会话管理器
    
    用于管理与 DashScope 的 WebSocket 连接
    
    Example:
        ```python
        session = OmniSession(config, on_event=handle_event)
        await session.connect()
        await session.send_audio(audio_b64)
        await session.close()
        ```
    """
    config: OmniConfig
    on_event: EventHandler  # 事件回调
    voice: str = ""
    system_prompt: Optional[str] = None
    _conversation: OmniRealtimeConversation = field(init=False, default=None)
    _connected: bool = field(init=False, default=False)
    _current_response_text: str = field(init=False, default="")
    _loop: asyncio.AbstractEventLoop = field(init=False, default=None)
    
    def __post_init__(self):
        if not self.voice:
            self.voice = self.config.default_voice

    def _create_callback(self) -> OmniRealtimeCallback:
        """创建 DashScope 回调"""
        session = self
        loop = self._loop

        class ProxyCallback(OmniRealtimeCallback):
            def on_open(self) -> None:
                session._connected = True
                asyncio.run_coroutine_threadsafe(
                    session._emit({"type": "state", "state": "connected", "message": "Omni connected"}),
                    loop
                )

            def on_close(self, code: int, msg: str) -> None:
                session._connected = False
                asyncio.run_coroutine_threadsafe(
                    session._emit({"type": "state", "state": "disconnected", "message": f"Closed: {msg}"}),
                    loop
                )

            def on_event(self, response: dict) -> None:
                event_type = response.get("type", "")
                
                # 累积 AI 回复文本
                if event_type == "response.audio_transcript.delta":
                    delta = response.get("delta", "")
                    session._current_response_text += delta
                elif event_type == "response.done":
                    if session._current_response_text:
                        session._current_response_text = ""
                
                # 事件处理
                handlers = {
                    "session.created": lambda r: asyncio.run_coroutine_threadsafe(
                        session._emit({"type": "state", "state": "session_started", "message": f"Session: {r.get('session', {}).get('id', '')}"}),
                        loop
                    ),
                    "conversation.item.input_audio_transcription.completed": lambda r: asyncio.run_coroutine_threadsafe(
                        session._emit({"type": "transcript", "text": r.get("transcript", ""), "is_user": True, "is_final": True}),
                        loop
                    ),
                    "response.audio_transcript.delta": lambda r: asyncio.run_coroutine_threadsafe(
                        session._emit({"type": "transcript", "text": r.get("delta", ""), "is_user": False, "is_final": False}),
                        loop
                    ),
                    "response.audio.delta": lambda r: asyncio.run_coroutine_threadsafe(
                        session._emit({"type": "audio", "data": r.get("delta", "")}),
                        loop
                    ),
                    "input_audio_buffer.speech_started": lambda r: asyncio.run_coroutine_threadsafe(
                        session._emit({"type": "vad", "event": "speech_start"}),
                        loop
                    ),
                    "input_audio_buffer.speech_stopped": lambda r: asyncio.run_coroutine_threadsafe(
                        session._emit({"type": "vad", "event": "speech_stop"}),
                        loop
                    ),
                    "response.done": lambda r: asyncio.run_coroutine_threadsafe(
                        session._emit({"type": "response_done"}),
                        loop
                    ),
                }
                
                handler = handlers.get(event_type)
                if handler:
                    try:
                        handler(response)
                    except Exception as e:
                        print(f"[OmniSession] Handler error: {e}")

        return ProxyCallback()

    async def _emit(self, event: dict) -> None:
        """发送事件"""
        try:
            self.on_event(event)
        except Exception as e:
            print(f"[OmniSession] Emit error: {e}")

    def _build_instructions(self) -> str:
        """构建系统提示词"""
        base_rules = """
语音表达规则：
1. 使用中文回复，语气自然亲切
2. 句子简短有力，避免冗长书面语
3. 适当使用"嗯""啊""呢"等语气词
"""
        if self.system_prompt:
            return f"{self.system_prompt}\n\n{base_rules}"
        return f"你是一个温暖、有情感的AI助手。\n\n{base_rules}"

    async def connect(self) -> bool:
        """连接到 Omni Realtime"""
        try:
            self.config.validate()
            dashscope.api_key = self.config.api_key
            
            self._loop = asyncio.get_running_loop()
            callback = self._create_callback()
            
            self._conversation = OmniRealtimeConversation(
                model=self.config.model,
                callback=callback,
                url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
            )
            
            # 连接
            await self._loop.run_in_executor(None, self._conversation.connect)
            
            # 等待连接
            for _ in range(50):
                if self._connected:
                    break
                await asyncio.sleep(0.1)
            
            if not self._connected:
                self._connected = True
            
            # 配置会话
            await self._loop.run_in_executor(
                None,
                lambda: self._conversation.update_session(
                    output_modalities=[MultiModality.AUDIO, MultiModality.TEXT],
                    voice=self.voice,
                    input_audio_format=AudioFormat.PCM_16000HZ_MONO_16BIT,
                    output_audio_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
                    enable_input_audio_transcription=True,
                    input_audio_transcription_model="gummy-realtime-v1",
                    enable_turn_detection=self.config.enable_turn_detection,
                    instructions=self._build_instructions(),
                )
            )
            
            return True
            
        except Exception as e:
            print(f"[OmniSession] Connect error: {e}")
            return False

    async def send_audio(self, audio_b64: str) -> None:
        """发送音频"""
        if self._conversation and self._connected:
            try:
                self._conversation.append_audio(audio_b64)
            except Exception as e:
                print(f"[OmniSession] Send audio error: {e}")

    async def send_image(self, image_b64: str, auto_respond: bool = False) -> None:
        """发送图片"""
        if self._conversation and self._connected:
            try:
                await self._loop.run_in_executor(
                    None,
                    lambda: self._conversation.append_video(image_b64)
                )
                if auto_respond:
                    await self.trigger_response("请描述这张图片")
            except Exception as e:
                print(f"[OmniSession] Send image error: {e}")

    async def send_video_frame(self, frame_b64: str) -> None:
        """发送视频帧"""
        if self._conversation and self._connected:
            try:
                await self._loop.run_in_executor(
                    None,
                    lambda: self._conversation.append_video(frame_b64)
                )
            except Exception as e:
                print(f"[OmniSession] Send video frame error: {e}")

    async def trigger_response(self, instructions: str = None) -> None:
        """触发 AI 回复"""
        if self._conversation and self._connected:
            try:
                await self._loop.run_in_executor(
                    None,
                    lambda: self._conversation.create_response(instructions=instructions)
                )
            except Exception as e:
                print(f"[OmniSession] Trigger response error: {e}")

    async def close(self) -> None:
        """关闭会话"""
        if self._conversation:
            try:
                await self._loop.run_in_executor(None, self._conversation.close)
            except Exception:
                pass
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected
