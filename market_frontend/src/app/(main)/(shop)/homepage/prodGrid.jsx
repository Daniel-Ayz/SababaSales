import './homepage.css'
import ItemSquare from './itemSquare';
export default function ProdGrid() {
  return (

    <div className="itemGrid">
        <ItemSquare className="gridItem" name={"Fashion"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-01.jpg"]} imgDesc={["Orange pouch"]}/>
        <ItemSquare className="gridItem" name={"Home design"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]} imgDesc={["blue bag"]}/>
        <ItemSquare className="gridItem" name={"Gaming"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]}  imgDesc={["blue bag"]}/>
        <ItemSquare className="gridItem" name={"Sports"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]}  imgDesc={["blue bag"]}/>
        <ItemSquare className="gridItem" name={"Electronics"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]}  imgDesc={["blue bag"]}/>
        <ItemSquare className="gridItem" name={"Books"} imgSource={["https://tailwindui.com/img/ecommerce-images/shopping-cart-page-04-product-02.jpg"]}  imgDesc={["blue bag"]}/>
    </div>
  );
}
