"""Configuration - 系统配置管理

This module implements the Settings class for system configuration using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """系统配置类 - 管理 Stratos 系统的所有配置"""

    # Application
    APP_NAME: str = "Stratos API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str
    REDIS_POOL_SIZE: int = 10

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # AI Services
    CLAUDE_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20240620"
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # DeepAgent 配置
    DEEPAGENT_API_URL: str
    DEEPAGENT_API_KEY: str

    # GitHub
    GITHUB_APP_ID: str
    GITHUB_PRIVATE_KEY: str
    GITHUB_WEBHOOK_SECRET: str

    # 飞书配置
    LARK_APP_ID: str
    LARK_APP_SECRET: str
    LARK_ENCRYPT_KEY: str = ""
    LARK_VERIFICATION_TOKEN: str = ""

    @classmethod
    @lru_cache
    def get(cls):
        """获取单例配置实例"""
        return cls()


settings = Settings()
