// pages/manage_stores/[store_id]/discounts.jsx
"use client";

import axios from "axios";
import React, { useState, useContext, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { UserContext } from '../../../layout';

axios.defaults.withCredentials = true;

export default function Discounts({ params }) {
  const store_id = params.store_id;

  const { user } = useContext(UserContext);
  const [simpleDiscounts, setSimpleDiscounts] = useState([]);
  const [conditionalDiscounts, setConditionalDiscounts] = useState([]);
  const [compositeDiscounts, setCompositeDiscounts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDiscounts = async () => {
      if (!user || !user.id) return;

      try {
        const response = await axios.post(`http://localhost:8000/api/stores/${store_id}/get_discount_policies`, {
          user_id: user.id,
          store_id: store_id
        });
        console.log('Fetched discounts:', response.data);

        const simpleDiscounts = [];
        const conditionalDiscounts = [];
        const compositeDiscounts = [];

        response.data.forEach(discount => {
          if (discount.hasOwnProperty('discount')) {
            conditionalDiscounts.push(discount);
          }
          else {
            simpleDiscounts.push(discount);
          }
        });

        setSimpleDiscounts(simpleDiscounts);
        setConditionalDiscounts(conditionalDiscounts);
        setCompositeDiscounts(compositeDiscounts);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching discounts:', error);
        toast.error('Failed to load discounts.');
        setLoading(false);
      }
    };

    fetchDiscounts();
  }, [store_id, user]);

  const handleAddDiscount = async (type) => {
    const discount = prompt('Enter discount details:');
    if (!discount) return;

    try {
      const response = await axios.post(`http://localhost:8000/api/stores/${store_id}/add_discount_policies`, {
        user_id: user.id,
        store_id: store_id
      });
      if (response.status === 200) {
        toast.success('Discount added successfully!');
        switch (type) {
          case 'simple':
            setSimpleDiscounts([...simpleDiscounts, discount]);
            break;
          case 'conditional':
            setConditionalDiscounts([...conditionalDiscounts, discount]);
            break;
          case 'composite':
            setCompositeDiscounts([...compositeDiscounts, discount]);
            break;
          default:
            break;
        }
      } else {
        toast.error('Failed to add discount.');
      }
    } catch (error) {
      console.error('Error adding discount:', error);
      toast.error('Failed to add discount.');
    }
  };

  const handleRemoveDiscount = async (type, index) => {
    try {
      const discountToRemove = { discount_id: '' };
      switch (type) {
        case 'simple':
          discountToRemove.discount_id = simpleDiscounts[index].id;
          break;
        case 'conditional':
          discountToRemove.discount_id = conditionalDiscounts[index].id;
          break;
        case 'composite':
          discountToRemove.discount_id = compositeDiscounts[index].id;
          break;
        default:
          break;
      }

      const response = await axios.delete(`http://localhost:8000/api/stores/${store_id}/remove_discount_policy`, {
        data: {
          role: {
            user_id: user.id,
            store_id: store_id
          },
          payload: {
            store_id: store_id,
            discount_id: discountToRemove.discount_id
          }
        }
      });

      if (response.status === 200) {
        toast.success('Discount removed successfully!');
        switch (type) {
          case 'simple':
            setSimpleDiscounts(simpleDiscounts.filter((_, i) => i !== index));
            break;
          case 'conditional':
            setConditionalDiscounts(conditionalDiscounts.filter((_, i) => i !== index));
            break;
          case 'composite':
            setCompositeDiscounts(compositeDiscounts.filter((_, i) => i !== index));
            break;
          default:
            break;
        }
      } else {
        toast.error('Failed to remove discount.');
      }
    } catch (error) {
      console.error('Error removing discount:', error);
      toast.error('Failed to remove discount.');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="flex flex-col h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-8">Manage Discounts for Store {store_id}</h1>
      <div className="grid grid-cols-3 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Simple Discounts</h2>
          <ul className="space-y-2">
            {simpleDiscounts.map((discount, index) => {
              const categories = JSON.parse(discount.applicable_categories || '[]');
              const products = (discount.applicable_products || []).map(product => product.name);
              return (
                <li key={index} className="flex flex-col justify-between items-start bg-white p-4 rounded shadow">
                  <div><strong>Percentage:</strong> {discount.percentage}%</div>
                  <div><strong>Applicable Categories:</strong> {categories.join(', ')}</div>
                  <div><strong>Applicable Products:</strong> {products.join(', ')}</div>
                  <button
                    onClick={() => handleRemoveDiscount('simple', index)}
                    className="text-red-500 hover:text-red-700 mt-2"
                  >
                    Remove
                  </button>
                </li>
              );
            })}
          </ul>
          <button
            onClick={() => handleAddDiscount('simple')}
            className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
          >
            Add Simple Discount
          </button>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-4">Conditional Discounts</h2>
          <ul className="space-y-2">
            {conditionalDiscounts.map((discount, index) => {
              const categories = JSON.parse(discount.discount.applicable_categories || '[]');
              const products = (discount.discount.applicable_products || []).map(product => product.name);
              return (
              <li key={index} className="flex flex-col justify-between items-start bg-white p-4 rounded shadow">
                {/* Replace with actual discount properties to render */}
                <div><strong>Percentage:</strong> {discount.discount.percentage}%</div>
                <div><strong>Applicable Categories:</strong> {categories.join(', ')}</div>
                <div><strong>Applicable Products:</strong> {products.join(', ')}</div>
                <div><strong>Details:</strong> {discount.details}</div>
                <button
                  onClick={() => handleRemoveDiscount('Conditional', index)}
                  className="text-red-500 hover:text-red-700 mt-2"
                >
                  Remove
                </button>
              </li>
              );
            })}
          </ul>
          <button
            onClick={() => handleAddDiscount('Conditional')}
            className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
          >
            Add Conditional Discount
          </button>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-4">Composite Discounts</h2>
          <ul className="space-y-2">
            {compositeDiscounts.map((discount, index) => (
              <li key={index} className="flex flex-col justify-between items-start bg-white p-4 rounded shadow">
                {/* Replace with actual discount properties to render */}
                <div><strong>Percentage:</strong> {discount.percentage}%</div>
                <div><strong>Details:</strong> {discount.details}</div>
                <button
                  onClick={() => handleRemoveDiscount('composite', index)}
                  className="text-red-500 hover:text-red-700 mt-2"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <button
            onClick={() => handleAddDiscount('composite')}
            className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
          >
            Add Composite Discount
          </button>
        </div>
      </div>
      <ToastContainer />
    </div>
  );
}
