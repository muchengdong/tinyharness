# tinyharness/env.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(BaseSettings):
    """
    TinyHarness 统一配置管理中心（基于 Pydantic-Settings）。
    全自动读取本地 .env 文件，并提供严格的类型检查和 IDE 补全。
    """

    llm_model_id: str = Field(default="gpt-4o-mini", description="大模型名称/ID")
    llm_api_key: str = Field(..., description="OpenAI API 密钥（必填）")
    llm_base_url: str | None = Field(default=None, description="大模型网关地址")
    llm_timeout: int = Field(default=60, description="API 请求超时时间（秒）")

    model_config = SettingsConfigDict(
        env_file=".env",  # 指定读取当前目录下的 .env 文件
        env_file_encoding="utf-8",  # 编码格式
        env_prefix="ai_",
        extra="ignore",  # 如果 .env 里有别的变量，不报错直接忽略
        env_nested_delimiter="__",  # 层级分隔符
    )


try:
    # 实例化为一个全局单例，供整个工程所有地方直接导入使用
    env = Environment()
except Exception as e:
    raise RuntimeError("环境配置初始化失败，请检查配置文件或依赖项！") from e
