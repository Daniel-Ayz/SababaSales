from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum


from users.models import Cart

class Purchase(models.Model):
    # many-to-one relationship with Cart
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE) 
    purchase_id = models.AutoField(primary_key=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    #total_price = models.DecimalField(max_digits=10, decimal_places=2)
    #total_quantity = models.IntegerField()
    #payment_method = models.CharField(max_length=50)
    #delivery_method = models.CharField(max_length=50)
    #delivery_address = models.CharField(max_length=255)
    #delivery_date = models.DateTimeField()
    #status = models.CharField(max_length=50)

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
