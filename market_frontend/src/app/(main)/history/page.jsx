"use client";
import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { UserContext } from '../layout';

const PurchaseHistory = () => {
    const { user } = useContext(UserContext);
    const [purchaseHistory, setPurchaseHistory] = useState([]);

    useEffect(() => {
        if (user) {
            console.log('Fetching purchase history for user:', user); // Debugging log
            axios.get(`http://localhost:8000/api/purchase/${user.id}/get_purchase_history`)
                .then(response => {
                    console.log('Purchase history data:', response.data); // Debugging log
                    setPurchaseHistory(response.data);
                })
                .catch(error => {
                    console.error('Error fetching purchase history:', error);
                });
        }
    }, [user]);

    const formatPrice = (price) => {
        return typeof price === 'number' ? price.toFixed(2) : parseFloat(price).toFixed(2);
    };

    if (!user) {
        return <p>Loading user data...</p>;
    }

    return (
        <div className="container mx-auto p-4 bg-gray-100 min-h-screen">
            {purchaseHistory.length > 0 ? (
                purchaseHistory.map((receipt) => (
                    <div key={receipt.purchase_id} className="border p-4 mb-4 rounded shadow-lg bg-white">
                        <div className="flex justify-between items-center mb-2">
                            <div>
                                <h2 className="text-xl font-bold text-slate-700">Purchase ID: {receipt.purchase_id}</h2>
                                <p className="text-slate-500">Purchase Date: {new Date(receipt.purchase_date).toLocaleDateString()}</p>
                                <p className="text-slate-500">Total Quantity: {receipt.total_quantity}</p>
                            </div>
                            <p className="text-xl font-bold text-teal-600">${formatPrice(receipt.total_price)}</p>
                        </div>
                        {(receipt.baskets || []).map((basket) => (
                            <div key={basket.basket_id} className="mt-4 border-t pt-4 border-slate-200">
                                <h3 className="text-lg font-bold text-slate-600">Basket ID: {basket.basket_id}</h3>
                                <p className="text-slate-500">Store ID: {basket.store_id}</p>
                                <p className="text-slate-500">Total Price: <span className="text-teal-600">${formatPrice(basket.total_price)}</span></p>
                                <p className="text-slate-500">Total Quantity: {basket.total_quantity}</p>
                                <p className="text-slate-500">Discount: <span className="text-rose-600">${formatPrice(basket.discount)}</span></p>
                                <div className="ml-4 mt-2">
                                    <h4 className="font-semibold text-slate-600">Products:</h4>
                                    {(basket.basket_products || []).map((product, index) => (
                                        <div key={index} className="flex justify-between mt-1">
                                            <p className="text-slate-500">{product.name} (x{product.quantity})</p>
                                            <p className="text-slate-500">${formatPrice(product.initial_price)}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                ))
            ) : (
                <p className="text-slate-500">No purchase history found.</p>
            )}
            <div className="mt-8 text-center">
                <a href="/" className="font-semibold leading-6 text-indigo-500 hover:text-indigo-500">Back to home page</a>
            </div>
        </div>
    );
};

export default PurchaseHistory;
