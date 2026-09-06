import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model

model = init_chat_model(model="deepseek-chat")

print(type(model))
#model.invoke阻塞输出，model.stream流式输出
#response = model.invoke("你是谁？")
#print(response)
stream = model.stream("你是谁？")
print(stream)
for chunk in stream:
    print(chunk.content,end="",flush=True)