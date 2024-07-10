import json
from datetime import time, datetime

from django.test import TestCase, TransactionTestCase
from ninja.testing import TestClient
from django.core.cache import cache

from .api import router
import threading
import queue


def string_to_list(string):
    jsonDec = json.decoder.JSONDecoder()
    return jsonDec.decode(string)


class StoreAPITestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = TestClient(router)
        self.user_id = 1

        data = {"name": "Dairy Store", "description": "Store for dairy products"}
        response = self.client.post(f"/?user_id={self.user_id}", json=data)
        self.store_id = response.json()["store_id"]

        data = {"name": "Meat Store", "description": "Store for meat products"}
        response = self.client.post(f"/?user_id={self.user_id}", json=data)
        self.store_id2 = response.json()["store_id"]

        # Add product to store
        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Milk",
                    "quantity": 100,
                    "initial_price": 7,
                    "category": "Dairy",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Cheese",
                    "quantity": 50,
                    "initial_price": 15,
                    "category": "Dairy",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Bread Loaf",
                    "quantity": 100,
                    "initial_price": 5,
                    "category": "Pastry",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Bun",
                    "quantity": 100,
                    "initial_price": 2,
                    "category": "Pastry",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Cottage Cheese",
                    "quantity": 100,
                    "initial_price": 3,
                    "category": "Dairy",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Yogurt",
                    "quantity": 100,
                    "initial_price": 4,
                    "category": "Dairy",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Pasta",
                    "quantity": 100,
                    "initial_price": 10,
                    "category": "Pasta",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Tomato",
                    "quantity": 100,
                    "initial_price": 7,
                    "category": "Vegetable",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Eggplant",
                    "quantity": 100,
                    "initial_price": 7,
                    "category": "Vegetable",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Vodka",
                    "quantity": 100,
                    "initial_price": 90,
                    "category": "Alcohol",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Corn",
                    "quantity": 10,
                    "initial_price": 15,
                    "category": "Vegetable",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id2},
                "payload": {
                    "name": "Steak",
                    "quantity": 10,
                    "initial_price": 100,
                    "category": "Meat",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id2},
                "payload": {
                    "name": "Bread Loaf",
                    "quantity": 20,
                    "initial_price": 10,
                    "category": "Pastry",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        response = self.client.post(
            "/{store_id}/add_product",
            json={
                "role": {"user_id": self.user_id, "store_id": self.store_id},
                "payload": {
                    "name": "Test Product",
                    "quantity": 5,
                    "initial_price": 50,
                    "category": "Test Category",
                    "image_link": "check",
                },
            },
        )
        assert response.status_code == 200

        # Add owner to store
        self.owner2_id = 2
        response = self.client.post(
            "/{store_id}/assign_owner",
            json={
                "user_id": self.owner2_id,
                "store_id": self.store_id,
                "assigned_by": self.user_id,
            },
        )
        assert response.status_code == 200

        # Add manager to store
        self.manager_id = 3
        response = self.client.post(
            "/{store_id}/assign_manager",
            json={
                "user_id": self.manager_id,
                "store_id": self.store_id,
                "assigned_by": self.owner2_id,
            },
        )
        assert response.status_code == 200

        # Add manager permissions
        response = self.client.post(
            "/{store_id}/change_manager_permissions?assigning_owner_id="
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
        assert response.status_code == 200

    def tearDown(self):
        cache.clear()

    def test_get_store(self):
        response = self.client.get(f"/{self.store_id}")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        json_data_excluded = {
            key: value for key, value in json_data.items() if key != "created_at"
        }
        self.assertEqual(
            json_data_excluded,
            {
                "id": self.store_id,
                "name": "Dairy Store",
                "description": "Store for dairy products",
                "is_active": True,
            },
        )

    def test_get_all_stores(self):
        try:
            response = self.client.get(f"/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 2)
        finally:
            self.tearDown()

    def test_get_store_with_invalid_id(self):
        try:
            response = self.client.get(f"/100")
            self.assertEqual(response.status_code, 404)
        finally:
            self.tearDown()

    def test_add_product(self):
        try:
            response = self.client.post(
                "/{store_id}/add_product",
                json={
                    "role": {"user_id": self.manager_id, "store_id": self.store_id},
                    "payload": {
                        "name": "New Product",
                        "quantity": 5,
                        "initial_price": 50,
                        "category": "New Category",
                        "image_link": "check",
                    },
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Product added successfully"})
        finally:
            self.tearDown()

    def test_remove_product(self):
        try:
            response = self.client.delete(
                "/{store_id}/remove_product?product_name=Test Product",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Product removed successfully"})
        finally:
            self.tearDown()

    def test_edit_product(self):
        try:
            response = self.client.put(
                "/{store_id}/edit_product",
                json={
                    "role": {"user_id": self.owner2_id, "store_id": self.store_id},
                    "payload": {
                        "name": "Test Product",
                        "quantity": 5,
                        "initial_price": 50,
                        "category": "New Category",
                        "image_link": "check",
                    },
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Product edited successfully"})
        finally:
            self.tearDown()

    def test_get_products(self):
        try:
            response = self.client.get(
                f"/{self.store_id}/get_products",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 12)
        finally:
            self.tearDown()

    def test_purchase_product(self):
        try:
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {
                        "product_name": "Test Product",
                        "quantity": 1,
                        "category": "Test Category",
                    }
                ],
            )
            self.assertEqual(response.status_code, 200)
            assert response.json()["total_price"] == 50.0
        finally:
            self.tearDown()

    def test_add_simple_discount_policy(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "percentage": 15.0,
                "applicable_products": ["Milk"],
                "applicable_categories": ["Dairy"],
            }

            # Add the simple discount policy
            response = self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": simple_discount_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple discount policy added successfully"

            # Get the discount policies to verify the added discount
            response = self.client.post(
                f"/{self.store_id}/get_discount_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200

            # Parse the response data
            policies = response.json()
            assert len(policies) > 0

            # Verify the added simple discount policy is in the response
            added_policy = next(
                (policy for policy in policies if policy["percentage"] == 15.0), None
            )
            assert added_policy is not None
            assert added_policy["applicable_products"][0]["name"] == "Milk"
            assert added_policy["store"]["id"] == self.store_id
            assert string_to_list(added_policy["applicable_categories"]) == ["Dairy"]
            assert added_policy["is_root"] is True
        finally:
            self.tearDown()

    def test_add_conditional_discount_policy(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 15.0,
                "applicable_products": ["Milk"],
            }

            condition = {
                "applies_to": "products",
                "name_of_apply": "Milk",
                "condition": "at_least",
                "value": 5,
            }

            # Add the conditional discount policy
            conditional_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
                "discount": simple_discount_payload,
            }

            # Add the conditional discount policy
            response = self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_discount_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Conditional discount policy added successfully"

            # Get the discount policies to verify the added discount
            response = self.client.post(
                f"/{self.store_id}/get_discount_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

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
        finally:
            self.tearDown()

    def test_add_composite_discount_policy(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 15.0,
                "applicable_products": ["Milk"],
            }
            simple_discount_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 10.0,
                "applicable_products": ["Cheese"],
            }

            condition1 = {
                "applies_to": "category",
                "name_of_apply": "Dairy",
                "condition": "at_least",
                "value": 1,
            }

            condition2 = {
                "applies_to": "category",
                "name_of_apply": "Pastry",
                "condition": "at_least",
                "value": 1,
            }

            conditions = [condition1, condition2]
            combine_function = "logical_and"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload, simple_discount_payload2],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            response = self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.post(
                f"/{self.store_id}/get_discount_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            policies = response.json()
            added_policy = next((policy for policy in policies), None)
            assert added_policy is not None
            assert added_policy["store"]["id"] == self.store_id
            assert added_policy["is_root"] is True
        finally:
            self.tearDown()

    def test_get_conditions_composite(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 15.0,
                "applicable_products": ["Milk"],
            }
            simple_discount_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 10.0,
                "applicable_products": ["Cheese"],
            }

            condition1 = {
                "applies_to": "category",
                "name_of_apply": "Dairy",
                "condition": "at_least",
                "value": 1,
            }

            condition2 = {
                "applies_to": "category",
                "name_of_apply": "Pastry",
                "condition": "at_least",
                "value": 1,
            }

            conditions = [condition1, condition2]
            combine_function = "logical_and"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload, simple_discount_payload2],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.post(
                f"/{self.store_id}/get_discount_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            discounts = response.json()[0]
            discount_id = discounts["id"]

            response = self.client.post(
                f"/{self.store_id}/get_conditions",
                json={
                    "store_id": self.store_id,
                    "target_id": discount_id,
                    "to_discount": True,
                },
            )

            conditions = response.json()
            assert response.status_code == 200
        finally:
            self.tearDown()

    def test_get_conditions_simple(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "percentage": 15.0,
                "applicable_products": ["Milk"],
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": simple_discount_payload,
                },
            )

            response = self.client.post(
                f"/{self.store_id}/get_discount_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            discounts = response.json()[0]
            discount_id = discounts["id"]

            response = self.client.post(
                f"/{self.store_id}/get_conditions",
                json={
                    "store_id": self.store_id,
                    "target_id": discount_id,
                    "to_discount": True,
                },
            )

            conditions = response.json()
            assert response.status_code == 200
        finally:
            self.tearDown()

    def test_remove_discount_policy(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "percentage": 15.0,
                "applicable_products": ["Milk"],
                "applicable_categories": ["Dairy"],
            }

            # Add the simple discount policy
            response = self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": simple_discount_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple discount policy added successfully"
            # remove the discount policy
            response = self.client.delete(
                f"/{self.store_id}/remove_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": {"store_id": self.store_id, "discount_id": 1},
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json().get("message") == "Discount policy removed successfully"

            # check if the discount policy is removed
            response = self.client.post(
                f"/{self.store_id}/get_discount_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            policies = response.json()
            assert len(policies) == 0
        finally:
            self.tearDown()

    def test_apply_simple_discount_policy_1(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "percentage": 50.0,
                "applicable_categories": ["Dairy"],
            }

            # Add the simple discount policy
            response = self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": simple_discount_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple discount policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[{"product_name": "Milk", "category": "Dairy", "quantity": 5}],
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == {
                "message": "Products purchased successfully",
                "total_price": 17.5,
                "original_price": 35.0,
                "original_prices": [
                    {
                        "name": "Milk",
                        "initial price": 7.0,
                        "quantity": 5,
                        "total price": 35.0,
                    }
                ],
            }
            assert response.json()["total_price"] == 17.5
        finally:
            self.tearDown()

    def test_apply_simple_discount_policy_2(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "percentage": 20.0,
                "applicable_categories": ["all"],
            }

            # Add the simple discount policy
            response = self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": simple_discount_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple discount policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Milk", "category": "Dairy", "quantity": 5},
                    {"product_name": "Cheese", "category": "Dairy", "quantity": 5},
                ],
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json()["total_price"] == 88.0
            assert response.json()["original_price"] == 110.0
        finally:
            self.tearDown()

    def test_apply_conditional_discount_policy(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 10.0,
                "applicable_products": ["Milk"],
            }

            condition = {
                "applies_to": "price",
                "name_of_apply": "total_price",
                "condition": "greater_than",
                "value": 200,
            }

            conditional_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
                "discount": simple_discount_payload,
            }

            # Add the simple discount policy
            response = self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_discount_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Conditional discount policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Milk", "category": "Dairy", "quantity": 50},
                    {"product_name": "Cheese", "category": "Dairy", "quantity": 20},
                ],
            )
            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json()["total_price"] == 615.0
            assert response.json()["original_price"] == 650.0
        finally:
            self.tearDown()

    def test_conditional_discount_policy_doesnt_apply(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 10.0,
                "applicable_products": ["Milk"],
            }

            condition = {
                "applies_to": "price",
                "name_of_apply": "total_price",
                "condition": "greater_than",
                "value": 200,
            }

            conditional_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
                "discount": simple_discount_payload,
            }

            # Add the simple discount policy
            response = self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_discount_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Conditional discount policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Milk", "category": "Dairy", "quantity": 5},
                    {"product_name": "Cheese", "category": "Dairy", "quantity": 5},
                ],
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json()["total_price"] == 110.0
            assert response.json()["original_price"] == 110.0
        finally:
            self.tearDown()

    def test_apply_composite_discount_policy_xor(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 10.0,
                "applicable_categories": ["Dairy"],
            }

            condition1 = {
                "applies_to": "category",
                "name_of_apply": "Dairy",
                "condition": "at_least",
                "value": 1,
            }
            condition2 = {
                "applies_to": "category",
                "name_of_apply": "Pastry",
                "condition": "at_least",
                "value": 1,
            }

            conditions = [condition1, condition2]
            combine_function = "logical_xor"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[{"product_name": "Milk", "category": "Dairy", "quantity": 5}],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 31.5
            assert response.json()["original_price"] == 35.0
        finally:
            self.tearDown()

    def test_doesnt_apply_composite_discount_policy_xor(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 10.0,
                "applicable_categories": ["Dairy"],
            }

            condition1 = {
                "applies_to": "category",
                "name_of_apply": "Dairy",
                "condition": "at_least",
                "value": 1,
            }
            condition2 = {
                "applies_to": "category",
                "name_of_apply": "Pastry",
                "condition": "at_least",
                "value": 1,
            }

            conditions = [condition1, condition2]
            combine_function = "logical_xor"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Milk", "category": "Dairy", "quantity": 5},
                    {"product_name": "Bread Loaf", "category": "Pastry", "quantity": 5},
                ],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 60.0
            assert response.json()["original_price"] == 60.0
        finally:
            self.tearDown()

    def test_apply_composite_discount_policy_and(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 5.0,
                "applicable_categories": ["Pastry"],
            }

            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Bun",
                "condition": "at_least",
                "value": 5,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Bread Loaf",
                "condition": "at_least",
                "value": 2,
            }

            conditions = [condition1, condition2]
            combine_function = "logical_and"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Bun", "category": "Pastry", "quantity": 5},
                    {"product_name": "Bread Loaf", "category": "Pastry", "quantity": 3},
                ],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 23.75
            assert response.json()["original_price"] == 25.0
        finally:
            self.tearDown()

    def test_doesnt_apply_composite_discount_policy_and(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 5.0,
                "applicable_categories": ["Pastry"],
            }

            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Bun",
                "condition": "at_least",
                "value": 5,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Bread Loaf",
                "condition": "at_least",
                "value": 2,
            }

            conditions = [condition1, condition2]
            combine_function = "logical_and"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Bun", "category": "Pastry", "quantity": 5},
                    {"product_name": "Bread Loaf", "category": "Pastry", "quantity": 1},
                ],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 15
            assert response.json()["original_price"] == 15
        finally:
            self.tearDown()

    def test_apply_composite_discount_policy_or(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 5.0,
                "applicable_categories": ["Dairy"],
            }

            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Cottage Cheese",
                "condition": "at_least",
                "value": 3,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Yogurt",
                "condition": "at_least",
                "value": 2,
            }

            conditions = [condition1, condition2]
            combine_function = "logical_or"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Cottage Cheese", "category": "Dairy", "quantity": 3},
                    {"product_name": "Yogurt", "category": "Dairy", "quantity": 1},
                ],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 12.35
            assert response.json()["original_price"] == 13
        finally:
            self.tearDown()

    def test_doesnt_apply_composite_discount_policy_or(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 5.0,
                "applicable_categories": ["Dairy"],
            }

            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Cottage Cheese",
                "condition": "at_least",
                "value": 3,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Yogurt",
                "condition": "at_least",
                "value": 2,
            }

            conditions = [condition1, condition2]
            combine_function = "logical_or"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Cottage Cheese", "category": "Dairy", "quantity": 2},
                    {"product_name": "Yogurt", "category": "Dairy", "quantity": 1},
                ],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 10
            assert response.json()["original_price"] == 10
        finally:
            self.tearDown()

    def test_apply_composite_discount_policy_max(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 17.0,
                "applicable_products": ["Milk"],
            }

            simple_discount_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 5.0,
                "applicable_products": ["Pasta"],
            }

            conditions = []
            combine_function = "max"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload, simple_discount_payload2],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Milk", "category": "Dairy", "quantity": 5},
                    {"product_name": "Pasta", "category": "Pasta", "quantity": 5},
                ],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 79.05
            assert response.json()["original_price"] == 85
        finally:
            self.tearDown()

    def test_apply_composite_discount_policy_addition(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "percentage": 5.0,
                "applicable_categories": ["Dairy"],
            }
            simple_discount_payload2 = {
                "store_id": self.store_id,
                "is_root": True,
                "percentage": 20.0,
                "applicable_categories": ["all"],
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": simple_discount_payload,
                },
            )

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": simple_discount_payload2,
                },
            )

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[{"product_name": "Milk", "category": "Dairy", "quantity": 5}],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 26.25
            assert response.json()["original_price"] == 35
        finally:
            self.tearDown()

    def test_remove_discount_policy(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "percentage": 15.0,
                "applicable_categories": ["Dairy"],
            }

            # Add the simple discount policy
            response = self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": simple_discount_payload,
                },
            )

            # remove
            response = self.client.delete(
                f"/{self.store_id}/remove_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": {"store_id": self.store_id, "discount_id": 1},
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json().get("message") == "Discount policy removed successfully"

            # check if the discount policy is removed
            response = self.client.post(
                f"/{self.store_id}/get_discount_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            policies = response.json()
            assert len(policies) == 0

            # try to buy
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[{"product_name": "Milk", "category": "Dairy", "quantity": 5}],
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json()["total_price"] == 35.0
            assert response.json()["original_price"] == 35.0
        finally:
            self.tearDown()

    def test_add_simple_purchase_policy1(self):
        try:
            condition = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }
            purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
            }

            # Add the simple purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple purchase policy added successfully"

            # Get the purchase policies to verify the added purchase policy
            response = self.client.post(
                f"/{self.store_id}/get_purchase_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            assert len(response.json()) == 1
        finally:
            self.tearDown()

    def test_add_simple_purchase_policy2(self):
        try:
            condition = {
                "applies_to": "time",
                "name_of_apply": "",
                "condition": "at_most",
                "value": 23,
            }
            purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
            }

            # Add the simple purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple purchase policy added successfully"

            # Get the purchase policies to verify the added purchase policy
            response = self.client.post(
                f"/{self.store_id}/get_purchase_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            assert len(response.json()) == 1
        finally:
            self.tearDown()

    def test_add_composite_purchase_policy_and(self):
        try:
            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Corn",
                "condition": "at_least",
                "value": 2,
            }

            simple_purchase_policy_payload1 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }

            simple_purchase_policy_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }

            conditions = [simple_purchase_policy_payload1, simple_purchase_policy_payload2]
            combine_function = "logical_and"

            composite_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "policies": conditions,
                "combine_function": combine_function,
            }

            # Add the composite purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Composite purchase policy added successfully"

            # Get the purchase policies to verify the added purchase policy
            response = self.client.post(
                f"/{self.store_id}/get_purchase_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            assert len(response.json()) == 1
        finally:
            self.tearDown()

    def add_composite_purchase_policy_or_condition(self):
        try:
            # can buy alcohol only if time <=23 and tomato <= 5
            # replaced with holiday because cant check that
            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }
            condition2 = {
                "applies_to": "time",
                "name_of_apply": "",
                "condition": "at_most",
                "value": 23,
            }
            condition3 = {
                "applies_to": "category",
                "name_of_apply": "Alcohol",
                "condition": "at_least",
                "value": 1,
            }

            simple_purchase_policy_payload1 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }

            simple_purchase_policy_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }

            simple_purchase_policy_payload3 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition3,
            }

            composite_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "policies": [
                    simple_purchase_policy_payload1,
                    simple_purchase_policy_payload2,
                ],
                "combine_function": "logical_and",
            }

            conditional_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": composite_purchase_policy_payload,
                "restriction": simple_purchase_policy_payload3,
            }

            # Add the conditional purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Conditional purchase policy added successfully"

            # Get the purchase policies to verify the added purchase policy
            response = self.client.post(
                f"/{self.store_id}/get_purchase_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            assert len(response.json()) == 1
        finally:
            self.tearDown()

    def test_apply_simple_purchase_policy1(self):
        try:
            condition = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }
            purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
            }

            # Add the simple purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple purchase policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[{"product_name": "Tomato", "category": "Vegetables", "quantity": 6}],
            )

            # Verify the response status code and message
            assert response.status_code == 400
            assert response.json().get("detail") == "Purchase policy validation failed"
        finally:
            self.tearDown()

    def test_doesnt_apply_simple_purchase_policy1(self):
        try:
            condition = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }
            purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
            }

            # Add the simple purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple purchase policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[{"product_name": "Tomato", "category": "Vegetables", "quantity": 5}],
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json()["total_price"] == 35.0
        finally:
            self.tearDown()

    def test_apply_conditional_purchase_policy1(self):
        try:
            # cant buy alcohol after 23 -> can buy alcohol only if time <= 23
            condition1 = {
                "applies_to": "time",
                "name_of_apply": "",
                "condition": "at_most",
                "value": 8,  # set time as you like
            }

            condition2 = {
                "applies_to": "category",
                "name_of_apply": "Alcohol",
                "condition": "at_least",
                "value": 1,
            }
            simple_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }

            simple_purchase_policy_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }

            conditional_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": simple_purchase_policy_payload,
                "restriction": simple_purchase_policy_payload2,
            }

            # Add the conditional purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Conditional purchase policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Tomato", "category": "Vegetables", "quantity": 5},
                    {"product_name": "Vodka", "category": "Alcohol", "quantity": 1},
                ],
            )

            assert response.status_code == 400
            assert response.json().get("detail") == "Purchase policy validation failed"
        finally:
            self.tearDown()

    def test_doesnt_apply_conditional_purchase_policy1(self):
        try:
            # cant buy alcohol after 23 -> can buy alcohol only if time <= 23
            condition1 = {
                "applies_to": "time",
                "name_of_apply": "",
                "condition": "at_most",
                "value": 8,  # set time as you like
            }

            condition2 = {
                "applies_to": "category",
                "name_of_apply": "Alcohol",
                "condition": "at_least",
                "value": 1,
            }
            simple_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }

            simple_purchase_policy_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }

            conditional_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": simple_purchase_policy_payload,
                "restriction": simple_purchase_policy_payload2,
            }

            # Add the conditional purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Conditional purchase policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[{"product_name": "Tomato", "category": "Vegetables", "quantity": 5}],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 35.0
        finally:
            self.tearDown()

    def test_apply_composite_purchase_policy_and(self):
        try:
            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Corn",
                "condition": "at_least",
                "value": 2,
            }

            simple_purchase_policy_payload1 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }

            simple_purchase_policy_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }

            conditions = [simple_purchase_policy_payload1, simple_purchase_policy_payload2]
            combine_function = "logical_and"

            composite_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "policies": conditions,
                "combine_function": combine_function,
            }

            # Add the composite purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Composite purchase policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Tomato", "category": "Vegetables", "quantity": 5},
                    {"product_name": "Corn", "category": "Vegetables", "quantity": 1},
                ],
            )

            assert response.status_code == 400
            assert response.json().get("detail") == "Purchase policy validation failed"
        finally:
            self.tearDown()

    def test_doesnt_apply_composite_purchase_policy_and(self):
        try:
            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Corn",
                "condition": "at_least",
                "value": 2,
            }

            simple_purchase_policy_payload1 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }

            simple_purchase_policy_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }

            conditions = [simple_purchase_policy_payload1, simple_purchase_policy_payload2]
            combine_function = "logical_and"

            composite_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "policies": conditions,
                "combine_function": combine_function,
            }

            # Add the composite purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Composite purchase policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Tomato", "category": "Vegetables", "quantity": 5},
                    {"product_name": "Corn", "category": "Vegetables", "quantity": 2},
                ],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 65.0
        finally:
            self.tearDown()

    def test_apply_conditional_composite_purchase_policy1(self):
        try:
            # can buy alcohol only if time <=23 and tomato <= 5
            # replaced with holiday because cant check that
            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }
            condition2 = {
                "applies_to": "time",
                "name_of_apply": "",
                "condition": "at_most",
                "value": 8,
            }
            condition3 = {
                "applies_to": "category",
                "name_of_apply": "Alcohol",
                "condition": "at_least",
                "value": 1,
            }

            simple_purchase_policy_payload1 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }

            simple_purchase_policy_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }

            simple_purchase_policy_payload3 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition3,
            }

            composite_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "policies": [
                    simple_purchase_policy_payload1,
                    simple_purchase_policy_payload2,
                ],
                "combine_function": "logical_and",
            }

            conditional_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": composite_purchase_policy_payload,
                "restriction": simple_purchase_policy_payload3,
            }

            # Add the conditional purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Conditional purchase policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Tomato", "category": "Vegetables", "quantity": 5},
                    {"product_name": "Vodka", "category": "Alcohol", "quantity": 1},
                ],
            )

            assert response.status_code == 400
            assert response.json().get("detail") == "Purchase policy validation failed"
        finally:
            self.tearDown()

    def test_doesnt_apply_conditional_composite_purchase_policy1(self):
        try:
            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }
            condition2 = {
                "applies_to": "time",
                "name_of_apply": "",
                "condition": "at_most",
                "value": 8,
            }
            condition3 = {
                "applies_to": "category",
                "name_of_apply": "Alcohol",
                "condition": "at_least",
                "value": 1,
            }

            simple_purchase_policy_payload1 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }

            simple_purchase_policy_payload2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }

            simple_purchase_policy_payload3 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition3,
            }

            composite_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "policies": [
                    simple_purchase_policy_payload1,
                    simple_purchase_policy_payload2,
                ],
                "combine_function": "logical_and",
            }

            conditional_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": composite_purchase_policy_payload,
                "restriction": simple_purchase_policy_payload3,
            }

            # Add the conditional purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Conditional purchase policy added successfully"

            # Purchase a product
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Tomato", "category": "Vegetables", "quantity": 5},
                ],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 35.0
        finally:
            self.tearDown()

    def test_apply_conditional_purchase_policy2(self):
        try:
            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Eggplant",
                "condition": "at_least",
                "value": 1,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_least",
                "value": 5,
            }

            simple_condition1 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }
            simple_condition2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }
            conditional_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": simple_condition1,
                "restriction": simple_condition2,
            }

            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_purchase_policy_payload,
                },
            )

            assert response.status_code == 200
            assert response.json() == "Conditional purchase policy added successfully"

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[{"product_name": "Tomato", "category": "Vegetable", "quantity": 5}],
            )

            assert response.status_code == 400
            assert response.json().get("detail") == "Purchase policy validation failed"
        finally:
            self.tearDown()

    def test_doesnt_apply_conditional_purchase_policy2(self):
        try:
            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Eggplant",
                "condition": "at_least",
                "value": 1,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_least",
                "value": 5,
            }

            simple_condition1 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition1,
            }
            simple_condition2 = {
                "store_id": self.store_id,
                "is_root": False,
                "condition": condition2,
            }
            conditional_purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": simple_condition1,
                "restriction": simple_condition2,
            }

            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": conditional_purchase_policy_payload,
                },
            )

            assert response.status_code == 200
            assert response.json() == "Conditional purchase policy added successfully"

            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {"product_name": "Tomato", "category": "Vegetable", "quantity": 5},
                    {"product_name": "Eggplant", "category": "Vegetable", "quantity": 1},
                ],
            )

            assert response.status_code == 200
            assert response.json()["total_price"] == 42.0
        finally:
            self.tearDown()

    def test_remove_purchase_policy_valid_user(self):
        try:
            condition = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }
            purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
            }

            # Add the simple purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple purchase policy added successfully"

            # Get the purchase policies to verify the added purchase policy
            response = self.client.post(
                f"/{self.store_id}/get_purchase_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            policies = response.json()
            assert len(policies) == 1

            # Remove the purchase policy
            response = self.client.delete(
                f"/{self.store_id}/remove_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": {"store_id": self.store_id, "policy_id": 1},
                },
            )
            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json().get("message") == "Purchase policy removed successfully"

            # Get the purchase policies to verify the removed purchase policy
            response = self.client.post(
                f"/{self.store_id}/get_purchase_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            policies = response.json()
            assert len(policies) == 0
        finally:
            self.tearDown()

    def test_remove_purchase_policy_invalid_user(self):
        try:
            condition = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }
            purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
            }

            # Add the simple purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple purchase policy added successfully"

            # Get the purchase policies to verify the added purchase policy
            response = self.client.post(
                f"/{self.store_id}/get_purchase_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            policies = response.json()
            assert len(policies) == 1

            # Remove the purchase policy
            response = self.client.delete(
                f"/{self.store_id}/remove_purchase_policy",
                json={
                    "role": {"user_id": 30, "store_id": self.store_id},
                    "payload": {"store_id": self.store_id, "policy_id": 1},
                },
            )

            # Verify the response status code and message
            assert response.status_code == 403
            assert (
                    response.json().get("detail")
                    == "User is not an owner or manager of the store"
            )

            # Get the purchase policies to verify the removed purchase policy
            response = self.client.post(
                f"/{self.store_id}/get_purchase_policies",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )

            # Verify the response status code
            assert response.status_code == 200
            policies = response.json()
            assert len(policies) == 1
        finally:
            self.tearDown()

    def test_add_product_with_invalid_data(self):
        try:
            response = self.client.post(
                "/{store_id}/add_product",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": {
                        "name": "Check false",
                        "quantity": -5,
                        "initial_price": -50,
                        "category": "New Category",
                        "image_link": "check",
                    },
                },
            )
            self.assertEqual(response.status_code, 400)
        finally:
            self.tearDown()

    def test_manager_without_permissions_add_product(self):
        try:
            response = self.client.post(
                "/{store_id}/assign_manager",
                json={
                    "user_id": 4,
                    "store_id": self.store_id,
                    "assigned_by": self.owner2_id,
                },
            )
            self.client.post(
                "/{store_id}/change_manager_permissions?assigning_owner_id=2",
                json={
                    "manager": {"user_id": 4, "store_id": self.store_id},
                    "payload": {
                        "can_add_product": False,
                        "can_edit_product": False,
                        "can_delete_product": False,
                    },
                },
            )
            response = self.client.post(
                "/{store_id}/add_product",
                json={
                    "role": {"user_id": 4, "store_id": self.store_id},
                    "payload": {
                        "name": "New Product",
                        "quantity": 5,
                        "initial_price": 50,
                        "category": "New Category",
                        "image_link": "check",
                    },
                },
            )
            self.assertEqual(response.status_code, 403)
        finally:
            self.tearDown()

    def test_remove_owner(self):
        try:
            self.owner3_id = 10
            self.manager2_id = 11
            # response = self.client.post("/{store_id}/assign_owner", json={
            #     "user_id": self.owner3_id, "store_id": self.store_id, "assigned_by": self.user_id
            # })
            # response = self.client.post("/{store_id}/assign_manager", json={
            #                  "user_id": self.manager2_id, "store_id": self.store_id, "assigned_by": self.owner3_id
            # })
            response = self.client.delete(
                "/{store_id}/remove_owner",
                json={
                    "user_id": self.owner2_id,
                    "store_id": self.store_id,
                    "removed_by": self.user_id,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Owner removed successfully"})
            response = self.client.post(
                f"/{self.store_id}/get_managers",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                len(response.json()), 0
            )  # manager should have been removed because owner is removed
        finally:
            self.tearDown()

    def test_remove_non_existent_product(self):
        try:
            response = self.client.delete(
                "/{store_id}/remove_product?product_name=Non Existent Product",
                json={"user_id": self.user_id, "store_id": self.store_id},
            )
            self.assertEqual(response.status_code, 404)
        finally:
            self.tearDown()

    def test_edit_non_existent_product(self):
        try:
            response = self.client.put(
                "/{store_id}/edit_product",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": {
                        "name": "Non Existent Product",
                        "quantity": 5,
                        "initial_price": 50,
                        "category": "New Category",
                        "image_link": "check",
                    },
                },
            )
            self.assertEqual(response.status_code, 404)
        finally:
            self.tearDown()

    def test_purchase_product_with_insufficient_quantity(self):
        try:
            response = self.client.put(
                f"/{self.store_id}/purchase_product",
                json=[
                    {
                        "product_name": "Test Product",
                        "quantity": 100,
                        "category": "Test Category",
                    }
                ],
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.json(),
                {"detail": "Insufficient quantity of Test Product in store"},
            )
        finally:
            self.tearDown()

    def test_concurrent_product_purchase(self):
        try:
            for i in range(5):  # test in loop?
                self.client.post(
                    "/{store_id}/add_product",
                    json={
                        "role": {"user_id": self.owner2_id, "store_id": self.store_id},
                        "payload": {
                            "name": "Test Product 2",
                            "quantity": 1,
                            "initial_price": 100,
                            "category": "Test Category",
                        },
                    },
                )

                def purchase_product(queue):
                    response = self.client.put(
                        f"/{self.store_id}/purchase_product",
                        json=[
                            {
                                "product_name": "Test Product 2",
                                "quantity": 1,
                                "category": "Test Category",
                            }
                        ],
                    )
                    queue.put(response)  # Put response in the queue

                # Create a queue to store responses
                response_queue = queue.Queue()

                # Create threads for each request
                thread1 = threading.Thread(target=purchase_product, args=(response_queue,))
                thread2 = threading.Thread(target=purchase_product, args=(response_queue,))

                # Start both threads
                thread1.start()
                thread2.start()

                # Wait for both threads to finish
                thread1.join()
                thread2.join()

                # Get responses from the queue
                response1 = response_queue.get()
                response2 = response_queue.get()

                # One of the requests should fail (return 404)
                self.assertTrue(
                    response1.status_code == 404 or response2.status_code == 404
                ) and self.assertTrue(
                    response1.status_code == 200 or response2.status_code == 200
                )
        finally:
            self.tearDown()

    def test_concurrent_product_deletion_and_purchase(self):
        try:
            for i in range(5):
                response = self.client.post(
                    "/{store_id}/add_product",
                    json={
                        "role": {"user_id": self.owner2_id, "store_id": self.store_id},
                        "payload": {
                            "name": "Test Product 3",
                            "quantity": 1,
                            "initial_price": 100,
                            "category": "Test Category",
                        },
                    },
                )

                def delete_product(queue):
                    response = self.client.delete(
                        "/{store_id}/remove_product?product_name=Test Product 3",
                        json={"user_id": self.user_id, "store_id": self.store_id},
                    )
                    queue.put(response)

                def purchase_product(queue):
                    response = self.client.put(
                        f"/{self.store_id}/purchase_product",
                        json=[
                            {
                                "product_name": "Test Product 3",
                                "quantity": 1,
                                "category": "Test Category",
                            }
                        ],
                    )
                    queue.put(response)

                # Create a queue to store responses
                response_queue = queue.Queue()

                # Create threads for each request
                thread1 = threading.Thread(target=delete_product, args=(response_queue,))
                thread2 = threading.Thread(target=purchase_product, args=(response_queue,))

                # Start both threads
                thread1.start()
                thread2.start()

                # Wait for both threads to finish
                thread1.join()
                thread2.join()

                # Get responses from the queue
                response1 = response_queue.get()
                response2 = response_queue.get()

                # One of the requests should fail (return 404)
                self.assertTrue(
                    response1.status_code == 404 or response2.status_code == 404
                ) and self.assertTrue(
                    response1.status_code == 200 or response2.status_code == 200
                )
        finally:
            self.tearDown()

    def test_empty_search(self):
        try:
            response = self.client.get(
                f"/search", json={"search_query": {}, "filter_query": {}}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 14)
        finally:
            self.tearDown()

    def test_search_product_in_store_no_filter(self):
        try:
            search = {"store_id": self.store_id, "product_name": "Bread Loaf"}

            filter = {}

            response = self.client.get(
                f"/search", json={"search_query": search, "filter_query": filter}
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 1)
            self.assertEqual(response.json()[0]["name"], "Bread Loaf")
        finally:
            self.tearDown()

    def test_search_product_in_store_with_filter(self):
        try:
            search = {"store_id": 1, "product_name": "Bread Loaf"}

            filter = {"max_price": 3}

            response = self.client.get(
                f"/search", json={"search_query": search, "filter_query": filter}
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 0)
        finally:
            self.tearDown()

    def test_search_product_in_market_no_filter(self):
        try:
            search = {"product_name": "Bread Loaf"}

            filter = {}

            response = self.client.get(
                f"/search", json={"search_query": search, "filter_query": filter}
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 2)
            self.assertEqual(response.json()[0]["name"], "Bread Loaf")
        finally:
            self.tearDown()

    def test_search_product_in_market_with_filter(self):
        try:
            search = {"product_name": "Bread Loaf"}

            filter = {"max_price": 5}

            response = self.client.get(
                f"/search", json={"search_query": search, "filter_query": filter}
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 1)
        finally:
            self.tearDown()

    def test_concurrent_manager_appointment(self):
        try:
            for i in range(5):
                self.owner3_id = 100 + i

                def make_request(queue, user_id, store_id, assigned_by):
                    response = self.client.post(
                        "/{store_id}/assign_owner",
                        json={
                            "user_id": user_id,
                            "store_id": self.store_id,
                            "assigned_by": assigned_by,
                        },
                    )
                    queue.put(response)  # Put response in the queue

                # Create a queue to store responses
                response_queue = queue.Queue()

                # Create threads for each request
                thread1 = threading.Thread(
                    target=make_request,
                    args=(response_queue, self.owner3_id, self.store_id, self.user_id),
                )
                thread2 = threading.Thread(
                    target=make_request,
                    args=(response_queue, self.owner3_id, self.store_id, self.user_id),
                )

                # Start both threads
                thread1.start()
                thread2.start()

                # Wait for both threads to finish
                thread1.join()
                thread2.join()

                # Get responses from the queue
                response1 = response_queue.get()
                response2 = response_queue.get()

                # Assert that at least one response has a conflict (400)
                self.assertTrue(
                    response1.status_code == 400 or response2.status_code == 400
                ) and self.assertTrue(
                    response1.status_code == 200 or response2.status_code == 200
                )
        finally:
            self.tearDown()

    def test_fake_data(self):
        try:
            response = self.client.post(f"/create_fake_data")
            assert response.status_code == 200
        finally:
            self.tearDown()

    def test_make_bid(self):
        try:
            response = self.client.post(
                "/{store_id}/make_bid",
                json={
                    "user_id": 100,
                    "store_id": self.store_id,
                    "product_name": "Bread Loaf",
                    "price": 2,
                    "quantity": 1,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Bid added successfully"})
        finally:
            self.tearDown()

    def test_get_bids(self):
        try:
            response = self.client.post(
                "/{store_id}/make_bid",
                json={
                    "user_id": 100,
                    "store_id": self.store_id,
                    "product_name": "Bread Loaf",
                    "price": 2,
                    "quantity": 1,
                },
            )
            self.assertEqual(response.status_code, 200)

            role_payload = {"user_id": self.user_id, "store_id": self.store_id}
            response = self.client.get(f"/{self.store_id}/get_bids", json=role_payload)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 1)
        finally:
            self.tearDown()

    def test_decide_on_bid(self):
        try:
            response = self.client.post(
                "/{store_id}/make_bid",
                json={
                    "user_id": 100,
                    "store_id": self.store_id,
                    "product_name": "Bread Loaf",
                    "price": 2,
                    "quantity": 1,
                },
            )
            self.assertEqual(response.status_code, 200)
            role_payload = {"user_id": self.user_id, "store_id": self.store_id}
            bid_payload = {"bid_id": 1, "decision": 1}

            response = self.client.put(
                f"/{self.store_id}/decide_on_bid",
                json={"role": role_payload, "payload": bid_payload},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Bid decision made successfully"})
        finally:
            self.tearDown()

    def test_make_purchase_on_bid_not_accepted_by_all(self):
        try:
            response = self.client.post(
                "/{store_id}/make_bid",
                json={
                    "user_id": 100,
                    "store_id": self.store_id,
                    "product_name": "Bread Loaf",
                    "price": 2,
                    "quantity": 1,
                },
            )
            self.assertEqual(response.status_code, 200)
            role_payload = {"user_id": self.user_id, "store_id": self.store_id}
            bid_payload = {"bid_id": 1, "decision": 1}

            response = self.client.put(
                f"/{self.store_id}/decide_on_bid",
                json={"role": role_payload, "payload": bid_payload},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Bid decision made successfully"})

            purchase_bid_payload = {"store_id": self.store_id, "bid_id": 1}

            response = self.client.put(
                f"/{self.store_id}/make_purchase_on_bid", json=purchase_bid_payload
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.json(),
                {"detail": "Bid has not been accepted by all managers or owners"},
            )
        finally:
            self.tearDown()

    def test_make_purchase_on_bid_accepted_by_all(self):
        try:
            response = self.client.post(
                "/{store_id}/make_bid",
                json={
                    "user_id": 100,
                    "store_id": self.store_id,
                    "product_name": "Bread Loaf",
                    "price": 2,
                    "quantity": 1,
                },
            )
            self.assertEqual(response.status_code, 200)
            role_payload = {"user_id": self.user_id, "store_id": self.store_id}
            bid_payload = {"bid_id": 1, "decision": 1}

            response = self.client.put(
                f"/{self.store_id}/decide_on_bid",
                json={"role": role_payload, "payload": bid_payload},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Bid decision made successfully"})

            role_payload = {"user_id": self.owner2_id, "store_id": self.store_id}
            bid_payload = {"bid_id": 1, "decision": 1}

            response = self.client.put(
                f"/{self.store_id}/decide_on_bid",
                json={"role": role_payload, "payload": bid_payload},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"message": "Bid decision made successfully"})

            purchase_bid_payload = {"store_id": self.store_id, "bid_id": 1}

            response = self.client.put(
                f"/{self.store_id}/make_purchase_on_bid", json=purchase_bid_payload
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["price"], 2)
        finally:
            self.tearDown()

    def test_validate_purchase_policy(self):
        try:
            condition = {
                "applies_to": "product",
                "name_of_apply": "Tomato",
                "condition": "at_most",
                "value": 5,
            }
            purchase_policy_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "condition": condition,
            }

            # Add the simple purchase policy
            response = self.client.post(
                f"/{self.store_id}/add_purchase_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": purchase_policy_payload,
                },
            )

            # Verify the response status code and message
            assert response.status_code == 200
            assert response.json() == "Simple purchase policy added successfully"

            # Purchase a product
            response = self.client.post(
                f"/{self.store_id}/validate_purchase_policy",
                json=[{"product_name": "Tomato", "category": "Vegetables", "quantity": 6}],
            )

            # Verify the response status code and message
            assert response.status_code == 400
        finally:
            self.tearDown()

    def test_calculate_cart_discount(self):
        try:
            simple_discount_payload = {
                "store_id": self.store_id,
                "is_root": False,
                "percentage": 5.0,
                "applicable_categories": ["Dairy"],
            }

            condition1 = {
                "applies_to": "product",
                "name_of_apply": "Cottage Cheese",
                "condition": "at_least",
                "value": 3,
            }

            condition2 = {
                "applies_to": "product",
                "name_of_apply": "Yogurt",
                "condition": "at_least",
                "value": 2,
            }

            conditions = [condition1, condition2]
            combine_function = "logical_or"

            composite_discount_payload = {
                "store_id": self.store_id,
                "is_root": True,
                "discounts": [simple_discount_payload],
                "combine_function": combine_function,
                "conditions": conditions,
            }

            self.client.post(
                f"/{self.store_id}/add_discount_policy",
                json={
                    "role": {"user_id": self.user_id, "store_id": self.store_id},
                    "payload": composite_discount_payload,
                },
            )

            response = self.client.post(
                f"/{self.store_id}/calculate_cart_discount",
                json=[
                    {"product_name": "Cottage Cheese", "category": "Dairy", "quantity": 3},
                    {"product_name": "Yogurt", "category": "Dairy", "quantity": 1},
                ],
            )
            assert response.status_code == 200
            assert response.json() == 0.65
        finally:
            self.tearDown()

    def test_fake_data_discount(self):
        try:
            response = self.client.post(f"/create_fake_data")
            assert response.status_code == 200

            search_schema = {
                "product_name": "Falafel Plate"
            }
            response = self.client.get("/search", json={"search_query": search_schema, "filter_query": {}})
            assert response.status_code == 200
            store_id = response.json()[0]["store"]["id"]
            cart_payload = [
                {"product_name": "Falafel Plate", "category": "Food", "quantity": 2}
            ]
            response = self.client.post(f"/{store_id}/calculate_cart_discount", json=cart_payload)
            assert response.status_code == 200
        finally:
            self.tearDown()

    # def test_cache_efficiency(self):
    #     #efficency will be checked by creating fake data, then trying to purchase; computing time, removing cache and then trying again
    #     #and again measuring time
    #     try:
    #         response = self.client.post(f"/create_fake_data")
    #         assert response.status_code == 200
    #
    #         search_schema = {
    #             "product_name": "Falafel Plate"
    #         }
    #         response = self.client.get("/search", json={"search_query": search_schema, "filter_query": {}})
    #         assert response.status_code == 200
    #         store_id = response.json()[0]["store"]["id"]
    #         cart_payload = [
    #             {"product_name": "Falafel Plate", "category": "Food", "quantity": 2}
    #         ]
    #         print("starting now")
    #         start = datetime.now()
    #         response = self.client.put(f"/{store_id}/purchase_product", json=cart_payload)
    #         assert response.status_code == 200
    #         end = datetime.now()
    #         print("First time: ", end-start)
    #
    #         cache.clear()
    #
    #         start = datetime.now()
    #         response = self.client.put(f"/{store_id}/purchase_product", json=cart_payload)
    #         assert response.status_code == 200
    #         end = datetime.now()
    #         print("Second time: ", end-start)
    #     finally:
    #         self.tearDown()

    def test_get_bids_on_product(self):
        try:
            response = self.client.post(
                "/{store_id}/make_bid",
                json={
                    "user_id": 100,
                    "store_id": self.store_id,
                    "product_name": "Bread Loaf",
                    "price": 2,
                    "quantity": 1,
                },
            )
            self.assertEqual(response.status_code, 200)

            response = self.client.post(
                "/{store_id}/make_bid",
                json={
                    "user_id": 101,
                    "store_id": self.store_id,
                    "product_name": "Bread Loaf",
                    "price": 5,
                    "quantity": 2,
                },
            )
            self.assertEqual(response.status_code, 200)

            response = self.client.post(
                "/{store_id}/get_bids_on_product",
                json={
                    "store_id": self.store_id,
                    "product_name": "Bread Loaf"
                }
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 2)
        finally:
            self.tearDown()

    def test_get_bids_by_user(self):
        try:
            response = self.client.post(
                "/{store_id}/make_bid",
                json={
                    "user_id": 100,
                    "store_id": self.store_id,
                    "product_name": "Bread Loaf",
                    "price": 2,
                    "quantity": 1,
                },
            )
            assert response.status_code == 200

            response = self.client.post(
                "/{store_id}/make_bid",
                json={
                    "user_id": 100,
                    "store_id": self.store_id,
                    "product_name": "Milk",
                    "price": 5,
                    "quantity": 2,
                },
            )
            assert response.status_code == 200

            response = self.client.get(
                "/get_bids_by_user?user_id=100"
            )
            assert response.status_code == 200
            assert len(response.json()) == 2
        finally:
            self.tearDown()





