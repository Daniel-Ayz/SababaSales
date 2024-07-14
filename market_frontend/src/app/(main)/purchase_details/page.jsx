// pages/checkout.js
"use client"
import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { UserContext } from '../layout';
import { useRouter } from 'next/navigation';
import Alert from '@mui/material/Alert';
import Link from 'next/link';

axios.defaults.withCredentials = true;

export default function Details() {
  const { user } = useContext(UserContext);
  const [errorState, setErrorState] = useState(''); 
  const [showAlert, setShowAlert] = useState(false);
  const [showAlertGood, setShowAlertGood] = useState(false);
  const [showAlertBad, setShowAlertBad] = useState(false);
  const [paymentInfo, setPaymentInfo] = useState('');
  const [deliveryInfo, setDeliveryInfo] = useState('');
  
  const router = useRouter();

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

  const handleShippingChange = (e) => {
    const { name, value } = e.target;
    setShippingInfo({ ...shippingInfo, [name]: value });
  };

  useEffect(() => {
    // Fetch payment information when the component mounts
    if (user.loggedIn) {
      axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${user.id}/get_payment_information`)
        .then(response => {
          setPaymentInfo(response.data);
        })
        .catch(error => {
          console.error('Error fetching payment information:', error);
          // Handle error fetching payment information
        });

      axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${user.id}/get_delivery_information`)
      .then(response => {
        setDeliveryInfo(response.data);
      })
      .catch(error => {
        console.error('Error fetching delivery information:', error);
        // Handle error fetching delivery information
      });
    }
  }, [user]);


  async function makePurchase(e) {
    e.preventDefault();

    if (!user.loggedIn) {
      console.log("user not logged in. please login before making a purchase");
      setShowAlert(true);
    } else {
      axios.post(`${process.env.NEXT_PUBLIC_PURCHASE_ROUTE}/${user.id}/${user.cart_id}/make_purchase`)
        .then(function (response) {
          console.log('Order successful:', response.data);
          setShowAlertGood(true);
          setErrorState('');
        })
        .catch(function (error) {
          console.error('Order failed:', error);
          setShowAlertBad(true);
          setErrorState(error.response ? error.response.data : 'Unknown error');
        });
    }
  }

  const renderError = () => {
    if (typeof errorState === 'string') {
      return errorState;
    } else if (typeof errorState === 'object') {
      return JSON.stringify(errorState['detail']);
    }
    return 'An unknown error occurred';
  }

  return (
    <div className="container mx-auto p-4 h-screen flex flex-col justify-between">
      {showAlert && (
        <div className="mb-4">
          <Alert severity="error">Please login before making a purchase</Alert>
          <p className="text-center text-xs text-gray-500">
            Not logged in?{' '}
            <Link href="/login" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
              Login here
            </Link>
          </p>
        </div>
      )}

      <h1 className="text-2xl font-bold mb-4 text-center">Checkout</h1>
      
      <form className="flex-1 overflow-auto" onSubmit={makePurchase}>
        <div className="mb-4">
          <h2 className="text-lg font-semibold mb-2">Shipping Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        </div>
      </div>

          <div>
            <h2 className="flex w-full justify-center text-lg font-semibold mb-4">Payment Information</h2>
            <input
              type="text"
              name="Holder:"
              value={paymentInfo.holder}
              placeholder="paymentInfo.holder"
              className="border p-2 w-full rounded"
            />
            <input
              type="text"
              name="Identification Number:"
              value={paymentInfo.holder_identification_number}
              placeholder="paymentInfo.holder_identification_number"
              className="border p-2 w-full rounded"
            />
            <input
              type="text"
              name="Currency:"
              value={paymentInfo.currency}
              placeholder="paymentInfo.currency"
              className="border p-2 w-full rounded"
            />
            <input
              type="text"
              name="Credit Card Number:"
              value={paymentInfo.credit_card_number}
              placeholder="paymentInfo.credit_card_number"
              className="border p-2 w-full rounded"
            />
            <input
              type="text"
              name="Expiration Date:"
              value={paymentInfo.expiration_date}
              placeholder="paymentInfo.expiration_date"
              className="border p-2 w-full rounded"
            />
          </div>

          <div>
            <h2 className="flex w-full justify-center text-lg font-semibold mb-4">Delivery Information</h2>
            <input
              type="text"
              name="Address:"
              value={deliveryInfo.address}
              placeholder="deliveryInfo.address"
              className="border p-2 w-full rounded"
            />
            <input
              type="text"
              name="City:"
              value={deliveryInfo.city}
              placeholder="deliveryInfo.city"
              className="border p-2 w-full rounded"
            />
            <input
              type="text"
              name="Country:"
              value={deliveryInfo.country}
              placeholder="deliveryInfo.country"
              className="border p-2 w-full rounded"
            />
            <input
              type="text"
              name="Zip:"
              value={deliveryInfo.zip}
              placeholder="deliveryInfo.zip"
              className="border p-2 w-full rounded"
            />
          </div>

        <p className="flex w-full justify-center text-lg font-semibold mb-4">
          Want to change payment/delivery details?{' '}
          <Link href="/edit_profile" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
            Click here
          </Link>
        </p>
        
        <div>
          <button
            type="submit"
            className="flex w-full justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Confirm Order
          </button>
        </div>
      </form>

      {showAlertBad && (
        <div className="mt-4">
          <Alert severity="error">
            Unsuccessful Order<br />
            {renderError()}
          </Alert>
        </div>
      )}

      {showAlertGood && (
        <div className="mt-4">
          <Alert severity="success">Order confirmed!</Alert>
          <p className="text-center text-xs text-gray-500">
            <Link href="/history" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
              To your orders
            </Link>
          </p>
        </div>
      )}

      <p className="text-center text-xs text-gray-500 mt-4">
        <Link href="/" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
          Back to home page
        </Link>
      </p>
    </div>
  );
}
