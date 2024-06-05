import './productViewDesign.css'
import '../homepage/homepage.css'
import {FaStar} from 'react-icons/fa'
import {useState} from 'react'
export default function ProductStars({rating}) {
  return (
    <div className="stars">
      {[...Array(5)].map((star,index) => {
        return (
          <label>
            <FaStar className = "star" size={20}
            color={ (index < rating) ? "#ffc107" : " #e4e5e9"} 
            />
          </label>
        );
      })}
    </div>
  );
}
