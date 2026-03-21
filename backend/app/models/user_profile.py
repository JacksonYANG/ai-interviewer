"""
用户画像数据模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from ..database import Base


class UserProfile(Base):
    """用户画像模型"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    real_name = Column(String(100))
    phone = Column(String(20))
    target_location = Column(String(200))
    target_positions = Column(String(500))
    years_of_experience = Column(Integer)
    current_salary = Column(String(50))
    expected_salary = Column(String(50))
