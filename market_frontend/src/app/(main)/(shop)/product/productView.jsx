import './productViewDesign.css'
import '../homepage/homepage.css'
import ProductRating from './productRating'
import ProductStars from './productStars'
import Link from 'next/link'

// Function to generate a random star rating between 1 and 5
function getRandomRating(id) {
  return Math.floor(Math.random() * 5) + 1;
}

// Placeholder image URL
const placeholderImage = "https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg";
;

export default function Prod({ prod ,store_id,storename}) {
  const randomRating = getRandomRating(prod.id);

  return (
<div className='productPreview'>
  <div className="rectangle relative">
    <Link href={`/stores/${store_id}/${prod.name}`} className='imageRef block'>
      <img className="productImage" src={placeholderImage} alt={prod.name} />
    </Link>
    <div className="mt-auto">
      <Link className="nameRef" href={`/stores/${store_id}/${prod.name}`}>
        <h3 className="productName">{prod.name}</h3>
      </Link>
      <div className="flex items-center">
        <ProductStars className="rating" rating={randomRating} />
        <h4 className='info price ml-auto'>${prod.initial_price}</h4>
      </div>
      <Link href={`/stores/${store_id}`} className='storeLink text-gray-600 hover:text-blue-500'>
        <h3 className='info storeName'>{storename}</h3>
      </Link>
    </div>
  </div>
</div>


  );
}
