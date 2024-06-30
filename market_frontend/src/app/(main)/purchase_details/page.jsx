// pages/checkout.js
"use client"
import React from 'react';
import { useState } from 'react';
import axios from 'axios';
axios.defaults.withCredentials = true;
import { UserContext } from '../layout';
import { useContext } from "react";
import { useRouter } from 'next/navigation';
import Alert from '@mui/material/Alert';
import Link from 'next/link'

export default function Details() {
  const { user } = useContext(UserContext); // Access user context
  const [state, setState] = useState(false); // Mark the component as a Client Component
  const [showAlert, setShowAlert] = useState(false)
  const [showAlertGood, setShowAlertGood] = useState(false);
  const [showAlertBad, setShowAlertBad] = useState(false);
  
  const router = useRouter()

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
  
  const handleShippingChange = (e) => {
    const { name, value } = e.target;
    setShippingInfo({ ...shippingInfo, [name]: value });
  };

  const handlePaymentChange = (e) => {
    const { name, value } = e.target;
    setPaymentInfo({ ...paymentInfo, [name]: value });
  };

  async function makePurchase() {
    
    if(!user.loggedIn){
      console.log("user not logged in. please login before making a purchase")
      setShowAlert(true)
    }
    else{
      axios.post(`http://localhost:8000/api/purchase/${user.id}/${user.cart_id}/make_purchase`)
        .then(function (response){
          console.log('Order successful:', response.data)
          setShowAlertGood(true)
        })
        .catch (function (error) {
          console.error('Order failed:', error)
          setShowAlertBad(true)
        });
    }
  }

  return (
    <div className="container mx-auto p-2 h-screen flex flex-col justify-between">
        {showAlert && (
      <Alert severity="error">please login before making a purchase</Alert>
      )}
        {showAlert && (<p className="text-center text-xs text-gray-500">
        Not logged in?{' '}
        <Link href ="/login" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
          Login here
        </Link>
      </p>)}
      <h1 className="text-xl font-bold mb-2">Checkout</h1>
      <form className="flex-1 overflow-auto" action={makePurchase}>
        <div className="mb-2">
          <h2 className="text-lg font-semibold">Shipping Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <input
              type="text"
              name="firstName"
              value={shippingInfo.firstName}
              onChange={handleShippingChange}
              placeholder="First name"
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="lastName"
              value={shippingInfo.lastName}
              onChange={handleShippingChange}
              placeholder="Last name"
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="company"
              value={shippingInfo.company}
              onChange={handleShippingChange}
              placeholder="Company"
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="address"
              value={shippingInfo.address}
              onChange={handleShippingChange}
              placeholder="Address"
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="apartment"
              value={shippingInfo.apartment}
              onChange={handleShippingChange}
              placeholder="Apartment, suite, etc."
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="city"
              value={shippingInfo.city}
              onChange={handleShippingChange}
              placeholder="City"
              className="border p-1 w-full"
            />
            <select
              name="country"
              value={shippingInfo.country}
              onChange={handleShippingChange}
              className="border p-1 w-full"
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
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="postalCode"
              value={shippingInfo.postalCode}
              onChange={handleShippingChange}
              placeholder="Postal code"
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="phone"
              value={shippingInfo.phone}
              onChange={handleShippingChange}
              placeholder="Phone"
              className="border p-1 w-full"
            />
          </div>
        </div>

        <div className="mb-2">
          <h2 className="text-lg font-semibold">Delivery Method</h2>
          <div className="flex gap-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="deliveryMethod"
                value="standard"
                checked={deliveryMethod === 'standard'}
                onChange={() => setDeliveryMethod('standard')}
                className="mr-1"
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
                className="mr-1"
              />
              Express (2-5 business days) - $16.00
            </label>
          </div>
        </div>

        <div className="mb-2">
          <h2 className="text-lg font-semibold">Payment</h2>
          <div className="flex gap-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="paymentMethod"
                value="creditCard"
                checked={true}
                readOnly
                className="mr-1"
              />
              Credit card
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="paymentMethod"
                value="paypal"
                className="mr-1"
              />
              PayPal
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="paymentMethod"
                value="etransfer"
                className="mr-1"
              />
              eTransfer
            </label>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
            <input
              type="text"
              name="cardNumber"
              value={paymentInfo.cardNumber}
              onChange={handlePaymentChange}
              placeholder="Card number"
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="nameOnCard"
              value={paymentInfo.nameOnCard}
              onChange={handlePaymentChange}
              placeholder="Name on card"
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="expirationDate"
              value={paymentInfo.expirationDate}
              onChange={handlePaymentChange}
              placeholder="Expiration date (MM/YY)"
              className="border p-1 w-full"
            />
            <input
              type="text"
              name="cvc"
              value={paymentInfo.cvc}
              onChange={handlePaymentChange}
              placeholder="CVC"
              className="border p-1 w-full"
            />
          </div>
        </div>
        <div>
          <button
            type="submit"
            className="flex w-full justify-center rounded-md bg-indigo-600 px-2 py-1 text-xs font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
              Confirm Order
          </button>
        </div>
      </form>
      {showAlertBad && (
          <Alert severity="error">Unsuccessful Order.</Alert>
          )}
        {showAlertGood && (
          <Alert severity="success">Order confirmed!</Alert>
          )}

      <p className="text-center text-xs text-gray-500">
          <Link href = "/" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
            Back to home page
            </Link>
        </p>

        {showAlertGood && (
          <p className="text-center text-xs text-gray-500">
          <Link href = "/history" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
            To your orders
            </Link>
        </p>
        )}
    </div>
  );
};
