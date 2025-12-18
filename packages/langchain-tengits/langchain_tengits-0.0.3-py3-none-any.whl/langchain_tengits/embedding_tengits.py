
import inspect
import random
from typing import Dict, Optional

import httpx
from httpx import Client
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from loguru import logger
from openai.resources.embeddings import Embeddings as OpenAI_Embeddings
from pydantic import Field, BaseModel

from langchain_tengits.shcema import LLMServerType


def _get_params(params: dict, server_config: dict, model_config: dict, model_keys: list[str]) -> dict:

    if server_config.get('openai_proxy'):
        params['openai_proxy'] = server_config.get('openai_proxy')

    filtered = {
        "model_kwargs": {},
        'model': params['model'],
        'base_url': params['base_url'].rstrip('/')
    }
    if model_keys:
        # 从keys中随机取一个key
        filtered['api_key'] = model_keys[random.randint(0, len(model_keys) - 1)]

    if not filtered['model']:
        raise Exception('openai model is empty')
    if not filtered['api_key']:
        raise Exception('openai api_key is empty')
    if not filtered['base_url']:
        raise Exception('openai base_url is empty')

    sig = inspect.signature(OpenAI_Embeddings.create)
    chat_valid_fields = list(sig.parameters.keys())  # set(ChatOpenAI.model_fields.keys())
    instance_valid_fields = set(OpenAIEmbeddings.model_fields.keys())
    for k in instance_valid_fields:
        # 查找映射或直接匹配
        v = params.get(k)
        if v is not None:
            filtered[k] = v
    for mk in filtered['model_kwargs']:
        if mk not in chat_valid_fields:
            filtered['model_kwargs'].pop(mk, None)

    return filtered


llm_embedding_node_type: Dict = {

    # 官方API服务
    LLMServerType.OPENAI.value: OpenAIEmbeddings

}


class TengitsEmbeddingClient(BaseModel,Embeddings):
    model_config = {"arbitrary_types_allowed": True}
    """
        Use the llm model that has been launched in model management
    """
    base_url: Optional[str] = Field(..., description="后端服务地址")
    model_name: Optional[str] = Field(..., description="模型名称")
    server_name: Optional[str] = Field(..., description="模型服务商名称")
    client_timout: Optional[float] = Field(default=30,description="请求超时时间")
    client: Client = Field(default=None, exclude=True)

    model_id: Optional[int] = Field(default=0, exclude=True)




    def __init__(self ,**kwargs):
        logger.debug(f"init tengits embedding llm, kwargs={kwargs}")
        super().__init__(**kwargs)
        self.client = httpx.Client(base_url=self.base_url,timeout=self.client_timout)




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


    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """embedding"""

        self.init_model_id()
        logger.debug(f"embedding,model_id={self.model_id}, texts={texts}")
        res = self.client.post(f"/model-server/llm/embedding",json={
            "modelId": self.model_id,
            "texts": texts}
        )
        res.raise_for_status()
        res = res.json()
        if res.get('status') != 0:
            raise Exception(f'嵌入向量失败:res={res}')

        data = res.get("data")
        return data

    def embed_query(self, text: str) -> list[float]:
        """embedding"""
        logger.debug(f"embed_query,model_id={self.model_id}, text={text}")
        return self.embed_documents([text])[0]


