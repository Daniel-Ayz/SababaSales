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
  const [managers, setManagers] = useState([]);
  const [owners, setOwners] = useState([]);

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
        const managers_response = await axios.post(`http://localhost:8000/api/stores/${store_id}/get_managers`, {
          user_id: user.id,
          store_id: store_id
        });
        for (let i = 0; i < managers_response.data.length; i++) {
          const full_name = await axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${managers_response.data[i].user_id}/get_full_name`);
          managers_response.data[i].Full_name = full_name.data;
        }

        setManagers(managers_response.data);
        const owners_response = await axios.post(`http://localhost:8000/api/stores/${store_id}/get_owners`, {
          user_id: user.id,
          store_id: store_id
        });
        for (let i = 0; i < owners_response.data.length; i++) {
          const full_name = await axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}${owners_response.data[i].user_id}/get_full_name`);
          owners_response.data[i].Full_name = full_name.data;
        }
        setOwners(owners_response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching store data:', error);
        setLoading(false);
      }
    };

    fetchStoreData();
  }, [store_id, user]);

  const removeItem = async (item_name) => {
    // ask the user if they are sure they want to delete the item
    if (confirm(`Are you sure you want to remove ${item_name} from the store?`)) {
      const response = await axios.delete(`http://localhost:8000/api/stores/${store_id}/remove_product`, {
        params: {
          product_name: item_name
        },
        data: {
          user_id: user.id,
          store_id: store_id
        },
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const updatedItems = items.filter(item => item.name !== item_name);
      setItems(updatedItems);
    }
  };

  const assignOwner = async () => {
    try {
      const response_ = await axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/get_user_id?email=${email}`);
      const user_id_ = response_.data.id;
      const response = await axios.post(`http://localhost:8000/api/stores/${store_id}/assign_owner`, {
        user_id: user_id_,
        store_id,
        assigned_by: user.id,
      });
      if (response.status === 200) {
        toast.success("Owner appointed successfully!");
        setEmail('');
        // Update the owners list
        const full_name = await axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${user_id_}/get_full_name`);
        setOwners([...owners, { user_id: user_id_, Full_name: full_name.data }]);
      } else {
        toast.error("Failed to appoint owner.");
      }
    } catch (error) {
      console.error("Error assigning owner:", error);
      toast.error("Failed to appoint owner.");
    }
  };

  const assignManager = async () => {
    try {
      const response_ = await axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/get_user_id?email=${email}`);
      const user_id_ = response_.data.id;
      const response = await axios.post(`http://localhost:8000/api/stores/${store_id}/assign_manager`, {
        user_id: user_id_,
        store_id,
        assigned_by: user.id,
      });
      if (response.status === 200) {
        toast.success("Manager appointed successfully!");
        setEmail('');
        // Update the managers list
        const full_name = await axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/${user_id_}/get_full_name`);
        setManagers([...managers, { user_id: user_id_, Full_name: full_name.data }]);
      } else {
        toast.error("Failed to appoint manager.");
      }
    } catch (error) {
      console.error("Error assigning manager:", error);
      toast.error("Failed to appoint manager.");
    }
  };

  const manageDiscountRules = () => {
    window.location.href = `/manage_stores/${store_id}/discounts`;
  };

  const managePurchaseRules = () => {
    window.location.href = `/manage_stores/${store_id}/purchase_rules`;
  };

  const addItem = () => {
    // Implement the logic for adding discount rule
    window.location.href = `/manage_stores/${store_id}/addProduct`
    //alert('Add discount rule logic to be implemented');
  };

  const EditItem = () => {
    // Implement the logic for adding discount rule
    window.location.href = `/manage_stores/${store_id}/editProduct`
    //alert('Add discount rule logic to be implemented');
  };

  const removeManager = async (user_id_) => {
    // Ask the user if they are sure they want to delete the item
    if (confirm(`Are you sure you want to remove this manager from the store?`)) {
      try {
        const response = await axios.delete(`http://localhost:8000/api/stores/${store_id}/remove_manager`, {
          data: {
            user_id: user_id_,
            store_id: store_id,
            removed_by: user.id,
          },
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (response.status === 200) {
          toast.success("Manager removed successfully!");
          setManagers(managers.filter(member => member.user_id !== user_id_));
        }
      } catch (error) {
        console.error("Error removing manager:", error);
        toast.error("Failed to remove manager.");
      }
    }
  };

  const removeOwner = async (user_id_) => {
    // Ask the user if they are sure they want to delete the item
    if (confirm(`Are you sure you want to remove this owner from the store?`)) {
      try {
        if (user.id === user_id_) {
          const query = `http://localhost:8000/api/stores/${store_id}/leave_ownership`;
        }
        else {
          const query = `http://localhost:8000/api/stores/${store_id}/remove_owner`;
        }
        const response = await axios.delete(query, {
          data: {
            user_id: user_id_,
            store_id: store_id,
            removed_by: user.id,
          },
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (response.status === 200) {
          toast.success("Owner removed successfully!");
          setOwners(owners.filter(member => member.user_id !== user_id_));
        }
      } catch (error) {
        console.error("Error removing owner:", error);
        toast.error("Failed to remove owner.");
      }
    }
  };



  // Ensure the user context is fully initialized before rendering
  if (user.loggedIn === undefined || loading) return null;

  if (!store) return <div>Loading...</div>;

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <main className="flex-1 overflow-y-auto p-8">
        <div className='w-[92vw] h-auto bg-white rounded-[40px] shadow-lg mx-auto grid grid-cols-[22vw_1fr_1fr] grid-rows-[auto_auto_auto_auto_1fr] gap-8 p-8'>
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

            <h3 className="text-lg font-medium leading-6 text-gray-900">Add Item</h3>
            <button
              onClick={() => addItem(store.id)}
              className="w-full flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Add Item
            </button>
            <h3 className="text-lg font-medium leading-6 text-gray-900">Edit Item</h3>
            <button
              onClick={() => EditItem(store.id)}
              className="w-full flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Edit Item
            </button>
            <h3 className="text-lg font-medium leading-6 text-gray-900">Appoint Owner</h3>
            <Dialog>
              <DialogTrigger asChild>
                <button
                  className="w-full flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                  Appoint Owner
                </button>
              </DialogTrigger>
              <DialogContent className="bg-white">
                <DialogHeader>
                  <DialogTitle>Appoint Owner</DialogTitle>
                  <DialogDescription>
                    Enter the email of the user new owner you want to appoint.
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
                    onClick={assignOwner}
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

            <h3 className="text-lg font-medium leading-6 text-gray-900">Appoint Manager</h3>
            <Dialog>
              <DialogTrigger asChild>
                <button
                  className="w-full flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                  Appoint Manager
                </button>
              </DialogTrigger>
              <DialogContent className="bg-white">
                <DialogHeader>
                  <DialogTitle>Appoint Manager</DialogTitle>
                  <DialogDescription>
                    Enter the email of the user you want to appoint as Manager.
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
                    onClick={assignManager}
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

            <h3 className="text-lg font-medium leading-6 text-gray-900">Manage Discount Rules</h3>
            <button
              onClick={manageDiscountRules}
              className="w-full flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Manage Discount Rules
            </button>

            <h3 className="text-lg font-medium leading-6 text-gray-900">Manage Purchase Rules</h3>
            <button
              onClick={managePurchaseRules}
              className="w-full flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Manage Purchase Rules
            </button>

            <p className="mt-10 text-center text-sm text-gray-500">
              <Link href="/manage_stores" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
                Back to Manage Stores
              </Link>
            </p>
          </div>
          <div className="space-y-4">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Select to remove an item</h3>
            <ul>
              {items.map(item => (
                <li key={item.id} className="flex items-center justify-between p-4 bg-white rounded-md shadow-sm ring-1 ring-gray-300 cursor-pointer" onClick={() => removeItem(item.name)}>
                  <span className="text-lg font-medium text-gray-900">{item.name}</span>
                  <span className="text-lg font-medium text-gray-500">${item.initial_price}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="space-y-4">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Select to remove an owner</h3>
            <ul>
              {owners.map(member => (
                <li key={member.user_id} className="flex items-center justify-between p-4 bg-white rounded-md shadow-sm ring-1 ring-gray-300 cursor-pointer" onClick={() => removeOwner(member.user_id)}>
                  <span className="text-lg font-medium text-gray-900">{member.Full_name}</span>
                  <span className="text-lg font-medium text-gray-500">{member.is_founder ? "Founder" : ""}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="space-y-4">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Select to remove a manager</h3>
            <ul>
              {managers.map(member => (
                <li key={member.user_id} className="flex items-center justify-between p-4 bg-white rounded-md shadow-sm ring-1 ring-gray-300 cursor-pointer" onClick={() => removeManager(member.user_id)}>
                  <span className="text-lg font-medium text-gray-900">{member.Full_name}</span>
                  <span className="text-lg font-medium text-gray-500">{member.is_founder ? "Founder" : ""}</span>
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
