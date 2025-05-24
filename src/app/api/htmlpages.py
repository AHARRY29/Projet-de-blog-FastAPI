from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse

import json
from datetime import datetime

from app import config
from app.api import crud, users
from app.api.models import User, ContactMsg
from app.send_email import send_email_async

# page_frag.py contains common page fragments, like .header & .footer.
# This is passed to page templates for repeated use of common html fragments: 
from app.page_frags import FRAGS 


TEMPLATES = Jinja2Templates(directory=str(config.get_base_path() / "templates"))

# Ajouter un filtre personnalisé pour formater les dates
def strftime_filter(date, format_str):
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return date
    return date.strftime(format_str)

# Enregistrer le filtre dans l'environnement Jinja2
TEMPLATES.env.filters["strftime"] = strftime_filter


# define a router for the html returning endpoints: 
router = APIRouter()


   
# ------------------------------------------------------------------------------------------------------------------
# added to get favicon served:
favicon_path = config.get_base_path() / 'favicon.ico'
@router.get("/favicon.ico", status_code=200, include_in_schema=False) 
def favicon():
    """
    Favicon.ico GET
    """
    # print(f"favicon_path is {favicon_path}")
    return FileResponse(favicon_path)


# ------------------------------------------------------------------------------------------------------------------
# serve homepage thru a Jinja2 template:
@router.get("/", status_code=200, response_class=HTMLResponse)
async def root( request: Request ):

    # Récupérer les articles de blog pour la page d'accueil
    blogPostList = await crud.get_all_blogposts()
    
    # Génération d'une interface moderne style ZenBlog
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>ZenBlog - FastAPI Blog</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{--bs-primary: #5465ff; --bs-primary-rgb: 84, 101, 255;}}
            body {{background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}}
            .navbar {{box-shadow: 0 2px 10px rgba(0,0,0,0.1);}}
            .hero {{background: linear-gradient(135deg, #5465ff 0%, #788bff 100%); color: white; padding: 80px 0; margin-bottom: 40px;}}
            .card {{border: none; transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(0,0,0,0.05);}}
            .card:hover {{transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1);}}
            .card-title {{color: #5465ff;}}
            .btn-primary {{background-color: #5465ff; border-color: #5465ff;}}
            .btn-primary:hover {{background-color: #4254ee; border-color: #4254ee;}}
            .category-badge {{background-color: rgba(84, 101, 255, 0.1); color: #5465ff; padding: 5px 10px; border-radius: 50px; font-size: 0.8rem;}}
            .footer {{background-color: #212529; color: #f8f9fa; padding: 40px 0; margin-top: 60px;}}
            .footer a {{color: #f8f9fa; text-decoration: none;}}
            .post-meta {{color: #6c757d; font-size: 0.9rem;}}
        </style>
    </head>
    <body>
        <!-- Navigation Bar -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary sticky-top">
            <div class="container">
                <a class="navbar-brand fw-bold" href="/"><i class="fas fa-blog me-2"></i>ZenBlog</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item"><a class="nav-link active" href="/"><i class="fas fa-home me-1"></i> Accueil</a></li>
                        <li class="nav-item"><a class="nav-link" href="/blogposts"><i class="fas fa-newspaper me-1"></i> Articles</a></li>
                        <li class="nav-item"><a class="nav-link" href="/notes"><i class="fas fa-sticky-note me-1"></i> Notes</a></li>
                        <li class="nav-item"><a class="nav-link" href="/login"><i class="fas fa-sign-in-alt me-1"></i> Connexion</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <!-- Hero Section -->
        <section class="hero text-center">
            <div class="container">
                <h1 class="display-4 fw-bold mb-3">Bienvenue sur ZenBlog</h1>
                <p class="lead mb-4">Découvrez les articles les plus intéressants sur le développement, la technologie et bien plus encore.</p>
                <a href="/blogposts" class="btn btn-light btn-lg px-4">Parcourir tous les articles</a>
            </div>
        </section>

        <!-- Featured Posts Section -->
        <section class="container mb-5">
            <h2 class="text-center mb-4">Articles à la une</h2>
            <div class="row">
    """
    
    # Ajouter les articles de blog avec un design amélioré
    if blogPostList:
        for post in blogPostList:
            # Déterminer la catégorie (premier tag s'il existe)
            category = post.tags.split(',')[0] if post.tags else "Blog"
            
            html_content += f"""
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <span class="category-badge mb-2 d-inline-block">{category}</span>
                            <h5 class="card-title fw-bold">{post.title}</h5>
                            <p class="post-meta"><i class="far fa-calendar me-1"></i> {datetime.now().strftime("%d/%m/%Y")} • <i class="far fa-user me-1"></i> Admin</p>
                            <p class="card-text">{post.description[:150]}...</p>
                            <a href="/blog/{post.id}" class="btn btn-primary">Lire l'article <i class="fas fa-arrow-right ms-1"></i></a>
                        </div>
                    </div>
                </div>
            """
    else:
        html_content += """
                <div class="col-12 text-center">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i> Aucun article disponible pour le moment.
                    </div>
                </div>
        """
    
    html_content += """
            </div>
        </section>

        <!-- Features Section -->
        <section class="container mb-5">
            <div class="row text-center">
                <div class="col-md-4 mb-4">
                    <div class="p-4 bg-white rounded shadow-sm">
                        <i class="fas fa-laptop-code text-primary fa-3x mb-3"></i>
                        <h4>Développement Web</h4>
                        <p class="text-muted">Découvrez les dernières tendances et technologies en développement web.</p>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="p-4 bg-white rounded shadow-sm">
                        <i class="fas fa-mobile-alt text-primary fa-3x mb-3"></i>
                        <h4>Design Responsive</h4>
                        <p class="text-muted">Créez des sites web adaptés à tous les appareils.</p>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="p-4 bg-white rounded shadow-sm">
                        <i class="fas fa-server text-primary fa-3x mb-3"></i>
                        <h4>Backend FastAPI</h4>
                        <p class="text-muted">Utilisez FastAPI pour créer des API performantes et sécurisées.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="footer">
            <div class="container">
                <div class="row">
                    <div class="col-lg-4 mb-4 mb-lg-0">
                        <h5 class="fw-bold"><i class="fas fa-blog me-2"></i>ZenBlog</h5>
                        <p>Une plateforme moderne de blog développée avec FastAPI et Bootstrap 5.</p>
                    </div>
                    <div class="col-lg-4 mb-4 mb-lg-0">
                        <h5 class="fw-bold">Liens rapides</h5>
                        <ul class="list-unstyled">
                            <li><a href="/">Accueil</a></li>
                            <li><a href="/blogposts">Articles</a></li>
                            <li><a href="/notes">Notes</a></li>
                        </ul>
                    </div>
                    <div class="col-lg-4">
                        <h5 class="fw-bold">Contact</h5>
                        <p><i class="fas fa-envelope me-2"></i> contact@example.com</p>
                        <div class="d-flex gap-3 mt-3">
                            <a href="#" class="text-white"><i class="fab fa-twitter fa-lg"></i></a>
                            <a href="#" class="text-white"><i class="fab fa-facebook fa-lg"></i></a>
                            <a href="#" class="text-white"><i class="fab fa-instagram fa-lg"></i></a>
                            <a href="#" class="text-white"><i class="fab fa-github fa-lg"></i></a>
                        </div>
                    </div>
                </div>
                <hr class="my-4 bg-light">
                <div class="text-center">
                    <p class="mb-0">&copy; 2025 ZenBlog - FastAPI Blog. Tous droits réservés.</p>
                </div>
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
    

# ------------------------------------------------------------------------------------------------------------------
# serve registration page thru a Jinja2 template:
@router.get("/register", status_code=status.HTTP_201_CREATED, response_class=HTMLResponse)
async def register( request: Request ):

    blogPostList = await crud.get_all_blogposts()
    
    return TEMPLATES.TemplateResponse(
        "register.html",
        {"request": request, "frags": FRAGS, "blogPosts": blogPostList}, 
    )
    
# ------------------------------------------------------------------------------------------------------------------
# serve login page thru a Jinja2 template:
@router.get("/login", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def login( request: Request ):

    blogPostList = await crud.get_all_blogposts()
    
    return TEMPLATES.TemplateResponse(
        "login.html",
        {"request": request, "frags": FRAGS, "blogPosts": blogPostList}, 
    )
    

# ------------------------------------------------------------------------------------------------------------------
# serve the requested page thru direct HTML generation:
@router.get("/blog/{post_id}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def blogPage( request: Request, post_id: int ):
    
    blogpost = await crud.get_blogpost(post_id)
    if not blogpost:
        raise HTTPException(status_code=404, detail="BlogPost not found")

    blogPostList = await crud.get_all_blogposts()
    
    # Générer du HTML directement pour garantir le fonctionnement
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{blogpost.title} - FastAPI Blog</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container">
                <a class="navbar-brand" href="/">FastAPI Blog</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item"><a class="nav-link" href="/">Accueil</a></li>
                        <li class="nav-item"><a class="nav-link" href="/blogposts">Blog</a></li>
                        <li class="nav-item"><a class="nav-link" href="/notes">Notes</a></li>
                    </ul>
                </div>
            </div>
        </nav>
        
        <div class="container">
            <div class="row">
                <div class="col-lg-8">
                    <article>
                        <h1 class="mb-4">{blogpost.title}</h1>
                        <div class="d-flex align-items-center mb-4">
                            <span class="text-muted">Par Admin | {datetime.now().strftime("%d/%m/%Y")}</span>
                        </div>
                        <div class="mb-4">
                            <span class="badge bg-primary me-2">{blogpost.tags.split(',')[0] if blogpost.tags else "Blog"}</span>
                        </div>
                        <div class="content">
                            {blogpost.description}
                        </div>
                    </article>
                </div>
                
                <div class="col-lg-4">
                    <div class="card mb-4">
                        <div class="card-header">Articles récents</div>
                        <div class="card-body">
                            <ul class="list-unstyled">
    """
    
    # Ajouter les articles récents
    for post in blogPostList[:5]:
        if post.id != post_id:  # Exclure l'article actuel
            html_content += f"""
                                <li class="mb-2"><a href="/blog/{post.id}">{post.title}</a></li>
            """
    
    html_content += """
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="bg-dark text-white mt-5 py-4">
            <div class="container text-center">
                <p>&copy; 2025 FastAPI Blog. Tous droits réservés.</p>
            </div>
        </footer>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
    

# ------------------------------------------------------------------------------------------------------------------
# serve blogposts list page with direct HTML generation:
@router.get("/blogposts", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def blogposts_list(request: Request):
    
    blogPostList = await crud.get_all_blogposts()
    
    # Générer du HTML directement pour garantir le fonctionnement
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Liste des articles - FastAPI Blog</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container">
                <a class="navbar-brand" href="/">FastAPI Blog</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item"><a class="nav-link" href="/">Accueil</a></li>
                        <li class="nav-item"><a class="nav-link active" href="/blogposts">Blog</a></li>
                        <li class="nav-item"><a class="nav-link" href="/notes">Notes</a></li>
                    </ul>
                </div>
            </div>
        </nav>
        
        <div class="container">
            <h1 class="mb-4">Liste des articles</h1>
            
            <div class="row">
                <div class="col-lg-8">
    """
    
    # Ajouter les articles
    if blogPostList:
        for post in blogPostList:
            # Déterminer la catégorie (premier tag s'il existe)
            category = post.tags.split(',')[0] if post.tags else "Blog"
            
            html_content += f"""
                    <div class="card mb-4">
                        <div class="card-body">
                            <h2 class="card-title">{post.title}</h2>
                            <div class="mb-2">
                                <span class="badge bg-primary">{category}</span>
                                <small class="text-muted ms-2">Par Admin | {datetime.now().strftime("%d/%m/%Y")}</small>
                            </div>
                            <p class="card-text">{post.description[:200]}...</p>
                            <a href="/blog/{post.id}" class="btn btn-primary">Lire plus</a>
                        </div>
                    </div>
            """
    else:
        html_content += """
                    <div class="alert alert-info">Aucun article disponible pour le moment.</div>
        """
    
    html_content += """
                </div>
                
                <div class="col-lg-4">
                    <div class="card mb-4">
                        <div class="card-header">Catégories</div>
                        <div class="card-body">
                            <ul class="list-unstyled mb-0">
                                <li><a href="/blogposts?category=Technology">Technologie</a></li>
                                <li><a href="/blogposts?category=Web">Web</a></li>
                                <li><a href="/blogposts?category=Python">Python</a></li>
                                <li><a href="/blogposts?category=FastAPI">FastAPI</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="bg-dark text-white mt-5 py-4">
            <div class="container text-center">
                <p>&copy; 2025 FastAPI Blog. Tous droits réservés.</p>
            </div>
        </footer>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# ------------------------------------------------------------------------------------------------------------------
# serve blog post page with an editor on it thru a template:
@router.get("/Editor/{post_id}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def editor( request: Request, post_id: int, current_user: User = Depends(users.get_current_active_user) ):
    
    blogpost = await crud.get_blogpost(post_id)
    if not blogpost:
        raise HTTPException(status_code=404, detail="BlogPost not found")

    blogPostList = await crud.get_all_blogposts()
    
    return TEMPLATES.TemplateResponse(
        "tinymcEditor.html", # "editor.html",
        {"request": request, "contentPost": blogpost, "frags": FRAGS, "blogPosts": blogPostList}, 
    )
    
# ------------------------------------------------------------------------------------------------------------------
# serve a user profile page thru a template:
@router.get("/Settings", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def user_settings_page( request: Request, current_user: User = Depends(users.get_current_active_user) ):
    
    # default info available to the page: 
    page_data = {
        'username': current_user.username,
        'email': current_user.email,
        'roles': current_user.roles,
    }
    
    # list of blog posts:
    blogPostList = await crud.get_all_blogposts()
    
    # if an ordinary user get user_page, if admin get admin_page: 
    page = 'user_page.html'
    if users.user_has_role( current_user, "admin"):
        page = 'admin_page.html'
        
        # get site_config note to add to the admin page 
        # more items that can be changed:
        site_config = await crud.get_note(1) # site_config has id 1
        if site_config:
            site_config.data = json.loads(site_config.data)
            page_data.update(site_config.data)
       
    return TEMPLATES.TemplateResponse(
        page,
        {"request": request, "data": page_data, "frags": FRAGS, "blogPosts": blogPostList}, 
    )
    
     
    
# ------------------------------------------------------------------------------------------------------------------
@router.post('/send-email/contact', response_model=ContactMsg)
async def send_contact_email_asynchronous(msg: ContactMsg):
    settings = config.get_settings() # application config settings
    await send_email_async( settings.ADMIN_EMAIL, 
                            { 'msg': { 'subject': msg.subject, 'body': msg.msg}},
                            'basic_email.html')
    return msg

# ------------------------------------------------------------------------------------------------------------------
# serve an auth requiring contact page with an editor on it thru a template:
@router.get("/Contactp", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def contact_page_protected( request: Request, 
                                  current_user: User = Depends(users.get_current_active_user) ):
            
    # print("contact_page_protected: rendering template")
    
    email = {
        'subject': 'your subject',
        'msg': 'your message'
    }

    blogPostList = await crud.get_all_blogposts()
    
    return TEMPLATES.TemplateResponse(
        "contact.html",
        {"request": request, 
         "contentPost": email, 
         "frags": FRAGS, 
         "blogPosts": blogPostList}, 
    )

# ------------------------------------------------------------------------------------------------------------------
# serve a contact page with an editor on it thru a template:
@router.get("/Contact", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def contact_page( request: Request ):
    
    # get site_config to check if current endpoint should be protected:
    site_config = await crud.get_note(1) # site_config has id 1
    if site_config:
        # print(f"raw site_config.data is {site_config.data}")
        site_config.data = json.loads(site_config.data)
        # print(f"recovered site_config.data is {site_config.data}")
        if site_config.data["protect_contact"]:
            # print("redirecting!")
            response = RedirectResponse(url='/Contactp') 
            return response
        
    email_json = {
        'subject': 'your subject',
        'msg': 'your message',
    }

    blogPostList = await crud.get_all_blogposts()
    
    return TEMPLATES.TemplateResponse(
        "contact.html",
        { "request": request, 
          "contentPost": email_json, 
          "frags": FRAGS, 
          "blogPosts": blogPostList
        }, 
    )

# ------------------------------------------------------------------------------------------------------------------
# serve the requested page thru a Jinja2 template:
@router.get("/precontact", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def precontact( request: Request ):

    blogPostList = await crud.get_all_blogposts()
    
    return TEMPLATES.TemplateResponse(
        "precontact.html",
        { "request": request, 
          "frags": FRAGS, 
          "blogPosts": blogPostList }, 
    )
    
# ------------------------------------------------------------------------------------------------------------------
# serve the requested page thru a Jinja2 template:
@router.get("/a3da_basic", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def a3da_basic( request: Request ):

    blogPostList = await crud.get_all_blogposts()
    
    return TEMPLATES.TemplateResponse(
        "a3da_basic.html",
        { "request": request, 
          "frags": FRAGS, 
          "blogPosts": blogPostList }, 
    )
    
# ------------------------------------------------------------------------------------------------------------------
# serve the requested page thru a Jinja2 template:
@router.get("/a3da_newBody", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def a3da_basic( request: Request ):

    blogPostList = await crud.get_all_blogposts()
    
    return TEMPLATES.TemplateResponse(
        "a3da_newBody.html",
        { "request": request, 
          "frags": FRAGS, 
          "blogPosts": blogPostList }, 
    )
    
# ------------------------------------------------------------------------------------------------------------------
# serve the requested page thru a Jinja2 template:
@router.get("/flyingcars", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def flyingcars( request: Request ):

    blogPostList = await crud.get_all_blogposts()
    
    return TEMPLATES.TemplateResponse(
        "flyingcars.html",
        { "request": request, 
          "frags": FRAGS, 
          "blogPosts": blogPostList }, 
    )

# ------------------------------------------------------------------------------------------------------------------
# serve a minimal test page to diagnose template issues
@router.get("/minimal", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def minimal_test( request: Request ):
    
    return TEMPLATES.TemplateResponse(
        "minimal.html",
        {"request": request}, 
    )

# ------------------------------------------------------------------------------------------------------------------
# serve a basic bootstrap page
@router.get("/basic", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def basic_page( request: Request ):
    
    # Récupérer les articles de blog pour la page d'accueil
    blogPostList = await crud.get_all_blogposts()
    
    # Récupérer les dernières notes pour la page d'accueil
    notesList = await crud.get_all_notes()
    
    # Préparer les données pour le template
    # Transformer les données pour correspondre au format attendu par le template
    featured_posts = []
    for post in blogPostList[:3]:  # Limiter aux 3 premiers articles
        featured_posts.append({
            "id": post.id,
            "title": post.title,
            "content": post.description,  # Utiliser description comme contenu
            "category": post.tags.split(',')[0] if post.tags else "Blog",  # Utiliser le premier tag comme catégorie
            "author": "Admin",  # Valeur par défaut
            "created_date": datetime.now().strftime("%Y-%m-%d")  # Date actuelle comme valeur par défaut
        })
    
    # Transformer les notes pour correspondre au format attendu par le template
    latest_notes = []
    for note in notesList[:4]:  # Limiter aux 4 premières notes
        latest_notes.append({
            "id": note.id,
            "title": note.title,
            "content": note.description
        })
    
    return TEMPLATES.TemplateResponse(
        "basic_index.html",
        {"request": request, "featured_posts": featured_posts, "latest_notes": latest_notes}, 
    )