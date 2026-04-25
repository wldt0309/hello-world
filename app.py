"""
Supabase + MiniMax Hello World Application
使用FastAPI构建的Web应用，展示数据库存储和AI对话功能
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client

# 加载环境变量
load_dotenv()

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化
app = FastAPI(title="Supabase + MiniMax Hello World")

# 配置模板
templates = Jinja2Templates(directory="templates")

# 初始化Supabase客户端
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Optional[Client] = (
    create_client(supabase_url, supabase_key)
    if supabase_url and supabase_key
    else None
)

# MiniMax配置
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"
MINIMAX_MODEL = "abab6.5s-chat"
MAX_MESSAGE_LENGTH = 2000  # 消息最大长度限制
MESSAGE_PAGE_SIZE = 10     # 每页消息数量


def _fetch_messages(limit: int = MESSAGE_PAGE_SIZE):
    """从Supabase获取最新消息，内部函数避免重复代码"""
    if not supabase:
        return []
    try:
        response = supabase.table("messages").select(
            "*"
        ).order("created_at", desc=True).limit(limit).execute()
        return response.data or []
    except Exception as e:
        logger.warning(f"获取消息失败: {e}")
        return []


async def _call_minimax_async(prompt: str) -> str:
    """异步调用MiniMax API，使用httpx异步客户端"""
    if not MINIMAX_API_KEY:
        raise HTTPException(status_code=503, detail="MiniMax API 未配置")

    if len(prompt) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"消息长度不能超过 {MAX_MESSAGE_LENGTH} 字符"
        )

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MINIMAX_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                MINIMAX_API_URL, headers=headers, json=payload
            )
            response.raise_for_status()
            result = response.json()

        if result.get("choices") and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            logger.error(f"MiniMax API 异常响应: {result}")
            raise HTTPException(status_code=502, detail="AI 返回格式异常")

    except httpx.HTTPStatusError as e:
        logger.error(f"MiniMax HTTP 错误: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=502, detail="AI 服务调用失败")
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="AI 服务连接超时")
    except httpx.RequestError as e:
        logger.error(f"MiniMax 请求错误: {e}")
        raise HTTPException(status_code=502, detail="AI 服务请求失败")


def _build_template_context(request: Request, messages: list, extra: Optional[dict] = None):
    """构建模板渲染上下文，避免端点间重复"""
    ctx = {
        "request": request,
        "messages": messages,
        "supabase_connected": supabase is not None,
        "ai_connected": bool(MINIMAX_API_KEY),
    }
    if extra:
        ctx.update(extra)
    return ctx


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """主页，显示聊天界面和历史消息"""
    messages = _fetch_messages()
    return templates.TemplateResponse(
        "index.html",
        _build_template_context(request, messages)
    )


@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, user_message: str = Form(...)):
    """处理用户消息，调用MiniMax API并存储到Supabase"""

    # 输入校验在 _call_minimax_async 中统一处理

    # 异步调用 MiniMax API
    try:
        ai_message = await _call_minimax_async(user_message)
    except HTTPException:
        raise  # 已是 HTTPException，直接透传
    except Exception as e:
        logger.exception("MiniMax 调用未预期错误")
        raise HTTPException(status_code=500, detail="AI 服务内部错误")

    # 存储到 Supabase（不阻塞响应）
    if supabase:
        try:
            supabase.table("messages").insert({
                "user_message": user_message,
                "ai_message": ai_message,
            }).execute()
        except Exception as e:
            logger.warning(f"存储消息失败: {e}")
            # 不影响主流程，仅记录

    # 获取更新后的消息列表
    messages = _fetch_messages()
    return templates.TemplateResponse(
        "index.html",
        _build_template_context(request, messages, {
            "last_user_message": user_message,
            "last_ai_message": ai_message,
        })
    )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "supabase": "connected" if supabase else "not configured",
        "minimax": "configured" if MINIMAX_API_KEY else "not configured",
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Supabase + MiniMax Hello World")
    print("=" * 50)
    print("访问 http://localhost:8000 查看应用")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
