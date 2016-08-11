from django.db import models
from account.conf import settings


# Create your models here.
class Profile(models.Model):
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    autotask_username = models.CharField(max_length=254)
    autotask_password = models.CharField(max_length=254)
    about = models.TextField()
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BookingInDetails(models.Model):
    account_id = models.CharField(max_length=254)
    ticket_id = models.CharField(max_length=254)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    software_collected = models.CharField(max_length=254)
    chargers_collected = models.CharField(max_length=254)
    cables_collected = models.CharField(max_length=254)
    item = models.CharField(max_length=254)
    passwords = models.CharField(max_length=254)
    action_required = models.CharField(max_length=254)
    condition = models.CharField(max_length=254)
    ifotheraction = models.CharField(max_length=254)
    damaged = models.CharField(max_length=254)
    front = models.CharField(max_length=254)
    lside = models.CharField(max_length=254)
    rside = models.CharField(max_length=254)
    top = models.CharField(max_length=254)
    bottom = models.CharField(max_length=254)
    screen = models.CharField(max_length=254)
    cables = models.CharField(max_length=254)
    keyboard = models.CharField(max_length=254)
    other = models.CharField(max_length=254)
    rside = models.CharField(max_length=254)
    rside = models.CharField(max_length=254)
    created_at = models.DateTimeField(auto_now_add=True)

class Upsell(models.Model):
    product_name = models.CharField(max_length=254)
    account_id = models.CharField(max_length=254)
    product_price = models.FloatField()
    product_cost = models.FloatField()
    product_id = models.IntegerField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    opportunity_id = models.CharField(max_length=254)
    created_at = models.DateTimeField(auto_now_add=True)

class Picklist(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    key = models.CharField(max_length=254)
    value = models.CharField(max_length=254)

class Validation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    entity = models.CharField(max_length=254)
    key = models.CharField(max_length=254)
    operator = models.CharField(max_length=254)
    picklist_number = models.IntegerField()
    value = models.CharField(max_length=254)
