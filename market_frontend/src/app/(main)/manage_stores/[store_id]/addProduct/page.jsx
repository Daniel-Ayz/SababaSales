"use client"
import axios from "axios";
import Alert from '@mui/material/Alert';
import Link from 'next/link';
import { useState, useContext } from "react";
import { UserContext } from "../../../layout";
import { useRouter } from 'next/navigation';

axios.defaults.withCredentials = true;

export default function AddProduct({ params }) {
    const store_id = params.store_id;
    const { user } = useContext(UserContext);
    const [showAlert, setShowAlert] = useState(false);
    const [alertMessage, setAlertMessage] = useState('');
    const router = useRouter();

    async function addProduct(event) {
        event.preventDefault();

        const formData = new FormData(event.target);

        const productData = {
            role: {
                user_id: user.id,
                store_id: parseInt(store_id),
            },
            payload: {
                name: formData.get('name'),
                initial_price: parseFloat(formData.get('initial_price')),
                quantity: parseInt(formData.get('quantity')),
                category: formData.get('category'),
                image_link: formData.get('image_link'),
            }
        };

        console.log('Product data to be sent:', productData);

        try {
            const response = await axios.post(`${process.env.NEXT_PUBLIC_SOTRES_ROUTE}${store_id}/add_product`, productData, {
                headers: { 'Content-Type': 'application/json' },
                withCredentials: true
            });
            console.log('Response:', response.data);
            router.push(`/manage_stores/${store_id}`);
        } catch (error) {
            console.error('There was an error adding the product:', error);
            console.error('Error response:', error.response);

            let errorMessage = 'There was an error adding the product.';
            if (error.response && error.response.data) {
                const errorData = error.response.data;
                if (errorData.detail) {
                    errorMessage = Array.isArray(errorData.detail)
                        ? errorData.detail.map(e => e.msg).join(', ')
                        : errorData.detail;
                } else if (errorData.msg) {
                    errorMessage = errorData.msg;
                }
            }

            setAlertMessage(errorMessage);
            setShowAlert(true);
        }
    }

    return (
        <>
            <div className="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
                <div className="sm:mx-auto sm:w-full sm:max-w-sm">
                    <img
                        className="mx-auto h-10 w-auto object-cover h-48 w-46"
                        src="SababaSales-logoB.png"
                        alt="Your Company"
                    />
                    <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                        Add Product
                    </h2>
                </div>
                <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
                    <form className="space-y-6" onSubmit={addProduct}>
                        <div>
                            <label htmlFor="name" className="block text-sm font-medium leading-6 text-gray-900">
                                Product Name
                            </label>
                            <div className="mt-2">
                                <input
                                    id="name"
                                    name="name"
                                    type="text"
                                    required
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>
                        <div>
                            <label htmlFor="initial_price" className="block text-sm font-medium leading-6 text-gray-900">
                                Initial Price
                            </label>
                            <div className="mt-2">
                                <input
                                    id="initial_price"
                                    name="initial_price"
                                    type="number"
                                    step="0.01"
                                    required
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>
                        <div>
                            <label htmlFor="quantity" className="block text-sm font-medium leading-6 text-gray-900">
                                Quantity
                            </label>
                            <div className="mt-2">
                                <input
                                    id="quantity"
                                    name="quantity"
                                    type="number"
                                    required
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>
                        <div>
                            <label htmlFor="category" className="block text-sm font-medium leading-6 text-gray-900">
                                Category
                            </label>
                            <div className="mt-2">
                                <input
                                    id="category"
                                    name="category"
                                    type="text"
                                    required
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                            <label htmlFor="category" className="block text-sm font-medium leading-6 text-gray-900">
                                Image Link - Not Required
                            </label>
                            <div className="mt-2">
                                <input
                                    id="image_link"
                                    name="image_link"
                                    type="text"
                                    className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                />
                            </div>
                        </div>
                        <div>
                            <button
                                type="submit"
                                className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                            >
                                Add Product
                            </button>
                        </div>
                        {showAlert && (
                            <Alert severity="error">{alertMessage}</Alert>
                        )}
                    </form>
                </div>
            </div>
        </>
    );
}
