import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

load_dotenv()

model = init_chat_model(
    model="qwen3.8-flash",
    model_provider="openai",
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    api_key=os.getenv("DASHSCOPE_API_KEY")
)

web_search = TavilySearch(max_results=5, topics="general")

system_prompt = """你是一名私人厨师。收到用户提供的食材照片或清单后，请按以下流程操作：
1. 识别和评估食材：若用户提供照片，首先辨识所有可见食材。
2. 智能食谱检索：优先调用 web_search 工具，以"可用食材清单"为核心关键词，查找可行菜谱。
3. 多维度评估与排序：从营养价值和制作难度两个维度对检索到的候选食谱进行量化打分。
4. 结构化方案输出：把排序后的食谱整理为一份结构清晰的建议报告。
请严格按照流程，优先调用 web_search 工具搜索食谱，搜索不到的情况下才能自己发挥。"""

print("=== 测试4: create_agent 无 checkpointer ===")
try:
    agent = create_agent(
        model=model,
        tools=[web_search],
        system_prompt=system_prompt,
    )
    result = agent.invoke({"messages": [HumanMessage(content="西红柿，鸡蛋")]})
    last_msg = result["messages"][-1]
    print(f"成功: {last_msg.content[:100] if last_msg.content else 'no content'}")
except Exception as e:
    print(f"失败: {e}")

print("\n=== 测试5: create_agent + stream ===")
try:
    agent2 = create_agent(
        model=model,
        tools=[web_search],
        system_prompt=system_prompt,
    )
    for chunk, metadata in agent2.stream(
        {"messages": [HumanMessage(content="西红柿，鸡蛋")]},
        stream_mode="messages"
    ):
        if hasattr(chunk, 'content') and chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n成功!")
except Exception as e:
    print(f"\n失败: {e}")