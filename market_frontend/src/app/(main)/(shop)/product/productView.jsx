import './productViewDesign.css'
import '../homepage/homepage.css'
import ProductRating from './productRating'
import ProductStars from './productStars'
import Link from 'next/link'

// Function to generate a random star rating between 1 and 5
const ratingMap = {};

function hashString(str) {
  let hash = 0;
  if (str.length === 0) {
    return hash;
  }
  for (let i = 0; i < str.length; i++) {
    let char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return hash;
}

function getRandomRating(name) {
  // Simple hash function to convert name to a numeric value
  let hash = 0;
  if(name === null || typeof name === 'undefined' || name === '') {
    return 1;
  }
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Ensure the result is within 1 to 5
  const rating = ((hash % 5) + 5) % 5 + 1;
  return rating;
}



export default function Prod({ prod ,store_id,storename}) {
  const randomRating =  getRandomRating(prod.name);

  return (
<div className='productPreview'>
  <div className="rectangle relative">
    <Link href={`/stores/${store_id}/${prod.name}`} className='imageRef block'>
      <img className="productImage" src={prod.image_link} alt={prod.name} />
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
      <p className='info'>
        <span className="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700">{prod.category}</span>
      </p> {/* Add this line for product category */}
    </div>
  </div>
</div>



  );
}
