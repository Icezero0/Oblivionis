"""
Oblivionis Backend - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import cards, settings, users, draw, stats
from .utils.database import create_tables

# 创建 FastAPI 应用
app = FastAPI(
    title="Oblivionis API",
    description="A note-taking application backend",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表
@app.on_event("startup")
async def startup_event():
    """应用启动时创建数据库表"""
    create_tables()

# 注册路由
app.include_router(users.router)
app.include_router(cards.router)
app.include_router(settings.router)
app.include_router(draw.router)
app.include_router(stats.router)

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {"message": "Oblivionis Backend API", "status": "running"}
