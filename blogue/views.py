import json
import time

from django.shortcuts import render,redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, StreamingHttpResponse

from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import send_mail
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank,\
    TrigramSimilarity

# Les librairies tierces
from taggit.models import Tag

from blogue.models import Post, Comment, Category
from blogue.forms import CommentForm, PostSearchForm, PostForm, EmailPostForm
# Create your views here.
# Pour définir une vue nous avons deux méthodes : vue fondé sur les classes et
# vue fondé sur les méthodes

# Fonction joue un double rôle, il permet d'afficher la liste des publications et 
# il permet d'afficher la liste des publications par categorie
def post_list(request, category=None, tag_slug=None):
    # nous utilisons ici le manager published que nous avons crée nous même 
    # qui permet de recuperer que les publications qui ont été publié
    posts = Post.published.all().order_by('-publish')
    # recupère la liste des categories
    categories = Category.objects.all()
    tag = None
    # si la category recupere en paramètre existe alors
    if category:
        # recupère moi la categorie dont le slug correspond au nom de la categorie
        # passer en paramètre dans le cas contraire elève une exception d'ou la présence 
        # du get_object_or_404
        category = get_object_or_404(Category, slug=category)
        # ensuite recupère moi tout les publications liés à cette categorie
        posts = posts.filter(category=category)
    # si tag_slug existe et n'est pas vide alors
    if tag_slug:
        # recupère moi le tag dont le slug correspond au nom du tag passer en paramètre
        # dans le cas contraire elève une exception d'ou la présence du get_object_or_404
        tag = get_object_or_404(Tag, slug=tag_slug)
        # une fois le tag trouvé, on filtre les publications pour inclure uniquement
        # celles qui ont le tag récupéré dans l'étape précédente
        posts = posts.filter(tags__in=[tag])
    # instancier la classe paginator qui prend en paramètre la liste des publication
    # et le nbre d'élément par page
    paginator = Paginator(posts, 2)
    # renvoie la page courante
    page = request.GET.get('page') 
    try:
        # recupère les éléments de la page courante
        posts = paginator.page(page) 
    # si le num de la page n'est pas un entier alors 
    except PageNotAnInteger:
        # retourne moi la liste des publication première page
        posts = paginator.page(1)
    # si l'utilisateur entre un num de page manuellement au niveau de notre url
    # et que celui ci depasse le nbre total de page alors
    except EmptyPage:
        # la nouvelle liste de publication sera egale à la liste des publication 
        # de la dernière page (num_pages)
        posts = paginator.page(paginator.num_pages) 
    context = {'posts': posts, 'page': page, 'categories': categories,
               'category': category, 'tag': tag}
    return render(request, 'blog/post/postList.html', context)

# Fonction qui permet d'afficher le détail d'une publication
def detail_list(request, year:int, month:int, day: int, slug:str):
    # permet de recuperer les publications publié et dont le slug 
    # correspond au slug, année, mois, jour passer en paramètre 
    # [(publish__year):permet de filtrer les objets Post 
    # pour ne récupérer que ceux qui ont été publiés pendant une année spécifique]
    post = get_object_or_404(Post, slug=slug, status='published', 
                             publish__year=year, publish__month=month, publish__day=day)
    # recupérer les commentaiires associés à la publication
    comments = Comment.objects.filter(post=post.id)
    new_comment = None
    # si un formulaire est soumis
    if request.method == 'POST':
        # on recupère les données du formulaire
        comment_form = CommentForm(data=request.POST)
        # ensuite on vérifie si ces éléments sont valide
        if comment_form.is_valid():
            # alors nous allons créer un nouveau commentaire sans enregistrer au niveau du DB
            # (commit=False)
            body = comment_form.cleaned_data['body']
            new_comment = comment_form.save(commit=False)
            # ensuite nous allons associé le commantaire à une publication
            new_comment.post = post
            # ensuite associe le commentaire à l'auteur connecté
            new_comment.author = request.user
            # puis finalement l'enregistrer dans la DB
            new_comment.save()
    # maintenant dans le cas ou la requête n'est pas de type post alors
    else:
        # on renvoie un formulaire vide
        comment_form = CommentForm()
    return render(request, 'blog/post/postDetail.html', {
        'post':post, 'new_comment': new_comment, 
        'comment_form':comment_form, 'comments': comments})
    
# Cette fonction permet de rechercher des publications, à noté que lorsque 
# l'utilisateur fera une recherche il sera rediriger vers une page de recherche
def post_search(request):
    # cette variable sera utilisée pour stocker le terme de recherche saisi par l'utilisateur.
    query = None
    # va stocker les resultats de notre recherche
    results = []
    # lorsque la vue est appelé le formulaire est appelé
    search_form = PostSearchForm()
    # Vérifie si le paramètre 'query' est présent dans les données GET de la requête. 
    # Cela signifie qu'un terme de recherche a été soumis. 
    if 'query' in request.GET:
        # recupère les données de mon formulaire et stock la dans une variable
        # en d'autre terme Crée une nouvelle instance du formulaire PostSearchForm 
        # en utilisant les données GET de la requête, ce qui permet 
        # de pré-remplir le formulaire avec le terme de recherche soumis.
        search_form = PostSearchForm(request.GET)
        # ensuite verifie si les données de mon formulaire est valide
        if search_form.is_valid():
            # reécupère le terme de recherche proprement dit 
            # à partir des données valides du formulaire
            query = search_form.cleaned_data['query']
            # combine les resultats de la recherche au niveau du titre et du body
            # et s'il trouve le terme de recherche dans le titre ou le body classe
            # en terme de poids (le champs ayant le poids A à plus de poids que le B)
            vector_search = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            # crée un objet SearchQuery à partir du terme de recherche. 
            # cet objet représente le terme de recherche lui-même et sera
            # utilisé pour filtrer les résultats de la recherche.
            query_search = SearchQuery(query)
            # Cette ligne effectue la recherche proprement dite. Elle utilise annotate 
            # pour ajouter une colonne virtuelle search à chaque objet Post de la requête,
            # qui contient le résultat de la recherche. Ensuite, elle filtre les objets
            # Post pour ne retourner que ceux qui correspondent 
            # à la recherche (c'est-à-dire ceux pour lesquels search contient le terme 
            # de recherche). Enfin, elle trie les résultats par ordre de pertinence (rank),
            # en utilisant SearchRank pour calculer la pertinence de chaque résultat 
            # par rapport au terme de recherche.
            results = Post.published.annotate(search=vector_search, rank=SearchRank(vector_search, query_search)
                                              ).filter(search=query_search).order_by('-rank')
            
            # retourne les publications qui contient ou à une similarité de 10% avec le terme de recherche
            # results = Post.published.annotate(
            # similarity=TrigramSimilarity("title", query),
            # ).filter(
            # similarity__gt=0.1
            # ).order_by("-similarity")
    return render(request, 'blog/post/search.html', 
                  {'search_form': search_form, 'query': query, 'results': results})

# Cette fonction permet d'ajouter un nouvel article de blog en utilisant un formulaire
# Elle s'assure que l'article est associé à l'utilisateur connecté et le redirige vers
# la liste des articles après l'ajout.
def post_add(request):
    # si un formulaire a été soumis
    if request.method == 'POST':
        # crée une instance de PostForm avec les données de la requête (request.POST)
        # et les fichiers envoyés (request.FILES).
        form_post = PostForm(request.POST or None, request.FILES or None)
        # vérifie si le formulaire est valide 
        if form_post.is_valid():
            # sauvegarde l'objet Post sans enregistrer les données ds la BD
            post = form_post.save(commit=False)
            # relie le post à l'utilisateur connecté
            post.author = request.user
            # et finalement enregistrer le ds la DB
            post.save()
            # permet d'enregistrer les modifications des champs many-to-many
            # après avoir enregistré l'instance principale du modèle lorsque
            # vous utilisez commit=False.
            form_post.save_m2m()
            # puis redirige utilisateur vers la liste des publications
            return redirect('post_list')
    # sinon renvoie la vue avec le formulaire vide
    else:
        form_post = PostForm()
    return render(request, 'blog/post/postAdd.html', {'form_post': form_post})


# Les événements SSE (Server-Sent Events) sont une technologie web qui permet au serveur
# d'envoyer des mises à jour au client de manière unidirectionnelle, c'est-à-dire du 
# serveur vers le client. Voici comment fonctionnent les événements SSE et quelques 
# contextes d'utilisation :

# Fonctionnement des événements SSE :

# Établissement de la connexion : Le client établit une connexion HTTP avec le serveur 
# en utilisant l'URL de l'événement SSE (/stream_view dans votre exemple).
# Échange de données : Une fois la connexion établie, le serveur peut envoyer 
# des données au client à tout moment en utilisant le format SSE. Les données 
# sont envoyées sous forme d'événements, chaque événement étant une unité de données.
# Format des événements SSE : Chaque événement SSE est une chaîne de texte au format 
# spécifique. Il commence par data: suivi des données à envoyer, et se termine par 
# deux retours à la ligne (\n\n).
# Traitement côté client : Le client peut recevoir les événements SSE 
# à l'aide de l'API EventSource en JavaScript. Lorsqu'un événement est reçu, 
# le client peut mettre à jour l'interface utilisateur en fonction des données reçues.
# Contextes d'utilisation des événements SSE :

# Mises à jour en temps réel : Les événements SSE sont souvent utilisés pour fournir 
# des mises à jour en temps réel dans les applications web. Par exemple, un site 
# d'actualités peut utiliser SSE pour afficher de nouveaux articles dès qu'ils 
# sont publiés.
# Notifications : Les événements SSE peuvent également être utilisés pour envoyer 
# des notifications aux utilisateurs. Par exemple, un site de médias sociaux peut 
# utiliser SSE pour informer les utilisateurs des nouveaux messages ou des interactions
# sur leur profil.
# Suivi des modifications : Les événements SSE peuvent être utilisés pour suivre 
# les modifications apportées à un ensemble de données. Par exemple, un tableau 
# de bord de suivi des stocks peut utiliser SSE pour afficher en temps réel les 
# modifications de prix des actions.
# Chargement progressif : Les événements SSE peuvent être utilisés pour charger 
# progressivement les données d'une page web. Plutôt que de charger toutes les 
# données en une seule fois, le serveur peut envoyer des données au fur et à 
# mesure que celles-ci sont disponibles.
# En résumé, les événements SSE sont un outil puissant pour fournir des mises à 
# jour en temps réel et des notifications dans les applications web, offrant 
# une alternative légère et efficace aux technologies plus lourdes comme les WebSockets.


# Cette fonction permet à un utilisateur de modifier un article de blog existant 
# en utilisant un formulaire Django. Une fois les modifications enregistrées, 
# l'utilisateur est redirigé vers la page de détail de l'article.
def post_update(request, year:int, month:int, day: int, slug:str):
    post = get_object_or_404(Post, slug=slug, status='published', 
                             publish__year=year, publish__month=month, publish__day=day)
    # Initialisation d'un dictionnaire context pour stocker les données à passer au template.
    context = {}
    # si le formulaire a été soumis pour mettre à jour l'article
    if request.method == 'POST':
        # alors un formulaire (PostForm) est créé avec les données 
        # de la requête et l'instance de l'article à mettre à jour
        form_post = PostForm(request.POST, request.FILES, instance=post)
        # si le formulaire est valide, les modifications sont enregistrées
        # dans la base de données à l'aide de form_post.save()
        if form_post.is_valid():
            form_post.save()
            # return HttpResponseRedirect(f'/{post.get_absolute_url()}')
            # Redirection de l'utilisateur vers la page de détail 
            # de l'article mis à jour après la sauvegarde.
            return HttpResponseRedirect(f'/{year}/{month}/{day}/{slug}/')
    # sinon renvoie moi le formulaire avec les données actuelles de l'article 
    # dans le formulaire
    else:
        form_post = PostForm(instance=post)
    context['form_post'] = form_post
    context['post'] = post
    return render(request, 'blog/post/postAdd.html', context)


# Cette fonction permet à un client (comme un navigateur web) de se connecter à cette vue 
# et de recevoir des mises à jour en temps réel sur les commentaires associés à un post
# spécifique. Chaque fois qu'un nouveau commentaire est ajouté ou modifié, 
# le flux d'événements SSE envoie les données mises à jour au client, 
# lui permettant ainsi de mettre à jour l'affichage sans recharger la page. 
def stream_comment_view(request, post_id):
    # defini un générateur qui produit les événements SSE à envoyer au client.
    def event_stream():
        # initialise une donnée
        initial_data = ''
        # pour lire un générateur il faut utiliser la boucle while
        while True:
            # recuperer tout les commentaires associés au publication dont l'id est post_id 
            # sur laquelle je suis branché post__id permet de recuperer 
            # uniquement les id des publications
            comments = Comment.objects.filter(post__id=post_id)\
                .values('body', 'created', 'author__username', 'post__id')
            # permet de convertir les commentaires en une liste json
            data = json.dumps(list(comments), cls=DjangoJSONEncoder)
            # si la donnée initiale est differente de data
            if not initial_data == data:
                # Le générateur surveille les changements dans les données JSON 
                # des commentaires. S'il détecte un changement, il envoie un événement SSE
                # contenant les nouvelles données.
                yield '\n'
                yield f'data: {data}'
                yield '\n\n'
                initial_data = data
            time.sleep(1)
    # La vue retourne un objet StreamingHttpResponse qui utilise le générateur 
    # event_stream comme source de données pour le flux d'événements SSE.
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

# cette fonction permet aux utilisateurs d'envoyer un article de blog par e-mail 
# en remplissant un formulaire, puis envoie l'e-mail à l'auteur de l'article avec
# un message personnalisé.
def email_post(request, post_id:int):
    # récupère l'objet Post correspondant à l'identifiant post_id ou retourne 
    # une page d'erreur 404 si l'objet n'existe pas.
    post = get_object_or_404(Post, pk=post_id)
    # initialise la variable sent à False, qui sera utilisée pour indiquer 
    # si l'e-mail a été envoyé avec succès.
    sent = False
    # si un formulaire a été soumis
    if request.method == 'POST':
        # récupère les données du formulaire dans une variable form_post
        form_post = EmailPostForm(request.POST)
        # si les données du formulaire sont valide 
        if form_post.is_valid():
            # récupère les données nettoyées du formulaire.
            cd = form_post.cleaned_data
            # construit l'URL absolue de l'article de blog pour l'inclure 
            # dans le message d'e-mail
            post_url = request.build_absolute_uri(post.get_absolute_url())
            # construit le sujet de l'e-mail en incluant le nom de l'expéditeur 
            # et le titre de l'article.
            subject = f"{cd['name']} vous recommande de lire {post.title}"
            # construit le corps de l'e-mail en incluant l'URL de l'article, 
            # le nom de l'expéditeur et son commentaire.
            message = f"Vous avez reçu un nouveau partage d'article sur {post_url}\n\n" \
                      f"{cd['name']} a laissé ce commentaire: {cd['comments']}" 
            # Envoie l'e-mail en utilisant la fonction send_mail de Django 
            # avec le sujet, le message, l'adresse e-mail de l'expéditeur 
            # et l'adresse e-mail du destinataire.
            send_mail(subject, message, cd['email'], [cd['to']])
            # Met à jour la variable sent pour indiquer que l'e-mail a été envoyé avec succès.
            sent = True
    # si un formulaire n'a pas été soumis renvoie moi un formulaire vide.
    else:
        form_post = EmailPostForm()
    # rend la page 'emailPost.html' avec le formulaire, l'état d'envoi de l'e-mail 
    # et les détails de l'article de blog pour affichage à l'utilisateur.
    return render(request, 'blog/post/emailPost.html', {'form_post':form_post,'sent':sent, 'post':post})