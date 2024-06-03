import json

from django.test import TestCase
from ninja.testing import TestClient

from .api import router


def string_to_list(string):
    jsonDec = json.decoder.JSONDecoder()
    return jsonDec.decode(string)


class StoreAPITestCase(TestCase):

    def setUp(self):
        self.client = TestClient(router)
        self.user_id = 1

        data = {
            "name": "Dairy Store",
            "description": "Store for dairy products"
        }
        response = self.client.post(f'/stores?user_id={self.user_id}', json=data)
        self.store_id = response.json()['store_id']

        data = {
            "name": "Meat Store",
            "description": "Store for meat products"
        }
        response = self.client.post(f'/stores?user_id={self.user_id}', json=data)
        self.store_id2 = response.json()['store_id']

        # Add product to store
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Milk", "quantity": 100, "initial_price": 7, "category": "Dairy"}
        })
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Cheese", "quantity": 50, "initial_price": 15, "category": "Dairy"}
        })
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Bread Loaf", "quantity": 100, "initial_price": 5, "category": "Pastry"}
        })
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Bun", "quantity": 100, "initial_price": 2, "category": "Pastry"}
        })
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Cottage Cheese", "quantity": 100, "initial_price": 3, "category": "Dairy"}
        })
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Yogurt", "quantity": 100, "initial_price": 4, "category": "Dairy"}
        })
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Pasta", "quantity": 100, "initial_price": 10, "category": "Pasta"}
        })

        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id2},
            "payload": {"name": "Steak", "quantity": 10, "initial_price": 100, "category": "Meat"}
        })

        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Test Product", "quantity": 5, "initial_price": 50, "category": "Test Category"}
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

        reponse = self.client.post("/stores/{store_id}/add_purchase_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id2},
            "payload": {"max_items_per_purchase": 10}
        })

        # # Set discount policy
        # response = self.client.post("/stores/{store_id}/add_discount_policy", json={
        #     "role": {"user_id": self.user_id, "store_id": self.store_id},
        #     "payload": {"min_items": 5, "min_price": 500}
        # })

    def test_get_store(self):
        response = self.client.get(f'/stores/1')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        json_data_excluded = {key: value for key, value in json_data.items() if key != 'created_at'}
        self.assertEqual(json_data_excluded, {
            "id": self.store_id,
            "name": "Dairy Store",
            "description": "Store for dairy products",
            "is_active": True
        })

    def test_get_all_stores(self):
        response = self.client.get(f'/stores')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_store_with_invalid_id(self):
        response = self.client.get(f'/stores/100')
        self.assertEqual(response.status_code, 404)

    def test_add_product(self):
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.manager_id, "store_id": self.store_id},
            "payload": {"name": "New Product", "quantity": 5, "initial_price": 50, "category": "New Category"}
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
            "payload": {"name": "Test Product", "quantity": 5, "initial_price": 50, "category": "New Category"}
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Product edited successfully"})

    def test_get_products(self):
        response = self.client.get(f'/stores/{self.store_id}/get_products', json={
            "user_id": self.user_id, "store_id": self.store_id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 8)

    def test_purchase_product(self):
        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product",
            "quantity": 1,
            "category": "Test Category"
        }])
        self.assertEqual(response.status_code, 200)
        assert response.json()["total_price"] == 50.0

    def test_add_simple_discount_policy(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "percentage": 15.0,
            "applicable_products": ["Milk"],
            "applicable_categories": ["Dairy"]
        }

        # Add the simple discount policy
        response = self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": simple_discount_payload
        })

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json() == "Simple discount policy added successfully"

        # Get the discount policies to verify the added discount
        response = self.client.get(f"/stores/{self.store_id}/get_discount_policies", json={
            "user_id": self.user_id,
            "store_id": self.store_id
        })

        # Verify the response status code
        assert response.status_code == 200

        # Parse the response data
        policies = response.json()
        assert len(policies) > 0

        # Verify the added simple discount policy is in the response
        added_policy = next((policy for policy in policies if policy["percentage"] == 15.0), None)
        assert added_policy is not None
        assert added_policy["applicable_products"][0]["name"] == "Milk"
        assert added_policy["store"]["id"] == self.store_id
        assert string_to_list(added_policy["applicable_categories"]) == ["Dairy"]
        assert added_policy["is_root"] is True

    def test_add_conditional_discount_policy(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 15.0,
            "applicable_products": ["Milk"]
        }

        condition = {
            "applies_to": "products",
            "name_of_apply": "Milk",
            "condition": "at_least",
            "value": 5

        }

        # Add the conditional discount policy
        conditional_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "condition": condition,
            "discount": simple_discount_payload
        }

        # Add the conditional discount policy
        response = self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": conditional_discount_payload
        })

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json() == "Conditional discount policy added successfully"

        # Get the discount policies to verify the added discount
        response = self.client.get(f"/stores/{self.store_id}/get_discount_policies", json={
            "user_id": self.user_id,
            "store_id": self.store_id
        })

        # Verify the response status code
        assert response.status_code == 200

        # Parse the response data
        policies = response.json()
        assert len(policies) > 0

        # Verify the added conditional discount policy is in the response
        added_policy = next((policy for policy in policies), None)
        category = string_to_list(added_policy["discount"]["applicable_categories"])
        assert added_policy is not None
        assert added_policy["store"]["id"] == self.store_id
        assert added_policy["is_root"] is True

    def test_add_composite_discount_policy(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 15.0,
            "applicable_products": ["Milk"]
        }
        simple_discount_payload2 = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 10.0,
            "applicable_products": ["Cheese"]
        }

        condition1 = {
            "applies_to": "category",
            "name_of_apply": "Dairy",
            "condition": "at_least",
            "value": 1
        }

        condition2 = {
            "applies_to": "category",
            "name_of_apply": "Pastry",
            "condition": "at_least",
            "value": 1
        }


        conditions = [condition1, condition2]
        combine_function = 'logical_and'

        composite_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "discounts": [simple_discount_payload, simple_discount_payload2],
            "combine_function": combine_function,
            "conditions": conditions
        }

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": composite_discount_payload
        })

        response = self.client.get(f"/stores/{self.store_id}/get_discount_policies", json={
            "user_id": self.user_id,
            "store_id": self.store_id
        })

        policies = response.json()
        added_policy = next((policy for policy in policies), None)
        assert added_policy is not None
        assert added_policy["store"]["id"] == self.store_id
        assert added_policy["is_root"] is True

    def test_remove_discount_policy(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "percentage": 15.0,
            "applicable_products": ["Milk"],
            "applicable_categories": ["Dairy"]
        }

        # Add the simple discount policy
        response = self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": simple_discount_payload
        })

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json() == "Simple discount policy added successfully"
        #remove the discount policy
        response = self.client.delete(f"/stores/{self.store_id}/remove_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"store_id": self.store_id, "discount_id": 1}
        })

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json().get("message") == "Discount policy removed successfully"

        #check if the discount policy is removed
        response = self.client.get(f"/stores/{self.store_id}/get_discount_policies", json={
            "user_id": self.user_id,
            "store_id": self.store_id
        })

        # Verify the response status code
        assert response.status_code == 200
        policies = response.json()
        assert len(policies) == 0

    def test_apply_simple_discount_policy_1(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "percentage": 50.0,
            "applicable_categories": ["Dairy"]
        }

        # Add the simple discount policy
        response = self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": simple_discount_payload
        })

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json() == "Simple discount policy added successfully"

        # Purchase a product
        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Milk",
            "category": "Dairy",
            "quantity": 5
        }])

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json() == {"message": "Products purchased successfully", "total_price": 17.5,
                                   "original_price": 35.0, "original_prices": [{'Milk': 35.0}]}
        assert response.json()["total_price"] == 17.5

    def test_apply_simple_discount_policy_2(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "percentage": 20.0,
            "applicable_categories": ["all"]
        }

        # Add the simple discount policy
        response = self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": simple_discount_payload
        })

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json() == "Simple discount policy added successfully"

        # Purchase a product
        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Milk",
            "category": "Dairy",
            "quantity": 5
        },
            {
                "product_name": "Cheese",
                "category": "Dairy",
                "quantity": 5
            }])

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json()["total_price"] == 88.0
        assert response.json()["original_price"] == 110.0

    def test_apply_conditional_discount_policy(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 10.0,
            "applicable_products": ["Milk"]
        }

        condition = {
            "applies_to": "price",
            "name_of_apply": "total_price",
            "condition": "greater_than",
            "value": 200
        }

        conditional_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "condition": condition,
            "discount": simple_discount_payload
        }

        # Add the simple discount policy
        response = self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": conditional_discount_payload
        })

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json() == "Conditional discount policy added successfully"

        # Purchase a product
        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Milk",
            "category": "Dairy",
            "quantity": 50
        },
            {
                "product_name": "Cheese",
                "category": "Dairy",
                "quantity": 20
            }])
        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json()["total_price"] == 615.0
        assert response.json()["original_price"] == 650.0

    def test_conditional_discount_policy_doesnt_apply(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 10.0,
            "applicable_products": ["Milk"]
        }

        condition = {
            "applies_to": "price",
            "name_of_apply": "total_price",
            "condition": "greater_than",
            "value": 200
        }

        conditional_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "condition": condition,
            "discount": simple_discount_payload
        }

        # Add the simple discount policy
        response = self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": conditional_discount_payload
        })

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json() == "Conditional discount policy added successfully"

        # Purchase a product
        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Milk",
            "category": "Dairy",
            "quantity": 5
        },
            {
                "product_name": "Cheese",
                "category": "Dairy",
                "quantity": 5
            }])

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json()["total_price"] == 110.0
        assert response.json()["original_price"] == 110.0

    def test_apply_composite_discount_policy_xor(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 10.0,
            "applicable_categories": ["Dairy"]
        }

        condition1 = {
            "applies_to": "category",
            "name_of_apply": "Dairy",
            "condition": "at_least",
            "value": 1
        }
        condition2 = {
            "applies_to": "category",
            "name_of_apply": "Pastry",
            "condition": "at_least",
            "value": 1
        }


        conditions = [condition1, condition2]
        combine_function = 'logical_xor'

        composite_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "discounts": [simple_discount_payload],
            "combine_function": combine_function,
            "conditions": conditions
        }

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": composite_discount_payload
        })

        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Milk",
            "category": "Dairy",
            "quantity": 5
        }])

        assert response.status_code == 200
        assert response.json()["total_price"] == 31.5
        assert response.json()["original_price"] == 35.0

    def test_doesnt_apply_composite_discount_policy_xor(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 10.0,
            "applicable_categories": ["Dairy"]
        }

        condition1 = {
            "applies_to": "category",
            "name_of_apply": "Dairy",
            "condition": "at_least",
            "value": 1
        }
        condition2 = {
            "applies_to": "category",
            "name_of_apply": "Pastry",
            "condition": "at_least",
            "value": 1
        }

        conditions = [condition1, condition2]
        combine_function = 'logical_xor'

        composite_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "discounts": [simple_discount_payload],
            "combine_function": combine_function,
            "conditions": conditions
        }

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": composite_discount_payload
        })

        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Milk",
            "category": "Dairy",
            "quantity": 5
        },
            {
                "product_name": "Bread Loaf",
                "category": "Pastry",
                "quantity": 5
            }])


        assert response.status_code == 200
        assert response.json()["total_price"] == 60.0
        assert response.json()["original_price"] == 60.0

    def test_apply_composite_discount_policy_and(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 5.0,
            "applicable_categories": ["Pastry"]
        }

        condition1 = {
            "applies_to": "product",
            "name_of_apply": "Bun",
            "condition": "at_least",
            "value": 5
        }

        condition2 = {
            "applies_to": "product",
            "name_of_apply": "Bread Loaf",
            "condition": "at_least",
            "value": 2
        }

        conditions = [condition1, condition2]
        combine_function = 'logical_and'

        composite_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "discounts": [simple_discount_payload],
            "combine_function": combine_function,
            "conditions": conditions
        }

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": composite_discount_payload
        })

        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Bun",
            "category": "Pastry",
            "quantity": 5
        },
            {
                "product_name": "Bread Loaf",
                "category": "Pastry",
                "quantity": 3
            }])

        assert response.status_code == 200
        assert response.json()["total_price"] == 23.75
        assert response.json()["original_price"] == 25.0

    def test_doesnt_apply_composite_discount_policy_and(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 5.0,
            "applicable_categories": ["Pastry"]
        }

        condition1 = {
            "applies_to": "product",
            "name_of_apply": "Bun",
            "condition": "at_least",
            "value": 5
        }

        condition2 = {
            "applies_to": "product",
            "name_of_apply": "Bread Loaf",
            "condition": "at_least",
            "value": 2
        }

        conditions = [condition1, condition2]
        combine_function = 'logical_and'

        composite_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "discounts": [simple_discount_payload],
            "combine_function": combine_function,
            "conditions": conditions
        }

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": composite_discount_payload
        })

        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Bun",
            "category": "Pastry",
            "quantity": 5
        },
            {
                "product_name": "Bread Loaf",
                "category": "Pastry",
                "quantity": 1
            }])

        print(response.json())
        assert response.status_code == 200
        assert response.json()["total_price"] == 15
        assert response.json()["original_price"] == 15

    def test_apply_composite_discount_policy_or(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 5.0,
            "applicable_categories": ["Dairy"]
        }

        condition1 = {
            "applies_to": "product",
            "name_of_apply": "Cottage Cheese",
            "condition": "at_least",
            "value": 3
        }

        condition2 = {
            "applies_to": "product",
            "name_of_apply": "Yogurt",
            "condition": "at_least",
            "value": 2
        }

        conditions = [condition1, condition2]
        combine_function = 'logical_or'

        composite_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "discounts": [simple_discount_payload],
            "combine_function": combine_function,
            "conditions": conditions
        }

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": composite_discount_payload
        })

        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Cottage Cheese",
            "category": "Dairy",
            "quantity": 3
        },
            {
                "product_name": "Yogurt",
                "category": "Dairy",
                "quantity": 1
            }])


        print(response.json())

        assert response.status_code == 200
        assert response.json()["total_price"] == 12.35
        assert response.json()["original_price"] == 13

    def test_doesnt_apply_composite_discount_policy_or(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 5.0,
            "applicable_categories": ["Dairy"]
        }

        condition1 = {
            "applies_to": "product",
            "name_of_apply": "Cottage Cheese",
            "condition": "at_least",
            "value": 3
        }

        condition2 = {
            "applies_to": "product",
            "name_of_apply": "Yogurt",
            "condition": "at_least",
            "value": 2
        }

        conditions = [condition1, condition2]
        combine_function = 'logical_or'

        composite_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "discounts": [simple_discount_payload],
            "combine_function": combine_function,
            "conditions": conditions
        }

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": composite_discount_payload
        })

        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Cottage Cheese",
            "category": "Dairy",
            "quantity": 2
        },
            {
                "product_name": "Yogurt",
                "category": "Dairy",
                "quantity": 1
            }])


        assert response.status_code == 200
        assert response.json()["total_price"] == 10
        assert response.json()["original_price"] == 10

    def test_apply_composite_discount_policy_max(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 17.0,
            "applicable_products": ["Milk"]
        }

        simple_discount_payload2 = {
            "store_id": self.store_id,
            "is_root": False,
            "percentage": 5.0,
            "applicable_products": ["Pasta"]
        }

        conditions = []
        combine_function = 'max'

        composite_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "discounts": [simple_discount_payload, simple_discount_payload2],
            "combine_function": combine_function,
            "conditions": conditions
        }

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": composite_discount_payload
        })

        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Milk",
            "category": "Dairy",
            "quantity": 5
        },
            {
                "product_name": "Pasta",
                "category": "Pasta",
                "quantity": 5
            }])

        assert response.status_code == 200
        assert response.json()["total_price"] == 79.05
        assert response.json()["original_price"] == 85

    def test_apply_composite_discount_policy_addition(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "percentage": 5.0,
            "applicable_categories": ["Dairy"]
        }
        simple_discount_payload2 = {
            "store_id": self.store_id,
            "is_root": True,
            "percentage": 20.0,
            "applicable_categories": ["all"]
        }

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": simple_discount_payload
        })

        self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": simple_discount_payload2
        })

        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Milk",
            "category": "Dairy",
            "quantity": 5
        }])

        assert response.status_code == 200
        assert response.json()["total_price"] == 26.25
        assert response.json()["original_price"] == 35


    def test_remove_discount_policy(self):
        simple_discount_payload = {
            "store_id": self.store_id,
            "is_root": True,
            "percentage": 15.0,
            "applicable_categories": ["Dairy"]
        }

        # Add the simple discount policy
        response = self.client.post(f"/stores/{self.store_id}/add_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": simple_discount_payload
        })

        #remove
        response = self.client.delete(f"/stores/{self.store_id}/remove_discount_policy", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"store_id": self.store_id, "discount_id": 1}
        })

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json().get("message") == "Discount policy removed successfully"

        #check if the discount policy is removed
        response = self.client.get(f"/stores/{self.store_id}/get_discount_policies", json={
            "user_id": self.user_id,
            "store_id": self.store_id
        })

        # Verify the response status code
        assert response.status_code == 200
        policies = response.json()
        assert len(policies) == 0

        #try to buy
        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Milk",
            "category": "Dairy",
            "quantity": 5
        }])

        # Verify the response status code and message
        assert response.status_code == 200
        assert response.json()["total_price"] == 35.0
        assert response.json()["original_price"] == 35.0








        # Get the discount policies to verify the added discount

    # def test_get_discount_policies(self):
    #     response = self.client.get(f'/stores/{self.store_id}/get_discount_policies', json={
    #         "user_id": self.user_id, "store_id": self.store_id
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.json()), 1)

    # def test_add_simple_discount_policy(self):
    #     response = self.client.post("/stores/{store_id}/add_discount_policy", json={
    #         "role": {"user_id": self.user_id, "store_id": self.store_id},
    #         "payload": {"min_items": 5, "min_price": 500}
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), {"message": "Discount policy added successfully"})

    def test_add_product_with_invalid_data(self):
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.user_id, "store_id": self.store_id},
            "payload": {"name": "Check false", "quantity": -5, "initial_price": -50, "category": "New Category"}
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
            "payload": {"name": "New Product", "quantity": 5, "initial_price": 50, "category": "New Category"}
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
            "payload": {"name": "Non Existent Product", "quantity": 5, "initial_price": 50, "category": "New Category"}
        })
        self.assertEqual(response.status_code, 404)

    def test_purchase_product_with_insufficient_quantity(self):
        response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product",
            "quantity": 100,
            "category": "Test Category"
        }])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Insufficient quantity of Test Product in store"})

    def test_concurrent_product_purchase(self):
        # Create a second user
        self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.owner2_id, "store_id": self.store_id},
            "payload": {"name": "Test Product 2", "quantity": 1, "initial_price": 100, "category": "Test Category"}})

        # Both users try to purchase the last product at the same time
        response1 = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product 2",
            "quantity": 1,
            "category": "Test Category"

        }])
        response2 = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product 2",
            "quantity": 1,
            "category": "Test Category"
        }])
        # One of the requests should fail
        self.assertTrue(response1.status_code == 404 or response2.status_code == 404)

    def test_concurrent_product_deletion_and_purchase(self):
        response = self.client.post("/stores/{store_id}/add_product", json={
            "role": {"user_id": self.owner2_id, "store_id": self.store_id},
            "payload": {"name": "Test Product 3", "quantity": 1, "initial_price": 100, "category": "Test Category"}})
        # print(response.content)

        # Store owner deletes a product
        delete_response = self.client.delete("/stores/{store_id}/remove_product?product_name=Test Product 3", json={
            "user_id": self.user_id, "store_id": self.store_id
        })
        # print(delete_response.content)
        # At the same time, another user tries to buy the product
        purchase_response = self.client.put(f'/stores/{self.store_id}/purchase_product', json=[{
            "product_name": "Test Product 3",
            "quantity": 1,
            "category": "Test Category"
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
