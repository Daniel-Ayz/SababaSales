from django.test import TestCase

from marketapi.purchase.models import Product

# Create your tests here.
class TestPurchase(TestCase):
    def test_make_purchase_of_all_products_in_cart_positive(self):
        # Prepare test data
        products = [Product.objects.create(name='Product 1', stock_quantity=10, price=10),
                    Product.objects.create(name='Product 2', stock_quantity=5, price=20),
                    Product.objects.create(name='Product 3', stock_quantity=3, price=30)]
        
        # Perform the test
        response = self.client.post('/api/purchase/all', data={})
        self.assertEqual(response.status_code, 200)

        # Assertions
        # Verify that the purchase is successfully completed
        self.assertEqual(response.json()['status'], 'success')

        # Check if the order approval is received
        self.assertTrue(response.json()['order_approval'])

        # Verify that the stock quantity of each product is updated accordingly
        for product in products:
            updated_product = Product.objects.get(id=product.id)
            self.assertEqual(updated_product.stock_quantity, product.stock_quantity - 1)

        # Verify that the total price of the purchase is calculated correctly
        total_price = sum([product.price for product in products])
        self.assertEqual(response.json()['total_price'], total_price)
        self.assertEqual(response.json()['error_message'], 'Payment verification failed')



    def test_supply_service_failure(self):
        # Prepare test data
        products = [Product.objects.create(name='Product 1', stock_quantity=10, price=10),
                    Product.objects.create(name='Product 2', stock_quantity=5, price=20),
                    Product.objects.create(name='Product 3', stock_quantity=3, price=30)]
        
        # Simulate failure in supply service verification
        supply_service_verification = False
        
        # Perform the test
        response = self.client.post('/api/purchase/all', data={})
        self.assertEqual(response.status_code, 200)

        # Assertions
        # Verify that the purchase is canceled
        self.assertEqual(response.json()['status'], 'failure')

        # Check if the error message is sent to the guest
        self.assertEqual(response.json()['error_message'], 'Supply service verification failed')


    def test_payment_failure(self):
        # Prepare test data
        products = [Product.objects.create(name='Product 1', stock_quantity=10, price=10),
                    Product.objects.create(name='Product 2', stock_quantity=5, price=20),
                    Product.objects.create(name='Product 3', stock_quantity=3, price=30)]
        
        # Simulate failure in payment verification
        payment_verification = False
        
        # Perform the test
        response = self.client.post('/api/purchase/all', data={})
        self.assertEqual(response.status_code, 200)

        # Assertions
        # Verify that the purchase is canceled
        self.assertEqual(response.json()['status'], 'failure')

        # Check if the error message is sent to the guest
        self.assertEqual(response.json()['error_message'], 'Payment verification failed')


    def test_purchase_unavailable_product(self):
        # Prepare test data
        products = [Product.objects.create(name='Product 1', stock_quantity=0, price=10),
                    Product.objects.create(name='Product 2', stock_quantity=5, price=20),
                    Product.objects.create(name='Product 3', stock_quantity=3, price=30)]
        
        # Perform the test
        response = self.client.post('/api/purchase/all', data={})
        self.assertEqual(response.status_code, 200)

        # Assertions
        # Verify that the purchase is canceled
        self.assertEqual(response.json()['status'], 'failure')

        # Check if the error message is sent to the guest
        self.assertEqual(response.json()['error_message'], 'Unavailable product in the shopping cart')



    def test_get_purchase_history_positive(self):
        # Prepare test data
        store_owner_id = 1
        store_id = 1
        
        # Perform the test
        response = self.client.get(f'/api/purchase/history/{store_owner_id}/{store_id}')
        self.assertEqual(response.status_code, 200)

        # Assertions
        # Verify that the system returns the store purchase history
        self.assertTrue(response.json()['purchase_history'])


    def test_get_purchase_history_store_not_exist(self):
        # Prepare test data
        invalid_store_id = 999
        
        # Perform the test
        response = self.client.get(f'/api/purchase/history/{invalid_store_id}')
        self.assertEqual(response.status_code, 404)

        # Assertions
        # Verify that the system returns an appropriate message indicating that the store does not exist
        self.assertEqual(response.json()['message'], 'Store does not exist')


    def test_get_purchase_history_actor_not_store_owner(self):
        # Prepare test data
        regular_member_id = 1
        
        # Perform the test
        response = self.client.get(f'/api/purchase/history/{regular_member_id}')
        self.assertEqual(response.status_code, 403)

        # Assertions
        # Verify that the system returns an appropriate message indicating that the actor is not a store owner
        self.assertEqual(response.json()['message'], 'You are not a store owner')