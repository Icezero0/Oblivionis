"""
数据库模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系定义
    memory_cards = relationship("MemoryCard", back_populates="owner_user")
    sessions = relationship("Session", back_populates="user")
    draw_settings = relationship("UserDrawSettings", back_populates="user", uselist=False)

class UserDrawSettings(Base):
    __tablename__ = "user_draw_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    type_counts = Column(JSON)
    interval_count = Column(Integer, default=2)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系定义
    user = relationship("User", back_populates="draw_settings")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_number = Column(Integer, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    settings_used = Column(JSON)  # 记录本次使用的设置快照
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 关系定义
    user = relationship("User", back_populates="sessions")

class MemoryCard(Base):
    __tablename__ = "memory_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    card_type = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    appear_count = Column(Integer, default=0)
    last_appeared_session = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 关系定义
    owner_user = relationship("User", back_populates="memory_cards")
