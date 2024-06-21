
"use client";
import Link from 'next/link';
import react from 'react';
import './homepage.css'
const ItemSquare = ({ store, products }) => {
  // Mock data for testing
  const mockStore = {
    id: 1,
    name: 'Mock Store'
  };

  const mockProducts = [
    {
      image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg',
      description: 'Orange pouch'
    },
    {
      image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg',
      description: 'Blue bag'
    },
    {
      image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-03-product-01.jpg',
      description: 'Green hat'
    },
    {
      image: 'https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-04-product-01.jpg',
      description: 'Red shoes'
    }
  ];

  // Use mock data for testing
  products = products.length > 0 ? products : mockProducts;
  store = store ? store : mockStore;
  return (
    <div className="square">
      <h5 className="topic">{store.name}</h5> {/* Assuming the store object has a 'name' field */}
      <div className="itemGrid">
        {products.length > 0 ? (
          products.map((product, index) => (
            <div className="grid-item" key={index}>
              <a href="/productSearch">
                <img className="itemImg" src={product.image} alt={product.description} /> {/* Assuming each product object has 'image' and 'description' fields */}
              </a>
            </div>
          ))
        ) : (
          <p>No products available</p>
        )}
      </div>
          <Link className="inline-block bg-blue-700 hover:bg-blue-900 text-white py-2 px-4 rounded-md transition duration-300 ease-in-out block w-full text-center" href={`/productSearch/${store.id}`}>
            Continue shopping at {store.name}
          </Link>
    </div>
  );
};
export default ItemSquare;
// export default function ItemSquare({name, imgSource, imgDesc}) {
//   return (

//     <div className="square">
//         <h5 className="topic">{name}</h5>
//         <div className="itemGrid">
//             <div class="grid-item"><a href="/productSearch"><img className="itemImg" src= {imgSource[0]} alt={imgDesc[0]} /></a></div>
//             <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[1]} alt={imgDesc[1]} /></a></div>
//             <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[2]} alt={imgDesc[2]} /></a></div>
//             <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[3]} alt={imgDesc[3]} /></a></div>
//             <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[4]} alt={imgDesc[4]} /></a></div>
//             <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[5]} alt={imgDesc[5]} /></a></div>
//             <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[6]} alt={imgDesc[6]} /></a></div>
//             <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[7]} alt={imgDesc[7]} /></a></div>
//             <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[8]} alt={imgDesc[8]} /></a></div>
//         </div>
//         <a className="seeMore" href="#">see more &gt;</a>
//     </div>
//   );
// }
