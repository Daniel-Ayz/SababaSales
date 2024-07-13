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
import { CSSTransition } from 'react-transition-group';
import { CurrencyDollarIcon } from '@heroicons/react/24/solid';


axios.defaults.withCredentials = true;

//   async function add_to_cart(formData) {


//     axios.post('${process.env.NEXT_PUBLIC_USERS_ROUTE}/register', {
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
    const [bidcount, setBidCount] = useState(0);
    const [isBidDialogOpen, setIsBidDialogOpen] = useState(false);
    const [bidQuantity, setBidQuantity] = useState(1);
    const [bidPrice, setBidPrice] = useState('');
    const handleSendBid =async () => {
        // Send bid logic
        setIsBidDialogOpen(false); // Close the dialog after sending the bid
        // check that bid is a number and not a string:
        if (isNaN(bidPrice)) {
            toast.error('Please enter a valid number for your bid price', {
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
        if(!user.loggedIn){
            toast.error('Please login to bid on this product', {
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
                product_name: product.name,
                user_id: user.id,
                price: bidPrice,
                store_id: store_id,
                quantity: bidQuantity,


            };

            // Example POST request to add item to cart
            const response = await axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}${store_id}/make_bid`, data,{headers: {'Content-Type': 'application/json'}, withCredentials: true});
            console.log(response.data); // Log response from backend

            toast.success('Bid sent successfully. Make sure you keep track of it in your bid history!', {
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
            console.error('Error sending bid offer to store', error);
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

    const { name, initial_price, quantity, store, category, description, image, image_link } = product;
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
                image_link: image_link,

            };

            // Example POST request to add item to cart
            // console.log("DATAAAA", data);
            const response = await axios.post(`${process.env.NEXT_PUBLIC_USERS_ROUTE}cart/products`, data,{headers: {'Content-Type': 'application/json'}, withCredentials: true});
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
                         <button className="mt-4 bg-green-500 text-white px-6 py-3 rounded-md shadow-md flex items-center space-x-2 text-lg hover:bg-green-600 transition duration-200" onClick={() => setIsBidDialogOpen(true)}>
 <CurrencyDollarIcon className="h-6 w-6" />
                            <span>Bid on Product</span>
                        </button>
                    </div>
                </div>
            </main>
            <ToastContainer />
{isBidDialogOpen && (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center transition-opacity duration-900 ease-in-out">
        <div className="bg-white rounded-lg p-8 space-y-4 w-[80vw] md:w-[40vw] transform transition-transform duration-900 ease-in-out scale-100">
            <h2 className="text-2xl font-bold">Bid on Product</h2>
            <div className="flex flex-col space-y-4">
                <div className="flex items-center space-x-4">
                    <label className="w-1/3 text-lg">Quantity:</label>
                    <input
                        type="number"
                        min="1"
                        max={quantity}
                        value={bidQuantity}
                        onChange={(e) => setBidQuantity(e.target.value)}
                        className="flex-1 px-4 py-2 border rounded-md"
                    />
                </div>
                <div className="flex items-center space-x-4">
                    <label className="w-1/3 text-lg">Price:</label>
                    <div className="flex-1 flex items-center">
                        <span className="px-4 py-2 border border-r-0 rounded-l-md bg-gray-200">$</span>
                        <input
                            type="number"
                            value={bidPrice}
                            onChange={(e) => setBidPrice(e.target.value.replace(/\D/, ''))} // Removes non-numeric characters
                            className="flex-1 px-4 py-2 border rounded-r-md"
                        />
                    </div>
                </div>
            </div>
            <div className="flex justify-end space-x-4 mt-4">
                <button className="px-4 py-2 bg-gray-200 rounded-md" onClick={() => setIsBidDialogOpen(false)}>Cancel</button>
                <button className="px-4 py-2 bg-blue-500 text-white rounded-md" onClick={handleSendBid}>Send Bid</button>
            </div>
        </div>
    </div>
)}

        </div>
    );
}
