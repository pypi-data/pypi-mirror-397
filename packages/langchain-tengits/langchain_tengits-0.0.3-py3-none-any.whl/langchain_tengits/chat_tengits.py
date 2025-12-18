import json
from typing import Optional, Dict, AsyncIterator, Iterator

import httpx
from httpx import Client
from langchain_core.messages import AIMessageChunk, AIMessage
from loguru import logger
from pydantic import Field, BaseModel

from langchain_tengits.shcema import AIResult


class TengitsChatClient(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    """
        Use the llm model that has been launched in model management
    """
    base_url: Optional[str] = Field(..., description="后端服务地址")
    model_id: Optional[int] = Field(default=None, description="模型id")
    model_name: Optional[str] = Field("", description="模型名称")
    server_name: Optional[str] = Field("", description="模型服务商名称")

    config: Optional[Dict[str, any]] = Field(default=None, description='模型配置')

    client: Client = Field(default={}, exclude=True)
    client_timeout: Optional[float] = Field(default=None,description="请求超时时间")



    def __init__(self, **kwargs):
        logger.debug(f"init tengits embedding llm, kwargs={kwargs}")
        super().__init__(**kwargs)
        self.client = httpx.Client(base_url=self.base_url,timeout=self.client_timeout)



    def init_model_id(self):
        if not self.model_id:
            payload = {
                "modelName": self.model_name,
                "serverName": self.server_name
            }
            res = self.client.get("/model-server/llm/modelDetail", params=payload)
            res.raise_for_status()
            res = res.json()

            logger.debug(f"get model detail, res={res}")

            if res.get('status') != 0:
                raise Exception('获取模型失败')

            data = res.get("data")
            self.model_id = data.get("id")
            if not self.model_id:
                raise Exception('模型不存在')

    # async def astream(
    #         self,
    #         input: LanguageModelInput,
    #         config: RunnableConfig | None = None,
    #         *,
    #         stop: list[str] | None = None,
    #         **kwargs: Any,
    # ) -> AsyncIterator[AIMessageChunk]:
    #     self.init_model_id()
    #     payload = {
    #         "model_id": self.model_id,
    #         "messages": input,
    #         "config": self.config
    #     }
    #
    #     logger.debug(f"payload={payload}")
    #     with self.client.stream("POST", "/api/v1/llm/invoke",json=payload) as res:
    #
    #         res.raise_for_status()
    #         if "text/event-stream" not in res.headers.get("content-type", ""):
    #             raise ValueError("Response is not SSE")
    #         # 逐行读取
    #         for line in res.iter_lines():
    #             if line.startswith("data:"):
    #                 data_str = line[len("data:"):].strip()
    #                 if data_str == "[DONE]":  # 常见结束标志（如 OpenAI）
    #                     break
    #                 try:
    #                     info= json.loads(data_str)
    #                     yield AIMessageChunk.model_validate(info)
    #                 except json.JSONDecodeError:
    #                     logger.warning(f"Invalid JSON in SSE: {data_str}")
    #                     continue

    def invoke(self,
        messages: list[dict]
    ) -> AIResult:
        self.init_model_id()
        payload = {
            "modelId": self.model_id,
            "messages": messages,
            "config": self.config
        }
        payload['config']['stream'] = False
        logger.debug(f"_generate payload={payload}")
        res= self.client.post("/model-server/llm/invoke", json=payload)
        res.raise_for_status()
        res = res.json()
        info = res.get("data",{})
        return info

    def stream(
        self,
        messages: list[dict]
    ) -> Iterator[AIResult]:
        self.init_model_id()
        payload = {
            "modelId": self.model_id,
            "messages": messages,
            "config": self.config
        }
        logger.debug(f"payload={payload}")
        with self.client.stream("POST", "/model-server/llm/stream",json=payload) as res:
            res.raise_for_status()
            if "text/event-stream" not in res.headers.get("content-type", ""):
                raise ValueError("Response is not SSE")
            # 逐行读取
            for line in res.iter_lines():
                if line.startswith("data:"):
                    data_str = line[len("data:"):].strip()

                    try:
                        info= json.loads(data_str)
                        yield AIMessageChunk.model_validate(info)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in SSE: {data_str}")
                        continue

    async def astream(
        self,
        messages: list[dict]
    ) -> AsyncIterator[AIResult]:
         for chunk in self.stream(messages):
            yield chunk

    def _llm_type(self) -> str:
        return "tengits"










