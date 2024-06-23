from typing import List

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch

from .models import *
from .schemas import *
from django.contrib.auth.hashers import make_password
from ninja.errors import *
from datetime import datetime


class UserController:
    valid_id = lambda user, id: user.id == id

    def _get_cart(self, request):
        if request.user.is_authenticated:
            user = CustomUser.objects.get(id=request.user.id)
            return Cart.objects.get_or_create(user=user)[0]
        else:
            cart_id = request.session.get("cart_id", None)
            if cart_id:
                try:
                    return Cart.objects.get(id=cart_id)
                except Cart.DoesNotExist:
                    pass
            cart = Cart.objects.create(user=None)
            request.session["cart_id"] = cart.id
            return cart

    def _verify_user_id(self, request, user_id: int) -> bool:
        """
        this function is used the verify the current sesion user id, with the user id in the request.
        """

        return request.user.id == user_id

    def register(self, request, payload: UserRegisterSchema) -> CustomUser:
        # check if user exists
        if CustomUser.objects.filter(username=payload.username).exists():
            raise HttpError(401, "User already exists")
        # Hash the password before saving
        payload.password = make_password(payload.password)
        user = CustomUser.objects.create(
            username=payload.username, email=payload.email, password=payload.password
        )
        user.save()
        return user

    def login(self, request, payload: UserLoginSchema) -> UserSchema:
        user = authenticate(
            request, username=payload.username, password=payload.password
        )
        if user:
            login(request, user)
            # update session cart id
            return user
        else:
            raise AuthenticationError("Invalid credentials")

    def logout(self, request) -> any:
        logout(request)
        return {"msg": "Logged out"}

    def get_user(self, request) -> UserSchema:
        """
        returns the user with the given id,if the id matches the current session user id
        """
        user = CustomUser.objects.get(id=request.user.id)
        return user

    def delete_user(self, request, user_id) -> any:
        """
        deletes the user with the given id, if the id matches the current session user id
        """
        if not self._verify_user_id(request, user_id):
            raise HttpError(401, "Unauthorized")
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        return {"msg": "User deleted"}

    def get_all_users(self, request) -> List[UserSchema]:
        """
        returns all users
        """
        users = CustomUser.objects.all()
        return users

    def update_user(self, request, user_id, payload) -> UserSchema:
        """
        updates the user with the given id, if the id matches the current session user id
        """
        if not self._verify_user_id(request, user_id):
            raise HttpError(401, "Unauthorized")
        try:
            user = CustomUser.objects.get(id=user_id)
            user.username = payload.username
            user.email = payload.email
            user.password = make_password(payload.password)
            user.save()
            return user
        except CustomUser.DoesNotExist as e:
            raise HttpError(404, "User not found")

    def get_user_notifications(self, request):
        """
        returns the notifications of the current session user
        """
        user = CustomUser.objects.get(id=request.user.id)
        notifications = Notification.objects.filter(user=user)
        return notifications

    def send_notification(self, request, target_user_id, payload) -> NotificationSchema:
        """
        sends a notification from current session user to the target user

        """
        user = CustomUser.objects.get(id=request.user.id)
        try:
            target_user = CustomUser.objects.get(id=target_user_id)
        except CustomUser.DoesNotExist as e:
            return HttpError(404, "User not found")
        notification = Notification.objects.create(
            sent_by=user.username, message=payload.msg, user=target_user
        )
        notification.save()
        print(notification)

        return notification

    def get_user_cart(self, request) -> CartSchema:
        cart = self._get_cart(request)
        baskets = Basket.objects.filter(cart=cart)
        basket_list = []
        for basket in baskets:
            products = basket.products.all()
            basket_list.append(
                BasketSchema(
                    id=basket.id, store_id=basket.store_id, basket_products=products
                )
            )
        return CartSchema(user=request.user, baskets=basket_list)

    def add_basket_product(self, request, payload) -> BasketProductSchema:
        cart = self._get_cart(request)
        store_id = payload.store_id
        basket, _ = Basket.objects.get_or_create(cart=cart, store_id=store_id)
        product = BasketProduct.objects.create(
            store_product_id=payload.store_product_id,
            quantity=payload.quantity,
            name=payload.name,
            basket=basket,
            price=payload.price,
        )
        return product

    def delete_user_cart_product(self, request, basket_product_id) -> any:
        # delete basket product with the given id
        try:
            product = BasketProduct.objects.get(id=basket_product_id)
            product.delete()
            return {"msg": "Product deleted"}
        except BasketProduct.DoesNotExist as e:
            return {"error": "Product not found"}

    def get_user_basket(self, request, basket_id) -> BasketSchema:
        cart = self._get_cart(request)
        try:
            basket = Basket.objects.get(id=basket_id, cart=cart)
        except Basket.DoesNotExist as e:
            raise HttpError(404, "Basket not found")
        return BasketSchema(
            id=basket.id,
            store_id=basket.store_id,
            basket_products=basket.products.all(),
        )

    def get_user_products(self, request) -> List[BasketProductSchema]:
        cart = self._get_cart(request)
        baskets = Basket.objects.filter(cart=cart)
        products = []
        for basket in baskets:
            products.extend(basket.products.all())

        return products

    def get_user_full_name(self, request, user_id: int) -> str:
        if not self._verify_user_id(request, user_id):
            raise HttpError(401, "Unauthorized")
        user = CustomUser.objects.get(id=request.user.id)
        return user.Full_Name

    def get_user_identification_number(self, request, user_id: int) -> int:
        if not self._verify_user_id(request, user_id):
            raise HttpError(401, "Unauthorized")
        user = CustomUser.objects.get(id=request.user.id)
        return user.Id

    def get_user_payment_information(self, request, user_id: int) -> dict:
        if not self._verify_user_id(request, user_id):
            raise HttpError(401, "Unauthorized")
        user = CustomUser.objects.get(id=user_id)
        payment_info = PaymentInformationUser.objects.get(user=user)
        return payment_info

    def get_user_delivery_information(self, request, user_id: int) -> dict:
        if not self._verify_user_id(request, user_id):
            raise HttpError(401, "Unauthorized")
        user = CustomUser.objects.get(id=user_id)
        delivery_info = DeliveryInformationUser.objects.get(user=user)
        return delivery_info

    def create_fake_data(self):
        usernames = [
            "Yishay Butzim",
            "Hana Tzirlin",
            "Hanan Margilan",
            "Or Gazma",
            "Mor Tal Combat",
            "Adi Das",
            "Beti Paul",
            "Micha Napo",
            "Moti Batzia",
            "Itzik Hagingi",
            "Pupik Levi",
            "Ortal Gabot",
        ]
        passwords = [
            "user1",
            "user2",
            "user3",
            "user4",
            "user5",
            "user6",
            "user7",
            "user8",
            "user9",
            "user10",
            "user11",
            "user12",
        ]
        emails = [
            "user1@gmail.com",
            "user2@gmail.com",
            "user3@gmail.com",
            "user4@gmail.com",
            "user5@gmail.com",
            "user6@gmail.com",
            "user7@gmail.com",
            "user8@gmail.com",
            "user9@gmail.com",
            "user10@gmail.com",
            "user11@gmail.com",
            "user12@gmail.com",
        ]

        for i in range(len(usernames)):
            user = CustomUser.objects.create(
                username=usernames[i],
                email=emails[i],
                password=make_password(passwords[i]),
            )
            user.save()

            exp_date = "12/25"
            exp_month, exp_year = map(int, exp_date.split("/"))
            exp_year += 2000  # Assuming the year is in the format YY
            expiration_date = datetime(exp_year, exp_month, 1).date()
            payment_info = PaymentInformationUser.objects.create(
                user=user,
                currency="USD",
                holder=user.Full_Name,
                holder_id=user.Id,
                credit_card_number="1234567890",
                expiration_date=expiration_date,
                security_code="123",
            )
            payment_info.save()

        return {"msg": "Fake data created successfully"}
