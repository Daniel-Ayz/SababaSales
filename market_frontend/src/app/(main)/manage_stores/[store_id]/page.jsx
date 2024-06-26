// pages/manage_stores/[store_id]/page.jsx
"use client";

import axios from "axios";
import React, { useState, useContext, useEffect } from 'react';
import { UserContext, StoreProductsContext } from '../../layout';
import Alert from '@mui/material/Alert';
import Link from 'next/link';
import { ArrowLeftIcon } from '@heroicons/react/24/solid';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { X } from 'lucide-react'; // Import the X icon

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,

} from "@/components/dialog";

axios.defaults.withCredentials = true;

export default function ManageStore({ params }) {
  const store_id = params.store_id;
  const { user } = useContext(UserContext);
  const { storesProducts, setStoresProducts } = useContext(StoreProductsContext);
  const [store, setStore] = useState(null);
  const [items, setItems] = useState([]);
  const [staff, setStaff] = useState([]);
  const [discountRules, setDiscountRules] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');

  useEffect(() => {
    if (user.loggedIn === undefined) return; // Ensure the user context is fully initialized before fetching data

    if (!user.loggedIn) {
      window.location.href = '/unauthorized';
    }

    // Fetch store details and items
    const fetchStoreData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`http://localhost:8000/api/stores/${store_id}`);
        setStore(response.data);
        const itemsResponse = await axios.get(`http://localhost:8000/api/stores/${store_id}/products`);
        setItems(itemsResponse.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching store data:', error);
        setLoading(false);
      }
    };

    fetchStoreData();
  }, [store_id, user]);

  const manageItem = (itemId) => {
    alert(`Managing item with id: ${itemId}`);
    // Implement the logic for managing item, possibly showing a popup or navigating to another page
  };

  const assignStaff = async () => {
    try {
      // Implement the logic for assigning staff
      const response = await axios.post(`http://localhost:8000/api/stores/${store_id}/assign_staff`, { email });
      if (response.status === 200) {
        toast.success("Staff appointed successfully!");
        setEmail('');
      } else {
        toast.error("Failed to appoint staff.");
      }
    } catch (error) {
      console.error("Error assigning staff:", error);
      toast.error("Failed to appoint staff.");
    }
  };

  const addDiscountRule = () => {
    // Implement the logic for adding discount rule
    alert('Add discount rule logic to be implemented');
  };

  // Ensure the user context is fully initialized before rendering
  if (user.loggedIn === undefined || loading) return null;

  if (!store) return <div>Loading...</div>;

  const previewItems = items.slice(0, 5); // Select a few items to preview

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <main className="flex-1 overflow-y-auto p-8">
        <div className='w-[92vw] h-auto bg-white rounded-[40px] shadow-lg mx-auto grid grid-cols-[22vw_1fr] grid-rows-[auto_auto_auto_auto_1fr] gap-8 p-8'>
          <img className="border-2 border-gray-300 rounded-[20px] w-[20vw] h-[20vw] object-cover" src={store.image} alt={store.name} />
          <div className="flex flex-col space-y-4">
            <h3 className="text-3xl font-bold">{store.name}</h3>
            <h4 className='text-2xl font-semibold'>Store ID: {store.id}</h4>
            <Link href={`/stores/${store.id}`}>
              <button className="flex items-center space-x-2 text-blue-500 hover:text-blue-700 transition duration-200">
                <ArrowLeftIcon className="w-5 h-5" />
                <span>Go to Store</span>
              </button>
            </Link>
            {error && <Alert severity="error">{error}</Alert>}

            <h3 className="text-lg font-medium leading-6 text-gray-900">Add New Item</h3>
            <Link href={`/manage_stores/${store_id}/addItem`}>
              <button className="flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                Add Item
              </button>
            </Link>

            <h3 className="text-lg font-medium leading-6 text-gray-900">Appoint Staff</h3>
            <Dialog>
              <DialogTrigger asChild>
                <button
                  className="w-full flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                  Appoint Staff
                </button>
              </DialogTrigger>
              <DialogContent className="bg-white"> {/* Change the background color to white */}
                <DialogHeader>
                  <DialogTitle>Appoint Staff</DialogTitle>
                  <DialogDescription>
                    Enter the email of the user you want to appoint as staff for your store.
                  </DialogDescription>
                </DialogHeader>
                <div className="flex flex-col space-y-4">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter email"
                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  />
                  <button
                    onClick={assignStaff}
                    className="w-full flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                  >
                    Submit
                  </button>
                </div>
                <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none">
                  <X className="h-4 w-4" />
                  <span className="sr-only">Close</span>
                </DialogClose>
              </DialogContent>
            </Dialog>

            <h3 className="text-lg font-medium leading-6 text-gray-900">Add Discount Rule</h3>
            <button
              onClick={addDiscountRule}
              className="w-full flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Add Discount Rule
            </button>

            <p className="mt-10 text-center text-sm text-gray-500">
              <Link href="/manage_stores" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
                Back to Manage Stores
              </Link>
            </p>
          </div>
          <div className="space-y-4">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Preview Items</h3>
            <ul>
              {previewItems.map(item => (
                <li key={item.id} className="flex items-center justify-between p-4 bg-white rounded-md shadow-sm ring-1 ring-gray-300 cursor-pointer" onClick={() => manageItem(item.id)}>
                  <span className="text-lg font-medium text-gray-900">{item.name}</span>
                  <span className="text-lg font-medium text-gray-500">${item.price}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </main>
      <ToastContainer />
    </div>
  );
}
