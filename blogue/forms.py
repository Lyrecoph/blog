from django import forms

from blogue.models import Comment, Post

# cette manière de procéder permet d'heriter des champs de notre table comment 
# afin d'eviter d'inventer la roue pour notre formualaire

# Cette classe est chargé de nous générer un formualaire à partir de notre table comment
class CommentForm(forms.ModelForm):
    # permet de personnaliser les champs avec bootstrap
    # username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'row':3}))
    
    class Meta:
        model = Comment
        fields = ["body"]
        
# Cette classe permet de créer un formulaire standard pouvant nous permettre 
# de faire des recherche
class PostSearchForm(forms.Form):
    query = forms.CharField(max_length=100)
    
    class Meta:
        fields = ['query']
        
        
# Cette classe permet de generer un formulaire à partir des champs de la table post
class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ['title', 'body', 'category', 'tags', ]
        
# Cette classe nous permet d'envoyer un email
class EmailPostForm(forms.Form):
    # nom de celui qui veut partager la publication
    name = forms.CharField(max_length=20)
    email = forms.EmailField()
    # celui a qui nous voulons envoyer le mail
    to = forms.EmailField()
    # le commentaire que celui qui envoie l'email doit mettre
    comments = forms.CharField(max_length=500, widget=forms.Textarea)