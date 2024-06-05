import './priceRange.css'
//import Slider from 'react-slider';
import {useState} from 'react';
const MIN = 100;
const MAX = 12000;
export default function PriceRange(){
    const [values,setValues] = useState([MIN, MAX])
    console.log('values: ', values)
    return(
        <div className="app">
            <div className="box">
                <h3><span>Price Range</span></h3>
                <div className={"values"}>
                    ${values[0]} - ${values[1]}
                </div>
                <small>
                    Current Range: ${values[1]-values[0]}
                </small>
                {/*<Slider className ={"slider"}
                        onChange={setValues}
                        value={values}
                        min={MIN}
    max={MAX}/>*/}
                <button className='applyBtn'>Apply</button>
            </div>
        </div>
    )
}