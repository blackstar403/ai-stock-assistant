from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from app.api.api import api_router
from app.core.config import settings
from app.db.session import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # 获取端口，默认为 8000
    port = int(os.environ.get("PORT", 8000))
    
    # 启动服务器
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True) 