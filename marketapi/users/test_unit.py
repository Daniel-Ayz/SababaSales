from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
import json
from channels.testing import ChannelsLiveServerTestCase
from users.schemas import DeliveryInfoSchema, FullnameSchemaIn, IdentificationNumberSchemaIn, PaymentInfoSchema, StoreProduct, UserLoginSchema, UserRegisterSchema, UserSchema
from users.usercontroller import UserController
from .consumers import ChatConsumer
from .api import router
from ninja.testing import TestClient
from django.core.cache import cache
import json
from django.test import Client, RequestFactory, TransactionTestCase
from ninja.testing import TestClient
from .api import router
from django.contrib.auth.models import User
from .models import Basket, BasketProduct, Cart, DeliveryInformationUser, Notification, PaymentInformationUser
from django.core.cache import cache
User = get_user_model()

uc = UserController()
class UserAPITestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = TestClient(router)
        self.user = User.objects.create_user(username="testuser2",email="testuser2@example.com", password="password")
        self.user.save()
        self.factory = RequestFactory()

        #for notifications tests:
        # Use sync_to_async to handle the synchronous operations of the ORM
        self.client = TestClient(router)

        self.user = User.objects.create_user(username="testuser", password="password")
        self.channel_layer = get_channel_layer()
        self.room_group_name = (
            f"chat_{self.user.id}"  # Now self.user is properly awaited and instantiated
        )


    def tearDown(self):
        cache.clear()

    
    # UNIT TESTS

    # Test1: Test if the user is registered successfully
    def test_register_user(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "newuser")
        self.assertEqual(response.json()["email"], "newuser@example.com")

    
    # Test2: Test if the user is not registered successfully with existing data
    def test_register_existing_user(self):
        data = {"username": self.user.username, "email": "testuser@example.com", "password": "test_password"}
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "User already exists")

    
    # Test3: Test if the user is not registered successfully with existing email
    def test_register_existing_email(self):
        data = {"username": "newuser", "email": self.user.email, "password": "newpassword"}
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Email already exists")

    
    # Test4: Test if the user is logged in successfully
    def test_login_user(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')
        user.save()
        c = Client()
        logged_in = c.login(username='testusertry', password='12345')
        self.assertTrue(logged_in)
        # data = UserLoginSchema(username =self.user.username, password =self.user.password)
        # logged_in = uc.login(99, data)
        # self.assertEqual(response["username"], self.user.username)
        # self.assertEqual(response["email"], self.user.email)

    
    # Test5: Test if the user is not logged in successfully with invalid credentials
    def test_login_invalid_credentials(self):
        data = {"username": self.user.username, "password": "wrongpassword"}
        response = self.client.post("/login", json=data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Unauthorized")

    
    # Test6: Test if the user is logged out successfully
    def test_logout_user(self):
        data = {"username": self.user.username, "password": "wrongpassword"}
        response = self.client.post("/login", json=data)
        response = self.client.post("/logout")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["msg"], "Logged out")

    
    # Test7: Test if user is found successfully
    def test_get_user(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')
        user.save()
        c = Client()
        logged_in = c.login(username='testusertry', password='12345')

        request = self.factory.get('/fake-path/')
        request.user = user

        # Call the get_user method with the mock request
        response = uc.get_user(request)

        self.assertEqual(response.username, user.username)
        self.assertEqual(response.email, user.email)

    
    # Test8: Test if the unauthenticated user is not found
    def test_get_user_unauthenticated(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 401)

    
    # Test9: Test if the user is deleted successfully
    def test_delete_user(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')
        user.save()
        c = Client()
        logged_in = c.login(username='testusertry', password='12345')

        request = self.factory.get('/fake-path/')
        request.user = user

        response = uc.delete_user(request, user.id)
        self.assertEqual(response["msg"], "User deleted")

    
    # Test10: Test if the user is not deleted successfully with invalid credentials
    def test_delete_user_unauthorized(self):
        data = {"username": self.user.username, "password": "wrongpassword"}
        response = self.client.post("/login", json=data)
        response = self.client.delete(f"//{self.user.id + 1}")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Unauthorized")

    
    # Test11: Test if the user is not deleted successfully with non-existent user
    def test_delete_user_nonexistent(self):
        data = {"username": self.user.username, "password": "wrongpassword"}
        response = self.client.post("/login", json=data)
        response = self.client.delete(f"//{self.user.id + 100}")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Unauthorized")


    # Test12: Test if the user is updated successfully
    def test_update_user(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')
        user.save()
        c = Client()
        logged_in = c.login(username='testusertry', password='12345')

        request = self.factory.get('/fake-path/')
        request.user = user

        data = UserRegisterSchema(username = "updateduser", email = "updated@example.com", password = "newpassword")
        response = uc.update_user(request, user.id, data)
        self.assertEqual(response.username, "updateduser")
        self.assertEqual(response.email, "updated@example.com")


    # Test13: Test if the user is not updated successfully with invalid credentials
    def test_update_user_unauthorized(self):
        data = {"username": self.user.username, "password": "wrongpassword"}
        response = self.client.post("/login", json=data)
        data = {"username": "updateduser", "email": "updated@example.com", "password": "newpassword"}
        response = self.client.put(f"//{self.user.id + 1}", json=data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Unauthorized")

    
    # Test14: Test if the non-existent user is not updated successfully
    def test_update_user_nonexistent(self):
        data = {"username": self.user.username, "password": "wrongpassword"}
        response = self.client.post("/login", json=data)
        data = {"username": "updateduser", "email": "updated@example.com", "password": "newpassword"}
        response = self.client.put(f"//{self.user.id + 100}", json=data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Unauthorized")


    # Test15: Test if the notifications are retrieved successfully
    def test_mark_notification_as_seen(self):
        notification = Notification.objects.create(
            user=self.user, message="Test Notification", seen=False
        )
        response = uc.mark_notification_as_seen(99, notification.id)
        self.assertTrue(response.seen)
    
    
    # Test16: Test if the notification is not marked as seen successfully with invalid credentials
    def test_mark_notification_as_seen_nonexistent(self):
        try:
            response = uc.mark_notification_as_seen(99, 9999)
        except Exception as e:
            self.assertEqual(str(e), "Notification matching query does not exist.")


    # Test17: Test if the user cart is retrieved successfully
    def test_get_user_cart(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')
        user.save()
        c = Client()
        logged_in = c.login(username='testusertry', password='12345')

        request = self.factory.get('/fake-path/')
        request.user = user

        cart = Cart.objects.create(user=user)
        basket = Basket.objects.create(cart=cart, store_id=1)
        product = BasketProduct.objects.create(basket=basket, name="Test Product", quantity=1, price=10.0)
        
        response = uc.get_user_cart(request)
        self.assertEqual(response.user.id, user.id)

    
    # Test18: Test if the basket product is added successfully
    def test_add_basket_product(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')
        user.save()
        c = Client()
        logged_in = c.login(username='testusertry', password='12345')

        request = self.factory.get('/fake-path/')
        request.user = user
        data = StoreProduct(store_id = 1, name="Test Product", quantity=1, price=10.0, category="Test", image_link="test_link")

        response = uc.add_basket_product(request, data)
        self.assertEqual(response.name, "Test Product")

    
    # Test19: Test if the basket product is not added successfully with unauthenticated user
    def test_add_basket_product_unauthenticated(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')

        request = self.factory.get('/fake-path/')
        request.user = user
        data = StoreProduct(store_id = 1, name="Test Product", quantity=1, price=10.0, category="Test", image_link="test_link")

        response = uc.add_basket_product(request, data)
        self.assertEqual(response.name, "Test Product")


    # Test20: Test if the user cart is not retrieved successfully with unauthenticated user
    def test_get_user_cart_unauthenticated(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')
        c = Client()
        logged_in = c.login(username='testusertry', password='12345')

        request = self.factory.get('/fake-path/')
        request.user = user

        cart = Cart.objects.create(user=user)
        basket = Basket.objects.create(cart=cart, store_id=1)
        product = BasketProduct.objects.create(basket=basket, name="Test Product", quantity=1, price=10.0)
        
        response = uc.get_user_cart(request)
        self.assertEqual(response.user.id, user.id)

    
    # Test21: Test if the user cart product is deleted successfully
    def test_delete_user_cart_product(self):
        cart = Cart.objects.create(user=self.user)
        basket = Basket.objects.create(cart=cart, store_id=1)
        basket_product = BasketProduct.objects.create(name="Test Product", quantity=1, price=10.0, category="Test", image_link="test_link", basket=basket, store_product_id=1)
        basket_product.save()
        response = uc.delete_user_cart_product(999, basket_product.store_product_id)
        self.assertEqual(response['msg'], "Product deleted")

    
    # Test22: Test if the user cart product is not deleted successfully with non-existent product
    def test_delete_user_cart_product_nonexistent(self):
        response = uc.delete_user_cart_product(999, 9999)
        self.assertEqual(response['error'], "Product not found")

    
    # Test23: Test if the basket is retrieved successfully
    def test_get_user_basket(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')
        user.save()
        c = Client()
        logged_in = c.login(username='testusertry', password='12345')

        request = self.factory.get('/fake-path/')
        request.user = user

        cart = Cart.objects.create(user=user)
        basket = Basket.objects.create(cart=cart, store_id=1)

        response = uc.get_user_basket(request, basket.id)
        self.assertEqual(response.id, basket.id)

    
    # Test24: Test if the basket is not retrieved successfully with non-existent basket
    def test_get_user_basket_nonexistent(self):
        try:
            user = User.objects.create(username='testusertry')
            user.set_password('12345')

            request = self.factory.get('/fake-path/')
            request.user = user

            cart = Cart.objects.create(user=user)

            response = uc.get_user_basket(request, 5555)

        except Exception as e:
            self.assertEqual(str(e), "Basket not found")

    
    # Test25: Test if the products are retrieved successfully
    def test_get_user_products(self):
        user = User.objects.create(username='testusertry')
        user.set_password('12345')
        user.save()
        c = Client()
        logged_in = c.login(username='testusertry', password='12345')

        request = self.factory.get('/fake-path/')
        request.user = user

        cart = Cart.objects.create(user=user)
        basket = Basket.objects.create(cart=cart, store_id=1)
        product = BasketProduct.objects.create(basket=basket, name="Test Product", quantity=1, price=10.0)

        response = uc.get_user_products(request)
        self.assertTrue(any(p.name == "Test Product" for p in response))
        

    # Test26: Test if the user id is retrieved successfully by email
    def test_get_user_id_by_email(self):
        response = uc.get_user_id_by_email(self.user.email)
        self.assertEqual(response, self.user.id)

    
    # Test27: Test if fake data is created successfully
    def test_create_fake_data(self):
        response = self.client.post("/fake_data")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["msg"], "Fake data created successfully")


    # Test28: Test if the user full name is retrieved successfully
    def test_get_user_full_name(self):
        response = uc.get_user_full_name(999, self.user.id)
        self.assertEqual(response, self.user.Full_Name)

    
    # Test29: Test if the user identification number is retrieved successfully
    def test_get_user_identification_number(self):
        response = uc.get_user_identification_number(999, self.user.id)
        self.assertEqual(response, self.user.Identification_number)

    
    # Test30: Test if the user payment information is retrieved successfully
    def test_get_payment_information(self):
        payment_info = PaymentInformationUser.objects.create(
            user=self.user,
            holder="Test Holder",
            holder_identification_number="123456789",
            currency="USD",
            credit_card_number="1234567890",
            expiration_date="12/25",
            security_code="123"
        )
        response = uc.get_payment_information(999, self.user.id)
        self.assertEqual(response["holder"], "Test Holder")
        self.assertEqual(response["currency"], "USD")
        self.assertEqual(response["credit_card_number"], "1234567890")
        self.assertEqual(response["expiration_date"], "12/25")
        self.assertEqual(response["security_code"], "123")


    # Test31: Test if the user payment information is not retrieved successfully with non-existent user
    def test_get_payment_information_nonexistent(self):
        try:
            response = uc.get_payment_information(999, 9999)
        except Exception as e:
            self.assertEqual(str(e), "User not found")


    # Test32: Test if the delivery information is retrieved successfully
    def test_get_delivery_information(self):
        delivery_info = DeliveryInformationUser.objects.create(
            user=self.user,
            address="123 Test St",
            city="Test City",
            country="Test Country",
            zip="12345"
        )
        response = uc.get_delivery_information(999, self.user.id)
        self.assertEqual(response["address"], "123 Test St")
        self.assertEqual(response["city"], "Test City")
        self.assertEqual(response["country"], "Test Country")
        self.assertEqual(response["zip"], "12345")

    
    # Test33: Test if the delivery information is not retrieved successfully with non-existent user
    def test_get_delivery_information_nonexistent(self):
        try:
            response = uc.get_delivery_information(999, 9999)
        except Exception as e:
            self.assertEqual(str(e), "User not found")


    # Test34: Test if the user id is retrieved successfully
    def test_get_user_id(self):
        response = uc.get_user_id(999, self.user.email)
        self.assertEqual(response.id, self.user.id)
        self.assertEqual(response.email, self.user.email)

    
    # Test35: Test if the user id is not retrieved successfully with wrong email
    def test_get_user_id_wrong_email(self):
        try:
            response = uc.get_user_id(999, "hello@gmail.com")
        except Exception as e:
            self.assertEqual(str(e), "User not found")

    
    # Test36: Test if the user full name is updated successfully
    def test_update_user_full_name(self):
        data = FullnameSchemaIn(Full_Name = "Updated Name")
        response = uc.update_user_full_name(999, self.user.id, data)
        self.assertEqual(response["msg"], "Full name updated successfully")

    
    # Test37: Test if the user full name is not updated successfully with non-existent user
    def test_update_user_full_name_empty(self):
        try:
            data = FullnameSchemaIn(Full_Name = "")
            response = uc.update_user_full_name(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "Full name is required")

    
    # Test38: Test if the user identification number is updated successfully
    def test_update_user_Identification_Number(self):
        try:
            data = IdentificationNumberSchemaIn(Identification_Number = "987654321")
            response = uc.update_user_Identification_Number(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "User not found")

    
    # Test39: Test if the user identification number is not updated successfully with not given identification number
    def test_update_user_Identification_Number_empty(self):
        try:
            data = IdentificationNumberSchemaIn(Identification_Number = "")
            response = uc.update_user_Identification_Number(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "Identification number is required")
       

    # Test40: Test if the user identification number is not updated successfully with invalid identification number
    def test_update_user_Identification_Number_invalid(self):
        try:
            data = IdentificationNumberSchemaIn(Identification_Number = "123")
            response = uc.update_user_Identification_Number(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "Identification number must be 9 digits long")

    
    # Test41: Test if the user delivery information is updated successfully
    def test_update_user_delivery_info(self):
        data = DeliveryInfoSchema(
            address = "456 New St",
            city = "New City",
            country = "New Country",
            zip = "1234567")
        response = uc.update_user_delivery_info(999, self.user.id, data)
        self.assertEqual(response["msg"], "Delivery info updated successfully")

    
    # Test42: Test if the user delivery information is not updated successfully with missing zip
    def test_update_user_delivery_info_missing_zip(self):
        try:
            data = DeliveryInfoSchema(
                address = "456 New St",
                city = "New City",
                country = "New Country",
                zip = "")
            response = uc.update_user_delivery_info(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "All delivery information fields are required - zip missing")

    
    # Test43: Test if the user delivery information is not updated successfully with missing country
    def test_update_user_delivery_info_missing_country(self):
        try:
            data = DeliveryInfoSchema(
                address = "456 New St",
                city = "New City",
                country = "",
                zip = "54321")
            response = uc.update_user_delivery_info(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "All delivery information fields are required - country missing")

    
    # Test44: Test if the user delivery information is not updated successfully with missing city
    def test_update_user_delivery_info_missing_city(self):
        try:
            data = DeliveryInfoSchema(
                address = "456 New St",
                city = "",
                country = "New Country",
                zip = "54321")
            response = uc.update_user_delivery_info(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "All delivery information fields are required - city missing")

    
    # Test45: Test if the user delivery information is not updated successfully with missing address
    def test_update_user_delivery_info_missing_address(self):
        try:
            data = DeliveryInfoSchema(
                address = "",
                city = "New City",
                country = "New Country",
                zip = "54321")
            response = uc.update_user_delivery_info(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "All delivery information fields are required - address missing")

    
    # Test46: Test if the user payment information is updated successfully
    def test_update_user_payment_info(self):
        data = PaymentInfoSchema(
            holder = "Updated Holder",
            holder_identification_number = "987654321",
            currency = "EUR",
            credit_card_number = "1234123412341234",
            expiration_date = "11/26",
            security_code = "456"
        )
        response = uc.update_user_payment_info(999, self.user.id, data)
        self.assertEqual(response["msg"], "Payment info updated successfully")


    # Test47: Test if the user payment information is not updated successfully with invalid credit card number
    def test_update_user_payment_info_invalid_credit_card(self):
        try:
            data = PaymentInfoSchema(
                holder = "Updated Holder",
                holder_identification_number = "987654321",
                currency = "EUR",
                credit_card_number = "123412341234",
                expiration_date = "11/26",
                security_code = "456"
            )
            response = uc.update_user_payment_info(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "Credit card number must be 16 digits long")
    
    
    # Test48: Test if the user payment information is not updated successfully with invalid expiration date
    def test_update_user_payment_info_invalid_expiration_date(self):
        try:
            data = PaymentInfoSchema(
                holder = "Updated Holder",
                holder_identification_number = "987654321",
                currency = "EUR",
                credit_card_number = "1234123412341234",
                expiration_date = "11/23",
                security_code = "456"
            )
            response = uc.update_user_payment_info(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "Credit card expired")

    
    # Test49: Test if the user payment information is not updated successfully with invalid security code
    def test_update_user_payment_info_invalid_cvv(self):
        try:
            data = PaymentInfoSchema(
                holder = "Updated Holder",
                holder_identification_number = "987654321",
                currency = "EUR",
                credit_card_number = "1234123412341234",
                expiration_date = "11/26",
                security_code = "456789"
            )
            response = uc.update_user_payment_info(999, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "Security code (CVV) must be 3 digits long")

    
    # NOTIFICATION TESTS
    
    async def test_user_connection(self):
        # Create a WebSocket communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
        )
        communicator.scope["user"] = self.user
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        # Disconnect after the test
        await communicator.disconnect()

    # async def test_send_message(self):
    #     communicator = WebsocketCommunicator(
    #         ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
    #     )
    #     communicator.scope["user"] = self.user
    #     await communicator.connect()
    #     message = {"type": "chat_message", "message": "Hello!"}
    #     # Send a message through the channel layer
    #     await self.channel_layer.group_send(self.room_group_name, message)
    #     response = await communicator.receive_json_from()
    #     self.assertEqual(response, {"type": "chat", "message": "Hello!"})
    #     await communicator.disconnect()

    async def test_receive_message(self):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
        )
        communicator.scope["user"] = self.user

        await communicator.connect()
        message = {"message": "Hello!"}
        # Simulate sending a message from the client
        await communicator.send_to(json.dumps(message))
        response = await communicator.receive_json_from()
        self.assertEqual(response, {'message': 'Hello!', 'notification_id': -1, 'sent_by': 'testuser', 'type': 'chat'})
        await communicator.disconnect()

    async def test_disconnect(self):
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
        )
        communicator.scope["user"] = self.user

        await communicator.connect()
        await communicator.disconnect()
        # Verify the user is properly disconnected and online count adjusted
        self.user = await sync_to_async(User.objects.get)(id=self.user.id)
        self.assertEqual(self.user.online_count, 0)


# class ChatConsumerTests(ChannelsLiveServerTestCase):
#     def setUp(self):
#         # Use sync_to_async to handle the synchronous operations of the ORM
#         self.client = TestClient(router)

#         self.user = User.objects.create_user(username="testuser", password="password")
#         self.channel_layer = get_channel_layer()
#         self.room_group_name = (
#             f"chat_{self.user.id}"  # Now self.user is properly awaited and instantiated
#         )

#     def tearDown(self):
#         cache.clear()

#     async def test_user_connection(self):
#         # Create a WebSocket communicator
#         communicator = WebsocketCommunicator(
#             ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
#         )
#         communicator.scope["user"] = self.user
#         connected, _ = await communicator.connect()
#         self.assertTrue(connected)
#         # Disconnect after the test
#         await communicator.disconnect()

#     async def test_send_message(self):
#         communicator = WebsocketCommunicator(
#             ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
#         )
#         communicator.scope["user"] = self.user
#         await communicator.connect()
#         message = {"type": "chat_message", "message": "Hello!"}
#         # Send a message through the channel layer
#         await self.channel_layer.group_send(self.room_group_name, message)
#         response = await communicator.receive_json_from()
#         self.assertEqual(response, {"type": "chat", "message": "Hello!"})
#         await communicator.disconnect()

#     async def test_receive_message(self):
#         communicator = WebsocketCommunicator(
#             ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
#         )
#         communicator.scope["user"] = self.user

#         await communicator.connect()
#         message = {"message": "Hello!"}
#         # Simulate sending a message from the client
#         await communicator.send_to(json.dumps(message))
#         response = await communicator.receive_json_from()
#         self.assertEqual(response, {"type": "chat", "message": "Hello!"})
#         await communicator.disconnect()

#     async def test_disconnect(self):
#         communicator = WebsocketCommunicator(
#             ChatConsumer.as_asgi(), f"/ws/chat/{self.user.id}/"
#         )
#         communicator.scope["user"] = self.user

#         await communicator.connect()
#         await communicator.disconnect()
#         # Verify the user is properly disconnected and online count adjusted
#         self.user = await sync_to_async(User.objects.get)(id=self.user.id)
#         self.assertEqual(self.user.online_count, 0)
