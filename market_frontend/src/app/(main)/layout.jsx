"use client"
import React, { useState, useEffect ,useMemo} from 'react';
import axios from 'axios';
import { createContext } from 'react';
// import { headers } from 'next/headers';
// import UserContext from './usercontext'; // Path to your UserContext file

axios.defaults.withCredentials = true;

const CategoryContext = createContext();
const UserContext = createContext();
const StoreProductsContext = createContext();
const searchContext = createContext();
const Layout = ({ children }) => {
  const [storesProducts, setStoresProducts] = useState({
  });
  const [user, setUser] = useState({
    loggedIn: false,
    userName: null,
    id: null,
    cart_id: null,
  });
  const [categories, setCategories] = useState(null);
  const [search, setSearch] = useState(null);

useEffect(() => {
  axios.get('http://localhost:8000/api/users/', {
    headers: {'Content-Type': 'application/json'},
    withCredentials: true
  })
  .then(response => {
    const userData = response.data;

    // Update the user state with fetched data
    setUser({
      loggedIn: true,
      userName: userData.username,
      id: userData.id,
      cart_id: userData.cart_id,
    });
    console.log(user); // Note: This will log the old state due to closure. Consider using 'userData' instead for accurate logging.

  })
  .catch(error => {
    console.log('no logged in user');
    // Handle errors here if needed
  });
}, []); // Empty dependency array ensures this effect runs only once on mount
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
