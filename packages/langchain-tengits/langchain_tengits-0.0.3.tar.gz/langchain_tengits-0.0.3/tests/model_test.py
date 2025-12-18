from loguru import logger

from langchain_tengits.tengits_chat_model import TengitsChatModel

bailian = {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "sk-72e7da265ca346768c6c2b2340b3fe77",
    "model": "qwen-plus"
}
siliconflow = {
    "base_url": "https://api.siliconflow.cn/v1",
    "api_key": "sk-rpsiafjegvsukzghqwkisycrfcctkbnlrjfyunlfnsjnwbyw",
    "model": "inclusionAI/Ling-mini-2.0"
}
deepseek = {
    "base_url": "https://api.deepseek.com",
    "api_key": "sk-7e51c0a69e6b4c0a8b31eaead67129ff",
    "model": "deepseek-reasoner"
}
baidu_qifan = {
    "base_url": "https://qianfan.baidubce.com/v2",
    "api_key": "bce-v3/ALTAK-YLnEPvQfcvQWimcJYT5td/60ef80fedb56ae7dcd75067b3fd628ee9fa6357f",
    "model": "qwen3-8b"
}
moonshot={
    "base_url": "https://api.moonshot.cn/v1",
    "api_key": "sk-5MZQ0ovsDUFP5gqKqAXhiVQYFZlOq6RxSOGm9JOg5Nmmcrfv",
    "model": "kimi-k2-0905-preview"
}
zhipu={
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "api_key": "0d3c073dd58946cdbc8b56514f5f1792.t8ex8yNwF1ZJxfhn",
    "model": "glm-4.5-air"
}
volcengine={
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "api_key": "704e603d-1ae7-46a4-8ee9-d1ed0ce69897",
    "model": "doubao-seed-1-6-lite-251015"
}

# def test():
#     platform_list = [bailian]
#     for platform in platform_list:
#         llm = TengitsChatModel(server_type = "tengits",**platform)
#         res = llm.invoke(input=[{"role": "user", "content": "你好"}])
#         logger.debug(f"model={platform.get('model')},res = {res}")


def test_2():
    llm = TengitsChatModel.get_instance(
        server_name="bailian",
        model_name="qwen-plus",
        host="http://192.168.2.181:31001",
        extra_body = {
            "enable_thinking":True
        }
    )
    res = llm.invoke(input=[{"role": "user", "content": "你好"}])
    logger.debug(f"invoke res = {res}")
    for item in llm.stream([{"role": "user", "content": "你好"}]):
        logger.debug(item)

test_2()