"use client"
import axios from "axios";
import Alert from '@mui/material/Alert';
import React, { useContext, useEffect, useState } from 'react';
import ProductStars from "../../../product/productStars";
import { ShoppingCartIcon } from '@heroicons/react/24/outline';
import { StoreProductsContext, UserContext } from '../../../../layout';
// import { useRouter } from 'next/router'; // Import from 'next/router' instead of 'next/navigation'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Link from 'next/link'; // Import Link from next/link
import { ArrowLeftIcon } from '@heroicons/react/24/solid'; // Adjust the icon import as per your setup

axios.defaults.withCredentials = true;

//   async function add_to_cart(formData) {


//     axios.post('http://localhost:8000/api/users/register', {
//       username:  formData.get('username'),
//       email:  formData.get('email'),
//       password:  formData.get('password'),
//     },{headers: {'Content-Type': 'application/json'}, withCredentials: true})
//     .then(function (response) {
//       // set the user context and redirect:
//       console.log(response.data)
//       setSuccess(true)
//       setFailed(false)


//     })
//     .catch(function (error) {
//       console.log(error);
//       setFailed(true)
//       setSuccess(false)

//     });
export default function ProductBuyingPage({ params }) {
    const { store_id, product_id } = params;
    const { user } = useContext(UserContext);
    const { storesProducts } = useContext(StoreProductsContext);
    const [product, setProduct] = useState(null);
    const [count, setCount] = useState(0);

    useEffect(() => {
        const storeProducts = storesProducts[store_id];
        const decodedProductId = decodeURIComponent(product_id);
        const foundProduct = storeProducts ? storeProducts.find(p => p.name === decodedProductId) : null;
        if (foundProduct) {
            setProduct(foundProduct);
        } else {

            // Handle case where product is not found, e.g., redirect or show an error message
        }
    }, [store_id, product_id, storesProducts]);

    if (!product) {
        return <div>Loading...</div>;
    }

    const { name, initial_price, quantity, store, category, description, image } = product;
    console.log(product);


      const handleAddToCart = async () => {
        if (count === 0) {
            toast.error('You must add at least one item', {
                position: 'top-right',
                autoClose: 3000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
            });
            return

        }
        try {
            // Example of data to send to backend for adding to cart
            const data = {
                store_product_id: 0, // Assuming you have user context with id
                quantity: count,
                price: initial_price,
                name: name,
                store_id: product['store'].id,
                category: category,

            };

            // Example POST request to add item to cart
            const response = await axios.post('http://localhost:8000/api/users/cart/products', data,{headers: {'Content-Type': 'application/json'}, withCredentials: true});
            console.log(response.data); // Log response from backend

            toast.success('Item added to cart!', {
                position: 'top-right',
                autoClose: 3000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
            });

            // Optionally, you can redirect after adding to cart
            // router.push('/cart'); // Redirect to cart page after successful add

        } catch (error) {
            console.error('Error adding item to cart:', error);
            toast.error('Failed to add item to cart. Please try again later.', {
                position: 'top-right',
                autoClose: 3000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
            });
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            <main className="flex-1 overflow-y-auto p-8">
                <div className='w-[92vw] h-auto bg-white rounded-[40px] shadow-lg mx-auto grid grid-cols-[22vw_1fr] grid-rows-[auto_auto_auto_auto_1fr] gap-8 p-8'>
                    <img className="border-2 border-gray-300 rounded-[20px] w-[20vw] h-[20vw] object-cover" src={image} alt={name} />
                    <div className="flex flex-col space-y-4">
                        <h3 className="text-3xl font-bold">{name}</h3>
                        <ProductStars rating={2} />
                        <h4 className='text-2xl font-semibold'>${initial_price}</h4>
                            <Link href={`/stores/${store_id}`}>
                        <button className="flex items-center space-x-2 text-blue-500 hover:text-blue-700 transition duration-200">
                            <ArrowLeftIcon className="w-5 h-5" />
                            <span>Back to Store</span>
                        </button>
                        </Link>
                        <p className="text-gray-700">Product info: <br />{description}</p>
                        <div className="flex items-center space-x-4">
                            <button className="px-6 py-3 bg-gray-200 rounded-md shadow-md text-lg" onClick={() => setCount(count - 1)} disabled={count === 0}>-</button>
                            <span className="px-6 py-3 bg-gray-100 border-x border-gray-400 text-lg">{count}</span>
                            <button className="px-6 py-3 bg-gray-200 rounded-md shadow-md text-lg" onClick={() => setCount(count + 1)} disabled={count >= quantity}>+</button>
                        </div>
                        <button className="mt-10 bg-blue-500 text-white px-6 py-3 rounded-md shadow-md flex items-center space-x-2 text-lg hover:bg-blue-600 transition duration-200" onClick={handleAddToCart}>
                            <ShoppingCartIcon className="w-6" /> <span>Add To Cart</span>
                        </button>
                    </div>
                </div>
            </main>
            <ToastContainer />
        </div>
    );
}
