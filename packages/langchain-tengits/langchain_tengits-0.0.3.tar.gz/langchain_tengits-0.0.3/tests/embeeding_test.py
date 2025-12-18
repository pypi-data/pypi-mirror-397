import asyncio

from langchain_tengits.embedding_tengits import TengitsEmbeddingClient
from openai import base_url
from langchain_tengits.chat_tengits import  TengitsChatClient

model = TengitsEmbeddingClient(
    model_name='text-embedding-v4',
    server_name='bailian',
    base_url="http://192.168.2.181:31001"
)
# print(model.embed_query('hello world'))
def test():
    list = model.embed_documents(['hello world', 'hello world'])
    for item in list:
        print(item)

