// pages/manage_stores/[store_id]/discounts.jsx
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

export default function Discounts({ params }) {
  const store_id = params.store_id;

  const { user } = useContext(UserContext);
  const [simpleDiscounts, setSimpleDiscounts] = useState([]);
  const [conditionalDiscounts, setConditionalDiscounts] = useState([]);
  const [compositeDiscounts, setCompositeDiscounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [discountType, setDiscountType] = useState('');
  const [discountData, setDiscountData] = useState({
    percentage: 0,
    applicable_products: '',
    applicable_categories: '',
    condition: '',
    value: '',
    appliesTo: '',
    appliesOn: '',
    combineFunction: '',
    selectedDiscounts: [],
    conditions: []
  });

  useEffect(() => {
    const fetchDiscounts = async () => {
      if (!user || !user.id) return;

      try {
        const response = await axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${store_id}/get_discount_policies`, {
          user_id: user.id,
          store_id: store_id
        });

        const simpleDiscounts = [];
        const conditionalDiscounts = [];
        const conditionsConditionalDiscounts = [];
        const compositeDiscounts = [];

        for (const discount of response.data) {
          if (discount.hasOwnProperty('discount') && !discount.hasOwnProperty('combine_function')) {
            conditionalDiscounts.push(discount);
            const conditionsResponse = await axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${store_id}/get_conditions`, {
              store_id: store_id,
              to_discount: true,
              target_id: discount.id
            });
            conditionsConditionalDiscounts.push(conditionsResponse.data);
          } else if (discount.hasOwnProperty('combine_function')) {
            compositeDiscounts.push(discount);
          } else {
            simpleDiscounts.push(discount);
          }
        }
        // zip the conditions with the conditional discounts:
        const zippedConditionalDiscounts = conditionalDiscounts.map((discount, index) => ({
          ...discount,
          conditions: conditionsConditionalDiscounts[index]
        }));

        setSimpleDiscounts(simpleDiscounts);
        setConditionalDiscounts(zippedConditionalDiscounts);
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


  const handleAddDiscount = async () => {
    if (discountType === 'composite') {
      await handleAddCompositeDiscount();
    } else {
      await handleAddSimpleOrConditionalDiscount();
    }
  };

  const handleAddCompositeDiscount = async () => {
    if (!discountData.combineFunction || discountData.selectedDiscounts.length < 2) {
      toast.error('Please select a combination function and at least two discounts to combine.');
      return;
    }


    const selectedDiscountsPayload = discountData.selectedDiscounts.map(id => {
      const simpleDiscount = simpleDiscounts.find(d => d.id === parseInt(id));
      if (simpleDiscount) {
        return {
          store_id: store_id,
          is_root: false,
          percentage: simpleDiscount.percentage,
          applicable_products: simpleDiscount.applicable_products ? simpleDiscount.applicable_products.map(p => p.name) : [],
          applicable_categories: simpleDiscount.applicable_categories ? JSON.parse(simpleDiscount.applicable_categories) : [],
        };
      }

      const conditionalDiscount = conditionalDiscounts.find(d => d.id === parseInt(id));
      if (conditionalDiscount) {
        return {
          store_id: store_id,
          is_root: false,
          percentage: conditionalDiscount.discount.percentage,
          applicable_products: conditionalDiscount.discount.applicable_products ? conditionalDiscount.discount.applicable_products.map(p => p.name) : [],
          applicable_categories: conditionalDiscount.discount.applicable_categories ? JSON.parse(conditionalDiscount.discount.applicable_categories) : [],
          conditions: conditionalDiscount.conditions,
        };
      }

      return null;
    }).filter(d => d !== null);

    if (selectedDiscountsPayload.length === 0) {
      toast.error('No valid discounts selected to combine.');
      return;
    }

    const compositeDiscountPayload = {
      store_id: store_id,
      is_root: true,
      discounts: selectedDiscountsPayload,
      combine_function: discountData.combineFunction,
      conditions: discountData.conditions,
    };
    console.log(compositeDiscountPayload);

    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${store_id}/add_discount_policy`, {
        role: {
          user_id: user.id,
          store_id: store_id,
        },
        payload: compositeDiscountPayload,
      });
      if (response.status === 200) {
        toast.success('Composite discount added successfully!');
        setCompositeDiscounts([...compositeDiscounts, compositeDiscountPayload]);
        setDialogOpen(false);
      } else {
        toast.error('Failed to add composite discount.');
      }
    } catch (error) {
      console.error('Error adding composite discount:', error);
      toast.error('Failed to add composite discount.');
    }
  };


  const handleAddSimpleOrConditionalDiscount = async () => {
    const discount = { ...discountData };

    if (!discount.applicable_products && !discount.applicable_categories) {
      toast.error('Either applicable products or applicable categories must be specified.');
      return;
    }
    if (discount.applicable_products && discount.applicable_categories) {
      toast.error('Only one of applicable products or applicable categories can be specified.');
      return;
    }
    if (discountType === 'conditional' && (!discount.condition || !discount.value || discount.value <= 0)) {
      toast.error('Condition and value must be specified for conditional discounts.');
      return;
    }
    if (!discount.percentage || discount.percentage <= 0 || discount.percentage > 100) {
      toast.error('Invalid percentage value.');
      return;
    }

    if (discountType === 'simple') {
      try {
        const response = await axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${store_id}/add_discount_policy`, {
          role: {
            user_id: user.id,
            store_id: store_id,
          },
          payload: {
            store_id: store_id,
            is_root: true,
            percentage: discount.percentage,
            applicable_products: discount.applicable_products ? discount.applicable_products.split(',').map(item => item.trim()) : [],
            applicable_categories: discount.applicable_categories ? discount.applicable_categories.split(',').map(item => item.trim()) : [],
          },
        });
        if (response.status === 200) {
          toast.success('Discount added successfully!');
          setSimpleDiscounts([...simpleDiscounts, discount]);
          setDialogOpen(false);
        } else {
          toast.error('Failed to add discount.');
        }
      } catch (error) {
        console.error('Error adding discount:', error);
        toast.error('Failed to add discount.');
      }
    } else if (discountType === 'conditional') {
      try {
        const response = await axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${store_id}/add_discount_policy`, {
          role: {
            user_id: user.id,
            store_id: store_id,
          },
          payload: {
            store_id: store_id,
            is_root: true,
            condition: {
              applies_to: discount.appliesTo,
              name_of_apply: discount.appliesOn,
              condition: discount.condition,
              value: discount.value,
            },
            discount: {
              store_id: store_id,
              is_root: false,
              percentage: discount.percentage,
              applicable_products: discount.applicable_products ? discount.applicable_products.split(',').map(item => item.trim()) : [],
              applicable_categories: discount.applicable_categories ? discount.applicable_categories.split(',').map(item => item.trim()) : [],
            },
          },
        });
        if (response.status === 200) {
          toast.success('Discount added successfully!');
          setConditionalDiscounts([...conditionalDiscounts, discount]);
          setDialogOpen(false);
        } else {
          toast.error('Failed to add discount.');
        }
      } catch (error) {
        console.error('Error adding discount:', error);
        toast.error('Failed to add discount.');
      }
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
          discountToRemove.discount_id = index;
          break;
        default:
          break;
      }

      const response = await axios.delete(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${store_id}/remove_discount_policy`, {
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
            setCompositeDiscounts(compositeDiscounts.filter((discount) => discount.id !== index));
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

  const renderCompositeDiscount = (discount) => (
    <li key={discount.id} className="flex flex-col justify-between items-start bg-white p-4 rounded shadow">
      <div><strong>Combination Function:</strong> {discount.combine_function}</div>
      {discount.discounts && discount.discounts.map((subDiscount, index) => {
        let applicableCategories = [];
        try {
          applicableCategories = Array.isArray(subDiscount.applicable_categories)
            ? subDiscount.applicable_categories
            : JSON.parse(subDiscount.applicable_categories || '[]');
        } catch (e) {
          applicableCategories = [];
        }
        return (
          <div key={index} className="ml-4 mt-2 border-l-2 pl-2">
            <div><strong>Sub-Discount {index + 1}:</strong></div>
            <div><strong>Percentage:</strong> {subDiscount.percentage}%</div>
            {applicableCategories.length > 0 && <div><strong>Applicable Categories:</strong> {applicableCategories.join(', ')}</div>}
            {subDiscount.applicable_products && <div><strong>Applicable Products:</strong> {subDiscount.applicable_products.map(p => p.name).join(', ')}</div>}
            {subDiscount.conditions && subDiscount.conditions.length > 0 && (
              <div>
                <strong>Conditions:</strong>
                <ul className="ml-4 list-disc">
                  {subDiscount.conditions.map((condition, condIndex) => (
                    <li key={condIndex}>
                      <strong>Condition {condIndex + 1}:</strong> {condition.name_of_apply} must be {condition.condition} {condition.value}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {subDiscount.discounts && subDiscount.discounts.length > 0 && (
              <ul className="ml-4 space-y-2">
                {subDiscount.discounts.map(nestedDiscount => renderCompositeDiscount(nestedDiscount))}
              </ul>
            )}
          </div>
        );
      })}
      <button
        onClick={() => handleRemoveDiscount('composite', discount.id)}
        className="text-red-500 hover:text-red-700 mt-2"
      >
        Remove
      </button>
    </li>
  );



  if (loading) return <div>Loading...</div>;

  return (
    <div className="flex flex-col h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-8">Manage Discounts for Store {store_id}</h1>
      <div className="grid grid-cols-3 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Simple Discounts</h2>
          <ul className="space-y-2">
            {simpleDiscounts.map((discount, index) => {
              let categories = [];
              try {
                categories = Array.isArray(discount.applicable_categories)
                  ? discount.applicable_categories
                  : JSON.parse(discount.applicable_categories || '[]');
              } catch (e) {
                categories = [];
              }
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
            onClick={() => {
              setDiscountType('simple');
              setDialogOpen(true);
            }}
            className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
          >
            Add Simple Discount
          </button>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-4">Conditional Discounts</h2>
          <ul className="space-y-2">
            {conditionalDiscounts.map((discount, index) => {
              if (!discount.discount) return null;
              let categories = [];
              try {
                categories = Array.isArray(discount.discount.applicable_categories)
                  ? discount.discount.applicable_categories
                  : JSON.parse(discount.discount.applicable_categories || '[]');
              } catch (e) {
                categories = [];
              }
              const products = (discount.discount.applicable_products || []).map(product => product.name);
              const conditions = discount.conditions || [];
              return (
                <li key={index} className="flex flex-col justify-between items-start bg-white p-4 rounded shadow">
                  <div><strong>Percentage:</strong> {discount.discount.percentage}%</div>
                  <div><strong>Applicable Categories:</strong> {categories.join(', ')}</div>
                  <div><strong>Applicable Products:</strong> {products.join(', ')}</div>
                  <div><strong>Conditions:</strong>
                    <ul className="ml-4 list-disc">
                      {conditions.map((condition, condIndex) => (
                        <li key={condIndex}>
                          <strong>Condition {condIndex + 1}:</strong> {condition.name_of_apply} must be {condition.condition} {condition.value}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <button
                    onClick={() => handleRemoveDiscount('conditional', index)}
                    className="text-red-500 hover:text-red-700 mt-2"
                  >
                    Remove
                  </button>
                </li>
              );
            })}
          </ul>
          <button
            onClick={() => {
              setDiscountType('conditional');
              setDialogOpen(true);
            }}
            className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
          >
            Add Conditional Discount
          </button>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-4">Composite Discounts</h2>
          <ul className="space-y-2">
            {compositeDiscounts.map(discount => renderCompositeDiscount(discount))}
          </ul>
          <button
            onClick={() => {
              setDiscountType('composite');
              setDialogOpen(true);
            }}
            className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
          >
            Add Composite Discount
          </button>
        </div>
      </div>
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogTrigger asChild>
          <button className="hidden"></button>
        </DialogTrigger>
        <DialogContent className="bg-white">
          <DialogHeader>
            <DialogTitle>Add {discountType.charAt(0).toUpperCase() + discountType.slice(1)} Discount</DialogTitle>
            <DialogDescription>
              Fill in the details below to add a new discount.
            </DialogDescription>
          </DialogHeader>
          {discountType === 'composite' ? (
            <div className="flex flex-col space-y-4">
              <label>
                Combine Function:
                <select
                  value={discountData.combineFunction}
                  onChange={(e) => setDiscountData({ ...discountData, combineFunction: e.target.value })}
                  className="w-full p-2 border rounded"
                >
                  <option value="">Select Combine Function</option>
                  <option value="AND">AND</option>
                  <option value="OR">OR</option>
                  <option value="XOR">XOR</option>
                </select>
              </label>
              <label>
                Select Discounts to Combine:
                <select
                  multiple
                  value={discountData.selectedDiscounts}
                  onChange={(e) => setDiscountData({ ...discountData, selectedDiscounts: Array.from(e.target.selectedOptions, option => option.value) })}
                  className="w-full p-2 border rounded h-32"
                >
                  {simpleDiscounts.map((discount, index) => {
                    let categories = [];
                    try {
                      categories = Array.isArray(discount.applicable_categories)
                        ? discount.applicable_categories
                        : JSON.parse(discount.applicable_categories || '[]');
                    } catch (e) {
                      categories = [];
                    }
                    const products = (discount.applicable_products || []).map(product => product.name);
                    return (
                      <option key={index} value={discount.id}>
                        Simple: {discount.percentage}% - Categories: {categories.join(', ')} - Products: {products.join(', ')}
                      </option>
                    );
                  })}
                  {conditionalDiscounts.map((discount, index) => {
                    let categories = [];
                    try {
                      categories = Array.isArray(discount.discount.applicable_categories)
                        ? discount.discount.applicable_categories
                        : JSON.parse(discount.discount.applicable_categories || '[]');
                    } catch (e) {
                      categories = [];
                    }
                    const products = (discount.discount.applicable_products || []).map(product => product.name);
                    return (
                      <option key={index} value={discount.id}>
                        Conditional: {discount.discount.percentage}% - Categories: {categories.join(', ')} - Products: {products.join(', ')}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                Conditions:
                <textarea
                  value={discountData.conditions.map(JSON.stringify).join('\n')}
                  onChange={(e) => setDiscountData({ ...discountData, conditions: e.target.value.split('\n').map(condition => JSON.parse(condition)) })}
                  className="w-full p-2 border rounded"
                  placeholder='Enter conditions as JSON objects, one per line. E.g. {"applies_to": "category", "name_of_apply": "Dairy", "condition": "at_least", "value": 1}'
                />
              </label>
            </div>
          ) : (
            <div className="flex flex-col space-y-4">
              <label>
                Percentage:
                <input
                  type="number"
                  value={discountData.percentage}
                  onChange={(e) => setDiscountData({ ...discountData, percentage: e.target.value })}
                  className="w-full p-2 border rounded"
                />
              </label>
              <label>
                Applicable Products (comma separated):
                <input
                  type="text"
                  value={discountData.applicable_products}
                  onChange={(e) => setDiscountData({ ...discountData, applicable_products: e.target.value, applicable_categories: '' })}
                  className="w-full p-2 border rounded"
                />
              </label>
              <label>
                Applicable Categories (comma separated):
                <input
                  type="text"
                  value={discountData.applicable_categories}
                  onChange={(e) => setDiscountData({ ...discountData, applicable_categories: e.target.value, applicable_products: '' })}
                  className="w-full p-2 border rounded"
                />
              </label>
              {discountType === 'conditional' && (
                <>
                  <label>
                    Condition:
                    <select
                      value={discountData.condition}
                      onChange={(e) => setDiscountData({ ...discountData, condition: e.target.value })}
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
                      value={discountData.value}
                      onChange={(e) => setDiscountData({ ...discountData, value: e.target.value })}
                      className="w-full p-2 border rounded"
                    />
                  </label>
                  <label>
                    Applies To:
                    <select
                      value={discountData.appliesTo}
                      onChange={(e) => setDiscountData({ ...discountData, appliesTo: e.target.value })}
                      className="w-full p-2 border rounded"
                    >
                      <option value="">Select Applies To</option>
                      <option value="product">Product</option>
                      <option value="category">Category</option>
                      <option value="time">Time</option>
                      <option value="price">Price</option>
                    </select>
                  </label>
                  <label>
                    Applies On:
                    <input
                      type="text"
                      value={discountData.appliesOn}
                      onChange={(e) => setDiscountData({ ...discountData, appliesOn: e.target.value })}
                      className="w-full p-2 border rounded"
                      disabled={discountData.appliesTo === 'time'}
                    />
                  </label>
                </>
              )}
            </div>
          )}
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleAddDiscount}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md shadow-sm"
            >
              Add Discount
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
