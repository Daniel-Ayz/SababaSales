// layout.js
"use client"
import React, { useState, useEffect, createContext } from 'react';
import axios from 'axios';

axios.defaults.withCredentials = true;

const CategoryContext = createContext();
const UserContext = createContext();
const StoreProductsContext = createContext();
const searchContext = createContext();

const Layout = ({ children }) => {
  const [storesProducts, setStoresProducts] = useState({});
  const [user, setUser] = useState({
    loggedIn: undefined, // Set to undefined initially
    userName: null,
    id: null,
    cart_id: null,
  });
  const [categories, setCategories] = useState(null);
  const [search, setSearch] = useState(null);

  useEffect(() => {
    axios.get(`${process.env.NEXT_PUBLIC_USERS_ROUTE}`, {
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
          <searchContext.Provider value={{ search, setSearch }}>
        {children}
        </searchContext.Provider>
      </CategoryContext.Provider>
      </StoreProductsContext.Provider>
    </UserContext.Provider>
  );
};

export default Layout;
export { UserContext}
export { StoreProductsContext}
export { CategoryContext}
export { searchContext}
