from django.db import models
from django.conf import settings

# Create your models here.

# Cette table a été crée pour étendre la table user afin ajouter d'autre champs
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # blank=True signifie que le champs peut être vide, null=True signifie que le champs
    # peut être vide ou null dans la DB 
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/img/%Y/%m/%d', blank=True)
    
    def __str__(self) -> str:
        return 'Profile of %s' % self.user.username
