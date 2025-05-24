from typing import List, Optional, Dict, Any, Union
from sqlalchemy import asc, desc, and_, or_
from datetime import datetime

from app.api.models import NoteSchema, BlogPostSchema, UserReg
from app.schemas.article import ArticleCreate, ArticleUpdate

from app.db import DatabaseMgr, get_database_mgr
 
from app.api.models import UserInDB, BlogPostDB, NoteDB

from app.config import log

# -----------------------------------------------------------------------------------------
# for creating new notes
async def post_note(payload: NoteSchema, owner: int):
    db_mgr: DatabaseMgr = get_database_mgr()
    # Creates a SQLAlchemy insert object expression query
    query = db_mgr.get_notes_table().insert().values(title=payload.title, 
                                                     description=payload.description,
                                                     data=payload.data,
                                                     owner=owner)
    # Executes the query and returns the generated ID
    return await db_mgr.get_db().execute(query=query)

# -----------------------------------------------------------------------------------------
# for getting notes:
async def get_note(id: int) -> NoteDB:
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_notes_table().select().where(id == db_mgr.get_notes_table().c.id)
    return await db_mgr.get_db().fetch_one(query=query)

# -----------------------------------------------------------------------------------------
# for getting notes by their title:
async def get_note_by_title(title: str) -> NoteDB:
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_notes_table().select().where(title == db_mgr.get_notes_table().c.title)
    return await db_mgr.get_db().fetch_one(query=query)

# -----------------------------------------------------------------------------------------
# returns all notes:
async def get_all_notes() -> List[NoteDB]:
    db_mgr = get_database_mgr()
    query = db_mgr.get_notes_table().select().order_by(asc(db_mgr.get_notes_table().c.id))
    return await db_mgr.get_db().fetch_all(query=query)

# -----------------------------------------------------------------------------------------
# update a note:
async def put_note(id: int, payload: NoteSchema, owner: int):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = (
        db_mgr.get_notes_table()
        .update()
        .where(id == db_mgr.get_notes_table().c.id)
        .values(title=payload.title, 
                description=payload.description, 
                data=payload.data,
                owner=owner)
        .returning(db_mgr.get_notes_table().c.id)
    )
    return await db_mgr.get_db().execute(query=query)

# -----------------------------------------------------------------------------------------
# delete a note:
async def delete_note(id: int):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_notes_table().delete().where(id == db_mgr.get_notes_table().c.id)
    return await db_mgr.get_db().execute(query=query)



# -----------------------------------------------------------------------------------------
# for creating new blogposts
async def post_blogpost(payload: BlogPostSchema, user_id: int):
    log.info(f"post_blogpost: here!")
    db_mgr: DatabaseMgr = get_database_mgr()
    # Creates a SQLAlchemy insert object expression query
    query = db_mgr.get_blogposts_table().insert().values(owner=user_id, 
                                                         title=payload.title, 
                                                         description=payload.description,
                                                         tags=payload.tags)
    # Executes the query and returns the generated ID
    return await db_mgr.get_db().execute(query=query)

# -----------------------------------------------------------------------------------------
# for getting blogposts:
async def get_blogpost(id: int) -> BlogPostDB:
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_blogposts_table().select().where(id == db_mgr.get_blogposts_table().c.id)
    return await db_mgr.get_db().fetch_one(query=query)

# -----------------------------------------------------------------------------------------
# returns all blogposts:
async def get_all_blogposts():
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_blogposts_table().select().order_by(asc(db_mgr.get_blogposts_table().c.id))
    return await db_mgr.get_db().fetch_all(query=query)

# -----------------------------------------------------------------------------------------
# update a blogposts:
async def put_blogpost(id: int, payload: BlogPostSchema):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = (
        db_mgr.get_blogposts_table()
        .update()
        .where(id == db_mgr.get_blogposts_table().c.id)
        .values(title=payload.title, description=payload.description, tags=payload.tags)
        .returning(db_mgr.get_blogposts_table().c.id)
    )
    return await db_mgr.get_db().execute(query=query)

# -----------------------------------------------------------------------------------------
# delete a blogpost:
async def delete_blogpost(id: int):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_blogposts_table().delete().where(id == db_mgr.get_blogposts_table().c.id)
    return await db_mgr.get_db().execute(query=query)




# -----------------------------------------------------------------------------------------
# for creating new users:
async def post_user(user: UserReg, 
                    hashed_password: str,
                    verify_code: str,
                    roles: str):
    '''crud action to create a new user via PRE-VALIDATED data'''
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_users_table().insert().values( username=user.username, 
                                                      hashed_password=hashed_password,
                                                      verify_code=verify_code,
                                                      email=user.email,
                                                      roles=roles )
    # Executes the query and returns the generated ID
    return await db_mgr.get_db().execute(query)
    

# -----------------------------------------------------------------------------------------
# a few methods for getting users:
async def get_user_by_id(id: int):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_users_table().select().where(id == db_mgr.get_users_table().c.id)
    return await db_mgr.get_db().fetch_one(query=query)

async def get_user_by_name(username: str):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_users_table().select().where(db_mgr.get_users_table().c.username == username)
    return await db_mgr.get_db().fetch_one(query)


async def get_user_by_email(email: str):
    db_mgr = get_database_mgr()
    query = db_mgr.get_users_table().select().where(db_mgr.get_users_table().c.email == email)
    return await db_mgr.get_db().fetch_one(query)

# -----------------------------------------------------------------------------------------
# update a user passed an user id and an updated UserInDB. 
# Note: the id field in the UserInDB is ignored. 
async def put_user(id: int, user: UserInDB):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = (
        db_mgr.get_users_table()
        .update()
        .where(id == db_mgr.get_users_table().c.id)
        .values( username=user.username, 
                 hashed_password=user.hashed_password,
                 verify_code=user.verify_code,
                 email=user.email,
                 roles=user.roles
               ).returning(db_mgr.get_users_table().c.id)
        .returning(db_mgr.get_users_table().c.id)
    )
    return await db_mgr.get_db().execute(query=query)

# -----------------------------------------------------------------------------------------
# note: there is no user delete, that is accomplished by disabling a user. 
# A user is disabled by adding the "disabled" to their "roles" db field. 


# -----------------------------------------------------------------------------------------
# Article CRUD operations
# -----------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------
# for creating new articles
async def post_article(payload: ArticleCreate, user_id: int):
    log.info(f"post_article: here!")
    db_mgr: DatabaseMgr = get_database_mgr()
    # Creates a SQLAlchemy insert object expression query
    query = db_mgr.get_articles_table().insert().values(
        owner_id=user_id, 
        title=payload.title, 
        description=payload.description,
        tags=payload.tags,
        affiliate_url=str(payload.affiliate_url),
        commission_rate=payload.commission_rate,
        category=payload.category,
        clicks=0,
        last_clicked_at=None
    )
    # Executes the query and returns the generated ID
    return await db_mgr.get_db().execute(query=query)

# -----------------------------------------------------------------------------------------
# for getting articles:
async def get_article(id: int):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_articles_table().select().where(id == db_mgr.get_articles_table().c.id)
    return await db_mgr.get_db().fetch_one(query=query)

# -----------------------------------------------------------------------------------------
# returns all articles with optional filtering and sorting:
async def get_multi_articles(*, 
                         skip: int = 0, 
                         limit: int = 100, 
                         category: Optional[str] = None,
                         owner_id: Optional[int] = None,
                         sort_by: str = "created_at",
                         sort_order: str = "desc"):
    db_mgr = get_database_mgr()
    articles_table = db_mgr.get_articles_table()
    
    # Build filter conditions
    conditions = []
    if category:
        conditions.append(articles_table.c.category == category)
    if owner_id:
        conditions.append(articles_table.c.owner_id == owner_id)
    
    # Build query with filters
    if conditions:
        query = articles_table.select().where(and_(*conditions))
    else:
        query = articles_table.select()
    
    # Add sorting
    sort_column = getattr(articles_table.c, sort_by, articles_table.c.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # Add pagination
    query = query.offset(skip).limit(limit)
    
    return await db_mgr.get_db().fetch_all(query=query)

# -----------------------------------------------------------------------------------------
# returns popular articles (most clicked):
async def get_popular_articles(limit: int = 10):
    db_mgr = get_database_mgr()
    articles_table = db_mgr.get_articles_table()
    
    query = articles_table.select().order_by(desc(articles_table.c.clicks)).limit(limit)
    
    return await db_mgr.get_db().fetch_all(query=query)

# -----------------------------------------------------------------------------------------
# update an article:
async def put_article(id: int, payload: ArticleUpdate):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = (
        db_mgr.get_articles_table()
        .update()
        .where(id == db_mgr.get_articles_table().c.id)
        .values(
            title=payload.title, 
            description=payload.description, 
            tags=payload.tags,
            affiliate_url=str(payload.affiliate_url) if payload.affiliate_url else None,
            commission_rate=payload.commission_rate,
            category=payload.category
        )
        .returning(db_mgr.get_articles_table().c.id)
    )
    return await db_mgr.get_db().execute(query=query)

# -----------------------------------------------------------------------------------------
# click an article (increment clicks and update last_clicked_at):
async def click_article(id: int):
    db_mgr: DatabaseMgr = get_database_mgr()
    article = await get_article(id)
    if not article:
        return None
    
    # Update article with incremented clicks and current datetime
    query = (
        db_mgr.get_articles_table()
        .update()
        .where(id == db_mgr.get_articles_table().c.id)
        .values(
            clicks=article.clicks + 1,
            last_clicked_at=datetime.now()
        )
        .returning(db_mgr.get_articles_table().c.id)
    )
    article_id = await db_mgr.get_db().execute(query=query)
    
    # If article has commission_rate and owner exists, update owner's commission_balance
    if article.commission_rate is not None and article.owner_id is not None:
        user = await get_user_by_id(article.owner_id)
        if user and hasattr(user, 'commission_balance'):
            # S'assurer que commission_balance n'est pas None
            current_balance = user.commission_balance if user.commission_balance is not None else 0.0
            
            user_query = (
                db_mgr.get_users_table()
                .update()
                .where(user.id == db_mgr.get_users_table().c.id)
                .values(
                    commission_balance=current_balance + article.commission_rate
                )
            )
            await db_mgr.get_db().execute(query=user_query)
    
    return await get_article(id)

# -----------------------------------------------------------------------------------------
# delete an article:
async def delete_article(id: int):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = db_mgr.get_articles_table().delete().where(id == db_mgr.get_articles_table().c.id)
    return await db_mgr.get_db().execute(query=query)

# -----------------------------------------------------------------------------------------
# Update user's last_login_at
async def update_user_login_time(id: int):
    db_mgr: DatabaseMgr = get_database_mgr()
    query = (
        db_mgr.get_users_table()
        .update()
        .where(id == db_mgr.get_users_table().c.id)
        .values(last_login_at=datetime.now())
    )
    return await db_mgr.get_db().execute(query=query)