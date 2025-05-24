from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: str = Field(..., min_length=3, max_length=16384)
    tags: str = Field(..., min_length=3, max_length=80)
    affiliate_url: Optional[HttpUrl] = None
    commission_rate: Optional[float] = None
    category: Optional[str] = None

class ArticleCreate(ArticleBase):
    affiliate_url: HttpUrl

class ArticleUpdate(ArticleBase):
    pass

class ArticleInDBBase(ArticleBase):
    id: int
    clicks: int = 0
    last_clicked_at: Optional[datetime] = None
    owner_id: int
    
    class Config:
        orm_mode = True

class Article(ArticleInDBBase):
    pass

class ArticleWithOwner(ArticleInDBBase):
    owner: Optional[Dict[str, Any]] = None
