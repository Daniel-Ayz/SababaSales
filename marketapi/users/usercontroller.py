from typing import List

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch

from .models import *
from .schemas import *
from django.contrib.auth.hashers import make_password
from ninja.errors import *
from datetime import datetime
from .consumers import (
    reset_all_online_count,
    send_message_to_user,
    _mark_notification_as_seen,
)


class UserController:
    valid_id = lambda user, id: user.id == id

    def __init__(self):
        # Doesn't work - This is called also on migrations
        # reset_all_online_count()
        pass

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
        if CustomUser.objects.filter(email=payload.email).exists():
            raise HttpError(401, "Email already exists")
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

    def get_user(self, request) -> UserSetupSchema:
        """
        returns the user with the given id,if the id matches the current session user id
        """
        user = CustomUser.objects.get(id=request.user.id)
        cart = self._get_cart(request)
        cart_id = cart.id
        userSchema = UserSetupSchema(
            id=user.id, username=user.username, email=user.email, cart_id=cart_id
        )
        return userSchema

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

    def mark_notification_as_seen(self, request, notification_id) -> NotificationSchema:
        """
        marks a notification as seen
        """
        notification = Notification.objects.get(id=notification_id)
        notification.seen = True
        notification.save()
        return notification

    # Send notifications from an API call
    def _send_notification(
        self, request, target_user_id, payload
    ) -> NotificationSchema:
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

        if target_user.online_count > 0:
            send_message_to_user(
                target_user_id, payload.msg, notification.id, user.username
            )
            # _mark_notification_as_seen(notification.id)

        return notification

    # Send notifications from a System (Without API)
    @staticmethod
    def send_notification(sent_by: str, target_user_id: int, message: str):
        try:
            target_user = CustomUser.objects.get(id=target_user_id)
        except CustomUser.DoesNotExist as e:
            return False
        notification = Notification.objects.create(
            sent_by=sent_by, message=message, user=target_user
        )
        notification.save()

        if target_user.online_count > 0:
            send_message_to_user(target_user_id, message)
            _mark_notification_as_seen(notification.id)

        return True

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
        # check if the product already exists in the basket:
        try:
            product = basket.products.get(name=payload.name)
            product.quantity += payload.quantity
            product.save()
            return product
        except BasketProduct.DoesNotExist:
            pass
        product = BasketProduct.objects.create(
            store_product_id=payload.store_product_id,
            category=payload.category,
            quantity=payload.quantity,
            name=payload.name,
            basket=basket,
            price=payload.price,
            image_link=payload.image_link,
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
        user = CustomUser.objects.get(id=user_id)
        return user.Full_Name

    def get_user_identification_number(self, request, user_id: int) -> str:
        user = CustomUser.objects.get(id=user_id)
        return user.Identification_number

    def get_payment_information(self, request, user_id: int) -> dict:
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise HttpError(404, "User not found")
        payment_info = PaymentInformationUser.objects.get(user=user)
        payment_info_dict = {
            "holder": payment_info.holder,
            "holder_identification_number": payment_info.holder_identification_number,
            "currency": payment_info.currency,
            "credit_card_number": payment_info.credit_card_number,
            "expiration_date": payment_info.expiration_date,
            "security_code": payment_info.security_code,
        }
        return payment_info_dict

    def get_delivery_information(self, request, user_id: int) -> dict:
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise HttpError(404, "User not found")
        delivery_info = DeliveryInformationUser.objects.get(user=user)
        delivery_info_dict = {
            "address": delivery_info.address,
            "city": delivery_info.city,
            "country": delivery_info.country,
            "zip": delivery_info.zip,
        }
        return delivery_info_dict

    def get_user_id_by_email(self, email: str) -> int:
        user = CustomUser.objects.get(email=email)
        return user.id

    def create_fake_data(self):
        usernames = [
            "Yishay_Butzim",
            "Hana_Tzirlin",
            "Hanan_Margilan",
            "Or_Gazma",
            "Mor_Tal_Combat",
            "Adi_Das",
            "Beti_Paul",
            "Micha_Napo",
            "Moti_Batzia",
            "Itzik_Hagingi",
            "Pupik_Levi",
            "Ortal_Gabot",
        ]
        for i in range(len(usernames)):
            user = CustomUser.objects.create(
                username=usernames[i],
                email=f"{usernames[i]}@gmail.com",
                password=make_password(usernames[i]),
                Full_Name=usernames[i],
                Identification_number="123456789",
            )
            user.save()

            payment_info = PaymentInformationUser.objects.create(
                user=user,
                currency="USD",
                holder=user.Full_Name,
                holder_identification_number=user.Identification_number,
                credit_card_number="1234567890123456",
                expiration_date="12/25",
                security_code="123",
            )
            payment_info.save()

            delivery_info = DeliveryInformationUser.objects.create(
                user=user,
                address=f"Tzarfati Street",
                city="Elifelet",
                country= "Israel",
                zip="1234567",
            )
            delivery_info.save()

        return {"msg": "Fake data created successfully"}

    def get_user_id(self, request, email: str) -> UserSchema:
        try:
            user = CustomUser.objects.get(email=email)
            return user
        except CustomUser.DoesNotExist as e:
            raise HttpError(404, "User not found")

    def update_user_full_name(
        self, request, user_id, payload: FullnameSchemaIn
    ) -> UserSchema:
        user = CustomUser.objects.get(id=user_id)
        user.Full_Name = payload.Full_Name
        user.save()
        return {"msg": "Full name updated successfully"}

    def update_user_Identification_Number(
        self, request, user_id, payload: IdentificationNumberSchemaIn
    ) -> UserSchema:
        user = CustomUser.objects.get(id=user_id)
        user.Identification_number = payload.Identification_Number
        user.save()
        return {"msg": "Identification number updated successfully"}

    def update_user_delivery_info(
        self, request, user_id, payload: DeliveryInfoSchema
    ) -> UserSchema:
        user = CustomUser.objects.get(id=user_id)
        try:
            delivery_info = DeliveryInformationUser.objects.get(user=user)
        except DeliveryInformationUser.DoesNotExist:
            delivery_info = DeliveryInformationUser.objects.create(user=user)
        delivery_info.address = payload.address
        delivery_info.city = payload.city
        delivery_info.country = payload.country
        delivery_info.zip = payload.zip
        delivery_info.save()
        return {"msg": "Delivery info updated successfully"}

    def update_user_payment_info(
        self, request, user_id, payload: PaymentInfoSchema
    ) -> UserSchema:
        user = CustomUser.objects.get(id=user_id)
        try:
            payment_info = PaymentInformationUser.objects.get(user=user)
        except PaymentInformationUser.DoesNotExist:
            payment_info = PaymentInformationUser.objects.create(user=user)
        payment_info.holder = payload.holder
        payment_info.holder_identification_number = payload.holder_identification_number
        payment_info.currency = payload.currency
        payment_info.credit_card_number = payload.credit_card_number
        # need to convert the expiration date to a date object

        payment_info.expiration_date = payload.expiration_date
        payment_info.security_code = payload.security_code
        payment_info.save()
        return {"msg": "Payment info updated successfully"}
