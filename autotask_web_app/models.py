from django.db import models
from account.conf import settings


# Create your models here.
class Profile(models.Model):
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    autotask_username = models.CharField(max_length=254)
    autotask_password = models.CharField(max_length=254)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
