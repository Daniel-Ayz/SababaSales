import './productViewDesign.css'
import '../homepage.css'
import ProductRating from './productRating'
import ProductStars from './productStars'
import product from './productData'
import Link from 'next/link';
export default function ProductView({prod}) {
  return (
    <div className='productPreview'>
        <div className="rectangle">
          <a href="/productBuying" className='imageRef'><img className="productImage" src={prod.imgSource} imgDesc={prod.imgDesc}/> </a>
          <a className="nameRef" href="/productBuying"><h3 className = "productName">{prod.prodName}</h3></a>
          <ProductStars className="rating" rating={prod.prodRat}/>
          <h4 className='info price'>{prod.prodPrice}</h4>
          <a href ={prod.storHref} className='info storeName'>{prod.prodStore}</a>
          <div className='footer'></div>
        </div> 
    </div>
  );
}
