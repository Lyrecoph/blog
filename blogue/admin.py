from django.contrib import admin

from blogue.models import Post
# Register your models here.

# admin.site.register(Post)
# cette manière de faire nous permet de personnaliser la table Post
@admin.register(Post) # il s'agit d'un décorateur
class PostAdmin(admin.ModelAdmin):
    # peremt de spécifier les colonnesou attributs à afficher au niveau de l'admin
    list_display = ('title', 'status', 'created', 'publish', 'author')
    # permet d'utiliser le contenu de champs title pour remplir automatiquement
    # le champs slug
    prepopulated_fields = {'slug' : ('title',)}
    # permet de faire des recherches à partir du title ou du body
    search_fields = ('title', 'body')
    # classer au niveau du tableau en fonction de la statut ou de l'auteur
    ordering = ('status', 'author')
    #filtrer par date de creation, auteur ou date de publication
    list_filter = ('created', 'author', 'publish')
