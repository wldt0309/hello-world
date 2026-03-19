"""
Supabase + Claude API Hello World Application
使用FastAPI构建的Web应用，展示数据库存储和AI对话功能
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
from anthropic import Anthropic

# 加载环境变量
load_dotenv()

# 初始化
app = FastAPI(title="Supabase + Claude Hello World")

# 配置模板
templates = Jinja2Templates(directory="templates")

# 初始化Supabase客户端
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

# 初始化Claude客户端
anthropic = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """主页，显示聊天界面和历史消息"""
    messages = []
    if supabase:
        try:
            response = supabase.table("messages").select("*").order("created_at", desc=True).limit(10).execute()
            messages = response.data or []
        except Exception as e:
            print(f"获取消息失败: {e}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "messages": messages,
        "supabase_connected": supabase is not None
    })


@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, user_message: str = Form(...)):
    """处理用户消息，调用Claude API并存储到Supabase"""

    ai_message = ""
    error = None

    # 调用Claude API
    try:
        if anthropic.api_key:
            response = anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            ai_message = response.content[0].text
        else:
            ai_message = "请配置CLAUDE_API_KEY环境变量"
    except Exception as e:
        error = str(e)
        ai_message = f"调用Claude API失败: {error}"

    # 存储到Supabase
    if supabase and not error:
        try:
            supabase.table("messages").insert({
                "user_message": user_message,
                "ai_message": ai_message
            }).execute()
        except Exception as e:
            print(f"存储消息失败: {e}")

    # 获取更新后的消息列表
    messages = []
    if supabase:
        try:
            response = supabase.table("messages").select("*").order("created_at", desc=True).limit(10).execute()
            messages = response.data or []
        except Exception as e:
            print(f"获取消息失败: {e}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "messages": messages,
        "supabase_connected": supabase is not None,
        "last_user_message": user_message,
        "last_ai_message": ai_message
    })


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "supabase": "connected" if supabase else "not configured",
        "claude": "configured" if anthropic.api_key else "not configured"
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 Supabase + Claude Hello World")
    print("=" * 50)
    print("请确保已配置以下环境变量:")
    print("  - SUPABASE_URL")
    print("  - SUPABASE_ANON_KEY")
    print("  - CLAUDE_API_KEY")
    print("=" * 50)
    print("访问 http://localhost:8000 查看应用")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
