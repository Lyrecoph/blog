from django import forms

from blogue.models import Comment

# cette manière de procéder permet d'heriter des champs de notre table comment 
# afin d'eviter d'inventer la roue pour notre formualaire

class CommentForm(forms.ModelForm):
    # permet de personnaliser les champs avec bootstrap
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'row':3}))
    class Meta:
        model = Comment
        fields = ["username", "email", "body"]