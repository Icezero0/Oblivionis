"""
用户抽题设置相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import UserDrawSettings
from ..schemas import UserDrawSettingsCreate, UserDrawSettingsUpdate, UserDrawSettingsResponse
from ..utils.database import get_db

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.post("/", response_model=UserDrawSettingsResponse)
async def create_or_update_settings(settings: UserDrawSettingsCreate, user_id: int, db: Session = Depends(get_db)):
    """创建或更新用户抽题设置"""
    # 查找现有设置
    db_settings = db.query(UserDrawSettings).filter(UserDrawSettings.user_id == user_id).first()
    
    if db_settings:
        # 更新现有设置
        db_settings.type_counts = settings.type_counts
        db_settings.interval_count = settings.interval_count
        from datetime import datetime, timezone
        db_settings.updated_at = datetime.now(timezone.utc)
    else:
        # 创建新设置
        db_settings = UserDrawSettings(
            user_id=user_id,
            type_counts=settings.type_counts,
            interval_count=settings.interval_count
        )
        db.add(db_settings)
    
    db.commit()
    db.refresh(db_settings)
    
    return db_settings

@router.get("/{user_id}", response_model=UserDrawSettingsResponse)
async def get_user_settings(user_id: int, db: Session = Depends(get_db)):
    """获取用户抽题设置"""
    settings = db.query(UserDrawSettings).filter(UserDrawSettings.user_id == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="用户设置不存在")
    return settings

@router.put("/{user_id}", response_model=UserDrawSettingsResponse)
async def update_user_settings(user_id: int, settings_update: UserDrawSettingsUpdate, db: Session = Depends(get_db)):
    """更新用户抽题设置"""
    db_settings = db.query(UserDrawSettings).filter(UserDrawSettings.user_id == user_id).first()
    if not db_settings:
        raise HTTPException(status_code=404, detail="用户设置不存在")
    
    # 更新字段
    if settings_update.type_counts is not None:
        db_settings.type_counts = settings_update.type_counts
    if settings_update.interval_count is not None:
        db_settings.interval_count = settings_update.interval_count
    
    from datetime import datetime, timezone
    db_settings.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_settings)
    
    return db_settings

@router.delete("/{user_id}")
async def delete_user_settings(user_id: int, db: Session = Depends(get_db)):
    """删除用户抽题设置（重置为默认）"""
    db_settings = db.query(UserDrawSettings).filter(UserDrawSettings.user_id == user_id).first()
    if not db_settings:
        raise HTTPException(status_code=404, detail="用户设置不存在")
    
    db.delete(db_settings)
    db.commit()
    
    return {"message": "用户设置已删除"}
