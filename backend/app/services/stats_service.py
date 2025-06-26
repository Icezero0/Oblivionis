"""
统计服务 - 数据统计和分析
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, case
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from ..models import MemoryCard, Session as DrawSession, UserDrawSettings, User

class StatsService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_overview(self, user_id: int) -> Dict[str, Any]:
        """获取用户总览统计"""
        # 基础统计
        total_cards = self.db.query(MemoryCard).filter(MemoryCard.owner == user_id).count()
        total_sessions = self.db.query(DrawSession).filter(DrawSession.user_id == user_id).count()
        
        # 卡片类型分布
        cards_by_type = self.db.query(
            MemoryCard.card_type,
            func.count(MemoryCard.id).label('count')
        ).filter(MemoryCard.owner == user_id).group_by(MemoryCard.card_type).all()
        
        # 抽题统计
        drawn_cards = self.db.query(MemoryCard).filter(
            MemoryCard.owner == user_id,
            MemoryCard.appear_count > 0
        ).count()
        
        # 最近7天的抽题会话
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_sessions = self.db.query(DrawSession).filter(
            DrawSession.user_id == user_id,
            DrawSession.created_at >= seven_days_ago
        ).count()
        
        return {
            "total_cards": total_cards,
            "total_sessions": total_sessions,
            "cards_by_type": {row.card_type: row.count for row in cards_by_type},
            "drawn_cards": drawn_cards,
            "never_drawn": total_cards - drawn_cards,
            "recent_sessions_7d": recent_sessions,
            "draw_rate": round(drawn_cards / total_cards * 100, 1) if total_cards > 0 else 0
        }
    
    def get_card_statistics(self, user_id: int, card_type: Optional[str] = None) -> Dict[str, Any]:
        """获取卡片详细统计"""
        query = self.db.query(MemoryCard).filter(MemoryCard.owner == user_id)
        
        if card_type:
            query = query.filter(MemoryCard.card_type == card_type)
        
        cards = query.all()
        
        # 出现次数分布
        appear_counts = [card.appear_count for card in cards]
        
        # 计算统计指标
        total_appears = sum(appear_counts)
        avg_appears = round(total_appears / len(cards), 2) if cards else 0
        max_appears = max(appear_counts) if appear_counts else 0
        min_appears = min(appear_counts) if appear_counts else 0
        
        # 按出现次数分组
        appear_distribution = {}
        for count in appear_counts:
            key = str(count)
            appear_distribution[key] = appear_distribution.get(key, 0) + 1
        
        # 最常出现的卡片
        most_drawn = query.filter(MemoryCard.appear_count > 0).order_by(
            desc(MemoryCard.appear_count), desc(MemoryCard.last_appeared_session)
        ).limit(5).all()
        
        # 从未出现的卡片
        never_drawn = query.filter(MemoryCard.appear_count == 0).limit(5).all()
        
        return {
            "total_cards": len(cards),
            "total_appears": total_appears,
            "avg_appears": avg_appears,
            "max_appears": max_appears,
            "min_appears": min_appears,
            "appear_distribution": appear_distribution,
            "most_drawn_cards": [
                {
                    "id": card.id,
                    "content": card.content[:50] + "..." if len(card.content) > 50 else card.content,
                    "appear_count": card.appear_count,
                    "last_session": card.last_appeared_session
                }
                for card in most_drawn
            ],
            "never_drawn_cards": [
                {
                    "id": card.id,
                    "content": card.content[:50] + "..." if len(card.content) > 50 else card.content,
                    "card_type": card.card_type
                }
                for card in never_drawn
            ]
        }
    
    def get_session_analytics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取会话分析数据"""
        # 时间范围
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # 会话查询
        sessions = self.db.query(DrawSession).filter(
            DrawSession.user_id == user_id,
            DrawSession.created_at >= start_date
        ).order_by(asc(DrawSession.created_at)).all()
        
        if not sessions:
            return {
                "total_sessions": 0,
                "avg_cards_per_session": 0,
                "daily_sessions": {},
                "type_preferences": {},
                "session_timeline": []
            }
        
        # 每日会话统计
        daily_sessions = {}
        type_preferences = {}
        session_timeline = []
        total_cards_drawn = 0
        
        for session in sessions:
            # 日期统计
            date_key = session.created_at.strftime("%Y-%m-%d")
            daily_sessions[date_key] = daily_sessions.get(date_key, 0) + 1
            
            # 类型偏好统计
            if session.settings_used and 'type_counts' in session.settings_used:
                type_counts = session.settings_used['type_counts']
                for card_type, count in type_counts.items():
                    if card_type not in type_preferences:
                        type_preferences[card_type] = 0
                    type_preferences[card_type] += count
                    total_cards_drawn += count
            
            # 会话时间线
            session_timeline.append({
                "session_number": session.session_number,
                "date": session.created_at.strftime("%Y-%m-%d %H:%M"),
                "settings": session.settings_used
            })
        
        return {
            "total_sessions": len(sessions),
            "avg_cards_per_session": round(total_cards_drawn / len(sessions), 1) if sessions else 0,
            "daily_sessions": daily_sessions,
            "type_preferences": type_preferences,
            "session_timeline": session_timeline[-10:]  # 最近10次会话
        }
    
    def get_learning_progress(self, user_id: int) -> Dict[str, Any]:
        """获取学习进度分析"""
        # 按类型分析进度
        cards_by_type = self.db.query(
            MemoryCard.card_type,
            func.count(MemoryCard.id).label('total'),
            func.sum(case((MemoryCard.appear_count > 0, 1), else_=0)).label('practiced'),
            func.avg(MemoryCard.appear_count).label('avg_appears')
        ).filter(MemoryCard.owner == user_id).group_by(MemoryCard.card_type).all()
        
        progress_by_type = {}
        for row in cards_by_type:
            practiced = row.practiced or 0
            total = row.total
            progress_by_type[row.card_type] = {
                "total": total,
                "practiced": practiced,
                "progress_rate": round(practiced / total * 100, 1) if total > 0 else 0,
                "avg_appears": round(row.avg_appears or 0, 1)
            }
        
        # 熟练度分析（基于出现次数）
        proficiency_levels = {
            "beginner": 0,    # 0次
            "practicing": 0,  # 1-2次
            "familiar": 0,    # 3-5次
            "mastered": 0     # 6次以上
        }
        
        cards = self.db.query(MemoryCard).filter(MemoryCard.owner == user_id).all()
        for card in cards:
            count = card.appear_count
            if count == 0:
                proficiency_levels["beginner"] += 1
            elif count <= 2:
                proficiency_levels["practicing"] += 1
            elif count <= 5:
                proficiency_levels["familiar"] += 1
            else:
                proficiency_levels["mastered"] += 1
        
        return {
            "progress_by_type": progress_by_type,
            "proficiency_levels": proficiency_levels,
            "total_cards": len(cards)
        }
    
    def get_recommendations(self, user_id: int) -> Dict[str, Any]:
        """获取学习建议"""
        recommendations = []
        
        # 分析用户数据
        overview = self.get_user_overview(user_id)
        progress = self.get_learning_progress(user_id)
        
        # 建议1: 检查未练习的卡片
        if overview["never_drawn"] > 0:
            recommendations.append({
                "type": "practice_new",
                "priority": "high",
                "message": f"您还有 {overview['never_drawn']} 张卡片从未练习过，建议优先练习这些新内容。"
            })
        
        # 建议2: 检查类型平衡
        if overview["cards_by_type"]:
            type_counts = overview["cards_by_type"]
            max_type = max(type_counts.items(), key=lambda x: x[1])
            min_type = min(type_counts.items(), key=lambda x: x[1])
            
            if max_type[1] > min_type[1] * 2:
                recommendations.append({
                    "type": "balance_types",
                    "priority": "medium",
                    "message": f"建议增加 {min_type[0]} 类型的卡片，以平衡各类型题目的数量。"
                })
        
        # 建议3: 检查练习频率
        if overview["recent_sessions_7d"] == 0:
            recommendations.append({
                "type": "increase_practice",
                "priority": "high",
                "message": "最近7天没有练习记录，建议保持定期练习以提高记忆效果。"
            })
        elif overview["recent_sessions_7d"] < 3:
            recommendations.append({
                "type": "increase_practice",
                "priority": "medium",
                "message": "建议增加练习频率，每周至少练习3-4次效果更佳。"
            })
        
        # 建议4: 熟练度分析
        beginner_rate = progress["proficiency_levels"]["beginner"] / progress["total_cards"] * 100
        if beginner_rate > 50:
            recommendations.append({
                "type": "focus_basics",
                "priority": "high",
                "message": f"有 {beginner_rate:.1f}% 的内容还未开始练习，建议先专注于基础内容的掌握。"
            })
        
        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
