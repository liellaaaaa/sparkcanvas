"""
数据库初始化脚本
"""
import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from models import Base
from models.user import User, EmailCode
from models.prompt import Prompt

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 直接读取配置，避免导入 core 模块（避免依赖冲突）
def get_mysql_url():
    """从环境变量或配置文件读取 MySQL URL"""
    # 优先从环境变量读取
    mysql_url = os.getenv("MYSQL_URL")
    if mysql_url:
        return mysql_url
    
    # 从 config.yaml 读取（简化版，不依赖 yaml 库）
    config_file = Path(__file__).parent.parent / "config" / "config.yaml"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 简单解析 mysql.url
            for line in content.split('\n'):
                if 'url:' in line and 'mysql' in line.lower():
                    url = line.split('url:')[1].strip().strip('"').strip("'")
                    return url
    
    # 默认值
    return "mysql+aiomysql://root:1234@127.0.0.1:3306/sparkcanvas?charset=utf8mb4"


async def init_database():
    """初始化数据库表"""
    # 获取数据库连接字符串
    mysql_url = get_mysql_url()
    db_info = mysql_url.split('@')[1] if '@' in mysql_url else mysql_url
    print(f"[INFO] 使用数据库: {db_info}")
    
    # 创建引擎
    engine = create_async_engine(
        mysql_url,
        echo=True,
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        # 删除所有表（开发环境用，需要时取消注释）
        # await conn.run_sync(Base.metadata.drop_all)
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("[SUCCESS] 数据库表创建成功！")


if __name__ == "__main__":
    asyncio.run(init_database())

