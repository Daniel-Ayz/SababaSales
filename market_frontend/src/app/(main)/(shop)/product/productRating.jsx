import './productViewDesign.css'
import '../homepage.css'
import {FaStar} from 'react-icons/fa'
import {useState} from 'react'
export default function ProductRating() {
  const [rating,setRating] = useState(null);
  const [hover,setHover] = useState(null); 
  return (
    <div className="stars">
      {[...Array(5)].map((star,index) => {
        const currentRating = index +1;
        return (
          <label>
            <input type="radio" name="rating" value={currentRating} onClick={() => setRating(currentRating)}/>
            <FaStar className = "chooseStar star" size={50}
            color={currentRating <= (hover || rating) ? "#ffc107" : " #e4e5e9"} 
            onMouseEnter={()=> setHover(currentRating)}
            onMouseLeave = {()=> setHover(null)}
            />
          </label>
        );
      })}
    </div>
  );
}
