"use client"
import axios from "axios"
import Alert from '@mui/material/Alert';
import React from 'react';
import Footer from '../(shop)/footer'; // Assuming Example component is in a separate file
import Cart from '../(shop)/cart'; // Assuming Example component is in a separate file
import Nav from '../(shop)/navbar/nav';
import '../(shop)/product/productViewDesign.css'
import '../(shop)/homepage.css'
import './productSearch.css'
import ProductScroll from '../(shop)/product/productScroll';
import { RESULTS } from './searchResults'; 
import PriceRange from './priceRange';
import StoresScroll from './storesScroll';
// import { headers } from "next/headers";
axios.defaults.withCredentials = true;
import { useState } from "react";
import { UserContext } from "../layout";
import { useContext } from "react";
import {useRouter } from 'next/navigation';
import ProductView from "../(shop)/product/productView";
export default function ProductBuyingPage({prod}) {
  const [showAlert, setShowAlert] = useState(false)
  const [count, setCount] = useState(0);
  const {user,setUser} = useContext(UserContext);
  const [currentPage, setCurrentPage] = useState(1)
  const recordsPerPage = 9;
  const lastIndex = currentPage * recordsPerPage;
  const firstIndex = lastIndex - recordsPerPage;
  const records = RESULTS.slice(firstIndex,lastIndex);
  const npage = Math.ceil(RESULTS.length / recordsPerPage);
  const numbers = [...Array(npage+1).keys()].slice(1)
  const router = useRouter()
  const [cart, setCart] = React.useState(false);
  return (
    // <UserContext.Provider value={{ user, setUser }}>
    <div className="flex flex-col h-screen">
      {/* Navigation Bar */}
      {/*<NavBar setCart = {setCart} />*/}
      <Nav setCart={setCart}/>
      <Cart isOpen={cart} setCart = {setCart}/>

      {/* Main Content */}
      <main className="main flex-1 overflow-y-auto bg-gray-100">
        <PriceRange />
        <div className='productCont'>
            {records.map((item,i)=> (
                                <div key={i} className='card'><ProductView prod={item}/></div>
                            ))
                            }
        </div>
        <nav>
          <ul className="pagination">
            <li className="page-item">
              <a href="#" className=" page-link" onClick={prePage}>Prev</a>
            </li>
            {
              numbers.map((n,i) => {
                <li className={'page-item'} key={i}>
                  <a href="#" className="page-link" onClick={()=>changeCPage(n)}>
                    hey {n}
                  </a>
                </li>
              })
            }
            <li className="page-item">
              <a href="#" className=" page-link" onClick={nextPage}>Next</a>
            </li>
          </ul>
        </nav>
        <div className='seperate'></div>
        <h2 className='shopBy'>Recommended Stores</h2>
        <StoresScroll className="storeScroll"/>
        <div className='seperate'></div>
        <h2 className='shopBy'>Recommended Products</h2>
        <ProductScroll />

      </main>

      {/* Footer (if needed) */}
      {/* <footer className="bg-gray-800 text-white text-center py-4"> */}
        {/* {/* Your footer content here */}
      {/* </footer>  */}
      <Footer />
    </div>
    // </UserContext.Provider>
  );

  function prePage(){
    if(currentPage !== 1){
      setCurrentPage(currentPage-1)
    }
  }
  function changeCPage(id){
    setCurrentPage(id)
  }
  function nextPage(){
    if(currentPage !== npage){
      setCurrentPage(currentPage+1)
    }
  }
}
