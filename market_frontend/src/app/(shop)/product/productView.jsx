import '@/app/(shop)/product/productViewDesign.css'
import '@/app/(shop)/homepage.css'
export default function ProductView({productHref, imgSource, imgDesc, prodName, prodPrice, prodStore}) {
  return (
    <a className="rectangle" href='#'>
        <img className="productImage" src="https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg" imgDesc={"Orange pouch"}/> 
        <h3 className = "productName">Tik katan</h3>
        <h4 className='info price'>73$</h4>
        <h4 className='info storeName'>Tikim</h4>
        <div className='footer'></div>
    </a>
  );
}
