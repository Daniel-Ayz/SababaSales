"use client"
import React from 'react';
import NavBar from './navbar'; // Assuming Example component is in a separate file
import Footer from './footer'; // Assuming Example component is in a separate file
import Cart from './cart'; // Assuming Example component is in a separate file
import ShopGrid from './shopGrid';
import ProdGrid from './prodGrid';
import ProductView from './product/productView';
import ProductStars from './product/productStars';
import ProductScroll from './product/productScroll';

const product = require('./product/productData');

const UserContext = React.createContext({
  loggedIn: false,
  userName: null,
  id: null,
});

const Layout = ({ children }) => {
  const [user, setUser] = React.useState({
    loggedIn: false,
    userName: null,
    id: null,
  });
  const [cart, setCart] = React.useState(true);
  return (
    <UserContext.Provider value={{ user, setUser }}>
    <div className="flex flex-col h-screen">
      {/* Navigation Bar */}
      <NavBar setCart = {setCart} />
      <Cart isOpen={cart} setCart = {setCart}/>

      {/* Main Content */}
      <main className="main">
        <h2 className="shopBy">Shop By Store</h2>
        <ShopGrid />
        <hr className="seperate"/>
        <h2 className="shopBy">Shop By Product</h2>
        <ProdGrid />
        <hr className="seperate"/>
        <h2 className="shopBy recommended">Recommended</h2>
        <ProductScroll />
        {/*{children}*/}
      </main>
      
      {/* Footer (if needed) */}
      {/* <footer className="bg-gray-800 text-white text-center py-4"> */}
        {/* {/* Your footer content here */}
      {/* </footer>  */}
      <Footer />
    </div>
    </UserContext.Provider>
  );
};

export default Layout;
export { UserContext };
