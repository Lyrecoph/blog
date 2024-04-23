from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

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