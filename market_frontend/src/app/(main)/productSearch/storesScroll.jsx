import '../(shop)/product/productViewDesign.css'
import '../(shop)/homepage.css'
import './productSearch.css'
import React, {useState, useRef} from "react";
import { STORES } from './stores'; 
import { FaArrowRightLong , FaArrowLeftLong} from "react-icons/fa6";
const ITEM_WIDTH = 600;
export default function StoresScroll() {
    const [scrollPosition, setScrollPosition] = useState(0);
    const containerRef = useRef();
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
                        width: "94vw",
                        overflowX: "scroll",
                        scrollBehavior: "smooth",
                        marginLeft: "3vw",
                        marginRight:"auto",
                    }}>
                        <div className = "content-box">
                            {STORES.map((item)=> (
                                <a href={item.storeHref} className='card'><img className="storeLogo" src={item.imgSource} alt={item.imgDesc} /></a>
                            ))
                            }
                        </div>
                    </div>
                </div>
                <div className="action-btns">
                        <button onClick={()=>{handleScroll(-ITEM_WIDTH)}}><FaArrowLeftLong /></button>
                        <button onClick={()=>{handleScroll(ITEM_WIDTH)}}><FaArrowRightLong /></button>
                </div>
        </div>
}
