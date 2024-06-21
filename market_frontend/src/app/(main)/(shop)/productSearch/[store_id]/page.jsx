"use client"
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ProductView from '../../product/productView';

const StorePage = ({params}) => {
  const storeid = params.store_id;
  const [products, setProducts] = useState(null);
  const [loading, setLoading] = useState(true);

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

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Store </h2>
      <div className="productCont">
        {products.map(product => (
          <div key={product.id} className="card">
            <ProductView prod={product} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default StorePage;
