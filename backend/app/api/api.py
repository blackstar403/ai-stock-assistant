from fastapi import APIRouter

from app.api.routes import stocks, ai, user

api_router = APIRouter()

# 注册路由
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(user.router, prefix="/user", tags=["user"]) 