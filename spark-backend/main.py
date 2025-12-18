"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import load_config, validate_config
from core.logger import logger
from routers.auth import router as auth_router
from routers.workspace import router as workspace_router

# 加载配置
config = load_config()

# 验证配置并输出警告
warnings = validate_config(config)
if warnings:
    logger.warning("配置警告：")
    for key, msg in warnings.items():
        logger.warning(f"  - {key}: {msg}")

# 创建 FastAPI 应用
app = FastAPI(
    title="SparkCanvas API",
    description="SparkCanvas 后端 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(workspace_router)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "Welcome to SparkCanvas API"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.app_host,
        port=config.app_port,
        reload=True
    )

