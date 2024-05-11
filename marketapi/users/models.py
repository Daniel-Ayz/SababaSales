from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass


class Notification(models.Model):
    sent_by = models.CharField(max_length=100)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    # many-to-one relationship with CustomUser
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Cart(models.Model):
    # one-to-one relationship with CustomUser (one cart per user)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Basket(models.Model):
    store_id = models.IntegerField()
    # many-to-one relationship with Cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)


class BasketProduct(models.Model):
    id = models.IntegerField(primary_key=True)
    quantity = models.IntegerField()
    # many-to-one relationship with Basket
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
