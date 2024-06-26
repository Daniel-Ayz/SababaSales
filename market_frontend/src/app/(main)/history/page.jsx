"use client"
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
        <div className="container mx-auto p-4">
            {purchaseHistory.length > 0 ? (
                purchaseHistory.map((receipt) => (
                    <div key={receipt.purchase_id} className="border p-4 mb-4 rounded shadow">
                        <div className="flex justify-between items-center mb-2">
                            <div>
                                <h2 className="text-xl font-bold">Purchase ID: {receipt.purchase_id}</h2>
                                <p>Purchase Date: {new Date(receipt.purchase_date).toLocaleDateString()}</p>
                                <p>Total Quantity: {receipt.total_quantity}</p>
                            </div>
                            <p className="text-xl font-bold">${formatPrice(receipt.total_price)}</p>
                        </div>
                        {(receipt.baskets || []).map((basket) => (
                            <div key={basket.basket_id} className="mt-4 border-t pt-4">
                                <h3 className="text-lg font-bold">Basket ID: {basket.basket_id}</h3>
                                <p>Store ID: {basket.store_id}</p>
                                <p>Total Price: ${formatPrice(basket.total_price)}</p>
                                <p>Total Quantity: {basket.total_quantity}</p>
                                <p>Discount: ${formatPrice(basket.discount)}</p>
                                <div className="ml-4 mt-2">
                                    <h4 className="font-semibold">Products:</h4>
                                    {(basket.basket_products || []).map((product, index) => (
                                        <div key={index} className="flex justify-between mt-1">
                                            <p>{product.name} (x{product.quantity})</p>
                                            <p>${formatPrice(product.initial_price)}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                ))
            ) : (
                <p>No purchase history found.</p>
            )}
        </div>
    );
};

export default PurchaseHistory;
