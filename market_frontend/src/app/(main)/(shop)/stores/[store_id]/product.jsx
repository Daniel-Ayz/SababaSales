import '../../product/productViewDesign.css'
import '../../homepage/homepage.css'
import ProductRating from '../../product/productRating'
import ProductStars from '../../product/productStars'
import Link from 'next/link'

// Function to generate a random star rating between 1 and 5
function getRandomRating(id) {
  return Math.floor(Math.random() * 5) + 1;
}

// Placeholder image URL
const placeholderImage = "https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg";
;

export default function ProductView({ prod ,store_id}) {
  const randomRating = getRandomRating(prod.id);

  return (
    <div className='productPreview'>
      <div className="rectangle">

        <a href={`/stores/${store_id}/${prod.name}`} className='imageRef'>
          <img className="productImage" src={placeholderImage} alt={prod.name} />
        </a>
        <a className="nameRef" href={`/stores/${store_id}/${prod.name}`}>
          <h3 className="productName">{prod.name}</h3>
        </a>
        <ProductStars className="rating" rating={randomRating} />
        <h4 className='info price'>${prod.initial_price}</h4>
        {/* <a href={`/store/${prod.store.id}`} className='info storeName'> */}
          {/* {prod.store.name} */}
        {/* </a> */}
        <div className='footer'></div>
      </div>
    </div>
  );
}
