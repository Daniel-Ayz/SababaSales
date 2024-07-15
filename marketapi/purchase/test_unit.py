from django.test import TransactionTestCase
from ninja.testing import TestClient

from store.models import Bid, Manager, ManagerPermission, Owner, Store, StoreProduct
from users.models import Cart, Basket, BasketProduct, DeliveryInformationUser, PaymentInformationUser
from .api import router
from store.api import router as store_router
from users.api import router as user_router

from purchase.services.payment_service import AbstractPaymentService
from purchase.services.delivery_service import AbstractDeliveryService
from purchase.purchase_controller import purchaseController

from django.core.cache import cache


class TestPurchaseUnit(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = TestClient(router)
        self.store_client = TestClient(store_router)
        self.user_client = TestClient(user_router)
        self.payment_service = AbstractPaymentService()
        self.delivery_service = AbstractDeliveryService()
        self.pc = purchaseController()

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
                "zip": "1234567",
            },
        )
        self.user_client.post(
            f"/{self.user_id}/update_payment_info",
            json={
                "holder": "Test User",
                "holder_identification_number": "123456789",
                "currency": "USD",
                "credit_card_number": "1234567890123456",
                "expiration_date": "01/30",
                "security_code": "262",
            },
        )

    def tearDown(self):
        cache.clear()

    def test_purchase_invalid_user(self):
        # Test 5: Negative test case, make purchase of all products in cart with invalid user
        invalid_user_id = 999
        response = self.client.post(f"/{invalid_user_id}/{self.cart_id}/make_purchase")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "User not found")

    def test_purchase_invalid_cart(self):
        # Test 6: Negative test case, make purchase of all products in cart with invalid cart
        invalid_cart_id = 999
        response = self.client.post(f"/{self.user_id}/{invalid_cart_id}/make_purchase")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "No Cart matches the given query.")
    
    def test_purchase_invalid_product(self):
        # Test 7: Negative test case, make purchase of all products in cart with invalid product
        BasketProduct.objects.filter(
            name="Test Product",
            basket=self.basket,
            category="Test Category",
        ).delete()

        response = self.client.post(f"/{self.user_id}/{self.cart_id}/make_purchase")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], 'No products to purchase')

    def test_get_purchase_history_positive(self):
        # Test 5: Positive test case, get purchase history
        response = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_purchase_history_negative(self):
        # Test 6: Negative test case, get purchase history of a user that does not exist
        invalid_user_id = 999
        response = self.client.get(f"/{invalid_user_id}/get_purchase_history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_bid_purchase_history_positive(self):
        # Test 7: Positive test case, get bid purchase history
        response = self.client.get(f"/{self.user_id}/get_bid_purchase_history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_bid_purchase_history_negative(self):
        # Test 8: Negative test case, get bid purchase history of a user that does not exist
        invalid_user_id = 999
        response = self.client.get(f"/{invalid_user_id}/get_bid_purchase_history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    #Unit tests for payment_service.py
    def test_payment_service_is_expired(self):
        # Test 8: Positive test case, check if a credit card is expired
        self.assertTrue(self.payment_service.is_expired("01/20"))

    def test_payment_service_is_not_expired(self):
        # Test 9: Negative test case, check if a credit card is not expired
        self.assertFalse(self.payment_service.is_expired("01/30"))

    def test_payment_service_make_payment_positive(self):
        # Test 10: Positive test case, make payment successfully
        payment_details = {
            "holder": "Test User",
            "holder_identification_number": "123456789",
            "currency": "USD",
            "credit_card_number": "1234567890123456",
            "expiration_date": "01/30",
            "security_code": "262",
            "total_price": 1000.00,
        }

        response = self.payment_service.process_payment(payment_details)
        self.assertTrue(response["result"])
        self.assertNotEqual(response["transaction_id"], -1)

    def test_payment_service_make_payment_invalid_holder(self):
        # Test 11: Negative test case, make payment with invalid holder
        payment_details = {
            "holder": "",
            "holder_identification_number": "123456789",
            "currency": "USD",
            "credit_card_number": "1234567890123456",
            "expiration_date": "01/30",
            "security_code": "262",
            "total_price": 1000,
        }

        with self.assertRaises(Exception) as context:
            self.payment_service.process_payment(payment_details)
        self.assertEqual(str(context.exception), "Invalid Payment Information")

    def test_payment_service_make_payment_invalid_holder_identification_number(self):
        # Test 12: Negative test case, make payment with invalid holder identification number
        payment_details = {
            "holder": "Test User",
            "holder_identification_number": "12345678",
            "currency": "USD",
            "credit_card_number": "1234567890123456",
            "expiration_date": "01/30",
            "security_code": "262",
            "total_price": 1000,
        }

        with self.assertRaises(Exception) as context:
            self.payment_service.process_payment(payment_details)
        self.assertEqual(str(context.exception), "Invalid Payment Information")

    def test_payment_service_make_payment_invalid_currency(self):
        # Test 13: Negative test case, make payment with invalid currency
        payment_details = {
            "holder": "Test User",
            "holder_identification_number": "123456789",
            "currency": "",
            "credit_card_number": "1234567890123456",
            "expiration_date": "01/30",
            "security_code": "262",
            "total_price": 1000,
        }

        with self.assertRaises(Exception) as context:
            self.payment_service.process_payment(payment_details)
        self.assertEqual(str(context.exception), "Invalid Payment Information")

    def test_payment_service_make_payment_invalid_credit_card_number(self):
        # Test 14: Negative test case, make payment with invalid credit card number
        payment_details = {
            "holder": "Test User",
            "holder_identification_number": "123456789",
            "currency": "USD",
            "credit_card_number": "123456789012345",
            "expiration_date": "01/30",
            "security_code": "262",
            "total_price": 1000,
        }

        with self.assertRaises(Exception) as context:
            self.payment_service.process_payment(payment_details)
        self.assertEqual(str(context.exception), "Invalid Payment Information")

    def test_payment_service_make_payment_invalid_expiration_date(self):
        # Test 15: Negative test case, make payment with invalid expiration date
        payment_details = {
            "holder": "Test User",
            "holder_identification_number": "123456789",
            "currency": "USD",
            "credit_card_number": "1234567890123456",
            "expiration_date": "00",
            "security_code": "262",
            "total_price": 1000,
        }

        with self.assertRaises(Exception) as context:
            self.payment_service.process_payment(payment_details)
        self.assertEqual(str(context.exception), "Invalid Payment Information")

    def test_payment_service_make_payment_invalid_security_code(self):
        # Test 16: Negative test case, make payment with invalid security code
        payment_details = {
            "holder": "Test User",
            "holder_identification_number": "123456789",
            "currency": "USD",
            "credit_card_number": "1234567890123456",
            "expiration_date": "01/30",
            "security_code": "26",
            "total_price": 1000,
        }

        with self.assertRaises(Exception) as context:
            self.payment_service.process_payment(payment_details)
        self.assertEqual(str(context.exception), "Invalid Payment Information")

    def test_payment_service_make_payment_invalid_total_price(self):
        # Test 17: Negative test case, make payment with invalid total price
        payment_details = {
            "holder": "Test User",
            "holder_identification_number": "123456789",
            "currency": "USD",
            "credit_card_number": "1234567890123456",
            "expiration_date": "01/30",
            "security_code": "262",
            "total_price": 0,
        }

        with self.assertRaises(Exception) as context:
            self.payment_service.process_payment(payment_details)
        self.assertEqual(str(context.exception), "Invalid Payment Information")

    def test_payment_service_make_payment_bad_cvv(self):
        # Test 18: Negative test case, make payment with invalid security code
        payment_details = {
            "holder": "Test User",
            "holder_identification_number": "123456789",
            "currency": "USD",
            "credit_card_number": "1234567890123456",
            "expiration_date": "01/30",
            "security_code": "984",
            "total_price": 1000,
        }

        response = self.payment_service.process_payment(payment_details)
        self.assertFalse(response["result"])
        self.assertEqual(response["transaction_id"], -1)

    def test_payment_service_cancel_payment_positive(self):
        # Test 19: Positive test case, cancel payment successfully
        payment_details = {
            "holder": "Test User",
            "holder_identification_number": "123456789",
            "currency": "USD",
            "credit_card_number": "1234567890123456",
            "expiration_date": "01/30",
            "security_code": "262",
            "total_price": 1000.00,
        }

        transaction_id = self.payment_service.process_payment(payment_details)["transaction_id"]

        response = self.payment_service.cancel_payment(transaction_id)
        self.assertTrue(response["result"])

    
    #Unit tests for delivery_service.py
    def test_delivery_service_create_shipment_positive(self):
        # Test 20: Positive test case, create shipment successfully
        delivery_method = {
            "address": "Test Address",
            "city": "Test City",
            "country": "Test Country",
            "zip": "1234567",
            "name": "Test User",
        }

        response = self.delivery_service.create_shipment(delivery_method)
        self.assertTrue(response["result"])
        self.assertNotEqual(response["transaction_id"], -1)

    def test_delivery_service_create_shipment_invalid_address(self):
        # Test 21: Negative test case, create shipment with invalid address
        delivery_method = {
            "address": "",
            "city": "Test City",
            "country": "Test Country",
            "zip": "1234567",
            "name": "Test User",
        }

        with self.assertRaises(Exception) as context:
            self.delivery_service.create_shipment(delivery_method)
        self.assertEqual(str(context.exception), "Invalid Delivery Information")

    def test_delivery_service_create_shipment_invalid_city(self):
        # Test 22: Negative test case, create shipment with invalid city
        delivery_method = {
            "address": "Test Address",
            "city": "",
            "country": "Test Country",
            "zip": "1234567",
            "name": "Test User",
        }

        with self.assertRaises(Exception) as context:
            self.delivery_service.create_shipment(delivery_method)
        self.assertEqual(str(context.exception), "Invalid Delivery Information")

    def test_delivery_service_create_shipment_invalid_country(self):
        # Test 23: Negative test case, create shipment with invalid country
        delivery_method = {
            "address": "Test Address",
            "city": "Test City",
            "country": "",
            "zip": "1234567",
            "name": "Test User",
        }

        with self.assertRaises(Exception) as context:
            self.delivery_service.create_shipment(delivery_method)
        self.assertEqual(str(context.exception), "Invalid Delivery Information")

    def test_delivery_service_create_shipment_invalid_zip(self):
        # Test 24: Negative test case, create shipment with invalid zip
        delivery_method = {
            "address": "Test Address",
            "city": "Test City",
            "country": "Test Country",
            "zip": "123",
            "name": "Test User",
        }

        with self.assertRaises(Exception) as context:
            self.delivery_service.create_shipment(delivery_method)
        self.assertEqual(str(context.exception), "Invalid Delivery Information")

    def test_delivery_service_create_shipment_invalid_name(self):
        # Test 25: Negative test case, create shipment with invalid name
        delivery_method = {
            "address": "Test Address",
            "city": "Test City",
            "country": "Test Country",
            "zip": "1234567",
            "name": "",
        }

        with self.assertRaises(Exception) as context:
            self.delivery_service.create_shipment(delivery_method)
        self.assertEqual(str(context.exception), "Invalid Delivery Information")

    def test_delivery_service_cancel_shipment_positive(self):
        # Test 26: Positive test case, cancel shipment successfully
        transaction_id = self.delivery_service.create_shipment(
            {
                "address": "Test Address",
                "city": "Test City",
                "country": "Test Country",
                "zip": "1234567",
                "name": "Test User",
            }
        )["transaction_id"]

        response = self.delivery_service.cancel_shipment(transaction_id)
        self.assertTrue(response["result"])


    def test_get_delivery_info_positive(self):
        # Test 27: Positive test case, get delivery information
        response = self.pc.get_delivery_info_dict("", 1)
        self.assertEqual(response["address"], "Test Address")
        self.assertEqual(response["city"], "Test City")
        self.assertEqual(response["country"], "Test Country")
        self.assertEqual(response["zip"], "1234567")

    def test_get_delivery_info_negative(self):
        # Test 28: Negative test case, get delivery information of a user that does not exist
        with self.assertRaises(Exception) as context:
            self.pc.get_delivery_info_dict("", 999)
        self.assertEqual(str(context.exception), "User not found")

    def test_get_payment_info_positive(self):
        # Test 29: Positive test case, get payment information
        response = self.pc.get_payment_info_dict("", 1)
        self.assertEqual(response["holder"], "Test User")
        self.assertEqual(response["holder_identification_number"], "123456789")
        self.assertEqual(response["currency"], "USD")
        self.assertEqual(response["credit_card_number"], "1234567890123456")
        self.assertEqual(response["expiration_date"], "01/30")
        self.assertEqual(response["security_code"], "262")

    def test_get_payment_info_negative(self):
        # Test 30: Negative test case, get payment information of a user that does not exist
        with self.assertRaises(Exception) as context:
            self.pc.get_payment_info_dict("", 999)
        self.assertEqual(str(context.exception), "User not found")