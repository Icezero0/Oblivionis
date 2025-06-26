"""
数据库工具函数
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from ..models import Base

# 数据库配置
DATABASE_DIR = Path(__file__).parent.parent.parent.parent / "data"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/oblivionis.db"

# SQLAlchemy 配置
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # 关闭 SQL 语句输出
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建数据库表
def create_tables():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)
    # print(f"数据库已创建: {DATABASE_URL}")
