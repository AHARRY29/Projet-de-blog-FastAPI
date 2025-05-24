# Plateforme de Blog avec FastAPI et Interface ZenBlog

## Projet DSIA-5201A - Blog FastAPI avec Interface Bootstrap 5

Ce projet est une plateforme de blog moderne développée avec FastAPI et une interface utilisateur ZenBlog basée sur Bootstrap 5. L'application permet de créer, gérer et visualiser des articles de blog avec une interface utilisateur élégante et responsive.

## Stack Technique

- **Backend**: FastAPI, Python 3.9+
- **Base de données**: PostgreSQL
- **ORM**: SQLAlchemy avec databases pour les requêtes asynchrones
- **Validation de données**: Pydantic
- **Authentification**: JWT (JSON Web Tokens)
- **Conteneurisation**: Docker, Docker Compose
- **Tests**: Pytest
- **Frontend**: Templates Jinja2 avec design ZenBlog (Bootstrap 5)

## Fonctionnalités Principales

- **Gestion d'articles de blog**: Création, lecture, mise à jour et suppression d'articles
- **Gestion de notes**: Système de notes complémentaire aux articles
- **Interface utilisateur moderne**: Design responsive adapté à tous les appareils
- **Authentification sécurisée**: Système complet avec JWT, refresh tokens et cookies sécurisés
- **API RESTful**: Endpoints bien documentés pour toutes les fonctionnalités
- **Rendu HTML direct**: Pages générées côté serveur pour une expérience utilisateur optimale

## Installation et Démarrage

### Prérequis

- Docker et Docker Compose
- Git

### Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-username/fastAPI_TDD_Docker.git
   cd fastAPI_TDD_Docker
   ```

2. Vérifiez le fichier `.env` à la racine du projet (il est déjà fourni avec des valeurs par défaut) :
   ```
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=web_dev
   ```

3. Lancez l'application avec Docker Compose :
   ```bash
   docker-compose up -d --build
   ```

4. Accédez à l'application à l'adresse http://localhost:8002

## Structure du Projet

```
fastAPI_TDD_Docker/
├── .env                      # Variables d'environnement
├── docker-compose.yml        # Configuration Docker Compose
├── README.md                 # Documentation du projet
└── src/                      # Code source
    ├── alembic/              # Migrations de base de données
    ├── app/                  # Application principale
    │   ├── api/              # API et endpoints
    │   │   ├── crud.py       # Opérations CRUD
    │   │   ├── htmlpages.py  # Pages HTML (interface utilisateur)
    │   │   ├── models.py     # Modèles Pydantic
    │   │   └── users.py      # Gestion des utilisateurs et authentification
    │   ├── db.py             # Configuration de la base de données
    │   ├── main.py           # Point d'entrée de l'application
    │   ├── schemas/          # Schémas additionnels
    │   ├── static/           # Fichiers statiques (CSS, JS, images)
    │   └── templates/        # Templates Jinja2
    └── tests/                # Tests unitaires
```

## Endpoints de l'API

### Endpoints HTML (Interface Utilisateur)

- `GET /` - Page d'accueil
- `GET /basic` - Version simplifiée de la page d'accueil
- `GET /minimal` - Page minimale pour tester le rendu
- `GET /blogposts` - Liste des articles de blog
- `GET /blog/{post_id}` - Détail d'un article de blog
- `GET /notes` - Liste des notes
- `GET /notes/{id}` - Détail d'une note

### Endpoints API

- `GET /blogposts/` - Liste tous les articles (JSON)
- `GET /blogposts/{id}` - Récupère un article par son ID (JSON)
- `POST /blogposts/` - Crée un nouvel article (authentification requise)
- `PUT /blogposts/{id}` - Met à jour un article existant (authentification requise)
- `DELETE /blogposts/{id}` - Supprime un article (authentification requise)

### Endpoints d'Authentification

- `POST /token` - Obtenir un token JWT
- `POST /refresh-token` - Rafraîchir un token JWT expiré

## Difficultés Rencontrées et Solutions

1. **Intégration des templates ZenBlog avec FastAPI**
   - **Problème** : Les templates complexes provoquaient des erreurs de rendu, notamment avec le filtre `strftime` pour le formatage des dates.
   - **Solution** : Création de versions simplifiées des templates et génération directe de HTML dans certains endpoints pour garantir le bon fonctionnement.

2. **Adaptation du système d'authentification**
   - **Problème** : L'authentification par cookie JWT nécessitait une adaptation spécifique pour fonctionner avec les templates.
   - **Solution** : Création d'une classe personnalisée `OAuth2PasswordBearerWithCookie` pour gérer les tokens JWT dans les cookies.

3. **Rendu des pages dynamiques**
   - **Problème** : La gestion des données dynamiques dans les templates était complexe, notamment pour les listes d'articles et les détails.
   - **Solution** : Création de fonctions de transformation des données pour adapter le format de la base de données au format attendu par les templates.

## Tests

Pour exécuter les tests :

```bash
docker-compose exec web pytest
```

Les tests couvrent les opérations CRUD sur les articles de blog, les notes et l'authentification des utilisateurs.

## Améliorations Futures

- Ajout de fonctionnalités de commentaires sur les articles
- Système de catégories plus élaboré pour les articles
- Interface d'administration pour les utilisateurs avec rôle admin
- Optimisation des requêtes pour améliorer les performances
- Intégration d'un éditeur WYSIWYG pour la création d'articles

## Conclusion

Ce projet répond aux exigences du cours DSIA-5201A en fournissant une application web complète avec une API FastAPI, une base de données PostgreSQL, un système d'authentification JWT et une interface utilisateur moderne. L'architecture conteneurisée avec Docker Compose facilite le déploiement et la maintenance.

---

*Ce projet est basé sur la structure [fastAPI_TDD_Docker](https://github.com/bsenftner/fastAPI_TDD_Docker) avec des améliorations significatives pour l'interface utilisateur et la gestion des articles de blog.*
