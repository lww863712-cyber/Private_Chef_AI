F:\python\PycharmProjects\PythonProject4\SYSTEM.md
# Personal Chef AI - 系统文档

> **版本**: 0.1.0
> **作者**: lww863712-cyber (lwww863712@gmail.com)
> **仓库**: https://github.com/lww863712-cyber/Private_Chef_AI.git
> **最后更新**: 2026-09-07

---

## 目录

1. [项目概述](#1-项目概述)
2. [系统架构](#2-系统架构)
3. [技术栈](#3-技术栈)
4. [项目结构](#4-项目结构)
5. [环境配置](#5-环境配置)
6. [核心模块详解](#6-核心模块详解)
7. [API 接口文档](#7-api-接口文档)
8. [数据模型](#8-数据模型)
9. [AI Agent 工作流](#9-ai-agent-工作流)
10. [数据库设计](#10-数据库设计)
11. [前端部署](#11-前端部署)
12. [构建与启动](#12-构建与启动)
13. [已知问题与注意事项](#13-已知问题与注意事项)

---

## 1. 项目概述

**Personal Chef AI（私人厨师 AI）** 是一个基于 AI 的智能食谱推荐系统。用户可以通过文字描述或上传食材照片，系统将自动识别食材、搜索食谱、进行营养和难度评估，并输出结构化的食谱推荐报告。

### 核心功能

- 📸 **多模态食材识别**：支持上传食材照片，AI 自动辨识食材种类与新鲜度
- 🔍 **智能食谱检索**：集成 Tavily 搜索引擎，基于食材清单搜索可行菜谱
- 📊 **多维度评估排序**：从营养价值和制作难度两个维度量化打分并排序
- 📋 **结构化报告输出**：生成包含食谱信息、得分、推荐理由、参考图片的建议报告
- 💬 **流式对话**：支持 SSE 流式输出，实时返回 AI 回复
- 🧵 **会话记忆**：基于 SQLite + LangGraph Checkpoint 实现多轮对话记忆持久化
- 🖼️ **图片上传**：通过阿里云 OSS 预签名 URL 实现安全的图片上传与访问

---

## 2. 系统架构

    ┌─────────────────────────────────────────────────────────┐
    │                  前端 (Next.js SPA)                      │
    │                    用户界面                               │
    └──────────────┬──────────────────────────────────────────┘
                   │ HTTP / SSE
                   ▼
    ┌─────────────────────────────────────────────────────────┐
    │                  后端 (FastAPI)                           │
    │                                                         │
    │  ┌──────────────────┐    ┌───────────────────┐          │
    │  │ chat.py 对话路由  │    │ oss.py OSS路由     │          │
    │  └────────┬─────────┘    └────────┬──────────┘          │
    └───────────┼───────────────────────┼─────────────────────┘
                │                       │
                ▼                       ▼
    ┌───────────────────────┐   ┌──────────────────┐
    │   AI 引擎 (实战.py)    │   │  阿里云 OSS       │
    │                       │   │  图片存储          │
    │  ┌─────────────────┐  │   └──────────────────┘
    │  │ qwen3.8-flash   │  │
    │  │ 多模态模型       │  │
    │  └─────────────────┘  │
    │  ┌─────────────────┐  │
    │  │ TavilySearch    │  │
    │  │ 搜索工具         │  │
    │  └─────────────────┘  │
    │  ┌─────────────────┐  │
    │  │ SqliteSaver     │  │
    │  │ 记忆持久化       │  │
    │  └─────────────────┘  │
    └───────────────────────┘

### 请求流程

1. **前端** 发送用户消息/图片到后端 API
2. **FastAPI** 接收请求，转发给 AI Agent
3. **Agent** 使用多模态模型识别食材，调用搜索工具检索食谱
4. **流式响应** 通过 SSE (Server-Sent Events) 实时推送到前端
5. **会话状态** 通过 SQLite Checkpoint 持久化，支持多轮对话

---

## 3. 技术栈

| 层级 | 技术 | 版本要求 | 用途 |
|------|------|----------|------|
| **语言** | Python | >= 3.13 | 后端开发语言 |
| **Web 框架** | FastAPI | >= 0.141.1 | RESTful API + SSE 流式响应 |
| **ASGI 服务器** | Uvicorn | >= 0.52.4 | 高性能异步服务器 |
| **AI 框架** | LangChain | >= 1.4.0 | AI 应用开发框架 |
| **Agent 编排** | LangGraph | (via langchain) | Agent 工作流编排 |
| **对话记忆** | langgraph-checkpoint-sqlite | >= 3.1.1 | SQLite Checkpoint 持久化 |
| **LLM 模型** | qwen3.8-flash (DashScope) | - | 多模态大语言模型 |
| **LLM 集成** | langchain-deepseek | >= 1.1.0 | DeepSeek 模型集成 |
| **搜索工具** | langchain-tavily | >= 0.2.18 | Tavily Web 搜索 |
| **对象存储** | alibabacloud-oss-v2 | >= 1.4.0 | 阿里云 OSS 图片存储 |
| **环境变量** | dotenv | >= 0.9.9 | .env 文件加载 |
| **构建工具** | uv (uv_build) | >= 0.12.10 | 依赖管理与构建 |
| **前端** | Next.js (静态导出) | - | SPA 前端应用 |
| **数据库** | SQLite3 | (内置) | 对话记忆持久化 |

---

## 4. 项目结构

    PythonProject4/
    ├── app/                            # 后端应用主包
    │   ├── api/                        # API 层
    │   │   ├── __init__.py
    │   │   └── v1/                     # v1 版本 API
    │   │       ├── __init__.py
    │   │       ├── chat.py             # 对话相关 API（流式对话/历史消息）
    │   │       └── oss.py              # OSS 预签名 URL API
    │   ├── common/                     # 公共模块
    │   │   ├── __init__.py
    │   │   └── logger.py               # 全局日志配置
    │   ├── models/                     # 数据模型
    │   │   ├── __init__.py
    │   │   └── schemas.py              # Pydantic 请求/响应模型
    │   ├── static/                     # 前端静态资源（Next.js 构建产物）
    │   │   ├── index.html              # SPA 入口
    │   │   ├── _next/                  # Next.js 编译产物
    │   │   ├── 404/                    # 404 页面
    │   │   └── ...                     # 其他静态资源
    │   ├── __init__.py
    │   └── main.py                     # FastAPI 应用入口 & 启动配置
    │
    ├── db/                             # 数据库目录
    │   ├── __init__.py
    │   └── personal_chif.db            # SQLite 数据库文件
    │
    ├── static/                         # 前端静态资源（根目录副本）
    ├── .env                            # 环境变量配置（不提交 Git）
    ├── .gitignore                      # Git 忽略规则
    ├── pyproject.toml                  # 项目配置 & 依赖声明
    ├── uv.lock                         # 依赖锁定文件
    ├── main.py                         # 根目录启动脚本
    ├── 实战.py                          # AI Agent 核心业务逻辑
    ├── test_model.py                   # 模型连通性测试脚本
    ├── test_model2.py                  # Agent 功能测试脚本
    └── hellword.py                     # 测试/调试脚本

---

## 5. 环境配置

### 5.1 环境变量（`.env` 文件）

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `DASHSCOPE_API_KEY` | ✅ | 阿里云 DashScope API 密钥 |
| `DASHSCOPE_BASE_URL` | ✅ | DashScope 兼容模式的 Base URL |
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API 密钥 |
| `TAVILY_API_KEY` | ✅ | Tavily 搜索 API 密钥 |
| `OSS_ACCESS_KEY_ID` | ✅ | 阿里云 AccessKey ID |
| `OSS_ACCESS_KEY_SECRET` | ✅ | 阿里云 AccessKey Secret |
| `OSS_BUCKET` | ✅ | 阿里云 OSS Bucket 名称 |
| `OSS_ENDPOINT` | ❌ | OSS Endpoint（默认 `oss-cn-beijing.aliyuncs.com`） |

### 5.2 环境要求

- **Python**: >= 3.13
- **构建工具**: uv >= 0.12.10
- **操作系统**: Windows / Linux / macOS

---

## 6. 核心模块详解

### 6.1 应用入口 (`app/main.py`)

**职责**: FastAPI 应用初始化、中间件配置、路由挂载、静态资源服务

**关键配置**:

- **CORS 中间件**: 允许所有来源（生产环境建议限制具体域名）
- **API 路由前缀**: `/api/v1`
- **静态资源挂载**: 将 `app/static/` 目录挂载为根路径
- **SPA Fallback**: 非 API 路径统一返回 `index.html`，支持前端路由

### 6.2 对话 API (`app/api/v1/chat.py`)

**职责**: 提供流式对话、历史消息查询、消息清空接口

| 方法 | 路径 | 功能 |
|------|------|------|
| `POST` | `/api/v1/chat/stream` | 流式对话（SSE） |
| `GET` | `/api/v1/chat/messages` | 获取历史消息 |
| `DELETE` | `/api/v1/chat/messages` | 清空历史消息 |

### 6.3 OSS API (`app/api/v1/oss.py`)

**职责**: 生成阿里云 OSS 预签名 URL，支持前端安全上传图片

**工作流程**:

1. 前端请求预签名 URL，传入文件名
2. 后端根据文件扩展名判断 Content-Type
3. 生成 **上传预签名 URL**（有效期 1 小时）
4. 生成 **访问预签名 URL**（有效期 24 小时，适用于私有 bucket）
5. 返回 `uploadUrl`、`contentType`、`accessUrl`

**支持的图片格式**: jpg, jpeg, png, gif, webp

### 6.4 AI Agent 核心 (`实战.py`)

**职责**: 整个 AI 智能体的核心逻辑，包括模型初始化、工具配置、Agent 创建、流式对话

**核心组件**:

| 组件 | 说明 |
|------|------|
| **LLM 模型** | `qwen3.8-flash`，通过 DashScope 兼容 OpenAI 接口调用 |
| **搜索工具** | `TavilySearch`，最大返回 5 条结果，主题为 general |
| **记忆系统** | `SqliteSaver`，基于 SQLite 的 Checkpoint 持久化 |
| **Agent 类型** | LangGraph `create_agent`，支持工具调用 + 多轮对话 |

**Agent 系统提示词**:

> 你是一名私人厨师。收到用户提供的食材照片或清单后，请按以下流程操作：
> 1. 识别和评估食材：若用户提供照片，首先辨识所有可见食材。基于食材的外观状态、评估其新鲜度与可用量，整理出一份"当前可用食材清单"。
> 2. 智能食谱检索：优先调用 web_search 工具，以"可用食材清单"为核心关键词，查找可行菜谱。
> 3. 多维度评估与排序：从营养价值和制作难度两个维度对检索到的候选食谱进行量化打分，并根据得分排序。
> 4. 结构化方案输出：把排序后的食谱整理为一份结构清晰的建议报告。
> 请严格按照流程，优先调用 web_search 工具搜索食谱，搜索不到的情况下才能自己发挥。

### 6.5 日志模块 (`app/common/logger.py`)

**职责**: 统一的日志配置与全局 logger 实例

- **日志格式**: `%(asctime)s - %(levelname)s - %(name)s - %(message)s`
- **日志级别**: INFO
- **输出目标**: 控制台（stdout）
- **全局实例**: `logger = logging.getLogger("personal_chief")`

### 6.6 数据模型 (`app/models/schemas.py`)

    class ChatRequest(BaseModel):
        message: str                      # 用户消息文本
        image_url: Optional[str] = None   # 可选的图片 URL
        thread_id: str                    # 会话线程 ID（用于多轮对话）

---

## 7. API 接口文档

### 7.1 流式对话

**POST** `/api/v1/chat/stream`

请求体:

    {
        "message": "冰箱里有西红柿和鸡蛋，能做什么菜？",
        "image_url": "https://xxx.oss-cn-beijing.aliyuncs.com/photo.jpg",
        "thread_id": "session-001"
    }

响应: `text/event-stream`

    data: 根据您提供的食材...
    data: 我为您推荐以下几道菜...

### 7.2 获取历史消息

**GET** `/api/v1/chat/messages?thread_id=session-001`

响应:

    {
        "messages": [
            {"role": "user", "content": "冰箱里有西红柿和鸡蛋"},
            {"role": "assistant", "content": "我为您推荐..."}
        ]
    }

### 7.3 清空历史消息

**DELETE** `/api/v1/chat/messages?thread_id=session-001`

响应:

    {
        "success": true
    }

### 7.4 获取 OSS 预签名 URL

**GET** `/api/v1/oss/presign?filename=uploads/photo_001.jpg`

响应:

    {
        "uploadUrl": "https://yyh12.oss-cn-beijing.aliyuncs.com/uploads/photo_001.jpg?...",
        "contentType": "image/jpeg",
        "accessUrl": "https://yyh12.oss-cn-beijing.aliyuncs.com/uploads/photo_001.jpg?..."
    }

---

## 8. 数据模型

### 8.1 请求模型

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | `str` | ✅ | 用户输入的文本消息 |
| `image_url` | `str` 或 `null` | ❌ | 食材图片的 URL（来自 OSS 访问地址） |
| `thread_id` | `str` | ✅ | 会话线程唯一标识，用于多轮对话记忆 |

### 8.2 消息格式

**纯文本消息** (无图片):

    HumanMessage(content="西红柿炒鸡蛋怎么做？")

**多模态消息** (带图片):

    HumanMessage(content=[
        {"type": "image_url", "image_url": {"url": "https://..."}},
        {"type": "text", "text": "这些食材能做什么？"}
    ])

---

## 9. AI Agent 工作流

    用户输入 (文字/图片)
            │
            ▼
       是否有图片?
      ╱          ╲
    是              否
    │                │
    ▼                ▼
    封装多模态消息    封装纯文本消息
    (image_url+text)
    │                │
    └───────┬────────┘
            ▼
    Agent 接收消息
            │
            ▼
    qwen3.8-flash 模型处理
            │
            ▼
       需要搜索?
      ╱          ╲
    是              否
    │                │
    ▼                │
    调用 TavilySearch │
    搜索食谱         │
    │                │
    ▼                │
    模型整合搜索结果  │
    │                │
    └───────┬────────┘
            ▼
    流式输出 (SSE) ──→ 前端实时渲染
            │
            ▼
    SQLite Checkpoint 保存状态

### 流式处理细节

1. Agent 以 `stream_mode="messages"` 模式流式输出
2. 仅处理 `AIMessageChunk` 类型的消息块
3. 内容安全检测：如果包含 `data_inspection_failed`，跳过该片段
4. 异常处理：区分内容审核失败和其他错误，给出不同提示

---

## 10. 数据库设计

### 10.1 SQLite 数据库

- **文件路径**: `db/personal_chif.db`
- **用途**: LangGraph Checkpoint 持久化存储
- **核心表**: `checkpoints`（由 `SqliteSaver.setup()` 自动创建）

### 10.2 Checkpoint 机制

| 概念 | 说明 |
|------|------|
| `thread_id` | 会话线程标识，每个对话独立 |
| `checkpoint` | 对话状态快照，包含完整消息历史 |
| `channel_values` | Checkpoint 中的消息通道，存储 `messages` 列表 |

### 10.3 数据库连接配置

    connection = sqlite3.connect(
        os.path.join(DB_DIR, "personal_chif.db"),
        check_same_thread=False  # 允许多线程并发访问
    )

> ⚠️ **注意**: `check_same_thread=False` 在开发环境可用，生产环境建议改用 PostgreSQL。

---

## 11. 前端部署

### 11.1 前端技术栈

- **框架**: Next.js（静态导出模式）
- **部署方式**: 构建产物直接由 FastAPI 静态文件服务托管

### 11.2 静态资源结构

    app/static/
    ├── index.html          # SPA 入口文件
    ├── _next/              # Next.js 编译产物
    │   └── static/
    │       ├── chunks/     # JS/CSS 代码分割块
    │       └── media/      # 字体、图标等媒体文件
    ├── 404/                # 404 页面
    ├── favicon.ico         # 网站图标
    └── *.svg               # 图标资源

### 11.3 SPA 路由支持

FastAPI 配置了 fallback 路由，所有非 `/api/` 开头的请求都会返回 `index.html`，确保前端路由正常工作。

---

## 12. 构建与启动

### 12.1 安装依赖

    # 使用 uv 安装所有依赖
    uv sync

    # 或使用 pip
    pip install -e .

### 12.2 启动服务

    # 方式一：通过 app 包启动（推荐）
    python -m app.main

    # 方式二：通过根目录 main.py 启动
    python main.py

    # 方式三：直接使用 uvicorn
    uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

### 12.3 服务信息

| 配置项 | 值 |
|--------|-----|
| **Host** | `127.0.0.1` |
| **Port** | `8001` |
| **热重载** | 已启用 (`reload=True`) |
| **API 文档** | `http://127.0.0.1:8001/docs` (Swagger UI) |
| **前端页面** | `http://127.0.0.1:8001/` |

### 12.4 运行测试

    # 模型连通性测试
    python test_model.py

    # Agent 功能测试
    python test_model2.py

---

## 13. 已知问题与注意事项

### 13.1 安全相关

| 问题 | 说明 | 建议 |
|------|------|------|
| CORS 全开放 | `allow_origins=["*"]` | 生产环境限制为具体域名 |
| `.env` 敏感信息 | API Key 明文存储 | 确保 `.env` 已加入 `.gitignore` |
| SQLite 并发 | `check_same_thread=False` | 生产环境建议改用 PostgreSQL |

### 13.2 内容审核

- DashScope 平台有内容安全审核机制
- 当返回内容包含 `data_inspection_failed` 时，系统会自动跳过并提示用户
- 建议用户开启新对话或更换图片/描述重试

### 13.3 多模态消息格式

- 图片消息必须使用 `image_url` 类型（非 `image`）
- 格式示例: `{"type": "image_url", "image_url": {"url": "..."}}`

### 13.4 数据库路径

- 使用绝对路径构造数据库文件路径，避免相对路径在不同工作目录下的问题
- 数据库目录 `db/` 不存在时会自动创建

### 13.5 OSS 私有 Bucket

- Bucket 为私有权限，外部无法直接访问
- 通过预签名 URL 实现安全的临时上传/访问
- 上传 URL 有效期 1 小时，访问 URL 有效期 24 小时

---

## 附录 A: 依赖清单

| 包名 | 版本 | 用途 |
|------|------|------|
| `fastapi` | >= 0.141.1 | Web 框架 |
| `uvicorn` | >= 0.52.4 | ASGI 服务器 |
| `langchain` | >= 1.4.0 | AI 应用框架 |
| `langchain-deepseek` | >= 1.1.0 | DeepSeek 模型集成 |
| `langchain-tavily` | >= 0.2.18 | Tavily 搜索工具 |
| `langgraph-checkpoint-sqlite` | >= 3.1.1 | SQLite Checkpoint |
| `alibabacloud-oss-v2` | >= 1.4.0 | 阿里云 OSS SDK |
| `dotenv` | >= 0.9.9 | 环境变量管理 |
| `checkpointer` | >= 2.14.12 | Checkpoint 支持 |
| `logger` | >= 1.4 | 日志工具 |
| `notebook` | >= 7.6.2 | Jupyter Notebook（开发调试） |
| `myapplication` | >= 0.1.0 | 应用依赖 |

---

## 附录 B: 端口与网络

| 服务 | 端口 | 说明 |
|------|------|------|
| FastAPI 主服务 | 8001 | 后端 API + 前端静态资源 |
| Swagger UI | 8001/docs | 自动生成的 API 文档 |
| ReDoc | 8001/redoc | 另一种 API 文档视图 |

---

## 附录 C: Git 配置

- **远程仓库**: `origin` - https://github.com/lww863712-cyber/Private_Chef_AI.git
- **默认分支**: `master`
- **忽略规则**: `.venv/`, `__pycache__/`, `.env`, `*.db` 等
