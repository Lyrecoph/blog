from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from accounts.forms import RegisterForm

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
            # verifie si le nom d'utilisateur et le mot de passe sont corrects et existe ds le DB
            user = authenticate(request, username=username, password=password)
            # si l'utilisateur est valide
            if user is not None:
                # alors connecte l'utilisateur 
                login(request, user)
                # redirige l'utilisateur vers la page des publications
                return redirect('post_list')
            else:
                # si l'utilisateur n'existe pas dans la DB alors retourne la page de connexion
                return render(request, 'registration/login.html')
            
        else:
            # sinon affiche le formulaire de connexion
            return render(request, 'registration/login.html')  
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
            # ensuite redirige l'utilisateur vers la page de connexion
            return redirect('login_view')
        # dans le cas ou le formulaire n'est valide alors
        else:
            # retourne moi encore la page d'incription
            return render(request, 'registration/register.html', {'user_form': user_form})
    # sinon retourne la page d'inscription avec un formulaire vide
    else: 
        user_form = RegisterForm()
        return render(request, 'registration/register.html', {'user_form': user_form})