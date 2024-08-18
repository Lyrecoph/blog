from typing import Any
from django import forms
from django.contrib.auth.models import User
from accounts.models import Profile

# Cette classe nous permet d'heriter des champs de la table User
class RegisterForm(forms.ModelForm):
    username = forms.CharField(label="Username", max_length=250, help_text='', required=True,
                               widget=forms.TextInput(attrs={"class":"form-control", "id":"username", "type":"text", "placeholder":"Username", "data-sb-validations":"required"}))

    first_name = forms.CharField(label="first_name", max_length=250, help_text='', required=True,
                               widget=forms.TextInput(attrs={"class": "form-control", "id": "first_name", "type": "text",
                                                             "placeholder": "First Name",
                                                             "data-sb-validations": "required"}))
    last_name = forms.CharField(label="last_name", max_length=250, min_length=5, help_text='', required=True,
                                 widget=forms.TextInput(
                                     attrs={"class": "form-control", "id": "last_name", "type": "text",
                                            "placeholder": "First Name",
                                            "data-sb-validations": "required"}))

    email = forms.EmailField(label="email", max_length=250, min_length=5 ,help_text='', required=True,
                                widget=forms.TextInput(
                                    attrs={"class": "form-control", "id": "email", "type": "email",
                                           "placeholder": "Email",
                                           "data-sb-validations": "required"}))

    password = forms.CharField(label="password", max_length=250, min_length=8, help_text='', required=True,
                             widget=forms.TextInput(
                                 attrs={"class": "form-control", "id": "password", "type": "password",
                                        "placeholder": "Password",
                                        "data-sb-validations": "required"}))

    confirm_password = forms.CharField(label="confirm_password", max_length=250, min_length=8, help_text='', required=True,
                               widget=forms.TextInput(
                                   attrs={"class": "form-control", "id": "confirm_password", "type": "password",
                                          "placeholder": "Confirm password",
                                          "data-sb-validations": "required"}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        
    # cette méthode assure que les champs password et confirm_password d'un formulaire
    # d'inscription correspondent, ce qui garantit que l'utilisateur saisit 
    # correctement son mot de passe.
    def clean_confirm_password(self):
        cleaned_data = super().clean()
        # c' est un dictionnaire contenant les valeurs nettoyées de tous les champs
        # du formulaire.
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('les deux mots de passe ne sont pas identique.')
        # Si les mots de passe correspondent, cette méthode renvoie la valeur du champ 
        # confirm_password, ce qui signifie que la validation a réussi et que 
        # le formulaire est prêt à être soumis.
        return confirm_password
        
    # class class Meta:
    #     db_table = ''
    #     managed = True
    #     verbose_name = 'ModelName'
    #     verbose_name_plural = 'ModelNames'
    
    
# Génere un formulaire à partir des champs de la table USER en tenant 
# compte de champs à afficher spécifié au niveau de la variable fields
class UserEditForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
# Génere un formulaire à partir des champs de la table PROFILE en tenant 
# compte de champs à afficher spécifié au niveau de la variable fields
class ProfileEditForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']