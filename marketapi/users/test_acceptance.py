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

    

    #ACCEPTANCE TESTS

    # 1. User Registration
    # Description: A new user registers an account.
    # Precondition: The user is not already registered.
    # Postcondition: The system is on.
    # Test Cases:
    # Successful registration with unique username and email.
    # Failed registration with an already existing username.
    # Failed registration with an already existing email.

    def test_register_user_success(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "newuser")
        self.assertEqual(response.json()["email"], "newuser@example.com")

    def test_register_user_existing_user(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)
        response = self.client.post("/register", json=data)
        self.assertEqual(response.status_code, 401)

    
    # 2. Guest Login as Member
    # Test Route – Positive
    # Case Description: A registered guest correctly enters their authentication
    # details to log into the system and successfully accesses the system as a
    # member.
    # Test Data: Correct authentication details (username, password).
    # Preconditions: The user is registered in the system but not logged in.
    # Expected Result: The system verifies the authentication details, logs the user
    # into the system as a member, and grants access to member-specific features.
    # Test Route – Positive (user tries to log in twice)
    # Case Description: A logged in guest correctly tries to log into the system.
    # Test Data: Logged in user, correct authentication details (username,
    # password).
    # Preconditions: The user is registered in the system and logged in.
    # Expected Result: The system identifies the user already logged in and
    # provides a prompt to the user that he is already logged in .
    # Test Route – Negative (Incorrect Authentication Details)
    # Case Description: A registered guest attempts to log in using incorrect
    # authentication details.
    # Test Data: Incorrect authentication details (username, password).
    # Preconditions: The user is registered in the system but not logged in.
    # Expected Result: The system fails to verify the incorrect details and prompts
    # the user to re-enter their details, denying access until the correct details are
    # provided.

    def test_login_user_positive(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')
        self.assertTrue(logged_in)

    def test_login_user_twice(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')
        logged_in = c.login(username='username', password='newpassword')
        self.assertTrue(logged_in)
        
    def test_login_invalid_credentials(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username1', password='newpassword1')
        self.assertFalse(logged_in)


    # 3. Member Logout
    # Test Route – Positive
    # Case Description: A member selects the option to log out of the system,
    # successfully logs out, and reverts to a guest status with their shopping cart
    # preserved.
    # Test Data: None required.
    # Preconditions: The user is logged into the system as a member.
    # Expected Result: The system effectively logs the user out, cancels their
    # member identification, reverts them to guest status, and ensures their
    # shopping cart remains intact for future sessions.
    # Test Route – Negative (Attempt to Log Out When Already Logged Out)
    # Case Description: A member who is already logged out attempts to log out
    # again.
    # Test Data: None required, simulate a user action where a logged-out member
    # tries to log out.
    # Preconditions: The user has already logged out but attempts to log out once
    # more.
    # Expected Result: The system detects that the user is not currently logged in as
    # a member and displays an appropriate error message indicating that they
    # cannot log out because they are not logged in.

    def test_logout_user_success(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')

        response = self.client.post("/logout")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["msg"], "Logged out")


    # 4. delete user account
    # Test Route – Positive
    # Case Description: A member selects the option to delete their account, confirms
    # the deletion, and successfully deletes their account from the system.
    # Test Data: None required.
    # Preconditions: The user is logged into the system as a member.
    # Expected Result: The system effectively deletes the user account.

    # Test Route – Negative (Attempt to Delete Account When not exist)
    # Case Description: trying to delete not existing user account
    # Test Data: None required.
    # Preconditions: The user trying to delete is not exist
    # Expected Result: The system detects that the user account is not exist and displays an appropriate error message indicating that the account
    # cannot be deleted.

    def test_delete_user_success(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')


        request = self.factory.get('/fake-path/')
        request.user = user

        response = uc.delete_user(request, user.id)
        self.assertEqual(response["msg"], "User deleted")


    def test_delete_user_nonexistent(self):
        try:
            data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
            response = self.client.post("/register", json=data)

            user = User.objects.create(username='username')
            user.set_password('newpassword')
            user.save()
            c = Client()
            logged_in = c.login(username='username', password='newpassword')


            request = self.factory.get('/fake-path/')
            request.user = user

            response = uc.delete_user(request, 9999)
        except Exception as e:
            self.assertEqual(str(e), "Unauthorized")

    # 5. Update User Account
    # Test Route – Positive
    # Case Description: A member selects the option to update their account details,
    # enters the new details, and successfully updates their account information.
    # Test Data: New account details.
    # Preconditions: The user is logged into the system as a member.
    # Expected Result: The system effectively updates the user account details.
    # Test Route – Negative (Attempt to Update Account When not exist)
    # Case Description: trying to update not existing user account
    # Test Data: New account details.
    # Preconditions: The user trying to update is not exist
    # Expected Result: The system detects that the user account is not exist and displays an appropriate error message indicating that the account
    # cannot be updated.
    # Test Route – Negative (Attempt to Update Account With Invalid Data)
    # Case Description: A member selects the option to update their account details,
    # enters invalid new details, and attempts to update their account information.
    # Test Data: Invalid new account details.
    # Preconditions: The user is logged into the system as a member.
    # Expected Result: The system detects the invalid data and displays an appropriate
    # error message indicating that the account cannot be updated with the invalid
    # data.
                                  
    def test_update_user_success(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')


        request = self.factory.get('/fake-path/')
        request.user = user

        data = UserRegisterSchema(username = "updateduser", email = "updated@example.com", password = "newpassword")
        response = uc.update_user(request, user.id, data)
        self.assertEqual(response.username, "updateduser")
        self.assertEqual(response.email, "updated@example.com")


    def test_update_user_invalid_details(self):
        try:
            data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
            response = self.client.post("/register", json=data)

            user = User.objects.create(username='username')
            user.set_password('newpassword')
            user.save()
            c = Client()
            logged_in = c.login(username='username', password='newpassword')

            data = {"username": "newuser1", "email": "newuser1@example.com", "password": "newpassword1"}
            response = self.client.post("/register", json=data)

            user1 = User.objects.create(username='username1')
            user1.set_password('newpassword1')
            user1.save()
            c = Client()
            logged_in = c.login(username='username1', password='newpassword1')


            request = self.factory.get('/fake-path/')
            request.user = user1

            data = UserRegisterSchema(username = "username", email = "newuser1@example.com", password = "newpassword1")
            response = uc.update_user(request, user1.id, data)
        except Exception as e:
            self.assertTrue(True)

    
    def test_update_user_nonexistent(self):
        try:
            data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
            response = self.client.post("/register", json=data)

            user = User.objects.create(username='username')
            user.set_password('newpassword')
            user.save()
            c = Client()
            logged_in = c.login(username='username', password='newpassword')


            request = self.factory.get('/fake-path/')
            request.user = user

            data = UserRegisterSchema(username = "updateduser", email = "updated@example.com", password = "newpassword")
            response = uc.update_user(request, 100, data)
        except Exception as e:
            self.assertEqual(str(e), "Unauthorized")

    # 6. add product to cart and delete it
    # Test Route – Positive
    # Case Description: A member selects the option to add a product to their cart,
    # successfully adds the product, and then deletes the product from their cart.
    # Test Data: Product details.
    # Preconditions: The user is logged into the system as a member.
    # Expected Result: The system effectively adds the product to the user’s cart and
    # then deletes the product from the cart.
    # Test Route – Negative (Attempt to Delete Product When not exist)
    # Case Description: trying to delete not existing product from cart
    # Test Data: Product details.
    # Preconditions: The user is logged into the system as a member.
    # Expected Result: The system detects that the product is not exist and displays an appropriate error message indicating that the product
    # cannot be deleted.
    # Test Route – Negative (Attempt to Add Product With Invalid Data)
    # Case Description: A member selects the option to add a product to their cart, enters
    # invalid product details, and attempts to add the product to their cart.
    # Test Data: Invalid product details.
    # Preconditions: The user is logged into the system as a member.
    # Expected Result: The system detects the invalid data and displays an appropriate
    # error message indicating that the product cannot be added to the cart with the
    # invalid data.

    def test_add_basket_product_and_delete_it(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')


        request = self.factory.get('/fake-path/')
        request.user = user

        data = StoreProduct(store_id = 1, name="Test Product", quantity=1, price=10.0, category="Test", image_link="test_link")

        response = uc.add_basket_product(request, data)

        response = uc.delete_user_cart_product(request, 1)
        self.assertEqual(response['msg'], "Product deleted")
    
    
    def test_delete_non_existed_product(self):
        try:
            data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
            response = self.client.post("/register", json=data)

            user = User.objects.create(username='username')
            user.set_password('newpassword')
            user.save()
            c = Client()
            logged_in = c.login(username='username', password='newpassword')


            request = self.factory.get('/fake-path/')
            request.user = user

            data = StoreProduct(store_id = 1, name="Test Product", quantity=1, price=10.0, category="Test", image_link="test_link")

            response = uc.delete_user_cart_product(request, 999)
        except Exception as e:
            self.assertEqual(str(e), "Product not found")

    
    #7. update user profile information
    # Test Route – Positive
    # Case Description: A member selects the option to update their profile information,
    # enters the new details, and successfully updates their profile information.
    # Test Data: New profile information.
    # Preconditions: The user is logged into the system as a member.
    # Expected Result: The system effectively updates the user profile information.
    # Test Route – Negative (Attempt to Update Profile Information When not exist)
    # Case Description: trying to update not existing user profile information
    # Test Data: New profile information.
    # Preconditions: The user trying to update is not exist
    # Expected Result: The system detects that the user profile information is not exist and displays an appropriate error message indicating that the profile
    # information cannot be updated.
    # Test Route – Negative (Attempt to Update Profile Information With Invalid Data)
    # Case Description: A member selects the option to update their profile information,
    # enters invalid new details, and attempts to update their profile information.
    # Test Data: Invalid new profile information.
    # Preconditions: The user is logged into the system as a member.
    # Expected Result: The system detects the invalid data and displays an appropriate
    # error message indicating that the profile information cannot be updated with the
    # invalid data.
    
    def test_update_user_identification(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')


        request = self.factory.get('/fake-path/')
        request.user = user

        data = IdentificationNumberSchemaIn(Identification_Number = "987654321")
        response = uc.update_user_Identification_Number(request, self.user.id, data)
        self.assertEqual(response['msg'], "Identification number updated successfully")

    
    def test_update_user_identification_not_exist_userID(self):
        try:
            data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
            response = self.client.post("/register", json=data)

            user = User.objects.create(username='username')
            user.set_password('newpassword')
            user.save()
            c = Client()
            logged_in = c.login(username='username', password='newpassword')


            request = self.factory.get('/fake-path/')
            request.user = user

            data = IdentificationNumberSchemaIn(Identification_Number = "987654321")
            response = uc.update_user_Identification_Number(request, 100, data)
        except Exception as e:
            self.assertEqual(str(e), "CustomUser matching query does not exist.")

    
    def test_update_user_identification_illegal(self):
        try:
            data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
            response = self.client.post("/register", json=data)

            user = User.objects.create(username='username')
            user.set_password('newpassword')
            user.save()
            c = Client()
            logged_in = c.login(username='username', password='newpassword')


            request = self.factory.get('/fake-path/')
            request.user = user

            data = IdentificationNumberSchemaIn(Identification_Number = "987654321151617")
            response = uc.update_user_Identification_Number(request, self.user.id, data)
        except Exception as e:
            self.assertEqual(str(e), "Identification number must be 9 digits long")

    
    def test_update_user_delivery_info(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')


        request = self.factory.get('/fake-path/')
        request.user = user

        data = DeliveryInfoSchema(
            address = "456 New St",
            city = "New City",
            country = "New Country",
            zip = "7654321")
        response = uc.update_user_delivery_info(request, self.user.id, data)
        self.assertEqual(response["msg"], "Delivery info updated successfully")


    def test_update_user_delivery_info_not_exist_userID(self):
        try:
            data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
            response = self.client.post("/register", json=data)

            user = User.objects.create(username='username')
            user.set_password('newpassword')
            user.save()
            c = Client()
            logged_in = c.login(username='username', password='newpassword')


            request = self.factory.get('/fake-path/')
            request.user = user

            data = DeliveryInfoSchema(
                address = "456 New St",
                city = "New City",
                country = "New Country",
                zip = "54321")
            response = uc.update_user_delivery_info(request, 1000, data)
        except Exception as e:
            self.assertTrue(True)

    
    def test_update_user_payment_info_not_exist_userID(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')


        request = self.factory.get('/fake-path/')
        request.user = user

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

    
    def test_update_user_payment_info(self):
        data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword"}
        response = self.client.post("/register", json=data)

        user = User.objects.create(username='username')
        user.set_password('newpassword')
        user.save()
        c = Client()
        logged_in = c.login(username='username', password='newpassword')


        request = self.factory.get('/fake-path/')
        request.user = user

        data = PaymentInfoSchema(
            holder = "Updated Holder",
            holder_identification_number = "987654321",
            currency = "EUR",
            credit_card_number = "1234123412341234",
            expiration_date = "11/26",
            security_code = "456"
        )
        response = uc.update_user_payment_info(999, self.user.id, data)
        self.assertEqual(response['msg'], "Payment info updated successfully")

