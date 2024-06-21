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
      id: 1,
      image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg',
      description: 'Orange pouch'
    },
    {
      id: 2,
      image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg',
      description: 'Blue bag'
    },
    {
      id: 3,
      image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-03-product-01.jpg',
      description: 'Green hat'
    },
    {
      id: 4,
      image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-04-product-01.jpg',
      description: 'Red shoes'
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
            <img src={product.image} alt={product.description} className="w-full h-32 object-cover" />
            <div className="p-2">
              <h3 className="text-sm font-semibold mb-2">{product.description}</h3>
            </div>
          </div>
        ))}
      </div>
      <Link
        className="block mt-4 bg-blue-600 hover:bg-blue-800 text-white py-2 px-3 rounded text-center"
        href={`/productSearch/${store.id}`}
      >
        Continue shopping at {store.name}
      </Link>
    </div>
  );
};

export default ItemSquare;
