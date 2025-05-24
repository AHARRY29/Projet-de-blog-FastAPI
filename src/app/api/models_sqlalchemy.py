from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    verify_code = Column(String)
    roles = Column(String)
    commission_balance = Column(Float, default=0.0)
    last_login_at = Column(DateTime, nullable=True)
    articles = relationship("Article", back_populates="owner")

class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)
    tags = Column(String(80), nullable=False)
    affiliate_url = Column(String, nullable=False)
    commission_rate = Column(Float, nullable=True)
    category = Column(String, index=True, nullable=True)
    clicks = Column(Integer, default=0, nullable=False)
    last_clicked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    owner = relationship("User", back_populates="articles")
