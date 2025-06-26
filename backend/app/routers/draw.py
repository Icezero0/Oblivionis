"""
抽题相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from ..models import Session as DrawSession
from ..schemas import DrawRequest, DrawResponse, DrawStatisticsResponse, SessionResponse
from ..services.draw_service import DrawService
from ..utils.database import get_db

router = APIRouter(prefix="/api/draw", tags=["draw"])

@router.post("/", response_model=DrawResponse)
async def draw_cards(draw_request: DrawRequest, user_id: int, db: Session = Depends(get_db)):
    """
    抽题接口
    
    Args:
        draw_request: 抽题请求，可以指定各类型数量和间隔次数
        user_id: 用户ID
        
    Returns:
        抽题结果，包含抽中的卡片和会话信息
    """
    draw_service = DrawService(db)
    
    try:
        result = draw_service.draw_cards(
            user_id=user_id,
            type_counts=draw_request.type_counts,
            interval_count=draw_request.interval_count
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"抽题失败: {str(e)}")

@router.get("/statistics/{user_id}", response_model=DrawStatisticsResponse)
async def get_draw_statistics(user_id: int, db: Session = Depends(get_db)):
    """获取用户的抽题统计信息"""
    draw_service = DrawService(db)
    
    try:
        stats = draw_service.get_draw_statistics(user_id)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取统计信息失败: {str(e)}")

@router.get("/sessions/{user_id}", response_model=List[SessionResponse])
async def get_user_sessions(
    user_id: int, 
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """获取用户的抽题会话历史"""
    sessions = db.query(DrawSession).filter(
        DrawSession.user_id == user_id
    ).order_by(
        DrawSession.session_number.desc()
    ).offset(skip).limit(limit).all()
    
    return sessions

@router.get("/sessions/detail/{session_id}", response_model=SessionResponse)
async def get_session_detail(session_id: int, db: Session = Depends(get_db)):
    """获取特定会话的详细信息"""
    session = db.query(DrawSession).filter(DrawSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return session

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_db)):
    """删除特定会话记录（注意：这会影响统计数据）"""
    session = db.query(DrawSession).filter(DrawSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    db.delete(session)
    db.commit()
    
    return {"message": "会话记录已删除"}

@router.get("/sessions/{user_id}/export")
async def export_sessions(user_id: int, db: Session = Depends(get_db)):
    """导出用户的所有会话数据（用于备份或分析）"""
    sessions = db.query(DrawSession).filter(
        DrawSession.user_id == user_id
    ).order_by(DrawSession.session_number.asc()).all()
    
    export_data = []
    for session in sessions:
        export_data.append({
            "session_number": session.session_number,
            "date": session.created_at.isoformat(),
            "settings_used": session.settings_used
        })
    
    return {
        "user_id": user_id,
        "total_sessions": len(export_data),
        "export_date": datetime.now(timezone.utc).isoformat(),
        "sessions": export_data
    }
