"use client"
import axios from "axios"
import Alert from '@mui/material/Alert';
import React from 'react';
import '../product/productViewDesign.css'
import '../homepage/homepage.css'
import './productSearch.css'
axios.defaults.withCredentials = true;
import { useState } from "react";
import Prod from '../product/productView';
import { StoreProductsContext } from "../../layout";
import { useContext } from "react";
//replace RESULTS with prod
export default function ProductSearch( ){
  const [currentPage, setCurrentPage] = useState(1);
  const {storesProducts, setStoresProducts} = useContext(StoreProductsContext);
  const recordsPerPage = 9;
  var products = [];
  for (var key in storesProducts) {
    products = products.concat(storesProducts[key]);
  }
  console.log(products)


  const lastIndex = currentPage * recordsPerPage;
  const firstIndex = lastIndex - recordsPerPage;
  const currentRecords = products.slice(firstIndex, lastIndex);
  const npage = Math.ceil(products.length / recordsPerPage);
  const numbers = [...Array(npage + 1).keys()].slice(1);

  const prePage = () => {
    if (currentPage !== 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const changeCPage = (id) => {
    setCurrentPage(id);
  };

  const nextPage = () => {
    if (currentPage !== npage) {
      setCurrentPage(currentPage + 1);
    }
  };


  return (
    <div className="flex flex-col h-screen">
      <main className="main flex-1 overflow-y-auto bg-gray-100">
        {/* <h2>Store</h2> */}
        <div className="productCont">
          {currentRecords.map(product => (
            <div key={product.name} className="card">
              <Prod prod={product} store_id={product.store['id']} storename ={product.store['name']} />
            </div>
          ))}
        </div>
        <nav>
          <ul className="pagination">
            <li className="page-item">
              <a href="#" className="page-link" onClick={prePage}>Prev</a>
            </li>
            {numbers.map(n => (
              <li className="page-item" key={n}>
                <a href="#" className="page-link" onClick={() => changeCPage(n)}>
                  {n}
                </a>
              </li>
            ))}
            <li className="page-item">
              <a href="#" className="page-link" onClick={nextPage}>Next</a>
            </li>
          </ul>
        </nav>
      </main>
    </div>
  );
};
