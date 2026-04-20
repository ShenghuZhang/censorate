from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    APP_NAME: str = "Censorate API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    ALLOWED_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,0.0.0.0"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Database
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:15432/aip_mvp"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_POOL_SIZE: int = 10

    # JWT
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # AI Services
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20240620"
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # DeepSeek
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # DeepAgent Configuration
    DEEPAGENT_API_URL: str = "http://localhost:8001"
    DEEPAGENT_API_KEY: str = ""

    # GitHub
    GITHUB_APP_ID: str = ""
    GITHUB_PRIVATE_KEY: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    # Lark (Feishu) Configuration
    LARK_APP_ID: str = ""
    LARK_APP_SECRET: str = ""
    LARK_ENCRYPT_KEY: str = ""
    LARK_VERIFICATION_TOKEN: str = ""

    # Skills directory
    SKILLS_DIR: str = "app/skills"
    SKILL_STORAGE_DIR: str = "app/storage/skills"

    # Skill upload limits
    MAX_FILE_SIZE: int = 1024 * 1024  # 1MB per file
    MAX_TOTAL_SIZE: int = 10 * 1024 * 1024  # 10MB total
    ALLOWED_EXTENSIONS: list = [".md", ".json", ".yaml", ".yml", ".txt", ".py", ".zip"]

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

    @classmethod
    @lru_cache()
    def get(cls):
        """Get cached settings instance."""
        return cls()
