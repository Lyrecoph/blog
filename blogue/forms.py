from django import forms
from blogue.models import Comment, Post, Category

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
    query = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', "placeholder":"Search posts"}))
    
    class Meta:
        fields = ['query']

class CategoryChoiceField(forms.ModelChoiceField):
    widget = forms.Select(attrs={'class': 'class-control'})
        
        
# Cette classe permet de generer un formulaire à partir des champs de la table post
class PostForm(forms.ModelForm):
    # title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}), label="Titre")
    # category = CategoryChoiceField(queryset=Category.objects.all())
    # tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-tags'}), label="Tags")
    # body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10}), label="Contenu")
    
    class Meta:
        model = Post
        fields = ['title', 'body', 'category', 'tags', ]
        # widgets = {
        #     # 'title': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        #     # 'category': forms.Select(attrs={'class': 'form-control'})
        #     # 'tags': forms.TextInput(attrs={'class': 'form-control form-control-tags'}),
        #     # 'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        # }
# Cette classe nous permet d'envoyer un email
class EmailPostForm(forms.Form):
    # nom de celui qui veut partager la publication
    name = forms.CharField(label="Name", max_length=100, required=True, 
                           widget=forms.TextInput(
                               attrs={'class': 'form-control', 
                                      "id":"username",
                                      "placeholder": "Nom de celui qui partage la publication", 
                                      "type":"text"}))
    email = forms.EmailField(label="email", max_length=50, min_length=5 ,help_text='', required=True,
                                widget=forms.TextInput(
                                    attrs={"class": "form-control", "id": "email", "type": "email",
                                           "placeholder": "Email de l'expéditeur",
                                           "data-sb-validations": "required"}))
    # celui a qui nous voulons envoyer le mail
    to = forms.EmailField(label="to", max_length=250, min_length=5 ,help_text='', required=True,
                                widget=forms.TextInput(
                                    attrs={"class": "form-control", "id": "email", "type": "email",
                                           "placeholder": "Email du destinataire",
                                           "data-sb-validations": "required"}))
    # le commentaire que celui qui envoie l'email doit mettre
    comments = forms.CharField(max_length=500, widget=forms.Textarea(
                            attrs={'class': 'form-control', 'rows': 10}), label="Commentaire")