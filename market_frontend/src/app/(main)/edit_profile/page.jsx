"use client"
import axios from "axios"
import Alert from '@mui/material/Alert';
import Link from 'next/link'
import { useState, useContext, useEffect } from "react";
import { UserContext } from "../layout";
import { useRouter } from 'next/navigation';

axios.defaults.withCredentials = true;

export default function EditProfile() {
  const { user, setUser } = useContext(UserContext);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    address: '',
    city: '',
    country: '',
    zip: '',
    holder: '',
    holder_identification_number: '',
    currency: '',
    credit_card_number: '',
    expiration_date: '',
    security_code: '',
    full_name: ''
  });
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertType, setAlertType] = useState('error');
  const router = useRouter();

  useEffect(() => {
    // Fetch current user data and populate form
    axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}`, {
      withCredentials: true
    })
    .then(response => {
      setFormData({
        username: response.data.username,
        email: response.data.email,
        password: '',
        address: response.data.address || '',
        city: response.data.city || '',
        country: response.data.country || '',
        zip: response.data.zip || '',
        holder: response.data.holder || '',
        holder_identification_number: response.data.holder_identification_number || '',
        currency: response.data.currency || '',
        credit_card_number: response.data.credit_card_number || '',
        expiration_date: response.data.expiration_date || '',
        security_code: response.data.security_code || '',
        full_name: response.data.full_name || ''
      });
    })
    .catch(error => {
      console.log("Error fetching user data:", error);
    });
  }, [user.id]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };
  const handleSubmitUserUpdate = () => {
    axios.put(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${user.id}`, {
      username: formData.username,
      email: formData.email,
      password: formData.password
    }, {
      headers: {'Content-Type': 'application/json'},
      withCredentials: true
    })
    .then(response => {
      setUser({ loggedIn: true, userName: response.data.username, id: response.data.id });
      setAlertMessage('Profile updated successfully!');
      setAlertType('success');
      setShowAlert(true);
    })
    .catch(error => {
      console.log("Error updating profile:", error.response);
      setAlertMessage('Failed to update profile. Please try again.');
      setAlertType('error');
      setShowAlert(true);
    });
  };

  const handleSubmit = (url, data) => {
    console.log("Sending data:", data);
    axios.post(url, data, {
      headers: {'Content-Type': 'application/json'},
      withCredentials: true
    })
    .then(response => {
      console.log("Response from server:", response.data);
      setAlertMessage('Update successful!');
      setAlertType('success');
      setShowAlert(true);
    })
    .catch(error => {
      console.log("Error updating:", error.response.data);
      setAlertMessage('Failed to update. Please try again.');
      setAlertType('error');
      setShowAlert(true);
    });
  };

  const handleDelete = () => {
    axios.delete(`${process.env.process.env.NEXT_PUBLIC_USERS_ROUTE}/${user.id}`, {
      withCredentials: true
    })
    .then(response => {
      setUser({loggedIn: false, userName: '', id: ''});
      router.push('/');
    })
    .catch(error => {
      console.log("Error deleting user:", error.response);
      setAlertMessage('Failed to delete user. Please try again.');
      setAlertType('error');
      setShowAlert(true);
    });
  };

  return (
    <>
      <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-sm">
          <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
            Edit Profile
          </h2>
        </div>

        <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
          <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); handleSubmitUserUpdate(); }}>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium leading-6 text-gray-900">
                  User Name
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium leading-6 text-gray-900">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div className="mt-4">
                <button
                  type="submit"
                  className="flex w-full justify-center rounded-md bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Update Profile
                </button>
              </div>
            </div>
          </form>


          <form className="space-y-6 mt-6" onSubmit={(e) => { e.preventDefault(); handleSubmit(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${user.id}/update_Full_Name`, { Full_Name: formData.full_name }); }}>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium leading-6 text-gray-900">
                  Full Name
                </label>
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  value={formData.full_name}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div className="mt-4">
                <button
                  type="submit"
                  className="flex w-full justify-center rounded-md bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Update Full Name
                </button>
              </div>
            </div>
          </form>

          <form className="space-y-6 mt-6" onSubmit={(e) => { e.preventDefault(); handleSubmit(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${user.id}/update_delivery_info`, { address: formData.address, city: formData.city, country: formData.country, zip: formData.zip }); }}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="address" className="block text-sm font-medium leading-6 text-gray-900">
                  Address
                </label>
                <input
                  id="address"
                  name="address"
                  type="text"
                  value={formData.address}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="city" className="block text-sm font-medium leading-6 text-gray-900">
                  City
                </label>
                <input
                  id="city"
                  name="city"
                  type="text"
                  value={formData.city}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="country" className="block text-sm font-medium leading-6 text-gray-900">
                  Country
                </label>
                <input
                  id="country"
                  name="country"
                  type="text"
                  value={formData.country}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="zip" className="block text-sm font-medium leading-6 text-gray-900">
                  Zip
                </label>
                <input
                  id="zip"
                  name="zip"
                  type="text"
                  value={formData.zip}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div className="mt-4">
              <button
                type="submit"
                className="flex w-full justify-center rounded-md bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Update Delivery Info
              </button>
            </div>
          </form>

          <form className="space-y-6 mt-6" onSubmit={(e) => { e.preventDefault(); handleSubmit(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${user.id}/update_payment_info`, { holder: formData.holder, holder_identification_number: formData.holder_identification_number, currency: formData.currency, credit_card_number: formData.credit_card_number, expiration_date: formData.expiration_date, security_code: formData.security_code }); }}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="holder" className="block text-sm font-medium leading-6 text-gray-900">
                  Card Holder Name
                </label>
                <input
                  id="holder"
                  name="holder"
                  type="text"
                  value={formData.holder}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="holder_identification_number" className="block text-sm font-medium leading-6 text-gray-900">
                  Holder Identification Number
                </label>
                <input
                  id="holder_identification_number"
                  name="holder_identification_number"
                  type="text"
                  value={formData.holder_identification_number}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="currency" className="block text-sm font-medium leading-6 text-gray-900">
                  Currency
                </label>
                <input
                  id="currency"
                  name="currency"
                  type="text"
                  value={formData.currency}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="credit_card_number" className="block text-sm font-medium leading-6 text-gray-900">
                  Credit Card Number
                </label>
                <input
                  id="credit_card_number"
                  name="credit_card_number"
                  type="text"
                  value={formData.credit_card_number}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="expiration_date" className="block text-sm font-medium leading-6 text-gray-900">
                  Expiration Date
                </label>
                <input
                  id="expiration_date"
                  name="expiration_date"
                  type="text"
                  value={formData.expiration_date}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>

              <div>
                <label htmlFor="security_code" className="block text-sm font-medium leading-6 text-gray-900">
                  Security Code
                </label>
                <input
                  id="security_code"
                  name="security_code"
                  type="text"
                  value={formData.security_code}
                  onChange={handleChange}
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div className="mt-4">
              <button
                type="submit"
                className="flex w-full justify-center rounded-md bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Update Payment Info
              </button>
            </div>
          </form>

          {showAlert && <Alert severity={alertType} onClose={() => setShowAlert(false)}>{alertMessage}</Alert>}

          <div className="mt-6 text-center">
            <button
              onClick={handleDelete}
              className="flex w-full justify-center rounded-md bg-red-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Delete Profile
            </button>
          </div>

          <div className="mt-6 text-center">
            <a href='/' className="text-indigo-600 hover:text-indigo-500">Back to Home</a>
          </div>
        </div>
      </div>
    </>
  );
}
