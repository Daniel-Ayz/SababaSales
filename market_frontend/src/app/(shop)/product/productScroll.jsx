import '@/app/(shop)/product/productViewDesign.css'
import '@/app/(shop)/homepage.css'
import React, {useState, useRef} from "react";
import { RECOMMENDED } from './recommendedProd'; 
import { FaArrowRightLong , FaArrowLeftLong} from "react-icons/fa6";
import ProductView from './productView'
const ITEM_WIDTH = 600;
export default function ProductScroll() {
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
                        width: "100vw",
                        overflowX: "scroll",
                        scrollBehavior: "smooth",
                        marginLeft: "auto",
                        marginRight:"auto",
                    }}>
                        <div className = "content-box">
                            {RECOMMENDED.map((item)=> (
                                <div className='card'><ProductView prod={item}/></div>
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
