from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Path, Depends, Query, status
from enum import Enum

from app.api import crud
from app.api.users import get_current_active_user, user_has_role
from app.api.models import User as UserModel
from app.schemas.article import Article, ArticleCreate, ArticleUpdate, ArticleWithOwner

from app.config import log

router = APIRouter()

# Enum pour les options de tri
class SortField(str, Enum):
    title = "title"
    created_at = "created_at"
    clicks = "clicks"
    category = "category"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

# ----------------------------------------------------------------------------------------------
# Créer un nouvel article (authentification requise)
@router.post("/", response_model=Article, status_code=201)
async def create_article(
    payload: ArticleCreate, 
    current_user: UserModel = Depends(get_current_active_user)
) -> Article:
    log.info(f"create_article: posting {payload}")
    
    article_id = await crud.post_article(payload, current_user.id)
    
    log.info(f"create_article: returning id {article_id}")
    
    article = await crud.get_article(article_id)
    return article

# ----------------------------------------------------------------------------------------------
# Obtenir un article par ID
@router.get("/{id}", response_model=Article)
async def read_article(id: int = Path(..., gt=0)) -> Article:
    article = await crud.get_article(id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

# ----------------------------------------------------------------------------------------------
# Obtenir tous les articles avec filtrage et tri
@router.get("/", response_model=List[Article])
async def read_all_articles(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    owner_id: Optional[int] = None,
    sort_by: SortField = SortField.created_at,
    sort_order: SortOrder = SortOrder.desc
) -> List[Article]:
    return await crud.get_multi_articles(
        skip=skip,
        limit=limit,
        category=category,
        owner_id=owner_id,
        sort_by=sort_by,
        sort_order=sort_order
    )

# ----------------------------------------------------------------------------------------------
# Obtenir les articles populaires (les plus cliqués)
@router.get("/popular/", response_model=List[Article])
async def read_popular_articles(limit: int = Query(10, gt=0, le=100)) -> List[Article]:
    return await crud.get_popular_articles(limit=limit)

# ----------------------------------------------------------------------------------------------
# Mettre à jour un article (authentification et autorisation requises)
@router.put("/{id}", response_model=Article)
async def update_article(
    payload: ArticleUpdate,
    id: int = Path(..., gt=0),
    current_user: UserModel = Depends(get_current_active_user)
) -> Article:
    article = await crud.get_article(id)
    
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if article.owner_id != current_user.id and not user_has_role(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this article"
        )
    
    await crud.put_article(id, payload)
    return await crud.get_article(id)

# ----------------------------------------------------------------------------------------------
# Incrémenter le compteur de clics et mettre à jour last_clicked_at
@router.post("/{id}/click", response_model=Article)
async def click_article(id: int = Path(..., gt=0)) -> Article:
    article = await crud.get_article(id)
    
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    updated_article = await crud.click_article(id)
    if updated_article is None:
        raise HTTPException(status_code=500, detail="Failed to update article click count")
    
    return updated_article

# ----------------------------------------------------------------------------------------------
# Supprimer un article (authentification et autorisation requises)
@router.delete("/{id}", response_model=dict)
async def delete_article(
    id: int = Path(..., gt=0),
    current_user: UserModel = Depends(get_current_active_user)
) -> dict:
    article = await crud.get_article(id)
    
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if article.owner_id != current_user.id and not user_has_role(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this article"
        )
    
    await crud.delete_article(id)
    return {"message": f"Article {id} deleted successfully"}
