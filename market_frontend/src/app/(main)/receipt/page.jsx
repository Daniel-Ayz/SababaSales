"use client"
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

const OrderConfirmation = () => {
  const [orderData, setOrderData] = useState(null);
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (router && router.query) {
      const { purchaseId } = router.query; // Get the purchaseId from the query params

      if (purchaseId) {
        axios.get(`${process.env.NEXT_PUBLIC_STORES_ROUTE}`, {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        })
          .then(response => {
            setOrderData(response.data);
            setLoading(false);
          })
          .catch(error => {
            console.error('Failed to fetch order data:', error);
            setLoading(false);
          });
      } else {
        setLoading(false);
      }
    }
  }, [router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!orderData) {
    return <div>No order data found.</div>;
  }


  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Order #{orderData.orderNumber}</h1>
      <a href="/invoice" className="text-indigo-600 hover:text-indigo-800">View invoice</a>
      {orderData.items.map(item => (
        <div key={item.id} className="mb-4 p-4 border rounded-md">
          <div className="flex">
            <img src={item.image} alt={item.name} className="w-24 h-24 object-cover mr-4" />
            <div>
              <h2 className="text-xl font-semibold">{item.name}</h2>
              <p className="text-gray-600">{item.description}</p>
              <p className="text-gray-600">{item.price}</p>
            </div>
          </div>
          <div className="mt-4">
            <p><strong>Delivery address:</strong> {orderData.deliveryAddress}</p>
            <p><strong>Shipping updates:</strong> {orderData.shippingUpdates}</p>
            <a href="/edit" className="text-indigo-600 hover:text-indigo-800">Edit</a>
          </div>
        </div>
      ))}
      <div className="mt-4">
        <h2 className="text-xl font-semibold">Order Summary</h2>
        <p>Subtotal: {orderData.subtotal}</p>
        <p>Shipping: {orderData.shipping}</p>
        <p>Tax: {orderData.tax}</p>
        <p>Total: {orderData.total}</p>
      </div>
    </div>
  );
};

export default OrderConfirmation;
