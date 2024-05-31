"use client"
import React, { useState, useEffect ,useMemo} from 'react';
import axios from 'axios';
import { createContext } from 'react';
// import { headers } from 'next/headers';
// import UserContext from './usercontext'; // Path to your UserContext file

axios.defaults.withCredentials = true;

const UserContext = createContext();
const Layout = ({ children }) => {

  const [user, setUser] = useState({
    loggedIn: false,
    userName: null,
    id: null,
  });

  useMemo(() => {
    axios.get('http://localhost:8000/api/users/', {
    headers: {'Content-Type': 'application/json'}, withCredentials: true })
      .then(response => {
        const userData = response.data;

        // Update the user state with fetched data
        setUser({
          loggedIn: true,
          userName: userData.username, // Replace with actual field name from your API response
          id: userData.id, // Replace with actual field name from your API response
        });
        console.log(user)

      })
      .catch(error => {
        console.log('no logged in user');

        // Handle errors here if needed
      });
  }, []);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
};

export default Layout;
export { UserContext}
