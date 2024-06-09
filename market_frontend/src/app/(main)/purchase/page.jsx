// pages/checkout.js
"use client"
import { useClient } from 'next/client';
import { useState } from 'react';
import axios from 'axios';
import { UserContext } from '../layout'; // Adjust the import according to your file structure
import { useContext } from "react";
import { useRouter } from 'next/navigation';
axios.defaults.withCredentials = true;

const Checkout = () => {
  const { user } = useContext(UserContext); // Access user context
  const [state, setState] = useState(false); // Mark the component as a Client Component

  const [shippingInfo, setShippingInfo] = useState({
    firstName: '',
    lastName: '',
    company: '',
    address: '',
    apartment: '',
    city: '',
    country: 'United States',
    state: '',
    postalCode: '',
    phone: '',
  });

  const [paymentInfo, setPaymentInfo] = useState({
    cardNumber: '',
    nameOnCard: '',
    expirationDate: '',
    cvc: '',
  });

  const [deliveryMethod, setDeliveryMethod] = useState('standard');
  const router = useRouter();
  
  const handleShippingChange = (e) => {
    const { name, value } = e.target;
    setShippingInfo({ ...shippingInfo, [name]: value });
  };

  const handlePaymentChange = (e) => {
    const { name, value } = e.target;
    setPaymentInfo({ ...paymentInfo, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const { id: user_id, cartId: cart_id } = user; // Destructure user context

    axios.post(`http://localhost:8000/api/${user_id}/${cart_id}/make_purchase`, user, {
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true,
    })
      .then(response => {
        const purchaseId = response.data.purchase_id; // Extract purchase ID from response
        console.log('Order successful:', response.data);
        // Redirect to the receipt page with the purchase ID
        router.push(`/receipt?purchaseId=${purchaseId}`);
      })
      .catch(error => {
        console.error('Order failed:', error);
        // Show an error message to the user
      });
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Checkout</h1>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <h2 className="text-xl font-semibold">Shipping Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              name="firstName"
              value={shippingInfo.firstName}
              onChange={handleShippingChange}
              placeholder="First name"
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="lastName"
              value={shippingInfo.lastName}
              onChange={handleShippingChange}
              placeholder="Last name"
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="company"
              value={shippingInfo.company}
              onChange={handleShippingChange}
              placeholder="Company"
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="address"
              value={shippingInfo.address}
              onChange={handleShippingChange}
              placeholder="Address"
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="apartment"
              value={shippingInfo.apartment}
              onChange={handleShippingChange}
              placeholder="Apartment, suite, etc."
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="city"
              value={shippingInfo.city}
              onChange={handleShippingChange}
              placeholder="City"
              className="border p-2 w-full"
            />
            <select
              name="country"
              value={shippingInfo.country}
              onChange={handleShippingChange}
              className="border p-2 w-full"
            >
              <option value="United States">United States</option>
              {/* Add more country options here */}
            </select>
            <input
              type="text"
              name="state"
              value={shippingInfo.state}
              onChange={handleShippingChange}
              placeholder="State / Province"
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="postalCode"
              value={shippingInfo.postalCode}
              onChange={handleShippingChange}
              placeholder="Postal code"
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="phone"
              value={shippingInfo.phone}
              onChange={handleShippingChange}
              placeholder="Phone"
              className="border p-2 w-full"
            />
          </div>
        </div>

        <div className="mb-4">
          <h2 className="text-xl font-semibold">Delivery Method</h2>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="deliveryMethod"
                value="standard"
                checked={deliveryMethod === 'standard'}
                onChange={() => setDeliveryMethod('standard')}
                className="mr-2"
              />
              Standard (4-10 business days) - $5.00
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="deliveryMethod"
                value="express"
                checked={deliveryMethod === 'express'}
                onChange={() => setDeliveryMethod('express')}
                className="mr-2"
              />
              Express (2-5 business days) - $16.00
            </label>
          </div>
        </div>

        <div className="mb-4">
          <h2 className="text-xl font-semibold">Payment</h2>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="paymentMethod"
                value="creditCard"
                checked={true}
                readOnly
                className="mr-2"
              />
              Credit card
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="paymentMethod"
                value="paypal"
                className="mr-2"
              />
              PayPal
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="paymentMethod"
                value="etransfer"
                className="mr-2"
              />
              eTransfer
            </label>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <input
              type="text"
              name="cardNumber"
              value={paymentInfo.cardNumber}
              onChange={handlePaymentChange}
              placeholder="Card number"
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="nameOnCard"
              value={paymentInfo.nameOnCard}
              onChange={handlePaymentChange}
              placeholder="Name on card"
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="expirationDate"
              value={paymentInfo.expirationDate}
              onChange={handlePaymentChange}
              placeholder="Expiration date (MM/YY)"
              className="border p-2 w-full"
            />
            <input
              type="text"
              name="cvc"
              value={paymentInfo.cvc}
              onChange={handlePaymentChange}
              placeholder="CVC"
              className="border p-2 w-full"
            />
          </div>
        </div>

        <button
          type="submit"
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
        <a
          href="/receipt"
          className="flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700"
        >
          Confirm Order
        </a>
        </button>
      </form>
    </div>
  );
};

// from the confirm order button we will call the page to show the order confirmation and receipt
// not written yet
export default Checkout;


