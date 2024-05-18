from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass


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
    quantity = models.IntegerField()
    name = models.CharField(max_length=100, default="product")
    # many-to-one relationship with Basket
    basket = models.ForeignKey(
        Basket, on_delete=models.CASCADE, related_name="products"
    )
