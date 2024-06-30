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
import { StoreProductsContext,CategoryContext,searchContext } from "../../layout";
import { useContext } from "react";
import Fuse from 'fuse.js';
// import * as React from 'react';
import Box from '@mui/material/Box';
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';

  const movingShineAnimation = `
    @keyframes movingShine {
      0% {
        background-position: 200% center;
      }
      100% {
        background-position: -200% center;
      }
    }
  `;
//replace RESULTS with prod
export default function ProductSearch( ){
  const [currentPage, setCurrentPage] = useState(1);
  const {storesProducts, setStoresProducts} = useContext(StoreProductsContext);
  const {search, setSearch} = useContext(searchContext);
  const {categories, setCategories} = useContext(CategoryContext);
  const handleChange = (_, newValue) => {
    setVal(newValue);
  };


  const recordsPerPage = 9;
  var max_price = 0;
  var products = [];
  for (var key in storesProducts) {
    products = products.concat(storesProducts[key]);

  }
  for (var i = 0; i < products.length; i++) {
    if (products[i].initial_price > max_price) {
      max_price = products[i].initial_price;
    }
  }

const MIN = 0;
const [val, setVal] = React.useState(max_price);
const MAX = max_price;
const marks = [
  {
    value: MIN,
    label: '',
  },
  {
    value: MAX,
    label: '',
  },
];


  // filter out products
  const fuse = new Fuse(products, {
    keys: ['name'],
    threshold: 0.3, // Adjust the threshold according to your needs
  });
  if (search !== null && search !== "") {
    products = fuse.search(search).map((result) => result.item);
  }
  // filter out categories
  console.log(categories)

  // products.map((product) => { console.log(product.category) });
  console.log(products)
MIN
  console.log(products)
  // filter initial_price:
  products = products.filter((product) => product.initial_price <= val);



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
        <div className="text-center mt-8">
          <h1 className="text-3xl font-bold text-gray-800 animate__animated animate__fadeIn animate__delay-1s animate__heartBeat">
            Browse Products
          </h1>
          <div className="mt-4 animate-bounce">
            <svg className="animate-bounce w-6 h-6 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
            </svg>
          </div>

          <div className="flex justify-center mt-8">
            <Box sx={{ width: 350 }}>
              <Slider
                marks={marks}
                step={1}
                value={val}
                valueLabelDisplay="auto"
                min={MIN}
                max={MAX}
                onChange={handleChange}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography
                  variant="body2"
                  onClick={() => setVal(MIN)}
                  sx={{ cursor: 'pointer' }}
                >
                  ${MIN}
                </Typography>
                <Typography
                  variant="body2"
                  onClick={() => setVal(MAX)}
                  sx={{ cursor: 'pointer' }}
                >
                  ${MAX}
                </Typography>
              </Box>
            </Box>
          </div>
        </div>

        <div className="productCont">
          {currentRecords.map(product => (
            <div key={product.name} className="card">
              <Prod prod={product} store_id={product.store['id']} storename={product.store['name']} />
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
