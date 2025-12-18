from enum import Enum
from typing import Optional, List, Dict, Literal, Any
from datetime import datetime
from pydantic import BaseModel, Field


# class LLMServer(BaseModel):
#     """
#     服务基础信息
#     """
#     id: int = Field(description='服务 ID')
#     name: str = Field(default='', description='服务名称')
#     description: Optional[str] = Field(default='', description='服务描述')
#     server_type: str = Field(description='服务提供方类型')  # 必填字段
#     config: Optional[Dict[str, any]] = Field(default=None, description='服务提供方公共配置')
#     user_id: int = Field(default=0, description='创建人ID')
#
#     model_config = {"arbitrary_types_allowed": True}
#
# class LLMModel(BaseModel):
#     """
#     模型基础信息
#     """
#     id: int = Field(description='模型 ID')
#     server_id: int = Field(description='服务ID')  # 可设为 Optional[int] 如果允许为空
#     name: str = Field(default='', description='模型展示名')
#     description: Optional[str] = Field(default='', description='模型描述')
#     model_name: str = Field(description='模型名称，实例化组件时用的参数')
#     model_type: Literal["llm", "embedding", "rerank"] = Field(description='模型类型: llm, embedding, rerank')
#     model_category: Optional[List[str]] = Field(default=None, description='模型分类: 视觉,自然语言处理,语音,其他')
#     model_keys: Optional[List[str]] = Field(default=None, description='模型密钥列表')
#     config: Optional[Dict[str, any]] = Field(default_factory=dict, description='模型配置')
#     status: int = Field(default=0, description='模型状态：0=未知，1=正常，2=异常')
#     remark: Optional[str] = Field(default='', description='异常原因')
#     online: int = Field(default=0, description='是否在线：0=初始化，1=在线，2=下线')
#     user_id: int = Field(default=0, description='创建人ID')
#
#     model_config = {"arbitrary_types_allowed": True}
class LLMServerType(Enum):
    OPENAI = 'openai'
    ALI_BAILIAN = 'ali_bailian'
    DEEPSEEK = 'deepseek'
    SILICONFLOW = 'siliconflow'
    BAIDU_QIANFAN='baidu_qianfan'
    MOONSHOT =  'moonshot'
    ZHIPU = 'zhipu'
    OLLAMA = 'ollama'
    VOLCENGINE = 'volcengine'


class LLMModelType(Enum):
    LLM = 'llm'
    EMBEDDING = 'embedding'
    RERANK = 'rerank'


class CompletionCreateParams(BaseModel):
    """
    大语言模型对话补全请求参数模型
    """
    model_config = {
        # "extra": "allow",  # 允许未声明字段，便于未来扩展
        "populate_by_name": True,
    }

    # 可选参数：是否启用流式响应
    streaming: Optional[bool] = Field(
        default=True,
        description='是否启用流式响应'
    )

    # 可选参数：采样温度，控制生成结果的随机性
    temperature: Optional[float] = Field(
        default=None,
        description='采样温度，范围0到2'
    )


    # 可选参数：额外HTTP头
    extra_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description='额外HTTP头',
        alias="extraHeaders"
    )

    # 可选参数：额外请求体参数
    extra_body: Optional[Dict[str, Any]] = Field(
        default=None,
        description='额外请求体参数',
        alias="extraBody"
    )

    # 可选参数：请求超时时间
    timeout: Optional[float] = Field(
        default=None,
        description='请求超时时间（秒）'
    )
    base_url: Optional[str] = Field(
        default=None,
        description='请求URL',
        alias="baseUrl"
    )

class AIUsage(BaseModel):
    """
    大语言模型对话使用情况
    """
    input: int = Field(default=0,description='输入字符数')
    output: int = Field(default=0,description='输出字符数')
    total: int = Field(default=0,description='总字符数')

class AIResult(BaseModel):
    """
    大语言模型对话结果
    """
    content: str = Field(default="",description='对话结果')
    reasoning_content: str = Field(default="",description='推理结果')
    usage: Optional[Dict[str, int]] = Field(default=None,description='使用情况')
    finish_reason: str = Field(default="",description='完成原因')
