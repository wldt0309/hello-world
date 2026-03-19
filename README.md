# Supabase + Claude API Hello World Project

一个展示Supabase数据库集成和Claude AI API调用的示例项目。

## 功能特性

- 使用Supabase存储用户消息历史
- 调用Claude API进行AI对话
- 简单的Web界面

## 环境配置

在运行前，需要设置以下环境变量：

```bash
# 复制.env.example为.env并填入你的凭证
cp .env.example .env
```

## .env.example 配置说明

```
# Supabase 配置
SUPABASE_URL=你的Supabase项目URL
SUPABASE_ANON_KEY=你的Supabase Anon Key

# Claude API 配置
CLAUDE_API_KEY=你的Claude API Key
```

## 获取凭证

### Supabase
1. 登录 [Supabase](https://supabase.com)
2. 创建新项目或选择已有项目
3. 进入 Settings > API
4. 复制 Project URL 和 anon public key

### Claude API
1. 登录 [Anthropic Console](https://console.anthropic.com)
2. 创建 API Key
3. 注意：API Key 以 `sk-ant-` 开头

## 项目结构

```
hello-world/
├── app.py              # 主应用
├── .env                # 环境变量（不提交）
├── .env.example        # 环境变量模板
├── requirements.txt   # Python依赖
├── static/
│   └── index.html      # 前端页面
└── README.md
```

## 运行项目

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
# 编辑 .env 文件，填入你的凭证

# 3. 运行应用
python app.py
```

然后打开浏览器访问 http://localhost:8000

## Supabase SQL 设置

在Supabase的SQL Editor中执行以下SQL创建表：

```sql
-- 创建消息表
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    user_message TEXT NOT NULL,
    ai_message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 启用RLS（可选）
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 允许匿名访问
CREATE POLICY "Allow anonymous insert" ON messages
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous select" ON messages
    FOR SELECT USING (true);
```

## GitHub Actions

项目已配置CI/CD，每次推送自动运行测试。
