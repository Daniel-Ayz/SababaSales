"use client"
import React from 'react';
import NavBar from './navbar'; // Assuming Example component is in a separate file
import Footer from './footer'; // Assuming Example component is in a separate file
import Cart from './cart'; // Assuming Example component is in a separate file
import Nav from './navbar/nav';
import ShopGrid from './shopGrid';
import ProdGrid from './prodGrid';
import ProductScroll from './product/productScroll';

const Layout = ({ children }) => {
  // const [user, setUser] = React.useState({
  //   loggedIn: false,
  //   userName: null,
  //   id: null,
  // });
  const [cart, setCart] = React.useState(false);
  return (
    // <UserContext.Provider value={{ user, setUser }}>
    <div className="flex flex-col h-screen">
      {/* Navigation Bar */}
      {/*<NavBar setCart = {setCart} />*/}
      <Nav setCart={setCart}/>
      <Cart isOpen={cart} setCart = {setCart}/>

      {/* Main Content */}
      <main className="main flex-1 overflow-y-auto bg-gray-100">
        <h2 className='shopBy'>Shop By Product</h2>
        <ProdGrid/>
        <div className='seperate'></div>
        <h2 className='shopBy'>Shop By Store</h2>
        <ShopGrid/>
        <div className='seperate'></div>
        <h2 className='shopBy'>Recommended</h2>
        <ProductScroll />

      </main>

      {/* Footer (if needed) */}
      {/* <footer className="bg-gray-800 text-white text-center py-4"> */}
        {/* {/* Your footer content here */}
      {/* </footer>  */}
      <Footer />
    </div>
    // </UserContext.Provider>
  );
};

export default Layout;
// export { UserContext };
