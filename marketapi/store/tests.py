from django.test import TestCase
from ninja.testing import TestClient

from .api import router


class StoreAPITestCase(TestCase):

    def setUp(self):
        self.client = TestClient(router)
        self.user_id = 1

        data = {
            "name": "Test Store",
            "description": "Test Description"
        }
        response = self.client.post(f'/stores?user_id={self.user_id}', json=data)
        self.store_id = response.json()['store_id']
        print(f'store id: {self.store_id}')

        # Add product to store
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Test Product", "quantity": 10, "initial_price": 100}
        })
        print(f'product added: {response.json()["message"]}')

        # Add owner to store
        self.owner2_id = 2
        response = self.client.post("/stores/{store_id}/assign_owner", json={
            "user_id": self.owner2_id, "store_id": self.store_id, "assigned_by": self.user_id
        })
        print(response.content)
        print(f'owner added: {response.json()["message"]}')


        # Add manager to store
        self.manager_id = 3
        response = self.client.post("/stores/{store_id}/assign_manager", json={
            "user_id": self.manager_id, "store_id": self.store_id, "assigned_by": self.owner2_id
        })
        print(response.content)
        print(f'manager added: {response.json()["message"]}')

        # Add manager permissions
        response = self.client.post("/stores/{store_id}/change_manager_permissions?assigning_owner_id="+self.owner2_id.__str__(), json={
            "manager": {"user_id": self.manager_id, "store_id": self.store_id},
            "payload": {"can_add_product": True, "can_edit_product": True, "can_delete_product": True},
        })
        print(f'manager permissions added:  {response.json()["message"]}')

        # Set purchase policy
        response = self.client.post("/stores/{store_id}/add_purchase_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"min_items_per_purchase": 1}
        })
        print(f'purchase policy added:  {response.json()["message"]}')

        # Set discount policy
        response = self.client.post("/stores/{store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"min_items": 5, "min_price": 500}
        })
        print(f'discount policy added: {response.json()["message"]}')

    def test_add_product(self):
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.manager_id, "store_id": self.store_id},
            "payload": {"name": "New Product", "quantity": 5, "initial_price": 50}
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Product added successfully"})

    def test_remove_product(self):
        response = self.client.delete("/stores/{store_id}/remove_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "product_name": "Test Product"
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"message": "Product not found"})

    def test_edit_product(self):
        response = self.client.put("/stores/{store_id}/edit_product", json={
            "role": {"user_id": self.owner2_id, "store_id": self.store_id},
            "payload": {"name": "New Product", "quantity": 5, "initial_price": 50}
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Product edited successfully"})

    def test_get_products(self):
        response = self.client.get("/stores/{store_id}/get_products", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id}
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_purchase_product(self):
        response = self.client.put("/stores/{store_id}/purchase_product", json=[{
            "store_id": self.store_id,
            "product_name": "New Product",
            "quantity": 1
        }])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Products purchased successfully", "total_price": 50})

    def test_add_product_with_invalid_data(self):
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Check false", "quantity": -5, "initial_price": -50}
        })
        self.assertEqual(response.status_code, 400)

    def test_remove_non_existent_product(self):
        response = self.client.delete("/stores/{store_id}/remove_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "product_name": "Non Existent Product"
        })
        self.assertEqual(response.status_code, 404)

    def test_edit_non_existent_product(self):
        response = self.client.put("/stores/{store_id}/edit_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Non Existent Product", "quantity": 5, "initial_price": 50}
        })
        self.assertEqual(response.status_code, 404)

    def test_purchase_product_with_insufficient_quantity(self):
        response = self.client.put("/stores/{store_id}/purchase_product", json=[{
            "store_id": self.store_id,
            "product_name": "New Product",
            "quantity": 100
        }])
        self.assertEqual(response.status_code, 400)

    def test_concurrent_product_purchase(self):
        # Create a second user
        self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.owner2_id, "store_id": self.store_id},
            "payload": {"name": "Test Product", "quantity": 1, "initial_price": 100}})

        # Both users try to purchase the last product at the same time
        response1 = self.client.put("/stores/{store_id}/purchase_product", json=[{
            "store_id": self.store_id,
            "product_name": "Test Product",
            "quantity": 1
        }])
        response2 = self.client.put("/stores/{store_id}/purchase_product", json=[{
            "store_id": self.store_id,
            "product_name": "Test Product",
            "quantity": 1
        }])
        # One of the requests should fail
        self.assertTrue(response1.status_code == 400 or response2.status_code == 400)

    def test_concurrent_product_deletion_and_purchase(self):
        self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.owner2_id, "store_id": self.store_id},
            "payload": {"name": "Test Product 2", "quantity": 1, "initial_price": 100}})

        # Store owner deletes a product
        delete_response = self.client.delete("/stores/{store_id}/remove_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "product_name": "Test Product 2"
        })

        # At the same time, another user tries to buy the product
        purchase_response = self.client.put("/stores/{store_id}/purchase_product", json=[{
            "store_id": self.store_id,
            "product_name": "Test Product 2",
            "quantity": 1
        }])

        # The purchase request should fail
        self.assertEqual(purchase_response.status_code, 400)

    # def test_concurrent_manager_appointment(self):
    #
    #     # Both owners try to appoint the same user as a manager at the same time
    #     response1 = self.client.post("/stores/{store_id}/add_manager", json={
    #         "role": {"user_id": self.user_id, "store_id": self.store_id},
    #         "payload": {"user_id": self.owner2.id}
    #     })
    #     response2 = self.client.post("/stores/{store_id}/add_manager", json={
    #         "role": {"user_id": self.user_id, "store_id": self.store_id},
    #         "payload": {"user_id": self.owner2.id}
    #     })
    #
    #     # One of the requests should fail
    #     self.assertTrue(response1.status_code == 400 or response2.status_code == 400)
