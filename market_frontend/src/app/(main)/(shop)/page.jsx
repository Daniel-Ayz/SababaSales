"use client"
import React from 'react';
import './homepage/homepage.css'
import ProdGrid from './homepage/prodGrid'
import ShopGrid from './homepage/shopGrid';
import ProductScroll from './product/productScroll';
export default function Home() {
  return (
    <main className=" main flex-1 overflow-y-auto">
      <h2 className='shopBy'>Shop By Product</h2>
        <ProdGrid/>
        <div className='seperate'></div>
        <h2 className='shopBy'>Shop By Store</h2>
        <ShopGrid/>
        <div className='seperate'></div>
        <h2 className='shopBy'>Recommended</h2>
        <ProductScroll />
    </main>
  );
}
