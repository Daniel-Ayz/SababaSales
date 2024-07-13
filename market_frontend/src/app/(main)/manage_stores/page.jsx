// pages/manage_stores.jsx
"use client";

import React, { useState, useContext, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import axios from 'axios';
import { UserContext } from '../layout';
import Alert from '@mui/material/Alert';

export default function ManageStores() {
  const { user } = useContext(UserContext);
  const [stores, setStores] = useState([]);
  const [newStore, setNewStore] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (user.loggedIn === false) {
      window.location.href = '/unauthorized';
    }

    // Fetch existing stores for the user
    axios.get(`${process.env.NEXT_PUBLIC_STORES_ROUTE}manager_or_owner?user_id=${user.id}`, {
      headers: { 'Content-Type': 'application/json' }
    })
    .then(response => {
      setStores(response.data);
    })
    .catch(error => {
      console.error('Error fetching stores:', error);
    });

  }, [user]);

  const addStore = () => {
    if (newStore.trim() !== '' && description.trim() !== '') {
      // Check if the store name already exists
      const storeExists = stores.some(store => store.name.toLowerCase() === newStore.toLowerCase());
      if (storeExists) {
        setError('Store with this name already exists.');
        return;
      }

      axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}?user_id=${user.id}`, {
        name: newStore,
        description: description,
      }, {
        headers: { 'Content-Type': 'application/json' }
      })
      .then(response => {
        const newStoreData = response.data;
        setStores([...stores, newStoreData]);
        setNewStore('');
        setDescription('');
        setError('');
        window.location.reload();
      })
      .catch(error => {
        setError('An error occurred while adding the store.');
        console.error('Error adding store:', error);
      });
    } else {
      setError('Store name and description cannot be empty.');
    }
  };

  const toggleStoreActiveStatus = (storeId, isActive) => {
    const endpoint = isActive
      ? `${process.env.NEXT_PUBLIC_STORES_ROUTE}stores/%7Bstore_id%7D/close_store`
      : `${process.env.NEXT_PUBLIC_STORES_ROUTE}stores/%7Bstore_id%7D/reopen_store`;

    axios.put(endpoint, {
      user_id: user.id,
      store_id: storeId
    }, {
      headers: { 'Content-Type': 'application/json' }
    })
    .then(response => {
      setStores(stores.map(store =>
        store.id === storeId ? { ...store, is_active: !isActive } : store
      ));
    })
    .catch(error => {
      console.error(`Error ${isActive ? 'closing' : 'reopening'} store:`, error);
    });
  };

  const manageStore = (id) => {
    window.location.href = `/manage_stores/${id}`;
  };


  // Ensure the user context is fully initialized before rendering
  if (user.loggedIn === undefined) return null;

  return (
    <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8 bg-gray-100">
      <Head>
        <title>Manage Your Stores</title>
        <meta name="description" content="A page to manage owned stores" />
      </Head>

      <div className="sm:mx-auto sm:w-full sm:max-w-lg">
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">Manage Your Stores</h2>
        <div className="mt-8 space-y-6">
          {error && (
            <Alert severity="error">{error}</Alert>
          )}
          <div className="flex flex-col space-y-4">
            <input
              type="text"
              value={newStore}
              onChange={(e) => setNewStore(e.target.value)}
              placeholder="Enter store name"
              className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            />
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter store description"
              className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            />
            <button
              onClick={addStore}
              className="flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Add Store
            </button>
          </div>

          <div className="mt-8 space-y-4">
            {stores.map(store => (
              <div key={store.id} className="flex items-center justify-between p-4 bg-white rounded-md shadow-sm ring-1 ring-gray-300">
                <span
                  onClick={() => manageStore(store.id)}
                  className="cursor-pointer text-lg font-medium text-gray-900"
                >
                  {store.name}
                </span>
                <button
                  onClick={() => toggleStoreActiveStatus(store.id, store.is_active)}
                  className={`ml-4 flex-shrink-0 ${
                    store.is_active
                      ? 'bg-green-600 hover:bg-green-500'
                      : 'bg-red-600 hover:bg-red-500'
                  } text-white font-semibold py-2 px-4 rounded-md shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
                    store.is_active ? 'focus-visible:outline-green-600' : 'focus-visible:outline-red-600'
                  }`}
                >
                  {store.is_active ? 'Open' : 'Close'}
                </button>
              </div>
            ))}
          </div>

          <p className="mt-10 text-center text-sm text-gray-500">
            <Link href="/" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
              Back to home page
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
