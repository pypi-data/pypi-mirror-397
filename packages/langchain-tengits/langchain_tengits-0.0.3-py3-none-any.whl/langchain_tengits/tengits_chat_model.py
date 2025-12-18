import random

import httpx
import openai
from langchain_core.messages import AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_openai.chat_models.base import BaseChatOpenAI
from loguru import logger
from pydantic import Field

from langchain_tengits.shcema import CompletionCreateParams


class TengitsChatModel(BaseChatOpenAI):
    server_type: str = Field("", description="模型服务商名称",exclude= True)
    @classmethod
    def get_instance(cls,host,
                   model_id=0,
                   server_name="",
                   model_name="",
                   timeout:int =30,
                    **kwargs):
        params = cls.get_params(host, model_id, server_name, model_name,timeout)
        exist_keys = params.keys()
        for k,v in kwargs.items():
            if k in exist_keys:
                continue
            params[k] = v

        logger.debug(f"params={params}")
        return cls(**params)
    @classmethod
    def get_params(cls,
                   host,
                   model_id=None,
                   server_name=None,
                   model_name=None,
                   timeout:int =30
                   ):
        client = httpx.Client(base_url=host,timeout= timeout)
        payload = {
            "modelId":model_id,
            "modelName": model_name,
            "serverName": server_name
        }
        logger.debug(f"payload={payload}")
        res = client.get("/model-server/llm/modelDetail", params=payload)
        res.raise_for_status()
        res = res.json()

        logger.debug(f"get model detail, res={res}")

        if res.get('status') != 0:
            raise Exception('获取模型失败')

        data = res.get("data")
        if not data:
            raise Exception('模型不存在')

        model_config = data.get("config",{})
        model_config = CompletionCreateParams.model_validate(model_config).model_dump(exclude_none= True)

        server_config = data.get("server",{}).get("config",{})
        server_config = CompletionCreateParams.model_validate(server_config).model_dump(
                                                                                        exclude_none=True)
        api_keys = data.get("modelKeys", [])
        logger.debug(f"api_keys: type={type(api_keys)},  value={api_keys}")
        key = random.choice(api_keys)
        merge_keys = {'extra_body', 'model_kwargs'}

        params = {
            'api_key': key,
            'model': data.get("modelName"),
            **{k: v for k, v in server_config.items() if v is not None and k not in merge_keys},
            **{k: v for k, v in model_config.items() if v is not None and k not in merge_keys},
            "server_type": data.get("server",{}).get("serverType"),
            "streaming":True,
            'model_kwargs': {'stream_options': {"include_usage": True}},
        }
        # params.pop("stream",None)
        return params




    def _create_chat_result(
        self,
        response: dict | openai.BaseModel,
        generation_info: dict | None = None,
    ) -> ChatResult:
        """Create a ChatResult from a response."""
        # logger.debug(f"response={response}")
        rtn = super()._create_chat_result(response, generation_info)
        # logger.debug(f"rtn={rtn}")
        if not isinstance(response, openai.BaseModel):
            return rtn

        for generation in rtn.generations:
            if generation.message.response_metadata is None:
                generation.message.response_metadata = {}
            generation.message.response_metadata["model_provider"] = "deepseek"

        choices = getattr(response, "choices", None)
        if choices and hasattr(choices[0].message, "reasoning_content"):
            rtn.generations[0].message.additional_kwargs["reasoning_content"] = choices[
                0
            ].message.reasoning_content
        # Handle use via OpenRouter
        elif choices and hasattr(choices[0].message, "model_extra"):
            model_extra = choices[0].message.model_extra
            if isinstance(model_extra, dict) and (
                reasoning := model_extra.get("reasoning")
            ):
                rtn.generations[0].message.additional_kwargs["reasoning_content"] = (
                    reasoning
                )

        return rtn

    def _convert_chunk_to_generation_chunk(
        self,
        chunk: dict,
        default_chunk_class: type,
        base_generation_info: dict | None,
    ) -> ChatGenerationChunk | None:
        # logger.debug(f"server_type={self.server_type},chunk={chunk}")
        generation_chunk = super()._convert_chunk_to_generation_chunk(
            chunk,
            default_chunk_class,
            base_generation_info,
        )
        if (choices := chunk.get("choices")) and generation_chunk:
            top = choices[0]
            if isinstance(generation_chunk.message, AIMessageChunk):
                generation_chunk.message.response_metadata = {
                    **generation_chunk.message.response_metadata,
                    "model_provider": self.server_type,
                }
                if (
                    reasoning_content := top.get("delta", {}).get("reasoning_content")
                ) is not None:
                    generation_chunk.message.additional_kwargs["reasoning_content"] = (
                        reasoning_content
                    )
                # Handle use via OpenRouter
                elif (reasoning := top.get("delta", {}).get("reasoning")) is not None:
                    generation_chunk.message.additional_kwargs["reasoning_content"] = (
                        reasoning
                    )
        # logger.debug(f"generation_chunk={generation_chunk}")
        return generation_chunk
