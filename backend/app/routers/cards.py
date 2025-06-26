"""
记忆卡片相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import MemoryCard, User
from ..schemas import MemoryCardCreate, MemoryCardBatchCreate, MemoryCardUpdate, MemoryCardResponse
from ..utils.database import get_db
from ..dependencies.auth import get_current_active_user

router = APIRouter(prefix="/api/cards", tags=["cards"])

@router.post("/", response_model=MemoryCardResponse)
async def create_card(
    card: MemoryCardCreate, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新的记忆卡片"""
    db_card = MemoryCard(
        content=card.content,
        card_type=card.card_type,
        notes=card.notes,
        owner=current_user.id
    )
    
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    
    return db_card

@router.post("/batch", response_model=List[MemoryCardResponse])
async def create_cards_batch(
    cards_batch: MemoryCardBatchCreate, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量创建记忆卡片"""
    if not cards_batch.cards:
        raise HTTPException(status_code=400, detail="卡片列表不能为空")
    
    if len(cards_batch.cards) > 100:  # 限制批量数量
        raise HTTPException(status_code=400, detail="批量创建数量不能超过100张")
    
    created_cards = []
    
    try:
        for card_data in cards_batch.cards:
            db_card = MemoryCard(
                content=card_data.content,
                card_type=card_data.card_type,
                notes=card_data.notes,
                owner=current_user.id
            )
            db.add(db_card)
            created_cards.append(db_card)
        
        db.commit()
        
        # 刷新所有创建的卡片以获取ID等信息
        for card in created_cards:
            db.refresh(card)
        
        return created_cards
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"批量创建失败: {str(e)}")

@router.get("/", response_model=List[MemoryCardResponse])
async def list_cards(
    current_user: User = Depends(get_current_active_user),
    card_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取记忆卡片列表"""
    query = db.query(MemoryCard).filter(MemoryCard.owner == current_user.id)
    
    if card_type:
        query = query.filter(MemoryCard.card_type == card_type)
    
    cards = query.offset(skip).limit(limit).all()
    return cards

@router.get("/{card_id}", response_model=MemoryCardResponse)
async def get_card(
    card_id: int, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取特定记忆卡片"""
    card = db.query(MemoryCard).filter(
        MemoryCard.id == card_id,
        MemoryCard.owner == current_user.id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="记忆卡片不存在")
    return card

@router.put("/{card_id}", response_model=MemoryCardResponse)
async def update_card(
    card_id: int, 
    card_update: MemoryCardUpdate, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新记忆卡片"""
    db_card = db.query(MemoryCard).filter(
        MemoryCard.id == card_id,
        MemoryCard.owner == current_user.id
    ).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="记忆卡片不存在")
    
    # 更新字段
    if card_update.content is not None:
        db_card.content = card_update.content
    if card_update.card_type is not None:
        db_card.card_type = card_update.card_type
    if card_update.notes is not None:
        db_card.notes = card_update.notes
    
    from datetime import datetime, timezone
    db_card.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_card)
    
    return db_card

@router.delete("/{card_id}")
async def delete_card(
    card_id: int, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除记忆卡片"""
    db_card = db.query(MemoryCard).filter(
        MemoryCard.id == card_id,
        MemoryCard.owner == current_user.id
    ).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="记忆卡片不存在")
    
    db.delete(db_card)
    db.commit()
    
    return {"message": "记忆卡片已删除"}
