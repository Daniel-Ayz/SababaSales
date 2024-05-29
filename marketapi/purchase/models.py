from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum


from users.models import Cart


class Purchase(models.Model):
    # many-to-one relationship with Cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    purchase_id = models.AutoField(primary_key=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    # total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # total_quantity = models.IntegerField()
    # payment_method = models.CharField(max_length=50)
    # delivery_method = models.CharField(max_length=50)
    # delivery_address = models.CharField(max_length=255)
    # delivery_date = models.DateTimeField()
    # status = models.CharField(max_length=50)


class PaymentMethod(BaseModel):
    billing_address = models.CharField(max_length=100)
    currency = models.CharField(max_length=10)
    credit_card_number = models.CharField(max_length=16)
    expiration_date = models.DateField()
    security_code = models.CharField(max_length=3)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
