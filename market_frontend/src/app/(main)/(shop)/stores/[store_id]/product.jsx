import '../../product/productViewDesign.css'
import '../../homepage/homepage.css'
import ProductRating from '../../product/productRating'
import ProductStars from '../../product/productStars'
import Link from 'next/link'

// Function to generate a random star rating between 1 and 5
function getRandomRating(name) {
  // Simple hash function to convert name to a numeric value
  let hash = 0;
  if (name === null) {
    return 1;
  }
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }

  // Ensure the result is within 1 to 5
  const rating = ((hash % 5) + 5) % 5 + 1;
  return rating;
}

// Placeholder image URL
const placeholderImage = "https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg";
;

export default function ProductView({ prod ,store_id}) {
  const randomRating = 2//getRandomRating(prod.name);

  return (
    <div className='productPreview'>
      <div className="rectangle">

        <Link href={`/stores/${store_id}/${prod.name}`} className='imageRef'>
          <img className="productImage" src={placeholderImage} alt={prod.name} />
        </Link>
        <Link className="nameRef" href={`/stores/${store_id}/${prod.name}`}>
          <h3 className="productName">{prod.name}</h3>
        </Link>
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
