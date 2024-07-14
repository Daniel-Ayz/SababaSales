from django.test import TransactionTestCase
from ninja.testing import TestClient

from store.models import Bid, Manager, ManagerPermission, Owner, Store, StoreProduct
from users.models import Cart, Basket, BasketProduct, DeliveryInformationUser, PaymentInformationUser
from .api import router
from store.api import router as store_router
from users.api import router as user_router

from purchase.services.payment_service import AbstractPaymentService
from purchase.services.delivery_service import AbstractDeliveryService

from django.core.cache import cache


# Create your tests here.
class TestPurchase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = TestClient(router)
        self.store_client = TestClient(store_router)
        self.user_client = TestClient(user_router)
        self.payment_service = AbstractPaymentService()
        self.delivery_service = AbstractDeliveryService()

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

        DeliveryInformationUser.objects.filter(user_id=self.user_id).update(zip="")

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

        PaymentInformationUser.objects.filter(user_id=self.user_id).update(
            expiration_date="00"
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

    def test_make_bid_purchase_positive(self):
        # Test 7: Positive test case, make bid purchase successfully
        store = Store.objects.create(
                    name="Test Store",
                    description="nice store",
                    is_active=True,
                )
        store_id = store.id
        owner = Owner.objects.create(user_id=1, store=store, is_founder=True)
        manager = Manager.objects.create(
            user_id=1, store=store, assigned_by=owner
        )
        manager_permissions = ManagerPermission.objects.create(
            manager=manager,
            can_add_product=True,
            can_delete_product=True,
            can_edit_product=True,
            can_add_discount_policy=True,
            can_remove_discount_policy=True,
            can_add_purchase_policy=True,
            can_remove_purchase_policy=True,
        )

        product = StoreProduct.objects.create(
                    store=store,
                    name="Test Product",
                    category="Test Category",
                    quantity=10,
                    initial_price=100.00,
                    image_link="Test Image Link",
                )
        
        bid = Bid.objects.create(
            store=store,
            product=product,
            price=50.00,
            quantity=5,
            #status="active",
            user_id = self.user_id,
            can_purchase = True
        )
        bid_id = bid.id

        history_before = self.client.get(f"/{self.user_id}/get_bid_purchase_history")
        response = self.client.post(
            f"/{self.user_id}/{store_id}/{bid_id}/make_bid_purchase"
        )

        # Ensure that the purchase history is updated
        history_after = self.client.get(f"/{self.user_id}/get_bid_purchase_history")
        self.assertNotEqual(history_before.json(), history_after.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Bid Purchase added successfully")

    def test_make_bid_purchase_negative_not_accepted(self):
        # Test 7: Positive test case, make bid purchase successfully
        store = Store.objects.create(
                    name="Test Store",
                    description="nice store",
                    is_active=True,
                )
        store_id = store.id
        owner = Owner.objects.create(user_id=1, store=store, is_founder=True)
        manager = Manager.objects.create(
            user_id=1, store=store, assigned_by=owner
        )
        manager_permissions = ManagerPermission.objects.create(
            manager=manager,
            can_add_product=True,
            can_delete_product=True,
            can_edit_product=True,
            can_add_discount_policy=True,
            can_remove_discount_policy=True,
            can_add_purchase_policy=True,
            can_remove_purchase_policy=True,
        )

        product = StoreProduct.objects.create(
                    store=store,
                    name="Test Product",
                    category="Test Category",
                    quantity=10,
                    initial_price=100.00,
                    image_link="Test Image Link",
                )
        
        bid = Bid.objects.create(
            store=store,
            product=product,
            price=50.00,
            quantity=5,
            #status="active",
            user_id = self.user_id,
            can_purchase = False
        )
        bid_id = bid.id

        response = self.client.post(
            f"/{self.user_id}/{store_id}/{bid_id}/make_bid_purchase"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Bid has not been accepted by all managers or owners")
        

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

    def test_get_purchase_receipt_negative(self):
        # Test 8: Negative test case, get a purchase receipt that does not exist
        response = self.client.get(
            f"/{self.user_id}/get_purchase_receipt?purchase_id=1"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Purchase not found")

    def test_get_bid_purchase_receipt_positive(self):
        # Test 9: positive test case, get a bid purchase receipt after a successful bid purchase
        store = Store.objects.create(
                    name="Test Store",
                    description="nice store",
                    is_active=True,
                )
        store_id = store.id
        owner = Owner.objects.create(user_id=1, store=store, is_founder=True)
        manager = Manager.objects.create(
            user_id=1, store=store, assigned_by=owner
        )
        manager_permissions = ManagerPermission.objects.create(
            manager=manager,
            can_add_product=True,
            can_delete_product=True,
            can_edit_product=True,
            can_add_discount_policy=True,
            can_remove_discount_policy=True,
            can_add_purchase_policy=True,
            can_remove_purchase_policy=True,
        )

        product = StoreProduct.objects.create(
                    store=store,
                    name="Test Product",
                    category="Test Category",
                    quantity=10,
                    initial_price=100.00,
                    image_link="Test Image Link",
                )
        
        bid = Bid.objects.create(
            store=store,
            product=product,
            price=50.00,
            quantity=5,
            #status="active",
            user_id = self.user_id,
            can_purchase = True
        )
        bid_id = bid.id

        response = self.client.post(
            f"/{self.user_id}/{store_id}/{bid_id}/make_bid_purchase"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Bid Purchase added successfully")

        response = self.client.get(
            f"1/get_bid_purchase_receipt"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["purchase_id"], 1)
        self.assertEqual(response.json()["bid_id"], bid_id)
        self.assertEqual(response.json()["total_price"], 50.00)
        self.assertEqual(response.json()["total_quantity"], 5)
        self.assertEqual(response.json()["product_name"], "Test Product")

    def test_get_bid_purchase_receipt_negative(self):
        # Test 10: Negative test case, get a bid purchase receipt that does not exist
        response = self.client.get(
            f"1/get_bid_purchase_receipt"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Bid Purchase not found")

    def test_get_bid_purchase_history_positive(self):
        # Test 11: Positive test case, get bid purchase history
        store = Store.objects.create(
                    name="Test Store",
                    description="nice store",
                    is_active=True,
                )
        store_id = store.id
        owner = Owner.objects.create(user_id=1, store=store, is_founder=True)
        manager = Manager.objects.create(
            user_id=1, store=store, assigned_by=owner
        )
        manager_permissions = ManagerPermission.objects.create(
            manager=manager,
            can_add_product=True,
            can_delete_product=True,
            can_edit_product=True,
            can_add_discount_policy=True,
            can_remove_discount_policy=True,
            can_add_purchase_policy=True,
            can_remove_purchase_policy=True,
        )

        product = StoreProduct.objects.create(
                    store=store,
                    name="Test Product",
                    category="Test Category",
                    quantity=10,
                    initial_price=100.00,
                    image_link="Test Image Link",
                )
        
        bid = Bid.objects.create(
            store=store,
            product=product,
            price=50.00,
            quantity=5,
            #status="active",
            user_id = self.user_id,
            can_purchase = True
        )
        bid_id = bid.id

        response = self.client.post(
            f"/{self.user_id}/{store_id}/{bid_id}/make_bid_purchase"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Bid Purchase added successfully")

        response = self.client.get(
            f"/{self.user_id}/get_bid_purchase_history"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)


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
