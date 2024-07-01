import './productViewDesign.css'
import '../homepage/homepage.css'
import React, {useState, useRef} from "react";
import { FaArrowRightLong , FaArrowLeftLong} from "react-icons/fa6";
import ProductView from './productView'
import { StoreProductsContext,CategoryContext,searchContext } from "../../layout";
import { useContext } from "react";

const ITEM_WIDTH = 600;
export default function ProductScroll() {
    const [scrollPosition, setScrollPosition] = useState(0);
    const containerRef = useRef();
    const {storesProducts, setStoresProducts} = useContext(StoreProductsContext);


    var products = [];
    for (var key in storesProducts) {
        products = products.concat(storesProducts[key]);
    }

    var RECOMMENDED = [];
    for (var i = 0; i < 10; i++) {
        RECOMMENDED.push(products[i]);
    }
    //function to handle scrolling when the button is clicked
    const handleScroll = (scrollAmount) => {
        //calculate the new scroll position
        const newScrollPos = scrollPosition+ scrollAmount;
        //update the state with the new scroll position
        setScrollPosition(newScrollPos);
        //access the containter element and set its scrollLeft property
        containerRef.current.scrollLeft = newScrollPos;
    };

    return <div>
                <div className='container'>
                    <div ref={containerRef} style={{
                        width: "100vw",
                        overflowX: "scroll",
                        scrollBehavior: "smooth",
                        marginLeft: "auto",
                        marginRight:"auto",
                    }}>
                        {RECOMMENDED.length > 0 && RECOMMENDED.length !== undefined && (
                            <div className="content-box">
                                {RECOMMENDED.map((item) => (
                                item && item.store && (
                                    <div className='card' key={item.id}>
                                    <ProductView prod={item} store_id={item.store.id} storename={item.store.name} />
                                    </div>
                                )
                                ))}
                            </div>
                            )}
                    </div>
                </div>
                <div className="action-btns">
                        <button onClick={()=>{handleScroll(-ITEM_WIDTH)}}><FaArrowLeftLong /></button>
                        <button onClick={()=>{handleScroll(ITEM_WIDTH)}}><FaArrowRightLong /></button>
                </div>
        </div>
}
