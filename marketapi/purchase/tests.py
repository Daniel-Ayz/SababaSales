from django.test import TestCase, TransactionTestCase
from ninja.testing import TestClient

import store.api
from users.models import Cart, CustomUser, Basket, BasketProduct
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

        self.user_id = 1
        response = self.store_client.post(
            f"/stores?user_id={self.user_id}",
            json={"name": "Test Store", "description": "Test Description"},
        )
        self.store_id = response.json()["store_id"]

        response = self.user_client.post(
            "/register",
            json={
                "username": "Test User",
                "email": "test@email.com",
                "password": "Test Password",
            },
        )
        self.user_id = response.json()["id"]
        self.user = CustomUser.objects.get(id=self.user_id)

        # Add product to store
        self.Product_1_Quality = 10
        response = self.store_client.post(
            "/stores/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Test Product",
                    "quantity": self.Product_1_Quality,
                    "initial_price": 100,
                    "category": "Test Category",
                },
            },
        )

        # find the cart id of the cart which belongs to the user with user_id from the db
        self.cart = Cart.objects.create(user=self.user)
        self.cart_id = self.cart.id

        self.basket = Basket.objects.create(cart=self.cart, store_id=self.store_id)
        self.basket_id = self.basket.id

        BasketProduct.objects.create(
            quantity=10, name="Test Product", basket=self.basket, category="Test Category"
        )

        # Add owner to store
        self.owner2_id = 2
        response = self.store_client.post(
            "/stores/{store_id}/assign_owner",
            json={
                "user_id": self.owner2_id,
                "store_id": self.store_id,
                "assigned_by": self.user_id,
            },
        )

        # Add manager to store
        self.manager_id = 3
        response = self.store_client.post(
            "/stores/{store_id}/assign_manager",
            json={
                "user_id": self.manager_id,
                "store_id": self.store_id,
                "assigned_by": self.owner2_id,
            },
        )

        # Add manager permissions
        response = self.store_client.post(
            "/stores/{store_id}/change_manager_permissions?assigning_owner_id="
            + self.owner2_id.__str__(),
            json={
                "manager": {"user_id": self.manager_id, "store_id": self.store_id},
                "payload": {
                    "can_add_product": True,
                    "can_edit_product": True,
                    "can_delete_product": True,
                },
            },
        )

        # Set purchase policy
        response = self.store_client.post(
            "/stores/{store_id}/add_purchase_policy",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {"min_items_per_purchase": 1},
            },
        )

    # Test 1: Positive test case, make purchase of all products in cart
    def test_make_purchase_of_all_products_in_cart_positive(self):
        # Ensure that the purchase was not made
        history_before = self.client.get(f"/{self.user_id}/get_purchase_history")

        response = self.client.post(f"/{self.user_id}/{self.cart_id}/make_purchase")
        self.assertEqual(response.status_code, 200)

        # Verify that the purchase is successfully completed
        self.assertEqual(response.json()["message"], "Purchase added successfully")
        
        # Ensure that the purchase was not made
        history_after = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertNotEqual(history_before.json(), history_after.json())
        self.assertEqual(history_after.json()[0]["purchase_id"], 1)
        self.assertEqual(history_after.json()[0]["cart"], self.cart_id)
        self.assertEqual(history_after.json()[0]["total_price"], '1000.00')
        self.assertEqual(history_after.json()[0]["total_quantity"], 10)


    # Test 2: Negative test case, make purchase of all products in cart with delivery failure
    def test_supply_service_failure(self):
      
       # Ensure that the purchase was not made
        history_before = self.client.get(f"/{self.user_id}/get_purchase_history")

        response = self.client.post(
            f"/{self.user_id}/{self.cart_id}/make_purchase_delivery_fail"
        )
        self.assertEqual(response.status_code, 401)  # check if fail code
        self.assertEqual(
            response.json()["detail"], "Unauthorized"
        )  # check if right fail message
        # Ensure that the purchase was not made
        history_after = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertEqual(history_before.json(), history_after.json())

    # Test 3: Negative test case, make purchase of all products in cart with payment failure
    def test_payment_failure(self):
        # Ensure that the purchase was not made
        history_before = self.client.get(f"/{self.user_id}/get_purchase_history")

        response = self.client.post(
            f"/{self.user_id}/{self.cart_id}/make_purchase_payment_fail"
        )
        self.assertEqual(response.status_code, 401)  # check if fail code
        self.assertEqual(
            response.json()["detail"], "Unauthorized"
        )  # check if right fail message
        
        # Ensure that the purchase was not made
        history_after = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertEqual(history_before.json(), history_after.json())


    # Test 4: Negative test case, make purchase of all products in cart with insufficient quantity
    def test_purchase_unavailable_product(self):
        # Ensure that the purchase was not made
        history_before = self.client.get(f"/{self.user_id}/get_purchase_history")
        
        # Add product to basket with insufficient quantity
        insufficient_quantity = self.Product_1_Quality + 100
        BasketProduct.objects.update(
            quantity=insufficient_quantity, name="Test Product", basket=self.basket, category="Test Category"
        )
        response = self.client.post(f"/{self.user_id}/{self.cart_id}/make_purchase")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"], "Insufficient quantity of Test Product in store"
        )
        # Ensure that the purchase was not made
        history_after = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertEqual(history_before.json(), history_after.json())
        

    # Test 5: Positive test case, get purchase history
    def test_get_purchase_history_positive(self):
        # Perform the test
        response = self.client.get(f"/{self.user_id}/get_purchase_history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    # Test 6: Negative test case, get purchase history of a user that does not exist
    def test_get_purchase_history_store_not_exist(self):
        # Prepare test data
        invalid_user_id = 999

        # Perform the test
        response = self.client.get(f"/{invalid_user_id}/get_purchase_history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    # Test 7: positive test case, get a purchase receipt after a successful purchase
    def test_get_purchase_receipt_positive(self):

        response = self.client.post(f"/{self.user_id}/{self.cart_id}/make_purchase")
        self.assertEqual(response.status_code, 200)

        # Verify that the purchase is successfully completed
        self.assertEqual(response.json()["message"], "Purchase added successfully")

        # Perform the test
        response = self.client.get(f"/{self.user_id}/get_purchase_receipt?purchase_id=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["purchase_id"], 1)
        self.assertEqual(response.json()["cart"], self.cart_id)
        self.assertEqual(response.json()["total_price"], '1000.00')
        self.assertEqual(response.json()["total_quantity"], 10) 


    # def test_get_purchase_history_actor_not_store_owner(self):
    # Prepare test data
    #     regular_member_id = 1

    # Perform the test
    #     response = self.client.get(f'/api/history/{regular_member_id}')
    #     self.assertEqual(response.status_code, 403)

    # Assertions
    # Verify that the system returns an appropriate message indicating that the actor is not a store owner
    #     self.assertEqual(response.json()['message'], 'You are not a store owner')
