// pages/manage_stores/[store_id]/purchase_policies.jsx
"use client";

import axios from "axios";
import React, { useState, useContext, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { UserContext } from '../../../layout';

axios.defaults.withCredentials = true;

export default function PurchasePolicies({ params }) {
  const store_id = params.store_id;

  const { user } = useContext(UserContext);
  const [purchasePolicies, setPurchasePolicies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPolicies = async () => {
      if (!user || !user.id) return;

      try {
        const response = await axios.post(`http://localhost:8000/api/stores/${store_id}/get_purchase_policies`, {
          user_id: user.id,
          store_id: store_id
        });
        console.log('Fetched policies:', response.data);

        setPurchasePolicies(response.data || []);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching policies:', error);
        toast.error('Failed to load policies.');
        setLoading(false);
      }
    };

    fetchPolicies();
  }, [store_id, user]);

  const handleAddPolicy = async () => {
    const policy = prompt('Enter policy details:');
    if (!policy) return;

    try {
      const response = await axios.post(`http://localhost:8000/api/stores/${store_id}/add_purchase_policy`, {
        user_id: user.id,
        store_id: store_id,
        policy: JSON.parse(policy)  // Assuming the policy details are entered as a JSON string
      });
      if (response.status === 200) {
        toast.success('Policy added successfully!');
        setPurchasePolicies([...purchasePolicies, response.data.policy]);
      } else {
        toast.error('Failed to add policy.');
      }
    } catch (error) {
      console.error('Error adding policy:', error);
      toast.error('Failed to add policy.');
    }
  };

  const handleRemovePolicy = async (index) => {
    try {
      const policyToRemove = purchasePolicies[index];
      const response = await axios.delete(`http://localhost:8000/api/stores/${store_id}/remove_purchase_policy`, {
        data: {
          role: {
            user_id: user.id,
            store_id: store_id
          },
          payload: {
            store_id: store_id,
            policy_id: policyToRemove.id
          }
        }
      });

      if (response.status === 200) {
        toast.success('Policy removed successfully!');
        setPurchasePolicies(purchasePolicies.filter((_, i) => i !== index));
      } else {
        toast.error('Failed to remove policy.');
      }
    } catch (error) {
      console.error('Error removing policy:', error);
      toast.error('Failed to remove policy.');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="flex flex-col h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-8">Manage Purchase Policies for Store {store_id}</h1>
      <div className="grid grid-cols-1 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Composite Purchase Policies</h2>
          <ul className="space-y-2">
            {purchasePolicies.map((policy, index) => (
              <li key={index} className="flex flex-col justify-between items-start bg-white p-4 rounded shadow">
                <div><strong>Combine Function:</strong> {policy.combine_function}</div>
                <div><strong>Policies:</strong>
                  <ul className="ml-4 list-disc">
                    {policy.policies && Array.isArray(policy.policies) ? (
                      policy.policies.map((subPolicy, subIndex) => (
                        <li key={subIndex}>
                          <strong>Policy {subIndex + 1}:</strong>
                          <div>Type: {subPolicy.type}</div>
                          <div>Details: {JSON.stringify(subPolicy.details)}</div>
                        </li>
                      ))
                    ) : (
                      <li>No policies available</li>
                    )}
                  </ul>
                </div>
                <button
                  onClick={() => handleRemovePolicy(index)}
                  className="text-red-500 hover:text-red-700 mt-2"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <button
            onClick={handleAddPolicy}
            className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
          >
            Add Composite Policy
          </button>
        </div>
      </div>
      <ToastContainer />
    </div>
  );
}
