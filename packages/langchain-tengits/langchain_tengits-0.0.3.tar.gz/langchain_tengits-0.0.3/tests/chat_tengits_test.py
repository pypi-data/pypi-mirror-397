import asyncio

from langchain_tengits.chat_tengits import TengitsChatClient

model = TengitsChatClient(
    server_name='bailian',
    model_name='qwen-plus',
    # modelId = 7,
    base_url="http://192.168.2.181:31001",
    config={
        "stream": True,
        "extra_body":{"enable_thinking": True}
    },
    client_timeout=30.0

)

def test_invoke():
    res = model.invoke([
        {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你是谁？"}
    ])
    print("invoke",res)
def test_stream():
    for item in model.stream([
        {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你是谁？"}
    ]
    ):
        print("stream",item)

    model.config['extra_body'] = {"enable_thinking": False}
    for item in model.stream([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"}
    ]
    ):
        print("stream with thinking", item)
async def run():
     async for item in model.astream([
        {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你是谁？"}
    ]
    ):
        print(item)
asyncio.run(run())

# test_invoke()
# test_stream()
