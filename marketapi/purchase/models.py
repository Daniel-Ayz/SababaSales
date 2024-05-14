from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


# how to add controllers, facade, and adapters from the UML?
# for now - purchase controller is CustomPurchaseController(?)

class CustomPurchaseController(models.Model):
    pass


class Cart(models.Model):
    user = models.ManyToOneRel(CustomPurchaseController, on_delete=models.CASCADE)


class Basket(models.Model):
    store_id = models.IntegerField()
    # many-to-one relationship with Cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)


class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    quantity = models.IntegerField()
    # many-to-one relationship with Basket
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)