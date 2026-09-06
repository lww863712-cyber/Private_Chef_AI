import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite import SqliteSaver
from hellword import model


model = init_chat_model(
    model="qwen3.8-flash",
    model_provider = "openai",
    base_url = os.getenv("DASHSCOPE_BASE_URL"),
    api_key = os.getenv("DASHSCOPE_API_KEY")
)
#web搜索工具，使用Tavily作为web搜索工具

web_search = TavilySearch(
    max_results=5,
    topics = "general",
)

#check_same_thread=False：允许多个线程同时访问数据库
connection = sqlite3.connect("resources/personal_chif.db",check_same_thread=False)




checkpoint = SqliteSaver(connection)
checkpoint.setup()

from langchain.agents import create_agent

system_prompt = """你是一名私人厨师。收到用户提供的食材照片或清单后，请按以下流程操作：
1. 识别和评估食材：若用户提供照片，首先辨识所有可见食材。基于食材的外观状态、评估其新鲜度与可用量，整理出一份“当前可用食材清单”。
2. 智能食谱检索：优先调用 web_search 工具，以“可用食材清单”为核心关键词，查找可行菜谱。
3. 多维度评估与排序：从营养价值和制作难度两个维度对检索到的候选食谱进行量化打分，并根据得分排序，制作简单且营养丰富的排名菜单。
4. 结构化方案输出：把排序后的食谱整理为一份结构清晰的建议报告，要包含食谱信息、得分、推荐理由、食谱的参考图片，帮助用户快速做出决策。
请严格按照流程，优先调用 web_search 工具搜索食谱，搜索不到的情况下才能自己发挥。"""

agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=system_prompt,
    checkpoint=checkpointer
)
