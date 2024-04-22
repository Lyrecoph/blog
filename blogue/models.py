from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

# il est préferable d'uitlisateur la table user par défaut de django si dans 
# votre projet vous devez crée une table utilisateur

# L'utilisation de related_name est principalement pour améliorer la lisibilité du code
# et rendre l'accès aux objets liés plus intuitif. Si vous utilisez select_related, vs
# pouvez tjrs accéder aux objets liés sans avoir spécifié de related_name, mais cela
# peut rendre votre code un peu moins clair surtout si vs avez plusieurs relations
# inverses pour le même modèle, en resumé related_name rend votre code plus instruitif 
# alors que select_name rend votre code performant mais possible d'utiliser les deux
# comme select_name('posted') avec posted definir au niveau de related_name('posted')

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    title = models.CharField(max_length=200) # attribut
    # utile pour gérer les urls de manière dynamique
    slug = models.SlugField(max_length=200) 
    body = models.TextField()
    # la date serait automatiquement ajouté
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # par defaut lorsque utilisateur publie un élément il faut que ça soit validé
    # l'admin avant d'apparaitre au niveau du blog du coup par défaut c'est desactivé
    status = models.CharField(choices=STATUS_CHOICES, default='draft', max_length=10)
    # il s'agit de la date à laquelle l'admin décide de publier un post
    publish = models.DateTimeField(default=timezone.now())
    # models.CASCADE signifie lorsqu'on supprime un utilisateur tout ces posts seront supp
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posted")
    
    # cette méthode permet de representer l'objet en chaine de caractère au niveau de DB
    def __str__(self) -> str:
        return self.title

class Comment(models.Model):
    # models.CASCADE lorsqu'on supprimer un post ces commentaires sont supprimer
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.post.title