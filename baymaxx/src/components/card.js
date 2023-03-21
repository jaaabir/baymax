import React,{useRef, useEffect} from "react";
import Display from "./display";
import { v4 as uuidv4 } from "uuid";

export default function Card({ history }) {
  const textHistory = history.map((element) => {
    return (
      <div className="" key={uuidv4()}>
        <Display
          alignment={element.isUser ? "justify-content-end" : "justify-content-start"}
          kolor={element.isUser ? "bg-secondary" : "bg-primary"}
          msg={element.message}
        />
      </div>
    );
  });

  const pointer = useRef(null)
  useEffect(() => {
   window.scrollTo(0, pointer.current.offsetTop); 
  }, [history])

  return (
    <>
      <div className="card" id="card">
        <div className="card-header text-center">Baymaxx</div>
        <div className="card-body">
          {textHistory}
        <div ref={pointer}></div>
        </div>
      </div>
    </>
  );
}
