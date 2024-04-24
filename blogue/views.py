from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

from blogue.models import Post, Comment, Category
from blogue.forms import CommentForm, PostSearchForm
# Create your views here.
# Pour définir une vue nous avons deux méthodes : vue fondé sur les classes et
# vue fondé sur les méthodes

# Fonction joue un double rôle, il permet d'afficher la liste des publications et 
# il permet d'afficher la liste des publications par categorie
def post_list(request, category=None):
    # nous utilisons ici le manager published que nous avons crée nous même 
    # qui permet de recuperer que les publications qui ont été publié
    posts = Post.published.all().order_by('-publish')
    # recupère la liste des categories
    categories = Category.objects.all()
    # si la category recupere en paramètre existe alors
    if category:
        # recupère moi tout la categorie dont le slug correspond au nom de la categorie
        # passer en paramètre dans le cas contraire elève une exception d'ou la présence 
        # du get_object_or_404
        category = get_object_or_404(Category, slug=category)
        # ensuite recupère moi tout les publications liés à cette categorie
        posts = posts.filter(category=category)
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
    context = {'posts': posts, 'page': page, 'categories': categories, 'category': category}
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
            new_comment = comment_form.save(commit=False)
            # ensuite nous allons associé le commantaire à une publication
            new_comment.post = post
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
                                    