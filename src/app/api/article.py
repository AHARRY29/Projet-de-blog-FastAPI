from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.db import Base

if TYPE_CHECKING:
    from .user import User

class Article(Base):
    __tablename__ = "article"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(16384), nullable=False)
    tags: Mapped[str] = mapped_column(String(80), nullable=False)
    affiliate_url: Mapped[str] = mapped_column(String, nullable=False)
    commission_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String, index=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="articles")
