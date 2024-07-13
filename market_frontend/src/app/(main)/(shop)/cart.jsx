import { Fragment, useEffect, useState } from 'react'
import { Dialog, DialogPanel, DialogTitle, Transition, TransitionChild } from '@headlessui/react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import axios from 'axios'
import Link from 'next/link'
import { UserContext } from '../layout';
import {useContext } from 'react';
import Alert from '@mui/material/Alert';

const products = [
  {
    id: 1,
    name: 'Throwback Hip Bag',
    href: '#',
    color: 'Salmon',
    price: '$90.00',
    quantity: 1,
    imageSrc: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg',
    imageAlt: 'Salmon orange fabric pouch with match zipper, gray zipper pull, and adjustable hip belt.',
  },
  {
    id: 2,
    name: 'Medium Stuff Satchel',
    href: '#',
    color: 'Blue',
    price: '$32.00',
    quantity: 1,
    imageSrc: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg',
    imageAlt:
      'Front of satchel with blue canvas body, black straps and handle, drawstring top, and front zipper pouch.',
  },
  // More products...
]
async function removeProductFromCart(product, setDeletedProduct) {


    axios.delete(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/cart/${product.id}`,
    {headers: {'Content-Type': 'application/json'}, withCredentials: true})
    .then(function (response) {
      // set the user context and redirect:
      console.log(response.data)
      setDeletedProduct(true)


    })
    .catch(function (error) {
      console.log('delete failed');
      setDeletedProduct(false)

    });
  }

// Cart.js
function Cart({ isOpen, setCart }) {
  const { user } = useContext(UserContext); // Access user context
  const [showAlert, setShowAlert] = useState(false)
 const [cartData, setCartData] = useState(
  {
    products: [],
  }
 );
 const [deletedProduct, setDeletedProduct] = useState(false);
 const [totalPrice, setTotalPrice] = useState(0);
 const [discount, setDiscount] = useState(0);
 const [total_discount, setTotalDiscount] = useState(0);

 useEffect(() => {
  if (!user.loggedIn) {
    console.log("user not logged in. please login before making a purchase")
    setShowAlert(true)
  }
  if (isOpen || deletedProduct) {
    axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}/cart`, {
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true
    })
    .then(response => {
      setTotalDiscount(0);
      const cartData = response.data;
      console.log("CART DATA",cartData)
      const productsList = [];
      var price = 0;

      cartData.baskets.forEach(basket => {
        basket.basket_products.forEach(product => {
          price += product.price * product.quantity;
          productsList.push({
            id: product.id,
            store_product_id: product.store_product_id,
            store_id: basket.store_id,
            quantity: product.quantity,
            name: product.name,
            price: product.price,
            image_link: product.image_link,
            category: product.category,
          });
        });
      });
      // Update the cart state with fetched data
      // check for discount:
      // var total_discount = 0;

      var disc_prod = [];
      var disc = 0;

      console.log(disc_prod);

      const discountPromises = cartData.baskets.map(basket => {
        disc_prod = basket.basket_products.map(product => ({
          product_name: product.name,
          category: product.category,
          quantity: product.quantity,
        }));

        return axios.post(`${process.env.NEXT_PUBLIC_STORES_ROUTE}/${basket.store_id}/calculate_cart_discount`,
          disc_prod,  // Send disc_prod directly as the payload
          {
            headers: { 'Content-Type': 'application/json' },
            withCredentials: true,
          })
          .then(response => {
            console.log(parseFloat(response.data));
            disc += parseFloat(response.data);
          })
          .catch(error => {
            console.log(error);
          });
      });

      Promise.all(discountPromises)
        .then(() => {
          setDiscount(disc);
          console.log("Total Discount:", disc);
        })
        .catch(error => {
          console.log("Error in processing discounts:", error);
        });


            setDiscount(disc);
            setCartData({ products: productsList });
            setTotalPrice(price);
            setDeletedProduct(false);
          })
          .catch(error => {
            console.log(error)
            // console.log('fetching cart failed');
            // Handle errors here if needed
          });
        }
      }, [isOpen,deletedProduct]); // Dependency array includes isOpen to refetch when cart is opened


    return (
        <Transition show={isOpen}>
        <Dialog className="relative z-10" onClose={() => {setCart(false)
          setDiscount(0)}}>
          <TransitionChild
            enter="ease-in-out duration-500"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in-out duration-500"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
          </TransitionChild>

          <div className="fixed inset-0 overflow-hidden">
            <div className="absolute inset-0 overflow-hidden">
              <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
                <TransitionChild
                  enter="transform transition ease-in-out duration-500 sm:duration-700"
                  enterFrom="translate-x-full"
                  enterTo="translate-x-0"
                  leave="transform transition ease-in-out duration-500 sm:duration-700"
                  leaveFrom="translate-x-0"
                  leaveTo="translate-x-full"
                >
                  <DialogPanel className="pointer-events-auto w-screen max-w-md">
                    <div className="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
                      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
                        <div className="flex items-start justify-between">
                          <DialogTitle className="text-lg font-medium text-gray-900">Shopping cart</DialogTitle>
                          <div className="ml-3 flex h-7 items-center">
                            <button
                              type="button"
                              className="relative -m-2 p-2 text-gray-400 hover:text-gray-500"
                              onClick={() => setCart(false)}
                            >
                              <span className="absolute -inset-0.5" />
                              <span className="sr-only">Close panel</span>
                              <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                            </button>
                          </div>
                        </div>

                        <div className="mt-8">
                          <div className="flow-root">
                            <ul role="list" className="-my-6 divide-y divide-gray-200">
                              {cartData.products.map((product) => (
                                <li key={product.id} className="flex py-6">
                                  <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-md border border-gray-200">
                                    <img
                                    // this is a temporary image, replace with actual image
                                      src={product.image_link}
                                      alt={"temp"}
                                      className="h-full w-full object-cover object-center"
                                    />
                                  </div>

                                  <div className="ml-4 flex flex-1 flex-col">
                                    <div>
                                      <div className="flex justify-between text-base font-medium text-gray-900">
                                        <h3>
                                          <a href={product.href}>{product.name}</a>
                                        </h3>
                                        <p className="ml-4">${product.price}</p>
                                      </div>
                                      <p className="mt-1 text-sm text-gray-500">{product.color}</p>
                                    </div>
                                    <div className="flex flex-1 items-end justify-between text-sm">
                                      <p className="text-gray-500">Qty {product.quantity}</p>

                                      <div className="flex">
                                        <button
                                          type="button"
                                          className="font-medium text-indigo-600 hover:text-indigo-500"
                                          onClick={() => removeProductFromCart(product,setDeletedProduct)}
                                        >
                                          Remove
                                        </button>
                                      </div>
                                    </div>
                                  </div>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>

                      <div className="border-t border-gray-200 px-4 py-6 sm:px-6">
                            <div className="flex justify-between text-base font-medium text-gray-900">
                    <p>Subtotal</p>
                    {discount > 0 ? (
                      <p>
                        <span className="line-through text-red-500">${totalPrice}</span>{' '}
                        <span className="rainbow-text">
                          It's your lucky day: ${totalPrice - discount}
                        </span>
                      </p>
                    ) : (
                      <p>${totalPrice}</p>
                    )}
                    <style jsx>{`
                      .rainbow-text {
                        background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet, red);
                        background-size: 300% 100%;
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        animation: rainbow-animation 5s linear infinite;
                      }

                      @keyframes rainbow-animation {
                        0% { background-position: 0% 50%; }
                        100% { background-position: 100% 50%; }
                      }
                    `}</style>
                  </div>
                                    <p className="mt-0.5 text-sm text-gray-500">Shipping and taxes calculated at checkout.</p>

                  {!user.loggedIn && (
                          <Alert severity="error">Please login before making a purchase</Alert>
                        )}
                        {!user.loggedIn && (
                          <p className="text-center text-xs text-gray-500">
                            Not logged in?{' '}
                            <Link href="/login" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
                              Login here
                            </Link>
                          </p>
                        )}
                        {user.loggedIn && (
                        <button>
                        <a
                          href="/purchase_details"
                          className="flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700"
                        >
                          Checkout
                        </a>
                        </button>)}


                        <div className="mt-6 flex justify-center text-center text-sm text-gray-500">
                          <p>
                            or{' '}
                            <button
                              type="button"
                              className="font-medium text-indigo-600 hover:text-indigo-500"
                              onClick={() => closeCart(false)}
                            >
                              Continue Shopping
                              <span aria-hidden="true"> &rarr;</span>
                            </button>
                          </p>
                        </div>
                      </div>
                    </div>
                  </DialogPanel>
                </TransitionChild>
              </div>
            </div>
          </div>
        </Dialog>
      </Transition>
    );
  }

  export default Cart;
