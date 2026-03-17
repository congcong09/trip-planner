"""FastAPI主应用"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..config import get_settings, print_config, validate_config

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于HelloAgents框架的智能旅行规划助手API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
# app.include_router()


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print(f"\n{'=' * 60}")
    print(f"🚀 {settings.app_name} v{settings.app_version}")
    print("=" * 60)

    print(os.environ.get("FASTAPI_HOST", "无"))
    print(os.environ.get("FASTAPI_PORT", "无"))

    # 打印配置信息
    print_config()

    # 验证配置
    try:
        validate_config()
        print("\n✅ 配置验证通过")
    except ValueError as e:
        print(f"\n❌ 配置验证失败：\n{e}")

    print(f"\n{'=' * 60}")
    print("📚 API文档: http://localhost:8000/docs")
    print("📖 ReDoc文档: http://localhost:8000/redoc")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("\n" + "=" * 60)
    print("👏 应用正在关闭...")
    print("=" * 60 + "\n")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
    }
