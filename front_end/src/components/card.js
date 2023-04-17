import React,{useRef, useEffect, useState} from "react";
import Display from "./display";
import { v4 as uuidv4 } from "uuid";
import { useSpeechSynthesis } from 'react-speech-kit';

export default function Card({ history }) {
  const [spk, setspk] = useState(false)
  const [fmsg, setfmsg] = useState(history[history.length-1].message) 
  const [counter, setcounter] = useState(1)
  const {speak} = useSpeechSynthesis();

  useEffect(()=>{
    if(!history[history.length-1].isUser){
    setfmsg(history[history.length-1].message)
    setspk(!history[history.length-1].isUser)
    setcounter(1)
    }
  },[history])

  useEffect(()=>{
    if(spk && counter > 0){
      speak({text:fmsg.replace(" (y/n)", "")})
      setcounter(0)
    }
  })

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
