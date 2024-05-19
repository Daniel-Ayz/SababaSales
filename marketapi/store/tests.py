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

    def test_get_store(self):
        response = self.client.get(f'/stores/1')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        json_data_excluded = {key: value for key, value in json_data.items() if key != 'created_at'}
        self.assertEqual(json_data_excluded, {
            "id": self.store_id,
            "name": "Test Store",
            "description": "Test Description",
            "is_active": True
        })

    def test_get_all_stores(self):
        response = self.client.get(f'/stores')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_store_with_invalid_id(self):
        response = self.client.get(f'/stores/100')
        self.assertEqual(response.status_code, 404)

    def test_add_product(self):
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.manager_id, "store_id": self.store_id},
            "payload": {"name": "New Product", "quantity": 5, "initial_price": 50}
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Product added successfully"})

    def test_remove_product(self):
        response = self.client.delete("/stores/{store_id}/remove_product?product_name=Test Product", json={
            "user_id": self.user_id, "store_id": self.store_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Product removed successfully"})

    def test_edit_product(self):
        response = self.client.put("/stores/{store_id}/edit_product", json={
            "role": {"user_id": self.owner2_id, "store_id": self.store_id},
            "payload": {"name": "Test Product", "quantity": 5, "initial_price": 50}
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Product edited successfully"})

    def test_get_products(self):
        response = self.client.get(f'/stores/{self.store_id}/get_products', json={
            "user_id": self.user_id, "store_id": self.store_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_purchase_product(self):
        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product",
            "quantity": 1
        }])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Products purchased successfully", "total_price": 100})

    def test_get_discount_policies(self):
        response = self.client.get(f'/stores/{self.store_id}/get_discount_policies', json={
            "user_id": self.user_id, "store_id": self.store_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_add_product_with_invalid_data(self):
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Check false", "quantity": -5, "initial_price": -50}
        })
        self.assertEqual(response.status_code, 400)

    def test_manager_without_permissions_add_product(self):
        response = self.client.post("/stores/{store_id}/assign_manager", json={
            "user_id": 4, "store_id": self.store_id, "assigned_by": self.owner2_id
        })
        self.client.post("/stores/{store_id}/change_manager_permissions?assigning_owner_id=2", json={
            "manager": {"user_id": 4, "store_id": self.store_id},
            "payload": {"can_add_product": False, "can_edit_product": False, "can_delete_product": False}
        })
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": 4, "store_id": self.store_id},
            "payload": {"name": "New Product", "quantity": 5, "initial_price": 50}
        })
        self.assertEqual(response.status_code, 403)

    def test_remove_owner(self):
        self.owner3_id = 10
        self.manager2_id = 11
        # response = self.client.post("/stores/{store_id}/assign_owner", json={
        #     "user_id": self.owner3_id, "store_id": self.store_id, "assigned_by": self.user_id
        # })
        # print(response.content)
        # response = self.client.post("/stores/{store_id}/assign_manager", json={
        #                  "user_id": self.manager2_id, "store_id": self.store_id, "assigned_by": self.owner3_id
        # })
        # print(response.content)
        response = self.client.delete("/stores/{store_id}/remove_owner", json={
            "user_id": self.owner2_id, "store_id": self.store_id, "removed_by": self.user_id
        })
        # print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Owner removed successfully"})
        response = self.client.get(f'/stores/{self.store_id}/get_managers', json={
            "user_id": self.user_id, "store_id": self.store_id
        })
        # print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)  #manager should have been removed because owner is removed

    def test_remove_non_existent_product(self):
        response = self.client.delete("/stores/{store_id}/remove_product?product_name=Non Existent Product", json={
            "user_id": self.user_id, "store_id": self.store_id
        })
        self.assertEqual(response.status_code, 404)

    def test_edit_non_existent_product(self):
        response = self.client.put("/stores/{store_id}/edit_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Non Existent Product", "quantity": 5, "initial_price": 50}
        })
        self.assertEqual(response.status_code, 404)

    def test_purchase_product_with_insufficient_quantity(self):
        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product",
            "quantity": 100
        }])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Insufficient quantity of Test Product in store"})

    def test_concurrent_product_purchase(self):
        # Create a second user
        self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.owner2_id, "store_id": self.store_id},
            "payload": {"name": "Test Product 2", "quantity": 1, "initial_price": 100}})

        # Both users try to purchase the last product at the same time
        response1 = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product 2",
            "quantity": 1
        }])
        response2 = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product 2",
            "quantity": 1
        }])
        # One of the requests should fail
        self.assertTrue(response1.status_code == 404 or response2.status_code == 404)

    def test_concurrent_product_deletion_and_purchase(self):
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.owner2_id, "store_id": self.store_id},
            "payload": {"name": "Test Product 3", "quantity": 1, "initial_price": 100}})
        # print(response.content)

        # Store owner deletes a product
        delete_response = self.client.delete("/stores/{store_id}/remove_product?product_name=Test Product 3", json={
            "user_id": self.user_id, "store_id": self.store_id
        })
        # print(delete_response.content)
        # At the same time, another user tries to buy the product
        purchase_response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product 3",
            "quantity": 1
        }])
        # print(purchase_response.content)

        # The purchase request should fail
        self.assertEqual(purchase_response.status_code, 404)

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
