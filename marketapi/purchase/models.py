from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum

# how to add controllers, facade, and adapters from the UML?
# for now - purchase controller is CustomPurchaseController(?)


class PurchaseController(models.Model):
    pass


class Cart(models.Model):
    user_id = models.IntegerField()


class Basket(models.Model):
    store_id = models.IntegerField()
    # many-to-one relationship with Cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)


class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    quantity = models.IntegerField()
    # many-to-one relationship with Basket
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)


class PaymentServiceType(str, Enum):
    PAYPAL = "paypal"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    # Add other payment services as needed


class PaymentMethod(BaseModel):
    service: PaymentServiceType  # Using the enum for service type
    currency: str
    amount: float
    billing_address: str
    additional_info: Optional[dict] = Field(
        default_factory=dict
    )  # For any extra details specific to the service
