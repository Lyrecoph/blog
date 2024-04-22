from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
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

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    
    class Meta:
        # permet de spécifie le nom de la table 
        verbose_name = "Category"
        # permet de spécifie le nom que prendra la table Category 
        # au niveau de l'admin si celui contient plusieurs éléments
        verbose_name_plural = "Categories" 
        
    def __str__(self) -> str:
        return self.name
    
    # cette fonction permet de générer le slug de la categorie en fonction 
    # du nom de la categorie
    # def save(self, *args, **kwargs):
    #     self.slug = self.name.lower().replace(' ', '-')
    #     return super(Category, self).save(*args, **kwargs)
    
    
# Cette classe a été crée afin de permet de vérifier si la publication a été validé
# par l'admin c'est à dire contient le statut published dans le cas contraire 
# il sera pas publié, en général ModelManager permettent de personnaliser le comportement
# des requêtes et d'ajouter des fonctionnalités supplémentaires aux modèles pour interagir
# avec les données de la DB de manière flexible et puissante  
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')
    
class Post(models.Model):
    # status choices contient deux choix en corbeille ou publié
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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts")
    objects = models.Manager() # manager par defaut
    # manager nous permettant de recuperer uniquement les posts publiés
    published = PublishedManager() 
    
    # cette méthode permet de representer l'objet en chaine de caractère au niveau de DB
    def __str__(self) -> str:
        return self.title

    # URL personnalisé ou canonique
    # cette méthode permet de passer plusieurs arguments en une seule fois 
    # et de les afficher au niveau de notre template
    # en resumé: cette pratique de définir des URLs de manière à ce qu'elle soient
    # significatives conviviales et coherents pour les utilisateurs et les moteurs de recherche
    # cela implique généralement d'utiliser des URLs qui décrivent le contenu de la page
    # de manière descriptive plutôt que des URls généres de manière aleatoire ou cryptique
    def get_absolute_url(self):
        # reverse permet d'injecter plusierus arguments au niveau d'un URL et de les capturer
        # automatiquement dans notre template
        return reverse('post_detail',args=[self.publish.year, self.publish.month, self.publish.day, self.slug])

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