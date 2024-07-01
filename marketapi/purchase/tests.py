from django.test import TransactionTestCase
from ninja.testing import TestClient

from users.models import Cart, Basket, BasketProduct
from .api import router
from store.api import router as store_router
from users.api import router as user_router


# Create your tests here.
class TestPurchase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = TestClient(router)
        self.store_client = TestClient(store_router)
        self.user_client = TestClient(user_router)

        # Register user and set up store
        response = self.user_client.post(
            "/register",
            json={
                "username": "Test User",
                "email": "test@email.com",
                "password": "Test Password",
            },
        )
        self.user_id = response.json()["id"]

        response = self.store_client.post(
            f"/?user_id={self.user_id}",
            json={"name": "Test Store", "description": "Test Description"},
        )
        self.store_id = response.json()["store_id"]

        self.cart = Cart.objects.create(user_id=self.user_id)
        self.cart_id = self.cart.id

        self.basket = Basket.objects.create(cart=self.cart, store_id=self.store_id)
        self.basket_id = self.basket.id

        BasketProduct.objects.create(
            quantity=10,
            name="Test Product",
            basket=self.basket,
            category="Test Category",
        )

        # @router.post("/{store_id}/add_product")
        # def add_product(request, role: RoleSchemaIn, payload: StoreProductSchemaIn):
        #     return sc.add_product(request, role, payload)

        response = self.store_client.post(
            f"/{self.store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Test Product",
                    "initial_price": 100.00,
                    "quantity": 10,
                    "category": "Test Category",
                    "image_link": "Test Image Link",
                },
            },
        )

        # Additional setup for user details
        self.user_client.post(
            f"/{self.user_id}/update_Full_Name",
            json={"Full_Name": "Test User"},
        )
        self.user_client.post(
            f"/{self.user_id}/update_Identification_Number",
            json={"Identification_Number": "123456789"},
        )
        self.user_client.post(
            f"/{self.user_id}/update_delivery_info",
            json={
                "address": "Test Address",
                "city": "Test City",
                "country": "Test Country",
                "zip": "123456",
            },
        )
        self.user_client.post(
            f"/{self.user_id}/update_payment_info",
            json={
                "holder": "Test User",
                "holder_identification_number": "123456789",
                "currency": "USD",
                "credit_card_number": "123456789",
                "expiration_date": "23/01",
                "security_code": "123",
            },
        )

    def test_make_purchase_of_all_products_in_cart_positive(self):
        # Test 1: Positive test case, make purchase of all products in cart
        history_before = self.client.get(f"/{self.user_id}/get_purchase_history")

        response = self.client.post(f"/{self.user_id}/{self.cart_id}/make_purchase")
        self.assertEqual(response.status_code, 200)  # Purchase should be successful

        # Verify that the purchase is successfully completed
        self.assertEqual(response.json()["message"], "Purchase added successfully")

        # Ensure that the purchase history is updated
        history_after = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertNotEqual(history_before.json(), history_after.json())
        self.assertEqual(history_after.json()[0]["purchase_id"], 1)
        self.assertEqual(history_after.json()[0]["cart_id"], self.cart_id)
        self.assertEqual(history_after.json()[0]["total_price"], 1000.00)
        self.assertEqual(history_after.json()[0]["total_quantity"], 10)

    def test_supply_service_failure(self):
        # Test 2: Negative test case, make purchase of all products in cart with delivery failure
        history_before = self.client.get(f"/{self.user_id}/get_purchase_history")

        self.user_client.post(
            f"/{self.user_id}/update_delivery_info",
            json={
                "address": "Test Address",
                "city": "Test City",
                "country": "Test Country",
                "zip": "",  # Change ZIP to empty string to cause delivery failure
            },
        )

        response = self.client.post(f"/{self.user_id}/{self.cart_id}/make_purchase")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid Delivery Information")

        # Ensure that the purchase was not made
        history_after = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertEqual(history_before.json(), history_after.json())

    def test_payment_failure(self):
        # Test 3: Negative test case, make purchase of all products in cart with payment failure
        history_before = self.client.get(f"/{self.user_id}/get_purchase_history")

        self.user_client.post(
            f"/{self.user_id}/update_payment_info",
            json={
                "holder": "Test User",
                "holder_identification_number": "123456789",
                "currency": "USD",
                "credit_card_number": "123456789",
                "expiration_date": "00",  # invalid expiration date
                "security_code": "123",
            },
        )
        response = self.client.post(f"/{self.user_id}/{self.cart_id}/make_purchase")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid Payment Information")

        # Ensure that the purchase was not made
        history_after = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertEqual(history_before.json(), history_after.json())

    def test_purchase_unavailable_product(self):
        # Test 4: Negative test case, make purchase of all products in cart with insufficient quantity
        history_before = self.client.get(f"/{self.user_id}/get_purchase_history")

        # Add product to basket with insufficient quantity
        insufficient_quantity = 100  # Assuming it's higher than the available quantity
        BasketProduct.objects.filter(
            name="Test Product",
            basket=self.basket,
            category="Test Category",
        ).update(quantity=insufficient_quantity)

        response = self.client.post(f"/{self.user_id}/{self.cart_id}/make_purchase")
        self.assertEqual(response.status_code, 400)  # Expecting a failure status code
        self.assertEqual(
            response.json()["detail"], "Insufficient quantity of Test Product in store"
        )

        # Ensure that the purchase was not made
        history_after = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertEqual(history_before.json(), history_after.json())

    def test_get_purchase_history_positive(self):
        # Test 5: Positive test case, get purchase history
        response = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_purchase_history_store_not_exist(self):
        # Test 6: Negative test case, get purchase history of a user that does not exist
        invalid_user_id = 999  # Assuming this user ID does not exist

        response = self.client.get(f"/{invalid_user_id}/get_purchase_history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_purchase_receipt_positive(self):
        # Test 7: positive test case, get a purchase receipt after a successful purchase
        response = self.client.post(f"/{self.user_id}/{self.cart_id}/make_purchase")
        self.assertEqual(response.status_code, 200)  # Purchase should be successful
        self.assertEqual(response.json()["message"], "Purchase added successfully")

        response = self.client.get(
            f"/{self.user_id}/get_purchase_receipt?purchase_id=1"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["purchase_id"], 1)
        self.assertEqual(response.json()["cart_id"], self.cart_id)
        self.assertEqual(response.json()["total_price"], 1000.00)
        self.assertEqual(response.json()["total_quantity"], 10)
