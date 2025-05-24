import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire parent au chemin de recherche des modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app.api import crud
from app.api.users import get_user
from app.api.models import UserReg
from app.api.encrypt import get_password_hash
from app.schemas.article import ArticleCreate
from app.db import get_database_mgr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_user(username: str, password: str, email: str, roles: str = "user"):
    """Crée un utilisateur s'il n'existe pas déjà"""
    user = await get_user(username)
    if not user:
        user_in = UserReg(
            username=username,
            password=password,
            email=email
        )
        hashed_password = get_password_hash(password)
        verify_code = "verified"  # Utilisateur déjà vérifié
        user_id = await crud.post_user(user_in, hashed_password, verify_code, roles)
        logger.info(f"Utilisateur créé: {username} (ID: {user_id})")
        return user_id
    logger.info(f"L'utilisateur {username} existe déjà")
    return user.id

async def create_article(
    owner_id: int,
    title: str,
    description: str,
    tags: str,
    affiliate_url: str,
    commission_rate: float = 0.05,
    category: str = None,
    clicks: int = 0
):
    """Crée un article avec les données fournies"""
    article_in = ArticleCreate(
        title=title,
        description=description,
        tags=tags,
        affiliate_url=affiliate_url,
        commission_rate=commission_rate,
        category=category
    )
    article_id = await crud.post_article(article_in, owner_id)
    
    # Si des clics sont spécifiés, simuler ces clics
    if clicks > 0:
        article = await crud.get_article(article_id)
        for _ in range(clicks):
            await crud.click_article(article_id)
    
    logger.info(f"Article créé: {title} (ID: {article_id})")
    return article_id

async def main():
    logger.info("Création des données initiales")
    db_mgr = get_database_mgr()
    await db_mgr.get_db().connect()
    
    try:
        # Création des utilisateurs
        admin_id = await create_user(
            username="admin",
            password="adminpassword123",
            email="admin@example.com",
            roles="admin"
        )
        
        user1_id = await create_user(
            username="alice",
            password="alicepassword123",
            email="alice@example.com"
        )
        
        user2_id = await create_user(
            username="bob",
            password="bobpassword123",
            email="bob@example.com"
        )
        
        # Création des articles pour l'administrateur
        await create_article(
            owner_id=admin_id,
            title="Meilleur smartphone 2023",
            description="Découvrez notre sélection des meilleurs smartphones de 2023 avec leurs caractéristiques et performances.",
            tags="tech,smartphone,2023",
            affiliate_url="https://example.com/smartphones",
            commission_rate=0.08,
            category="Tech",
            clicks=120
        )
        
        await create_article(
            owner_id=admin_id,
            title="Guide d'achat ordinateur portable",
            description="Comment choisir le meilleur ordinateur portable selon vos besoins et votre budget.",
            tags="tech,laptop,guide",
            affiliate_url="https://example.com/laptops",
            commission_rate=0.1,
            category="Tech",
            clicks=85
        )
        
        # Création des articles pour l'utilisateur 1
        await create_article(
            owner_id=user1_id,
            title="Top 10 des livres de développement personnel",
            description="Une sélection des meilleurs livres pour améliorer votre vie et atteindre vos objectifs.",
            tags="livres,développement personnel,lecture",
            affiliate_url="https://example.com/books",
            commission_rate=0.05,
            category="Livres",
            clicks=45
        )
        
        await create_article(
            owner_id=user1_id,
            title="Équipements de fitness à domicile",
            description="Les meilleurs équipements pour faire du sport chez soi sans se ruiner.",
            tags="fitness,sport,équipement",
            affiliate_url="https://example.com/fitness",
            commission_rate=0.07,
            category="Sport",
            clicks=65
        )
        
        # Création des articles pour l'utilisateur 2
        await create_article(
            owner_id=user2_id,
            title="Accessoires indispensables pour cuisine",
            description="Les ustensiles et accessoires qui vont révolutionner votre façon de cuisiner.",
            tags="cuisine,ustensiles,accessoires",
            affiliate_url="https://example.com/kitchen",
            commission_rate=0.06,
            category="Maison",
            clicks=95
        )
        
        await create_article(
            owner_id=user2_id,
            title="Meilleurs jeux vidéo 2023",
            description="Notre sélection des jeux vidéo à ne pas manquer cette année sur toutes les plateformes.",
            tags="jeux,gaming,2023",
            affiliate_url="https://example.com/games",
            commission_rate=0.09,
            category="Gaming",
            clicks=150
        )
        
        logger.info("Données initiales créées avec succès")
    
    finally:
        await db_mgr.get_db().disconnect()

if __name__ == "__main__":
    asyncio.run(main())
