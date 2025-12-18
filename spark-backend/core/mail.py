"""
邮件发送模块
"""
from fastapi_mail import FastMail, ConnectionConfig
from pydantic import SecretStr

from .config import AppConfig


def create_mail_instance(config: AppConfig) -> FastMail:
    """
    创建 FastMail 实例（每次调用返回新实例，线程/协程安全）
    
    Args:
        config: 应用配置对象
    
    Returns:
        FastMail实例
    """
    mail_config = ConnectionConfig(
        MAIL_USERNAME=config.mail_username,
        MAIL_PASSWORD=SecretStr(config.mail_password),
        MAIL_FROM=config.mail_from,
        MAIL_PORT=config.mail_port,
        MAIL_SERVER=config.mail_server,
        MAIL_FROM_NAME=config.mail_from_name,
        MAIL_STARTTLS=config.mail_starttls,
        MAIL_SSL_TLS=config.mail_ssl_tls,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return FastMail(mail_config)

