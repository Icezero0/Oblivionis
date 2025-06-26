"""
Pydantic 模型 - 请求和响应数据结构
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime

# ===== 用户相关 =====
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserAuth(BaseModel):
    """带认证信息的用户响应"""
    user: UserResponse
    access_token: str
    token_type: str

# ===== 记忆卡片相关 =====
class MemoryCardCreate(BaseModel):
    content: str
    card_type: str
    notes: Optional[str] = None

class MemoryCardBatchCreate(BaseModel):
    cards: List[MemoryCardCreate]

class MemoryCardUpdate(BaseModel):
    content: Optional[str] = None
    card_type: Optional[str] = None
    notes: Optional[str] = None

class MemoryCardResponse(BaseModel):
    id: int
    content: str
    card_type: str
    notes: Optional[str]
    owner: int
    appear_count: int
    last_appeared_session: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== 用户抽题设置相关 =====
class UserDrawSettingsCreate(BaseModel):
    type_counts: Dict[str, int]  # {"M": 5, "N": 3}
    interval_count: int = 2

class UserDrawSettingsUpdate(BaseModel):
    type_counts: Optional[Dict[str, int]] = None
    interval_count: Optional[int] = None

class UserDrawSettingsResponse(BaseModel):
    id: int
    user_id: int
    type_counts: Dict[str, int]
    interval_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== 会话相关 =====
class SessionResponse(BaseModel):
    id: int
    session_number: int
    user_id: int
    settings_used: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== 抽题相关 =====
class DrawRequest(BaseModel):
    type_counts: Optional[Dict[str, int]] = None  # {"M": 5, "N": 3}
    interval_count: Optional[int] = None

class DrawResponse(BaseModel):
    session: SessionResponse
    cards_by_type: Dict[str, List[MemoryCardResponse]]
    total_cards: int
    settings_used: Dict[str, Any]

class DrawStatisticsResponse(BaseModel):
    total_cards: int
    cards_by_type: Dict[str, int]
    drawn_cards: int
    never_drawn: int
    total_sessions: int

# ===== 高级统计相关 =====
class UserOverviewResponse(BaseModel):
    total_cards: int
    total_sessions: int
    cards_by_type: Dict[str, int]
    drawn_cards: int
    never_drawn: int
    recent_sessions_7d: int
    draw_rate: float

class CardStatisticsResponse(BaseModel):
    total_cards: int
    total_appears: int
    avg_appears: float
    max_appears: int
    min_appears: int
    appear_distribution: Dict[str, int]
    most_drawn_cards: List[Dict[str, Any]]
    never_drawn_cards: List[Dict[str, Any]]

class SessionAnalyticsResponse(BaseModel):
    total_sessions: int
    avg_cards_per_session: float
    daily_sessions: Dict[str, int]
    type_preferences: Dict[str, int]
    session_timeline: List[Dict[str, Any]]

class LearningProgressResponse(BaseModel):
    progress_by_type: Dict[str, Dict[str, Any]]
    proficiency_levels: Dict[str, int]
    total_cards: int

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    total_recommendations: int
