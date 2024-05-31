"use client"
import React from 'react';
import NavBar from './navbar'; // Assuming Example component is in a separate file
import Footer from './footer'; // Assuming Example component is in a separate file
import Cart from './cart'; // Assuming Example component is in a separate file


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
      <NavBar setCart = {setCart} />
      <Cart isOpen={cart} setCart = {setCart}/>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-gray-100">
        {children}
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
