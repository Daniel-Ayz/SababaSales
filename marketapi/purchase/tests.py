from django.test import TestCase
from ninja.testing import TestClient

import store.api
from users.models import Cart, CustomUser
from .api import router
from store.api import router as store_router
from users.api import router as user_router

# Create your tests here.
class TestPurchase(TestCase):
    def setUp(self):
        self.client = TestClient(router)
        self.store_client = TestClient(store_router)
        self.user_client = TestClient(user_router)

        # self.products = {
        #     "product1": {"name": 'Product 1', "stock quantity": 10, "price": 10},
        #     "product2": {"name": 'Product 2', "stock quantity": 5, "price": 20},
        #     "product3": {"name": 'Product 3', "stock quantity": 3, "price": 30}
        # }
        # self.basket = {"Basket 1": self.products}
        # self.cart = {"Cart 1": self.basket}
        # self.user = {"User 1": self.cart}

        self.user_id = 1
        response = self.store_client.post(f'/stores?user_id={self.user_id}', json={
            "name": "Test Store",
            "description": "Test Description"
        })
        self.store_id = response.json()['store_id']

        response = self.user_client.post("/register", json={
            "username": "Test User",
            "email": "test@email.com",
            "password": "Test Password"})
        self.user_id = response.json()['id']
        self.user = response.json()
        
        # find the cart id of the cart which belongs to the user with user_id from the db
        response = self.user_client.get(f'/users/cart')

        response = self.client.post(f'/baskets?cart_id={self.cart_id}', json={"store id": self.store_id})
        self.basket_id = response.json()['basket_id']

        # Add product to basket
        response = self.client.post("/cart/products", json={
            "payload": { "quantity": 10, "name": "Test Product", "store_id": self.store_id}
        })


        # Add product to store
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Test Product", "quantity": 10, "initial_price": 100}
        })

        # Add owner to store
        self.owner2_id = 2
        response = self.client.post("/stores/{store_id}/assign_owner", json={
            "user_id": self.owner2_id, "store_id": self.store_id, "assigned_by": self.user_id
        })

        # Add manager to store
        self.manager_id = 3
        response = self.client.post("/stores/{store_id}/assign_manager", json={
            "user_id": self.manager_id, "store_id": self.store_id, "assigned_by": self.owner2_id
        })

        # Add manager permissions
        response = self.client.post(
            "/stores/{store_id}/change_manager_permissions?assigning_owner_id=" + self.owner2_id.__str__(), json={
                "manager": {"user_id": self.manager_id, "store_id": self.store_id},
                "payload": {"can_add_product": True, "can_edit_product": True, "can_delete_product": True},
            })

        # Set purchase policy
        response = self.client.post("/stores/{store_id}/add_purchase_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"min_items_per_purchase": 1}
        })

        # Set discount policy
        response = self.client.post("/stores/{store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"min_items": 5, "min_price": 500}
        })


    def test_make_purchase_of_all_products_in_cart_positive(self):
        # Perform the test
        response = self.client.post(f'/purchase/{self.cart_id}/make_purchase')
        self.assertEqual(response.status_code, 200)

        # Assertions
        # Verify that the purchase is successfully completed
        self.assertEqual(response.json()['status'], 'success')

        # Check if the order approval is received
        self.assertTrue(response.json()['order_approval'])


    def test_supply_service_failure(self):

        # Simulate failure in supply service verification
        supply_service_verification = False
        
        # Perform the test
        response = self.client.post(f'/purchase/{self.cart_id}/make_purchase')
        self.assertEqual(response.status_code, 400)

        # Assertions
        # Verify that the purchase is canceled
        self.assertEqual(response.json()['status'], 'failure')

        # Check if the error message is sent to the guest
        self.assertEqual(response.json()['error_message'], 'Supply service verification failed')


    def test_payment_failure(self):
        # Simulate failure in payment verification
        payment_verification = False
        
        # Perform the test
        response = self.client.post(f'/purchase/{self.cart_id}/make_purchase')
        self.assertEqual(response.status_code, 400)

        # Assertions
        # Verify that the purchase is canceled
        self.assertEqual(response.json()['status'], 'failure')

        # Check if the error message is sent to the guest
        self.assertEqual(response.json()['error_message'], 'Payment verification failed')


    def test_purchase_unavailable_product(self):
        # Prepare test data

        # Add product to basket
        response = self.client.post("/cart/products", json={
            "payload": { "quantity": 11, "name": "Test Product", "store_id": self.store_id}
        })

        # Perform the test
        response = self.client.post(f'/purchase/{self.cart_id}/make_purchase')
        self.assertEqual(response.status_code, 400)

        # Assertions
        # Verify that the purchase is canceled
        self.assertEqual(response.json()['status'], 'failure')

        # Check if the error message is sent to the guest
        self.assertEqual(response.json()['error_message'], 'Unavailable product in the shopping cart')


    def test_get_purchase_history_positive(self):
        # Perform the test
        response = self.client.get(f'/purchase/{self.user_id}/get_purchase_history')
        self.assertEqual(response.status_code, 200)

        # Assertions
        # Verify that the system returns the store purchase history
        self.assertTrue(response.json()['purchase_history'])


    def test_get_purchase_history_store_not_exist(self):
        # Prepare test data
        invalid_user_id = 999
        
        # Perform the test
        response = self.client.get(f'/purchase/{invalid_user_id}/get_purchase_history')
        self.assertEqual(response.status_code, 404)

        # Assertions
        # Verify that the system returns an appropriate message indicating that the store does not exist
        self.assertEqual(response.json()['message'], 'User not found')


    # def test_get_purchase_history_actor_not_store_owner(self):
        # Prepare test data
        #     regular_member_id = 1

        # Perform the test
        #     response = self.client.get(f'/api/purchase/history/{regular_member_id}')
        #     self.assertEqual(response.status_code, 403)

        # Assertions
        # Verify that the system returns an appropriate message indicating that the actor is not a store owner
    #     self.assertEqual(response.json()['message'], 'You are not a store owner')