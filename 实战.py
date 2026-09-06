import os
import sqlite3

from app.common.logger import logger
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite import SqliteSaver


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")
os.makedirs(DB_DIR, exist_ok=True)

#web搜索工具，使用Tavily作为web搜索工具
web_search = TavilySearch(
    max_results=5,
    topics = "general",
)

#多模态模型
model = init_chat_model(
    model="qwen3.8-flash",
    model_provider = "openai",
    base_url = os.getenv("DASHSCOPE_BASE_URL"),
    api_key = os.getenv("DASHSCOPE_API_KEY")
)

#check_same_thread=False：允许多个线程同时访问数据库
connection = sqlite3.connect(os.path.join(DB_DIR, "personal_chif.db"),check_same_thread=False)
#初始化checkpoint保存器
checkpoint = SqliteSaver(connection)
#创建checkpoint表(自动建表）
checkpoint.setup()


#Agent提示词
system_prompt = """你是一名私人厨师。收到用户提供的食材照片或清单后，请按以下流程操作：
1. 识别和评估食材：若用户提供照片，首先辨识所有可见食材。基于食材的外观状态、评估其新鲜度与可用量，整理出一份"当前可用食材清单"。
2. 智能食谱检索：优先调用 web_search 工具，以"可用食材清单"为核心关键词，查找可行菜谱。
3. 多维度评估与排序：从营养价值和制作难度两个维度对检索到的候选食谱进行量化打分，并根据得分排序，制作简单且营养丰富的排名菜单。
4. 结构化方案输出：把排序后的食谱整理为一份结构清晰的建议报告，要包含食谱信息、得分、推荐理由、食谱的参考图片，帮助用户快速做出决策。
请严格按照流程，优先调用 web_search 工具搜索食谱，搜索不到的情况下才能自己发挥。"""
#创建智能体
agent = create_agent(
    model=model,                    #模型
    tools=[web_search],             #工具
    system_prompt=system_prompt,    #系统提示
    checkpointer=checkpoint         #记忆
)

# 流式对话
async def search_recipes(prompt: str, image: str, thread_id: str):
    """调用agent搜索食谱"""
    logger.info(f"[用户]: {prompt}, image: {image}, thread_id: {thread_id}")
    try:
        # 判断是否有图片，封装不同格式的消息
        if not image or image.strip() == "":
            message = HumanMessage(content=prompt)
        else:
            message = HumanMessage(content=[
                {"type": "image_url", "image_url": {"url": image}},
                {"type": "text", "text": prompt}
            ])

        # 流式调用Agent
        for chunk, metadata in agent.stream(
            {"messages": [message]},
            {"configurable": {"thread_id": thread_id}},
            stream_mode="messages"
        ):
            if isinstance(chunk, AIMessageChunk):
                content = chunk.content
                if not content:
                    continue
                if isinstance(content, str) and "data_inspection_failed" in content:
                    logger.warning("内容安全审核被触发，跳过该片段")
                    continue
                yield content

    except Exception as e:
        error_msg = str(e)
        logger.error(f"\n[错误]: {error_msg}")
        if "data_inspection_failed" in error_msg:
            yield "\n\n⚠️ 抱歉，平台内容审核未通过。建议：\n1. 开启一个新对话\n2. 更换食材描述或图片重试"
        else:
            yield "信息检索失败，试试看手动输入食物列表？"

# 清空会话
def clear_messages(thread_id: str):
    """清空会话"""
    logger.info(f"清空历史消息，thread_id: {thread_id}")
    connection.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
    connection.commit()

# 查询会话历史
def get_messages(thread_id: str) -> list[dict[str, str]]:
    """获取会话历史"""
    logger.info(f"获取历史消息，thread_id: {thread_id}")

    # 根据 thread_id 查询 checkpoint
    checkpoint_data = checkpoint.get({"configurable": {"thread_id": thread_id}})

    # 如果不存在，返回空列表
    if not checkpoint_data:
        return []

    # 安全获取 messages
    channel_values = checkpoint_data.get("channel_values")
    if not channel_values:
        return []

    messages = channel_values.get("messages", [])
    if not messages:
        return []

    # 转换消息格式
    result = []
    for msg in messages:
        if not msg.content:
            continue

        if isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": msg.content})

    return result