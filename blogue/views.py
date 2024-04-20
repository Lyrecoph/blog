from django.shortcuts import render, get_object_or_404

from blogue.models import Post
# Create your views here.
# Pour définir une vue nous avons deux méthodes : vue fondé sur les classes et
# vue fondé sur les méthodes

# Fonction qui permet d'afficher la liste des publications
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/post/postList.html', {'posts': posts})

# Fonction qui permet d'afficher le détail d'une publication
def detail_list(request, slug:str):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/post/postDetail.html', {'post':post})
    