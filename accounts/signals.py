# Ecoute lorsqu'on sauvegarde
from django.db.models.signals import post_save 
# dispatch envoie le signal
from django.dispatch import receiver
from django.conf import settings

from accounts.models import Profile

# ce code utilise les signaux Django pour créer et sauvegarder automatiquement
# un profil associé à chaque utilisateur créé ou mis à jour dans le système. 
# Cela garantit que chaque utilisateur a un profil, ce qui est utile pour stocker
# des informations supplémentaires sur les utilisateurs.

#  écouter les événements de sauvegarde (post_save) des instances du modèle utilisateur
# (settings.AUTH_USER_MODEL). Lorsqu'un utilisateur est créé (created) ou mis à jour, 
# ces signaux déclenchent des fonctions qui créent ou sauvegardent un profil associé à 
# l'utilisateur.

# Cela définit une fonction qui agit comme récepteur du signal post_save pour le modèle
# utilisateur spécifié dans les paramètres du projet (settings.AUTH_USER_MODEL), 
# qui est généralement le modèle User de Django.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
# Cette fonction est exécutée lorsqu'un nouvel utilisateur est créé. 
# Elle crée un profil associé à cet utilisateur en utilisant le modèle Profile
# et l'instance de l'utilisateur (instance) passée en paramètre.
def create_profile(sender, instance, created, **kwargs):
    # Cette condition vérifie si l'utilisateur est nouvellement créé (created),
    # auquel cas elle crée un nouveau profil (Profile) associé à cet utilisateur.
    if created:
        Profile.objects.create(user=instance)
        
# Cette fonction est appelée chaque fois qu'un utilisateur est sauvegardé (save).
@receiver(post_save, sender= settings.AUTH_USER_MODEL)
# Cette fonction est exécutée lorsqu'un utilisateur existant est sauvegardé. 
# Elle sauvegarde le profil associé à l'utilisateur (instance.profile.save()) 
# pour mettre à jour les éventuelles modifications apportées au profil.
def save_profile(sender, instance, **kwargs):
    instance.profile.save()