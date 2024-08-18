from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.forms import RegisterForm, UserEditForm, ProfileEditForm
from accounts.models import Profile

# Create your views here.


# Cette fonction permet de recuperer les infos de l'utilisateur et vérifie s'il a été 
# authentifié afin de le rediriger vers la liste des publications
def login_view(request):
    # si l'utilisateur n'est pas authentifié alors
    if not request.user.is_authenticated:
        # si un formulaire a été soumis alors
        if request.method == 'POST':
            # récupérer les valeurs des champs du formulaire
            username = request.POST['username']
            password = request.POST['password']
            
            if not username or not password:
                if not username:
                    messages.error(request, 'Nom d\'utilisateur est requit.')
                if not password:
                    messages.error(request, 'Mot de passe est requit.')
                return render(request, 'registration/login.html', {'session': 'login'})
            
            # verifie si le nom d'utilisateur et le mot de passe sont corrects et existe ds le DB
            user = authenticate(request, username=username, password=password)
            # si l'utilisateur est valide
            if user is not None:
                # alors connecte l'utilisateur 
                login(request, user)
                # redirige l'utilisateur vers la page des publications
                return redirect('post_list')
            else:
                # si l'utilisateur n'existe pas dans la DB alors retourne la page de connexion avec un message d'erreur
                messages.error(request, 'nom d\'utilisateur ou nom de passe incorrecte.')
                # si l'utilisateur n'existe pas dans la DB alors retourne la page de connexion
                return render(request, 'registration/login.html', {'session': 'login'})
            
        else:
            # sinon affiche le formulaire de connexion
            return render(request, 'registration/login.html', {'session': 'login'})  
    else:
        return redirect('post_list')
 
# Cette fonction permet de déconnecter l'utilisateur   
def logout_view(request):
    logout(request)
    return redirect('login_view')

# Cette fonction permet de gérer l'inscription d'un utilisateur
def register_view(request):
    # si un formulaire est soumise alors
    if request.method == 'POST':
        # recupère moi les données du formulaire
        user_form = RegisterForm(request.POST)
        # ensuite vérifie si les infos du formualaire est valide et si elles sont correctes
        if user_form.is_valid():
            # alors créer un nouveau user sans le sauvegarder (commit=False) ds le DB
            new_user = user_form.save(commit=False)
            # le mot de passe de l'utilisateur est enregistré en crypté (set_password)
            new_user.set_password(user_form.cleaned_data['password'])
            # apres ça sauvegarde le nouvel utilisateur dans la DB
            new_user.save()
            # associe le nouvel utilisateur crée au profile
            # Profile.objects.create(user=new_user) # decommenter cette ligne apres avoir desactiver le signal
            # ensuite redirige l'utilisateur vers la page de connexion
            return redirect('login_view')
        # dans le cas ou le formulaire n'est valide alors
        else:
            # retourne moi encore la page d'incription
            return render(request, 'registration/register.html', 
                          {'user_form': user_form, 'session':'signup'})
    # sinon retourne la page d'inscription avec un formulaire vide
    else: 
        user_form = RegisterForm()
        return render(request, 'registration/register.html', 
                      {'user_form': user_form, 'session':'signup'})

# @login_required indique que cette vue n'est accessible qu'après avoir été connecté
@login_required
# cette fonction permet d'afficher les info d'un profile
def dashboard(request):
    # recupère moi le profile de l'utilisateur connecté
    user_profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'profile/dashboard.html',
                  {'user_profile': user_profile, 'session': 'dashboard'})


# Cette fonction gère l'édition du profil d'un utilisateur. Elle utilise deux formulaires,
# UserEditForm et ProfileEditForm, pour permettre à l'utilisateur de modifier à la fois 
# les informations de base de son compte utilisateur (telles que le nom d'utilisateur,
# l'e-mail, etc.) et les informations spécifiques au profil (telles que la bio, 
# la date de naissance, la photo de profil, etc.)
@login_required
def editProfile(request):
    # si un formulaire est soumis alors
    if request.method == 'POST':
        # crée une instance 'user_edit_form' avec les données que l'utilisateur
        # veulent soumise et l'instance actuelle de l'utilisateur 
        user_edit_form = UserEditForm(instance=request.user, data=request.POST)
        # crée une instance de ProfileEditForm avec les données de la requête POST,
        # l'instance actuelle du profil de l'utilisateur, et les fichiers envoyés.
        profile_edit_form = ProfileEditForm(instance=request.user.profile, data=request.POST,
                                       files=request.FILES)
        # si les deux formulaires sont valides.
        if user_edit_form.is_valid() and profile_edit_form.is_valid():
            # les modifications sont enregistrées dans la DB
            user_edit_form.save()
            profile_edit_form .save()
            return redirect('dashboard')
            
    # sinon envoie moi la page avec les formulaires pré-remplis
    else:
        user_edit_form = UserEditForm(instance=request.user)
        profile_edit_form  = ProfileEditForm(instance=request.user.profile)
    return render(request, 'profile/editProfile.html', {'user_edit_form': user_edit_form,
                                                    'profile_edit_form': profile_edit_form })