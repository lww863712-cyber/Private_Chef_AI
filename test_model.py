import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

model = init_chat_model(
    model="qwen3.8-flash",
    model_provider="openai",
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    api_key=os.getenv("DASHSCOPE_API_KEY")
)

print("=== 测试1: 纯文本 ===")
try:
    response = model.invoke([HumanMessage(content="西红柿炒鸡蛋怎么做？")])
    print(f"成功: {response.content[:100]}")
except Exception as e:
    print(f"失败: {e}")

print("\n=== 测试2: 带系统提示词 ===")
try:
    response = model.invoke([
        SystemMessage(content="你是一名私人厨师。"),
        HumanMessage(content="西红柿炒鸡蛋怎么做？")
    ])
    print(f"成功: {response.content[:100]}")
except Exception as e:
    print(f"失败: {e}")

print("\n=== 测试3: 带工具定义 ===")
from langchain_tavily import TavilySearch
web_search = TavilySearch(max_results=5, topics="general")
try:
    model_with_tools = model.bind_tools([web_search])
    response = model_with_tools.invoke([
        SystemMessage(content="你是一名私人厨师。"),
        HumanMessage(content="西红柿炒鸡蛋怎么做？")
    ])
    print(f"成功: {response.content[:100] if response.content else 'tool_call'}")
except Exception as e:
    print(f"失败: {e}")