"use client";
import Link from 'next/link';
import React from 'react';
import './homepage.css'; // Assuming you have additional styles here

const ItemSquare = ({ store, products }) => {
  // Mock data for testing
  const mockStore = {
    id: 1,
    name: 'Mock Store'
  };

const mockProducts = [
  {
    name: 'Orange pouch',
    initial_price: 10.00,
    quantity: 0,
    store: {
      id: 1,
      name: 'Store 1',
      description: 'A store description',
      created_at: '2024-06-22T13:40:11.259Z',
      is_active: true
    },
    category: 'Accessories',
    // image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg',
  },
  {
    name: 'Blue bag',
    initial_price: 10.00,
    quantity: 0,
    store: {
      id: 2,
      name: 'Store 2',
      description: 'A store description',
      created_at: '2024-06-22T13:40:11.259Z',
      is_active: true
    },
    category: 'Bags',
    // image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg',
  },
  {
    name: 'Green hat',
    initial_price: 10.00,
    quantity: 0,
    store: {
      id: 3,
      name: 'Store 3',
      description: 'A store description',
      created_at: '2024-06-22T13:40:11.259Z',
      is_active: true
    },
    category: 'Hats',
    // image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-03-product-01.jpg',
  },
  {
    name: 'Red shoes',
    initial_price: 10.00,
    quantity: 0,
    store: {
      id: 4,
      name: 'Store 4',
      description: 'A store description',
      created_at: '2024-06-22T13:40:11.259Z',
      is_active: true
    },
    category: 'Shoes',
    // image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-04-product-01.jpg',
  }
];


  // Use mock data for testing
  products = products.length > 0 ? products : mockProducts;
  store = store ? store : mockStore;

  return (
   <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <h2 className="text-xl font-semibold mb-4">{store.name}</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {products.map((product, index) => (
          <div key={index} className="bg-gray-100 rounded-lg overflow-hidden shadow-sm">
            <img src={product.image} alt={product.name} className="w-full h-32 object-cover" />
            <div className="p-2">
              <h3 className="text-sm font-semibold mb-2">{product.name}</h3>
            </div>
          </div>
        ))}
      </div>
      <Link
        className="block mt-4 bg-blue-600 hover:bg-blue-800 text-white py-2 px-3 rounded text-center"
        href={`/stores/${store.id}`}
      >
        Continue shopping at {store.name}
      </Link>
    </div>
  );
};

export default ItemSquare;
