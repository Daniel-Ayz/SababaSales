
"use client";

import './homepage.css'
import ItemSquare from './itemSquare';
import axios from 'axios';
import React from 'react';
import {StoreProductsContext} from '../../layout';
import { useEffect, useState } from 'react';
import { useContext } from 'react';
import { UserContext } from '../../layout'; // Import the UserContext

export default function ShopGrid() {
// const [storesProducts, setStoresProducts] = useState({});
const [stores, setStores] = useState([]);
const [error, setError] = useState(null);
const {storesProducts, setStoresProducts}= useContext(StoreProductsContext);

  useEffect(() => {
    const fetchStores = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/stores', {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true
        });

        const stores = response.data;
        setStores(stores);
        const storesProducts = {};

        const fetchProducts = stores.map(async (store) => {
          try {
            const storeResponse = await axios.get(`http://localhost:8000/api/stores/${store.id}/products`, {
              headers: { 'Content-Type': 'application/json' },
              withCredentials: true
            });
            for (let i = 0; i < storeResponse.data.length; i++) {
              storeResponse.data[i]['image'] =  "https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg";

            }
            storesProducts[store.id] = storeResponse.data;

          } catch (error) {
            console.error(`Error fetching products for store ${store.id}:`, error);
            setError(error.message); // Set error if fetching products fails
          }
        });

        await Promise.all(fetchProducts);

        setStoresProducts(storesProducts);
        // setProducts({stores:["store1", "store2", "store3"]});


        // console.log('Stores:', stores);
        // console.log('Stores products:', storesProducts)
      } catch (error) {
        console.error('Error fetching stores:', error);
        setError(error.message); // Set error if fetching stores fails
      }
    };

    fetchStores();
  }, []);


  return (
 <div>
  {error && <p>Error: {error}</p>}
  {stores.length > 0 ? (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {stores.map((store) => (
        <ItemSquare
          key={store.id}
          store={store} // Pass the entire store object
          products={storesProducts[store.id] || []} // Pass the products of the store
        />
      ))}
    </div>
  ) : (
    <p>No products available</p>
  )}
</div>

  //   <div className="itemGrid">
  //      {stores.map((store) => (


  //                             ))}
  //       <ItemSquare className="gridItem" name={"Fashion"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg"]} imgDesc={["Orange pouch"]}/>
  //       <ItemSquare className="gridItem" name={"Home design"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]} imgDesc={["blue bag"]}/>
  //       <ItemSquare className="gridItem" name={"Gaming"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]}  imgDesc={["blue bag"]}/>
  //       <ItemSquare className="gridItem" name={"Sports"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]}  imgDesc={["blue bag"]}/>
  //       <ItemSquare className="gridItem" name={"Electronics"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]}  imgDesc={["blue bag"]}/>
  //       <ItemSquare className="gridItem" name={"Books"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]}  imgDesc={["blue bag"]}/>
  //   </div>
  );
}
