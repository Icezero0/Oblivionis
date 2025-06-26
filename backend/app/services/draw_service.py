"""
抽题服务 - 核心抽题逻辑
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
import random
from ..models import MemoryCard, Session as DrawSession, UserDrawSettings
from datetime import datetime, timezone

class DrawService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_next_session_number(self) -> int:
        """获取下一个会话编号"""
        last_session = self.db.query(DrawSession).order_by(DrawSession.session_number.desc()).first()
        return (last_session.session_number + 1) if last_session else 1
    
    def get_available_cards(self, user_id: int, card_type: str, interval_count: int, current_session: int) -> List[MemoryCard]:
        """获取可抽取的卡片"""
        # 计算可以抽取的最小会话编号
        min_session = current_session - interval_count
        
        # 查询条件：
        # 1. 属于指定用户
        # 2. 属于指定类型
        # 3. 从未被抽取过，或者距离上次抽取间隔足够
        query = self.db.query(MemoryCard).filter(
            MemoryCard.owner == user_id,
            MemoryCard.card_type == card_type
        ).filter(
            (MemoryCard.last_appeared_session.is_(None)) |  # 从未被抽取
            (MemoryCard.last_appeared_session <= min_session)  # 间隔足够
        )
        
        return query.all()
    
    def draw_cards_by_type(self, user_id: int, card_type: str, count: int, interval_count: int, current_session: int) -> List[MemoryCard]:
        """按类型抽取指定数量的卡片"""
        available_cards = self.get_available_cards(user_id, card_type, interval_count, current_session)
        
        # 如果可用卡片不足，返回所有可用的
        if len(available_cards) <= count:
            return available_cards
        
        # 随机抽取指定数量
        return random.sample(available_cards, count)
    
    def update_card_statistics(self, cards: List[MemoryCard], session_number: int):
        """更新卡片统计信息"""
        for card in cards:
            card.appear_count += 1
            card.last_appeared_session = session_number
            card.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
    
    def create_draw_session(self, user_id: int, settings_used: Dict[str, Any], session_number: int) -> DrawSession:
        """创建抽题会话记录"""
        session = DrawSession(
            session_number=session_number,
            user_id=user_id,
            settings_used=settings_used
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def draw_cards(self, user_id: int, type_counts: Optional[Dict[str, int]] = None, interval_count: Optional[int] = None) -> Dict[str, Any]:
        """
        主要抽题功能
        
        Args:
            user_id: 用户ID
            type_counts: 各类型题目数量，如 {"M": 5, "N": 3}，为空时使用用户设置
            interval_count: 间隔次数，为空时使用用户设置
            
        Returns:
            抽题结果字典，包含抽中的卡片和会话信息
        """
        
        # 获取用户设置
        user_settings = self.db.query(UserDrawSettings).filter(UserDrawSettings.user_id == user_id).first()
        
        # 使用传入参数或用户设置
        if type_counts is None:
            if user_settings and user_settings.type_counts:
                type_counts = user_settings.type_counts
            else:
                # 默认设置
                type_counts = {"M": 3, "N": 2}
        
        if interval_count is None:
            if user_settings:
                interval_count = user_settings.interval_count
            else:
                interval_count = 2
        
        # 获取下一个会话编号
        session_number = self.get_next_session_number()
        
        # 按类型抽取卡片
        drawn_cards_by_type = {}
        all_drawn_cards = []
        
        for card_type, count in type_counts.items():
            if count > 0:
                cards = self.draw_cards_by_type(user_id, card_type, count, interval_count, session_number)
                drawn_cards_by_type[card_type] = cards
                all_drawn_cards.extend(cards)
        
        # 更新卡片统计
        if all_drawn_cards:
            self.update_card_statistics(all_drawn_cards, session_number)
        
        # 创建会话记录
        settings_used = {
            "type_counts": type_counts,
            "interval_count": interval_count
        }
        session = self.create_draw_session(user_id, settings_used, session_number)
        
        return {
            "session": session,
            "cards_by_type": drawn_cards_by_type,
            "total_cards": len(all_drawn_cards),
            "settings_used": settings_used
        }
    
    def get_draw_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取抽题统计信息"""
        # 总卡片数
        total_cards = self.db.query(MemoryCard).filter(MemoryCard.owner == user_id).count()
        
        # 按类型统计卡片数
        cards_by_type = self.db.query(
            MemoryCard.card_type,
            func.count(MemoryCard.id).label('count')
        ).filter(MemoryCard.owner == user_id).group_by(MemoryCard.card_type).all()
        
        # 已抽取过的卡片数
        drawn_cards = self.db.query(MemoryCard).filter(
            MemoryCard.owner == user_id,
            MemoryCard.appear_count > 0
        ).count()
        
        # 总会话数
        total_sessions = self.db.query(DrawSession).filter(DrawSession.user_id == user_id).count()
        
        return {
            "total_cards": total_cards,
            "cards_by_type": {row.card_type: row.count for row in cards_by_type},
            "drawn_cards": drawn_cards,
            "never_drawn": total_cards - drawn_cards,
            "total_sessions": total_sessions
        }
