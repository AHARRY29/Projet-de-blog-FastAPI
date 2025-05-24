import json
import pytest
from datetime import datetime

from app.api.models import UserInDB
from app.schemas.article import Article

# Utilitaire pour créer un article de test
async def create_test_article(test_client, token, **kwargs):
    article_data = {
        "title": "Test Article",
        "description": "This is a test article description",
        "tags": "test,article,unit",
        "affiliate_url": "https://example.com/test",
        "commission_rate": 0.05,
        "category": "Test"
    }
    
    # Remplacer les valeurs par défaut par celles fournies
    article_data.update(kwargs)
    
    response = test_client.post(
        "/api/articles/",
        json=article_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response

# Test de création d'article
def test_create_article(test_client, normal_user_token):
    response = create_test_article(test_client, normal_user_token)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Article"
    assert data["description"] == "This is a test article description"
    assert data["tags"] == "test,article,unit"
    assert data["affiliate_url"] == "https://example.com/test"
    assert data["commission_rate"] == 0.05
    assert data["category"] == "Test"
    assert data["clicks"] == 0
    assert data["last_clicked_at"] is None

# Test de récupération d'un article par ID
def test_get_article(test_client, normal_user_token):
    # Créer un article
    create_response = create_test_article(test_client, normal_user_token)
    article_id = create_response.json()["id"]
    
    # Récupérer l'article
    response = test_client.get(f"/api/articles/{article_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == "Test Article"

# Test de récupération de tous les articles
def test_get_all_articles(test_client, normal_user_token):
    # Créer quelques articles
    create_test_article(test_client, normal_user_token)
    create_test_article(test_client, normal_user_token, title="Second Article")
    
    # Récupérer tous les articles
    response = test_client.get("/api/articles/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(article["title"] == "Test Article" for article in data)
    assert any(article["title"] == "Second Article" for article in data)

# Test de filtrage des articles par catégorie
def test_filter_articles_by_category(test_client, normal_user_token):
    # Créer des articles avec différentes catégories
    create_test_article(test_client, normal_user_token, category="Tech")
    create_test_article(test_client, normal_user_token, category="Books")
    
    # Filtrer par catégorie Tech
    response = test_client.get("/api/articles/?category=Tech")
    assert response.status_code == 200
    data = response.json()
    assert all(article["category"] == "Tech" for article in data)
    
    # Filtrer par catégorie Books
    response = test_client.get("/api/articles/?category=Books")
    assert response.status_code == 200
    data = response.json()
    assert all(article["category"] == "Books" for article in data)

# Test de tri des articles
def test_sort_articles(test_client, normal_user_token):
    # Créer des articles avec différents titres
    create_test_article(test_client, normal_user_token, title="Z Article")
    create_test_article(test_client, normal_user_token, title="A Article")
    
    # Trier par titre ascendant
    response = test_client.get("/api/articles/?sort_by=title&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    titles = [article["title"] for article in data]
    # Vérifier que "A Article" apparaît avant "Z Article"
    assert titles.index("A Article") < titles.index("Z Article")
    
    # Trier par titre descendant
    response = test_client.get("/api/articles/?sort_by=title&sort_order=desc")
    assert response.status_code == 200
    data = response.json()
    titles = [article["title"] for article in data]
    # Vérifier que "Z Article" apparaît avant "A Article"
    assert titles.index("Z Article") < titles.index("A Article")

# Test des articles populaires
def test_popular_articles(test_client, normal_user_token):
    # Créer des articles et simuler des clics
    article1_response = create_test_article(test_client, normal_user_token, title="Less Popular")
    article1_id = article1_response.json()["id"]
    
    article2_response = create_test_article(test_client, normal_user_token, title="Most Popular")
    article2_id = article2_response.json()["id"]
    
    # Simuler des clics sur le deuxième article
    for _ in range(5):
        test_client.post(f"/api/articles/{article2_id}/click")
    
    # Simuler moins de clics sur le premier article
    for _ in range(2):
        test_client.post(f"/api/articles/{article1_id}/click")
    
    # Récupérer les articles populaires
    response = test_client.get("/api/articles/popular/")
    assert response.status_code == 200
    data = response.json()
    
    # Vérifier que l'article le plus populaire est en premier
    assert data[0]["title"] == "Most Popular"
    assert data[0]["clicks"] == 5
    assert data[1]["title"] == "Less Popular"
    assert data[1]["clicks"] == 2

# Test de mise à jour d'un article
def test_update_article(test_client, normal_user_token):
    # Créer un article
    create_response = create_test_article(test_client, normal_user_token)
    article_id = create_response.json()["id"]
    
    # Mettre à jour l'article
    update_data = {
        "title": "Updated Title",
        "description": "Updated description",
        "tags": "updated,test",
        "affiliate_url": "https://example.com/updated",
        "commission_rate": 0.1,
        "category": "Updated"
    }
    
    response = test_client.put(
        f"/api/articles/{article_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["tags"] == "updated,test"
    assert data["affiliate_url"] == "https://example.com/updated"
    assert data["commission_rate"] == 0.1
    assert data["category"] == "Updated"

# Test de clic sur un article
def test_click_article(test_client, normal_user_token):
    # Créer un article
    create_response = create_test_article(test_client, normal_user_token)
    article_id = create_response.json()["id"]
    
    # Vérifier que les clics sont à 0 initialement
    initial_response = test_client.get(f"/api/articles/{article_id}")
    initial_data = initial_response.json()
    assert initial_data["clicks"] == 0
    assert initial_data["last_clicked_at"] is None
    
    # Cliquer sur l'article
    click_response = test_client.post(f"/api/articles/{article_id}/click")
    assert click_response.status_code == 200
    click_data = click_response.json()
    assert click_data["clicks"] == 1
    assert click_data["last_clicked_at"] is not None
    
    # Cliquer à nouveau et vérifier l'incrémentation
    click_response2 = test_client.post(f"/api/articles/{article_id}/click")
    assert click_response2.status_code == 200
    click_data2 = click_response2.json()
    assert click_data2["clicks"] == 2

# Test de suppression d'un article
def test_delete_article(test_client, normal_user_token):
    # Créer un article
    create_response = create_test_article(test_client, normal_user_token)
    article_id = create_response.json()["id"]
    
    # Supprimer l'article
    delete_response = test_client.delete(
        f"/api/articles/{article_id}",
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )
    assert delete_response.status_code == 200
    
    # Vérifier que l'article n'existe plus
    get_response = test_client.get(f"/api/articles/{article_id}")
    assert get_response.status_code == 404

# Test de permission - un utilisateur ne peut pas modifier l'article d'un autre utilisateur
def test_update_article_permission(test_client, normal_user_token, admin_user_token):
    # Créer un article avec l'utilisateur normal
    create_response = create_test_article(test_client, normal_user_token)
    article_id = create_response.json()["id"]
    
    # Essayer de mettre à jour l'article avec un autre utilisateur
    update_data = {
        "title": "Unauthorized Update",
        "description": "This should fail",
        "tags": "fail,test",
        "affiliate_url": "https://example.com/fail",
        "commission_rate": 0.2,
        "category": "Fail"
    }
    
    # Utiliser un token d'un autre utilisateur
    response = test_client.put(
        f"/api/articles/{article_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_user_token}"}  # Token d'un autre utilisateur
    )
    
    # L'admin peut modifier n'importe quel article
    assert response.status_code == 200
    
    # Créer un article avec l'admin
    admin_create_response = create_test_article(test_client, admin_user_token)
    admin_article_id = admin_create_response.json()["id"]
    
    # L'utilisateur normal ne peut pas modifier l'article de l'admin
    normal_update_response = test_client.put(
        f"/api/articles/{admin_article_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {normal_user_token}"}
    )
    
    assert normal_update_response.status_code == 403  # Forbidden
