# -*- coding: utf-8 -*-
"""
Bella Omni - FastAPI 路由模块

提供即插即用的 WebSocket 路由

Example:
    ```python
    from fastapi import FastAPI
    from bella_omni import create_omni_router, OmniConfig
    
    app = FastAPI()
    
    # 方式1: 默认配置（从环境变量读取 API Key）
    app.include_router(create_omni_router())
    
    # 方式2: 自定义配置
    config = OmniConfig(api_key="your-key", default_voice="Cherry")
    app.include_router(create_omni_router(config))
    ```
"""
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from .config import OmniConfig
from .session import OmniSession


# 默认可用语音
AVAILABLE_VOICES = [
    {"id": "Chelsie", "name": "Chelsie (中文女声)", "lang": "zh"},
    {"id": "Cherry", "name": "Cherry (中文女声)", "lang": "zh"},
    {"id": "Serena", "name": "Serena (英文女声)", "lang": "en"},
    {"id": "Ethan", "name": "Ethan (英文男声)", "lang": "en"},
]


def create_omni_router(config: Optional[OmniConfig] = None) -> APIRouter:
    """
    创建 Omni 实时对话路由
    
    Args:
        config: Omni 配置，不传则使用默认配置（从环境变量读取）
    
    Returns:
        FastAPI APIRouter 实例
    
    WebSocket 端点: /ws
    
    客户端消息格式:
    - {"type": "connect", "voice": "Cherry", "system_prompt": "..."}
    - {"type": "audio", "data": "<base64>"}
    - {"type": "image", "data": "<base64>"}
    - {"type": "video_frame", "data": "<base64>"}
    - {"type": "speech_end"}
    - {"type": "text_prompt", "text": "..."}
    - {"type": "disconnect"}
    
    服务端消息格式:
    - {"type": "state", "state": "connected", "message": "..."}
    - {"type": "transcript", "text": "...", "is_user": true, "is_final": true}
    - {"type": "audio", "data": "<base64>"}
    - {"type": "vad", "event": "speech_start"}
    - {"type": "response_done"}
    - {"type": "image_received", "message": "..."}
    """
    if config is None:
        config = OmniConfig.from_env()
    
    router = APIRouter(prefix=config.route_prefix, tags=["omni-realtime"])
    
    @router.websocket("/ws")
    async def realtime_websocket(websocket: WebSocket):
        """实时全模态对话 WebSocket 端点"""
        await websocket.accept()
        
        session: Optional[OmniSession] = None
        
        async def handle_event(event: dict):
            """事件处理器 - 转发到 WebSocket"""
            try:
                await websocket.send_json(event)
            except Exception as e:
                print(f"[Omni Router] Send error: {e}")
        
        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type", "")
                
                if msg_type == "connect":
                    # 创建会话
                    voice = data.get("voice", config.default_voice)
                    system_prompt = data.get("system_prompt")
                    
                    session = OmniSession(
                        config=config,
                        on_event=lambda e: handle_event(e),
                        voice=voice,
                        system_prompt=system_prompt,
                    )
                    
                    # 连接
                    success = await session.connect()
                    
                    if not success:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Connection failed"
                        })
                    else:
                        await websocket.send_json({
                            "type": "state",
                            "state": "connected",
                            "message": "Omni connected"
                        })
                        
                elif msg_type == "audio" and session:
                    audio_data = data.get("data", "")
                    if audio_data:
                        await session.send_audio(audio_data)
                        
                elif msg_type == "image" and session:
                    image_data = data.get("data", "")
                    if image_data:
                        await session.send_image(image_data, auto_respond=False)
                        await websocket.send_json({
                            "type": "image_received",
                            "message": "图片已上传，请输入问题后发送"
                        })
                        
                elif msg_type == "video_frame" and session:
                    frame_data = data.get("data", "")
                    if frame_data:
                        await session.send_video_frame(frame_data)
                
                elif msg_type == "speech_end" and session:
                    await session.trigger_response()
                
                elif msg_type == "text_prompt" and session:
                    text = data.get("text", "")
                    if text:
                        await session.trigger_response(text)
                        
                elif msg_type == "disconnect":
                    if session:
                        await session.close()
                    break
                    
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"[Omni Router] Error: {e}")
            try:
                await websocket.send_json({"type": "error", "message": str(e)})
            except:
                pass
        finally:
            if session:
                await session.close()
    
    @router.get("/config")
    async def get_config():
        """获取实时对话配置"""
        return {
            "voices": AVAILABLE_VOICES,
            "default_voice": config.default_voice,
            "model": config.model,
            "features": {
                "audio": True,
                "image": config.enable_image,
                "video_frame": config.enable_video,
            }
        }
    
    return router
