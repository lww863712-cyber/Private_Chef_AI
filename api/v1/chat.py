from fastapi import APIRouter
from typing import Optional
# 假设 ChatRequest 已定义在某个模型中，此处仅示意
# from app.models import ChatRequest

router = APIRouter()

# -------------------- 流式对话 --------------------



@router.post("/chat/stream")
async def chat_endpoint(request: ChatRequest):
    """流式对话"""
    # TODO: 实现流式响应逻辑
    pass

# -------------------- 获取历史消息 --------------------
@router.get("/chat/messages")
async def get_chat_messages(thread_id: str):
    """获取历史消息"""
    # TODO: 根据 thread_id 查询并返回消息列表
    pass

# -------------------- 清空历史消息 --------------------
@router.delete("/chat/messages")
async def clear_chat_messages(thread_id: str):
    """清空历史消息"""
    # TODO: 删除指定 thread_id 的所有消息
    pass