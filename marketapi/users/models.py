from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # make address optional
    Full_Name = models.CharField(max_length=100, blank=True)
    Identification_number = models.CharField(
        max_length=9, blank=True, null=True
    )  # because can start with 0
    address = models.CharField(max_length=100, blank=True)
    online_count = models.IntegerField(default=0)


class PaymentInformationUser(models.Model):
    # one-to-one relationship with CustomUser # This is in the for now
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    holder = models.CharField(max_length=100)  # double saving of information
    holder_identification_number = models.IntegerField()
    currency = models.CharField(max_length=10)
    credit_card_number = models.CharField(max_length=16)
    expiration_date = models.DateField()
    security_code = models.CharField(max_length=3)

    def __str__(self):
        return f"Payment information for {self.user.username}"


class DeliveryInformationUser(models.Model):
    # one-to-one relationship with CustomUser
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip = models.CharField(max_length=7)

    def __str__(self):
        return f"Delivery information for {self.user.username}"


class Notification(models.Model):
    sent_by = models.CharField(max_length=100)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)  # type: ignore
    # many-to-one relationship with CustomUser
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"sent by {self.sent_by} to {self.user.username} on {self.date}"


class Cart(models.Model):
    """
    Cart model that serves as the cart of the user. If the cart does not have a uesr associated with it,
    its ID will be stored in the anonymous users session.

    """

    user = models.OneToOneField(
        CustomUser, blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"cart for user {self.user}"


class Basket(models.Model):
    store_id = models.IntegerField()
    # many-to-one relationship with Cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    def __str__(self):
        return f"basket for store {self.store_id}, in cart {self.cart.id}"


class BasketProduct(models.Model):
    """
    Basket product associated with a single basket
    """

    # product_id = models.IntegerField()
    store_product_id = models.IntegerField(default=0)
    quantity = models.IntegerField()
    name = models.CharField(max_length=100, default="product")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # many-to-one relationship with Basket
    basket = models.ForeignKey(
        Basket, on_delete=models.CASCADE, related_name="products"
    )
    category = models.CharField(max_length=100, default="category")
