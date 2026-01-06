# """
# Chroma 向量数据库客户端封装
# """
# from typing import Optional
# from pathlib import Path

# try:
#     from langchain_community.vectorstores import Chroma
#     CHROMA_AVAILABLE = True
# except ImportError:
#     CHROMA_AVAILABLE = False
#     Chroma = None  # type: ignore

# from core.config import AppConfig
# from core.logger import logger
# from services.embedding_service import get_embeddings as get_dashscope_embeddings


# _chroma_client: Optional[Chroma] = None
# _embeddings = None


# def get_chroma_client(config: AppConfig) -> Optional[Chroma]:
#     """
#     获取 Chroma 客户端（单例模式）
    
#     Args:
#         config: 应用配置对象
    
#     Returns:
#         Chroma客户端实例，如果Chroma未安装或配置不完整则返回None
#     """
#     global _chroma_client, _embeddings
    
#     if not CHROMA_AVAILABLE:
#         logger.warning("[Chroma] langchain_community未安装，Chroma功能不可用")
#         return None
    
#     if not config.dashscope_api_key or not config.dashscope_embedding_model:
#         logger.warning(f"[Chroma] DashScope配置不完整: api_key={'已配置' if config.dashscope_api_key else '未配置'}, embedding_model={config.dashscope_embedding_model or '未配置'}")
#         return None
    
#     if _chroma_client is None:
#         try:
#             # 确保目录存在
#             persist_dir = Path(config.chroma_persist_directory)
#             persist_dir.mkdir(parents=True, exist_ok=True)
            
#             # 初始化 DashScope Embeddings
#             _embeddings = get_dashscope_embeddings(config)
#             if _embeddings is None:
#                 logger.error("[Chroma] DashScope Embeddings初始化失败")
#                 return None
            
#             # 初始化 Chroma
#             _chroma_client = Chroma(
#                 persist_directory=str(persist_dir),
#                 embedding_function=_embeddings,
#             )
#             logger.info(f"[Chroma] 客户端初始化成功，持久化目录: {persist_dir}")
#         except Exception as e:
#             logger.error(f"[Chroma] 客户端初始化失败: {e}")
#             import traceback
#             logger.error(f"[Chroma] 初始化异常详情: {traceback.format_exc()}")
#             return None
    
#     return _chroma_client


# def get_embeddings(config: AppConfig):
#     """
#     获取 Embeddings 实例
    
#     Args:
#         config: 应用配置对象
    
#     Returns:
#         DashScopeEmbeddings实例
#     """
#     return get_dashscope_embeddings(config)

"""
Chroma 向量数据库客户端封装
"""
from typing import Optional
from pathlib import Path
import sys

# 在导入chromadb之前，强制替换sqlite3模块
# chromadb在导入时会检查SQLite版本，必须在导入前完成替换
def _replace_sqlite3():
    """替换sqlite3模块为pysqlite3"""
    try:
        # 检查当前SQLite版本
        import sqlite3
        sqlite_version_info = sqlite3.sqlite_version_info
        current_version = sqlite3.sqlite_version
        
        # 如果版本满足要求，不需要替换
        if sqlite_version_info[0] > 3 or (sqlite_version_info[0] == 3 and sqlite_version_info[1] >= 35):
            return True
        
        # 版本过低，尝试替换
        try:
            # 删除现有的sqlite3模块
            if 'sqlite3' in sys.modules:
                del sys.modules['sqlite3']
            if '_sqlite3' in sys.modules:
                del sys.modules['_sqlite3']
            
            # 导入pysqlite3并替换
            import pysqlite3
            # 使用pysqlite3.dbapi2替换sqlite3
            # 这是pysqlite3推荐的替换方式
            import pysqlite3.dbapi2 as sqlite3_new
            sys.modules['sqlite3'] = sqlite3_new
            sys.modules['_sqlite3'] = sqlite3_new
            
            # 验证替换是否成功
            import sqlite3
            new_version = sqlite3.sqlite_version
            new_version_info = sqlite3.sqlite_version_info
            
            if new_version_info[0] > 3 or (new_version_info[0] == 3 and new_version_info[1] >= 35):
                print(f"[Chroma] SQLite版本已替换: {current_version} -> {new_version}")
                return True
            else:
                print(f"[Chroma] 警告: SQLite替换后版本仍不满足要求: {new_version}")
                return False
        except ImportError:
            print("[Chroma] 错误: pysqlite3未安装，无法替换sqlite3模块")
            print("[Chroma] 请运行: pip install pysqlite3-binary")
            return False
    except Exception as e:
        print(f"[Chroma] SQLite替换失败: {e}")
        return False

# 执行替换（在导入Chroma之前）
_replace_sqlite3()

try:
    from langchain_community.vectorstores import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    Chroma = None  # type: ignore

from core.config import AppConfig
from core.logger import logger
from services.embedding_service import get_embeddings as get_dashscope_embeddings


_chroma_client: Optional[Chroma] = None
_embeddings = None
_init_error: Optional[str] = None  # 记录初始化失败的原因


def get_chroma_client(config: AppConfig) -> Optional[Chroma]:
    """
    获取 Chroma 客户端（单例模式）
    
    Args:
        config: 应用配置对象
    
    Returns:
        Chroma客户端实例，如果Chroma未安装或配置不完整则返回None
    """
    global _chroma_client, _embeddings, _init_error
    
    logger.info("[Chroma] 开始初始化Chroma客户端...")
    
    if not CHROMA_AVAILABLE:
        error_msg = "langchain-community未安装，请运行: pip install langchain-community"
        logger.error(f"[Chroma] {error_msg}")
        _init_error = error_msg
        return None
    
    logger.info("[Chroma] langchain_community已安装")
    
    # 详细检查配置
    missing_configs = []
    if not config.dashscope_api_key:
        missing_configs.append("DASHSCOPE_API_KEY")
        logger.error("[Chroma] DASHSCOPE_API_KEY 未配置")
    else:
        logger.info(f"[Chroma] DASHSCOPE_API_KEY 已配置: {config.dashscope_api_key[:10]}...")
    
    if not config.dashscope_embedding_model:
        missing_configs.append("DASHSCOPE_EMBEDDING_MODEL")
        logger.error("[Chroma] DASHSCOPE_EMBEDDING_MODEL 未配置")
    else:
        logger.info(f"[Chroma] DASHSCOPE_EMBEDDING_MODEL 已配置: {config.dashscope_embedding_model}")
    
    if missing_configs:
        error_msg = f"DashScope配置不完整，缺少: {', '.join(missing_configs)}。请在 config.yaml 或 .env 文件中配置，或设置环境变量"
        logger.error(f"[Chroma] {error_msg}")
        _init_error = error_msg
        return None
    
    if _chroma_client is None:
        try:
            # 确保目录存在
            persist_dir = Path(config.chroma_persist_directory)
            persist_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"[Chroma] 持久化目录: {persist_dir.absolute()}")
            
            # 初始化 DashScope Embeddings
            logger.info(f"[Chroma] 正在初始化DashScope Embeddings，模型: {config.dashscope_embedding_model}")
            _embeddings = get_dashscope_embeddings(config)
            if _embeddings is None:
                error_msg = "DashScope Embeddings初始化失败，请检查配置和网络连接"
                logger.error(f"[Chroma] {error_msg}")
                _init_error = error_msg
                return None
            logger.info("[Chroma] DashScope Embeddings初始化成功")
            
            # 初始化 Chroma
            logger.info("[Chroma] 正在初始化Chroma向量数据库...")
            _chroma_client = Chroma(
                persist_directory=str(persist_dir),
                embedding_function=_embeddings,
            )
            logger.info(f"[Chroma] 客户端初始化成功，持久化目录: {persist_dir.absolute()}")
            _init_error = None  # 初始化成功，清除错误信息
        except RuntimeError as e:
            error_msg = str(e)
            # 检查是否是 SQLite 版本问题
            if "sqlite3" in error_msg.lower() or "unsupported version" in error_msg.lower():
                detailed_error = "SQLite版本不兼容，Chroma需要SQLite >= 3.35.0。解决方案：1. 升级系统SQLite版本 2. 使用pysqlite3-binary替代（pip install pysqlite3-binary）"
                logger.error(f"[Chroma] {detailed_error}")
                logger.error(f"[Chroma] 错误详情: {error_msg}")
                logger.error("[Chroma] 参考: https://docs.trychroma.com/troubleshooting#sqlite")
                _init_error = detailed_error
            else:
                logger.error(f"[Chroma] 客户端初始化失败: {error_msg}")
                _init_error = f"RuntimeError: {error_msg}"
            import traceback
            logger.error(f"[Chroma] 初始化异常详情: {traceback.format_exc()}")
            return None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"[Chroma] 客户端初始化失败: {error_msg}")
            import traceback
            logger.error(f"[Chroma] 初始化异常详情: {traceback.format_exc()}")
            _init_error = error_msg
            return None
    else:
        logger.debug("[Chroma] 使用已存在的Chroma客户端实例")
    
    return _chroma_client


def get_chroma_init_error() -> Optional[str]:
    """
    获取Chroma客户端初始化失败的原因
    
    Returns:
        错误信息字符串，如果初始化成功则返回None
    """
    return _init_error


def get_embeddings(config: AppConfig):
    """
    获取 Embeddings 实例
    
    Args:
        config: 应用配置对象
    
    Returns:
        DashScopeEmbeddings实例
    """
    return get_dashscope_embeddings(config)




