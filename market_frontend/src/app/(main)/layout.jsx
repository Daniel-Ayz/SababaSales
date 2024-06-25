// layout.js
"use client"
import React, { useState, useEffect, createContext } from 'react';
import axios from 'axios';

axios.defaults.withCredentials = true;

const CategoryContext = createContext();
const UserContext = createContext();
const StoreProductsContext = createContext();

const Layout = ({ children }) => {
  const [storesProducts, setStoresProducts] = useState({});
  const [user, setUser] = useState({
    loggedIn: undefined, // Set to undefined initially
    userName: null,
    id: null,
    cart_id: null,
  });
  const [categories, setCategories] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/users/', {
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true
    })
      .then(response => {
        const userData = response.data;
        setUser({
          loggedIn: true,
          userName: userData.username,
          id: userData.id,
          cart_id: userData.cart_id,
        });
      })
      .catch(error => {
        setUser({
          loggedIn: false,
          userName: null,
          id: null,
          cart_id: null,
        });
        console.log('No logged in user');
      });
  }, []);


  return (
    <UserContext.Provider value={{ user, setUser }}>
      <StoreProductsContext.Provider value={{ storesProducts, setStoresProducts }}>
        <CategoryContext.Provider value={{ categories, setCategories }}>
          {children}
        </CategoryContext.Provider>
      </StoreProductsContext.Provider>
    </UserContext.Provider>
  );
};

export default Layout;
export { UserContext, StoreProductsContext, CategoryContext };
