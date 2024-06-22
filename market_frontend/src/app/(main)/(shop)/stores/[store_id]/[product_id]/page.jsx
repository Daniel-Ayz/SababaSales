"use client"
import axios from "axios"
import Alert from '@mui/material/Alert';
import React from 'react';
import '../../../product/productViewDesign.css'
import '../../../homepage/homepage.css'
import './buyingPage.css'
import ProductStars from "../../../product/productStars";
// import product from '../product/productData'
import ProductScroll from '../../../product/productScroll';
import { ShoppingCartIcon } from '@heroicons/react/24/outline';


// import { headers } from "next/headers";
axios.defaults.withCredentials = true;
import { useState } from "react";
// import { UserContext } from "../layout";
// import { useContext } from "react";
import {useRouter } from 'next/navigation';
//replace product values with actual product
export default function ProductBuyingPage({prod}) {
  const [count, setCount] = useState(0);

  const router = useRouter()
  return (
    // <UserContext.Provider value={{ user, setUser }}>
    <div className="flex flex-col h-screen">
      {/* Navigation Bar */}
      {/*<NavBar setCart = {setCart} />*/}

      {/* Main Content */}
      <main className="main flex-1 overflow-y-auto bg-gray-100">
        <div className='productCont'>
            <img className="prodImage" src="" imgDesc=""/>
            <h3 className = "prodName">Name</h3>
            <ProductStars className="rating" rating={2}/>
            <div className="wrapper quantity">
              <button className="minus" onClick={()=>setCount(count-1)} disabled={count===0}>-</button>
              <button className="num">{count}</button>
              <button className="plus" onClick={()=> setCount(count+1)}>+</button>
            </div>
            <button className=" wrapper addToCart">
              <ShoppingCartIcon className="cartIcon"/>Add To Cart
            </button>
            <h4 className='info prodPrice'>10$</h4>
            <a href ="#" className='info prodStoreName'>store name</a>
            <p className="prodInfo">Product info: <br></br>{/*info*/}</p>
            <div className='footer'></div>
        </div>
        <div className='seperate'></div>
        <h2 className='shopBy'>Recommended</h2>
        <ProductScroll />

      </main>

      {/* Footer (if needed) */}
      {/* <footer className="bg-gray-800 text-white text-center py-4"> */}
        {/* {/* Your footer content here */}
      {/* </footer>  */}
    </div>
    // </UserContext.Provider>
  );
}
