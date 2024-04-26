from django.contrib import admin

from blogue.models import Post, Comment, Category
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    
# admin.site.register(Post)
# cette manière de faire nous permet de personnaliser la table Post
@admin.register(Post) # il s'agit d'un décorateur
class PostAdmin(admin.ModelAdmin):
    # peremt de spécifier les colonnesou attributs à afficher au niveau de l'admin
    list_display = ('title', 'status', 'created', 'publish', 'author', 'display_tags')
    # permet d'utiliser le contenu de champs title pour remplir automatiquement
    # le champs slug
    prepopulated_fields = {'slug' : ('title',)}
    # permet de faire des recherches à partir du title ou du body
    search_fields = ('title', 'body')
    # classer au niveau du tableau en fonction de la statut ou de l'auteur
    ordering = ('status', 'author')
    #filtrer par date de creation, auteur ou date de publication
    list_filter = ('created', 'author', 'publish')
    # ça est défini comme une liste de champs que vous souhaitez rendre éditables
    # dans la liste des objets d'un modèle dans l'interface d'administration Django. 
    list_editable = ['status']
    
    # cette méthode est définie pour renvoyer une chaîne de caractères contenant 
    # les noms des tags liés à chaque publication. Cette méthode est ajoutée 
    # à list_display pour afficher les tags dans la liste des publications 
    # dans l'interface d'administration Django.
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('created',)