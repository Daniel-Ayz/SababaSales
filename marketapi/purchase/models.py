from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum


from users.models import Cart
from store.models import Bid, StoreProduct


class Purchase(models.Model):
    # many-to-one relationship with Cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    purchase_id = models.AutoField(primary_key=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.IntegerField()
    # delivery_address = models.CharField(max_length=255)
    # delivery_date = models.DateTimeField()
    # status = models.CharField(max_length=50)

    def __str__(self):
        return f"purchase {self.purchase_id} for cart {self.cart.id}"
    
class BidPurchase(models.Model):
    bid_id = models.IntegerField()
    purchase_id = models.AutoField(primary_key=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.IntegerField()
    product_name = models.CharField(max_length=100)

class PaymentMethod(models.Model):
    holder = models.CharField(max_length=100)
    holder_identification_number = models.CharField(max_length=9)
    currency = models.CharField(max_length=10)
    credit_card_number = models.CharField(max_length=16)
    expiration_date = models.CharField(max_length=5)
    security_code = models.CharField(max_length=3)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)


class DeliveryMethod(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip = models.CharField(max_length=10)
    name = models.CharField(max_length=100)


class HistoryBasket(models.Model):
    basket_id = models.AutoField(primary_key=True)
    store_id = models.IntegerField()
    # many-to-one relationship with Cart
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)

    total_price = models.FloatField()
    total_quantity = models.IntegerField()
    discount = models.FloatField()

    def __str__(self):
        return f"basket for store {self.store_id}, in cart {self.cart.id}"


class HistoryBasketProduct(models.Model):
    """
    Basket product associated with a single basket
    """

    quantity = models.IntegerField()
    name = models.CharField(max_length=100, default="product")
    # many-to-one relationship with Basket
    history_basket = models.ForeignKey(
        HistoryBasket, on_delete=models.CASCADE, related_name="products"
    )
    initial_price = models.FloatField()

    def __str__(self):
        return self.name
