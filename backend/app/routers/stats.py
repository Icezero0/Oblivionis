"""
高级统计相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..schemas import (
    UserOverviewResponse, CardStatisticsResponse, SessionAnalyticsResponse,
    LearningProgressResponse, RecommendationResponse
)
from ..services.stats_service import StatsService
from ..utils.database import get_db

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("/overview/{user_id}", response_model=UserOverviewResponse)
async def get_user_overview(user_id: int, db: Session = Depends(get_db)):
    """获取用户学习总览"""
    stats_service = StatsService(db)
    
    try:
        overview = stats_service.get_user_overview(user_id)
        return overview
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取总览失败: {str(e)}")

@router.get("/cards/{user_id}", response_model=CardStatisticsResponse)
async def get_card_statistics(
    user_id: int, 
    card_type: Optional[str] = Query(None, description="筛选特定卡片类型"),
    db: Session = Depends(get_db)
):
    """获取卡片详细统计"""
    stats_service = StatsService(db)
    
    try:
        stats = stats_service.get_card_statistics(user_id, card_type)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取卡片统计失败: {str(e)}")

@router.get("/sessions/{user_id}", response_model=SessionAnalyticsResponse)
async def get_session_analytics(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="分析天数范围"),
    db: Session = Depends(get_db)
):
    """获取会话分析数据"""
    stats_service = StatsService(db)
    
    try:
        analytics = stats_service.get_session_analytics(user_id, days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取会话分析失败: {str(e)}")

@router.get("/progress/{user_id}", response_model=LearningProgressResponse)
async def get_learning_progress(user_id: int, db: Session = Depends(get_db)):
    """获取学习进度分析"""
    stats_service = StatsService(db)
    
    try:
        progress = stats_service.get_learning_progress(user_id)
        return progress
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取学习进度失败: {str(e)}")

@router.get("/recommendations/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """获取个性化学习建议"""
    stats_service = StatsService(db)
    
    try:
        recommendations = stats_service.get_recommendations(user_id)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取建议失败: {str(e)}")

@router.get("/dashboard/{user_id}")
async def get_dashboard_data(user_id: int, db: Session = Depends(get_db)):
    """获取仪表板综合数据"""
    stats_service = StatsService(db)
    
    try:
        # 综合多个统计数据
        overview = stats_service.get_user_overview(user_id)
        progress = stats_service.get_learning_progress(user_id)
        recommendations = stats_service.get_recommendations(user_id)
        recent_analytics = stats_service.get_session_analytics(user_id, 7)  # 最近7天
        
        return {
            "overview": overview,
            "progress": progress,
            "recommendations": recommendations,
            "recent_activity": {
                "sessions_7d": recent_analytics["total_sessions"],
                "daily_sessions": recent_analytics["daily_sessions"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取仪表板数据失败: {str(e)}")
