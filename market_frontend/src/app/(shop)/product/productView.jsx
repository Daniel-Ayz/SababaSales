import '@/app/(shop)/product/productViewDesign.css'
import '@/app/(shop)/homepage.css'
import ProductRating from './productRating'
import ProductStars from './productStars'
import product from './productData'
export default function ProductView({prod}) {
  return (
    <div className='productPreview'>
        <div className="rectangle">
          <a href={prod.productHref} className='imageRef'><img className="productImage" src={prod.imgSource} imgDesc={prod.imgDesc}/> </a>
          <a className="nameRef" href={prod.productHref}><h3 className = "productName">{prod.prodName}</h3></a>
          <ProductStars className="rating" rating={prod.prodRat}/>
          <h4 className='info price'>{prod.prodPrice}</h4>
          <a href ={prod.storHref} className='info storeName'>{prod.prodStore}</a>
          <div className='footer'></div>
        </div> 

    </div>
  );
}
