"use client"
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ProductView from './product';
import  '../../product/productViewDesign.css';
import '../../homepage/homepage.css';
import './productSearch.css';

const StorePage = ({ params }) => {
  const storeid = params.store_id;
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const recordsPerPage = 9;

  useEffect(() => {
    const fetchStoreData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`http://localhost:8000/api/stores/${storeid}/products`);
        setProducts(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching store data:', error);
        setLoading(false);
      }
    };

    if (storeid) {
      fetchStoreData();
    }
  }, [storeid]);

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

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="flex flex-col h-screen">
      <main className="main flex-1 overflow-y-auto bg-gray-100">
        <h2>Store</h2>
        <div className="productCont">
          {currentRecords.map(product => (
            <div key={product.id} className="card">
              <ProductView prod={product} store_id={storeid} />
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

export default StorePage;
