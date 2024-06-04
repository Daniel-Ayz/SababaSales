
import './homepage.css'
export default function ItemSquare({name, imgSource, imgDesc}) {
  return (

    <div className="square">
        <h5 className="topic">{name}</h5>
        <div className="itemGrid">
            <div class="grid-item"><a href="/productSearch"><img className="itemImg" src= {imgSource[0]} alt={imgDesc[0]} /></a></div>
            <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[1]} alt={imgDesc[1]} /></a></div>
            <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[2]} alt={imgDesc[2]} /></a></div>
            <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[3]} alt={imgDesc[3]} /></a></div>
            <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[4]} alt={imgDesc[4]} /></a></div>
            <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[5]} alt={imgDesc[5]} /></a></div>
            <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[6]} alt={imgDesc[6]} /></a></div>
            <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[7]} alt={imgDesc[7]} /></a></div>
            <div class="grid-item"><a href="#"><img className="itemImg" src= {imgSource[8]} alt={imgDesc[8]} /></a></div>
        </div>
        <a className="seeMore" href="#">see more &gt;</a>
    </div>
  );
}
