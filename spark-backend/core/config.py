from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import os
import yaml
from dotenv import load_dotenv


@dataclass
class AppConfig:
    """应用配置类"""
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    mysql_url: str = ""
    redis_url: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_model_name: str = ""
    openai_embedding_model: str = ""
    # JWT 配置
    jwt_secret_key: str = ""
    jwt_access_token_expires_hours: int = 2
    jwt_refresh_token_expires_days: int = 7
    # 邮件配置
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 587
    mail_server: str = ""
    mail_from_name: str = "SparkCanvas"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    # DALL·E 3 配置
    dalle_api_key: str = ""
    dalle_base_url: str = ""
    # Tavily Search 配置
    tavily_api_key: str = ""
    # Chroma 配置
    chroma_persist_directory: str = "./chroma_db"
    # 阿里云 DashScope 配置
    dashscope_api_key: str = ""
    dashscope_model: str = "qwen-max"
    dashscope_temperature: float = 0.7
    dashscope_embedding_model: str = "text-embedding-v4"


def _merge_dict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """递归合并字典"""
    result = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _merge_dict(result[k], v)
        else:
            result[k] = v
    return result


def load_config(env: str | None = None) -> AppConfig:
    """
    加载配置
    优先级：环境变量 > YAML配置文件 > 默认值
    
    Args:
        env: 环境名称（dev/prod），如果不指定则从 APP_ENV 环境变量读取
    
    Returns:
        AppConfig: 应用配置对象
    """
    # 1) 加载 .env 文件
    # 从 core/config.py 向上两级到 spark-backend，然后进入 config 目录
    env_file = Path(__file__).resolve().parents[1] / "config" / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()

    # 2) 加载 YAML 配置文件
    # 从 core/config.py 向上两级到 spark-backend，然后进入 config 目录
    config_dir = Path(__file__).resolve().parents[1] / "config"
    base_yaml = config_dir / "config.yaml"
    env = env or os.getenv("APP_ENV", "dev")
    env_yaml = config_dir / f"config.{env}.yaml"

    data: Dict[str, Any] = {}
    if base_yaml.exists():
        with base_yaml.open("r", encoding="utf-8") as f:
            data = _merge_dict(data, yaml.safe_load(f) or {})
    else:
        # 如果基础配置文件不存在，尝试从 sparkcanvas/config 目录读取（兼容旧路径）
        fallback_config_dir = Path(__file__).resolve().parents[2] / "config"
        fallback_base_yaml = fallback_config_dir / "config.yaml"
        if fallback_base_yaml.exists():
            with fallback_base_yaml.open("r", encoding="utf-8") as f:
                data = _merge_dict(data, yaml.safe_load(f) or {})
    
    if env_yaml.exists():
        with env_yaml.open("r", encoding="utf-8") as f:
            data = _merge_dict(data, yaml.safe_load(f) or {})
    else:
        # 如果环境配置文件不存在，尝试从 sparkcanvas/config 目录读取（兼容旧路径）
        fallback_config_dir = Path(__file__).resolve().parents[2] / "config"
        fallback_env_yaml = fallback_config_dir / f"config.{env}.yaml"
        if fallback_env_yaml.exists():
            with fallback_env_yaml.open("r", encoding="utf-8") as f:
                data = _merge_dict(data, yaml.safe_load(f) or {})

    # 3) 环境变量覆盖（优先级最高）
    cfg = AppConfig(
        app_host=os.getenv("APP_HOST", data.get("app", {}).get("host", "0.0.0.0")),
        app_port=int(os.getenv("APP_PORT", data.get("app", {}).get("port", 8000))),
        mysql_url=os.getenv("MYSQL_URL", data.get("mysql", {}).get("url", "")),
        redis_url=os.getenv("REDIS_URL", data.get("redis", {}).get("url", "")),
        openai_api_key=os.getenv("OPENAI_API_KEY", data.get("openai", {}).get("api_key", "")),
        openai_base_url=os.getenv("OPENAI_BASE_URL", data.get("openai", {}).get("base_url", "")),
        openai_model_name=os.getenv("OPENAI_MODEL_NAME", data.get("openai", {}).get("model", "")),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", data.get("openai", {}).get("embedding_model", "")),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", data.get("jwt", {}).get("secret_key", "")),
        jwt_access_token_expires_hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", data.get("jwt", {}).get("access_token_expires_hours", 2))),
        jwt_refresh_token_expires_days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", data.get("jwt", {}).get("refresh_token_expires_days", 7))),
        mail_username=os.getenv("MAIL_USERNAME", data.get("mail", {}).get("username", "")),
        mail_password=os.getenv("MAIL_PASSWORD", data.get("mail", {}).get("password", "")),
        mail_from=os.getenv("MAIL_FROM", data.get("mail", {}).get("from", "")),
        mail_port=int(os.getenv("MAIL_PORT", data.get("mail", {}).get("port", 587))),
        mail_server=os.getenv("MAIL_SERVER", data.get("mail", {}).get("server", "")),
        mail_from_name=os.getenv("MAIL_FROM_NAME", data.get("mail", {}).get("from_name", "SparkCanvas")),
        mail_starttls=os.getenv("MAIL_STARTTLS", str(data.get("mail", {}).get("starttls", True))).lower() == "true",
        mail_ssl_tls=os.getenv("MAIL_SSL_TLS", str(data.get("mail", {}).get("ssl_tls", False))).lower() == "true",
        dalle_api_key=os.getenv("DALLE_API_KEY", data.get("dalle", {}).get("api_key", "")),
        dalle_base_url=os.getenv("DALLE_BASE_URL", data.get("dalle", {}).get("base_url", "")),
        tavily_api_key=os.getenv("TAVILY_API_KEY", data.get("tavily", {}).get("api_key", "")),
        chroma_persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", data.get("chroma", {}).get("persist_directory", "./chroma_db")),
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", data.get("dashscope", {}).get("api_key", "")),
        dashscope_model=os.getenv("DASHSCOPE_MODEL", data.get("dashscope", {}).get("model", "qwen-max")),
        dashscope_temperature=float(os.getenv("DASHSCOPE_TEMPERATURE", data.get("dashscope", {}).get("temperature", 0.7))),
        dashscope_embedding_model=os.getenv("DASHSCOPE_EMBEDDING_MODEL", data.get("dashscope", {}).get("embedding_model", "text-embedding-v4")),
    )
    return cfg


def mask_secret(value: str) -> str:
    """
    脱敏处理敏感信息
    
    Args:
        value: 原始值
    
    Returns:
        脱敏后的值
    """
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return value[:4] + "****" + value[-4:]


def validate_config(cfg: AppConfig) -> Dict[str, Any]:
    """
    验证配置，返回各配置项的校验结果与告警信息
    仅日志提醒，不中断启动
    
    Args:
        cfg: 应用配置对象
    
    Returns:
        警告信息字典
    """
    warnings: Dict[str, Any] = {}
    if not cfg.mysql_url:
        warnings["mysql_url"] = "未配置，数据库相关功能可能不可用"
    if not cfg.redis_url:
        warnings["redis_url"] = "未配置，会话与限流将不可用"
    if not cfg.openai_api_key or not cfg.openai_base_url:
        warnings["openai"] = "未配置，LLM对话将返回降级提示"
    if not cfg.jwt_secret_key:
        warnings["jwt"] = "未配置JWT密钥，认证功能将不可用"
    if not cfg.mail_username or not cfg.mail_password:
        warnings["mail"] = "未配置邮件服务，验证码发送将不可用"
    if not cfg.dashscope_api_key:
        warnings["dashscope"] = "未配置DashScope API Key，RAG知识库功能将不可用"
    if not cfg.dashscope_embedding_model:
        warnings["dashscope_embedding"] = "未配置DashScope Embedding模型，RAG知识库功能将不可用"
    if not cfg.dalle_api_key:
        warnings["dalle"] = "未配置DALL·E API，配图生成将不可用"
    if not cfg.tavily_api_key:
        warnings["tavily"] = "未配置Tavily API，联网检索将不可用"
    return warnings

