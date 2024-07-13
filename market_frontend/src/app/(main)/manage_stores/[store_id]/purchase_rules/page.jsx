// pages/manage_stores/[store_id]/purchase_policies.jsx
"use client";

import axios from "axios";
import React, { useState, useContext, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { UserContext } from '../../../layout';

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

export default function PurchasePolicies({ params }) {
  const store_id = params.store_id;

  const { user } = useContext(UserContext);
  const [purchasePolicies, setPurchasePolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [policyData, setPolicyData] = useState({
    conditions: [],
    combine_function: "",
  });
  const [conditionData, setConditionData] = useState({
    applies_to: "",
    name_of_apply: "",
    condition: "",
    value: "",
  });

  useEffect(() => {
    const fetchPolicies = async () => {
      if (!user || !user.id) return;

      try {
        const response = await axios.post(`${process.env.NEXT_PUBLIC_SOTRES_ROUTE}${store_id}/get_purchase_policies`, {
          user_id: user.id,
          store_id: store_id
        });

        const policiesWithConditions = [];
        for (const policy of response.data) {
          const conditionsResponse = await axios.post(`${process.env.NEXT_PUBLIC_SOTRES_ROUTE}${store_id}/get_conditions`, {
            store_id: store_id,
            to_discount: false,
            target_id: policy.id
          });
          const combination_functions = await axios.post(`${process.env.NEXT_PUBLIC_SOTRES_ROUTE}${store_id}/get_combine_function`, {
            store_id: store_id,
            to_discount: false,
            target_id: policy.id
          });

          policiesWithConditions.push({
            ...policy,
            conditions: conditionsResponse.data,
            combine_function: combination_functions.data || null
          });
        }

        setPurchasePolicies(policiesWithConditions);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching policies:', error);
        toast.error('Failed to load policies.');
        setLoading(false);
      }
    };

    fetchPolicies();
  }, [store_id, user]);


  const handleAddCondition = () => {
    const condition = {
      applies_to: conditionData.applies_to,
      name_of_apply: conditionData.name_of_apply,
      condition: conditionData.condition,
      value: conditionData.value,
    };

    setPolicyData({
      ...policyData,
      conditions: [...policyData.conditions, condition],
    });

    setConditionData({
      applies_to: "",
      name_of_apply: "",
      condition: "",
      value: "",
    });
  };


  const handleAddPolicy = async () => {
    try {
      let payload = {
        store_id: store_id,
        is_root: true,
      };

      if (policyData.combine_function !== "") {
        payload = {
          ...payload,
          combine_function: policyData.combine_function,
          policies: policyData.conditions.map(condition => ({
            store_id: store_id,
            is_root: false,
            condition: condition,
          })),
        };
      } else {
        payload = {
          ...payload,
          condition: policyData.conditions[0],
        };
      }

      console.log('Adding policy with payload:', payload);

      const response = await axios.post(`${process.env.NEXT_PUBLIC_SOTRES_ROUTE}${store_id}/add_purchase_policy`, {
        role: {
          user_id: user.id,
          store_id: store_id,
        },
        payload: payload,
      });

      if (response.status === 200) {
        toast.success('Policy added successfully!');
        setPurchasePolicies([...purchasePolicies, response.data.policy]);
        setDialogOpen(false);
        setPolicyData({
          conditions: [],
          combine_function: "",
        });
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
      const response = await axios.delete(`${process.env.NEXT_PUBLIC_SOTRES_ROUTE}${store_id}/remove_purchase_policy`, {
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
                {policy && policy.combine_function && (
                  <div><strong>Combine Function:</strong> {policy.combine_function}</div>
                )}
                <div><strong>Conditions:</strong>
                  <ul className="ml-4 list-disc">
                    {policy && policy.conditions && Array.isArray(policy.conditions) ? (
                      policy.conditions.map((condition, condIndex) => (
                        <li key={condIndex}>
                          <strong>Condition {condIndex + 1}:</strong> {condition.applies_to} : {condition.name_of_apply} must be {condition.condition} {condition.value}
                        </li>
                      ))
                    ) : (
                      <li>No conditions available</li>
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
            onClick={() => setDialogOpen(true)}
            className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
          >
            Add Policy
          </button>
        </div>
      </div>
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogTrigger asChild>
          <button className="hidden"></button>
        </DialogTrigger>
        <DialogContent className="bg-white">
          <DialogHeader>
            <DialogTitle>Add Purchase Policy</DialogTitle>
            <DialogDescription>
              Fill in the details below to add a new purchase policy. Mind That the Combine Function is optional for one condition.
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col space-y-4">
            <label>
              Applies To:
              <select
                value={conditionData.applies_to}
                onChange={(e) => setConditionData({ ...conditionData, applies_to: e.target.value })}
                className="w-full p-2 border rounded"
              >
                <option value="">Select Applies To</option>
                <option value="product">Product</option>
                <option value="category">Category</option>
                <option value="time">Time</option>
                <option value="age">Age</option>
              </select>
            </label>
            <label>
              Name of Apply:
              <input
                type="text"
                value={conditionData.name_of_apply}
                onChange={(e) => setConditionData({ ...conditionData, name_of_apply: e.target.value })}
                className="w-full p-2 border rounded"
              />
            </label>
            <label>
              Condition:
              <select
                value={conditionData.condition}
                onChange={(e) => setConditionData({ ...conditionData, condition: e.target.value })}
                className="w-full p-2 border rounded"
              >
                <option value="">Select Condition</option>
                <option value="at_least">At Least</option>
                <option value="equal">Equal</option>
                <option value="at_most">At Most</option>
              </select>
            </label>
            <label>
              Value:
              <input
                type="number"
                value={conditionData.value}
                onChange={(e) => setConditionData({ ...conditionData, value: e.target.value })}
                className="w-full p-2 border rounded"
              />
            </label>
            <button
              onClick={handleAddCondition}
              className="bg-green-600 hover:bg-green-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
            >
              Add Condition
            </button>
            <label>
              Combine Function:
              <select
                value={policyData.combine_function}
                onChange={(e) => setPolicyData({ ...policyData, combine_function: e.target.value })}
                className="w-full p-2 border rounded"
              >
                <option value="">Select Function</option>
                <option value="AND">AND</option>
                <option value="OR">OR</option>
                <option value="XOR">XOR</option>
              </select>
            </label>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleAddPolicy}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
            >
              Add Policy
            </button>
          </div>
          <DialogClose asChild>
            <button className="hidden"></button>
          </DialogClose>
        </DialogContent>
      </Dialog>
      <ToastContainer />
    </div>
  );
}
