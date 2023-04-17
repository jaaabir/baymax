import React, { useEffect, useState, useRef, useCallback } from 'react'
import Modal from 'react-modal';
import Choices from './choices';
import Form from './form';

export default function Feedback(props) {
  const [feedback, setfeedback] = useState('')
  const [valid, setvalid] = useState('')

  useEffect(()=>{
    Modal.setAppElement('body');
  },[])

  const [userChoice, setUserChoice] = useState("");

  const handleKeyEvent = useCallback((e) => {
    if (e.key === "Enter") {
      updateFeedback()
    }
  });

  function handleUserChoice(value) {
    setUserChoice(value);
  }

  function updateInput(event) {
    setfeedback(event.target.value);
  }

  async function updateFeedback(){
    if (feedback!==''){
        const url = props.flaskURL + 'api/updatechat';
        const body = {
          userId: props.userId,
          feedback: feedback
        };

        const data = {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify(body),
        };

        const response = await fetch(url, data);
        if (!response.ok) {
          console.log("didnt update the msg");
        } else {
          console.log('Successfully updated feedback')
        }
        props.onRequestClose()
    }
  }

  const inpRef = useRef(null);
  useEffect(()=>{
    if (userChoice==='yes'){
      setfeedback(props.diseases)
      updateFeedback()
      setCounter(1)
      props.onRequestClose()
    }
    else if(userChoice==='no'){
      if (inpRef.current){
      inpRef.current.focus();
      }
      setCounter(1)
    }
  }, [userChoice])

  const [counter, setCounter] = useState(0)
  useEffect(()=>{
    console.log(counter)
    console.log(userChoice)
  }, [counter])

    return (
      <Modal
      isOpen={props.getFeedback}
      // ariaHideApp={false}
      onRequestClose={props.onRequestClose}
      contentLabel="Feedback Modal"
      style={{
        overlay: {
          backgroundColor: 'rgba(0, 0, 0, 0.5)'
        },
        content: {
          width:'50%',
          height:'50%',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)'
        }
      }}
    >
      {props.diseases}
      <p>Are the predicted diseases valid?</p>
      {counter === 0 ? <Choices handleUserChoice={handleUserChoice} isDisabled={false}></Choices> : <></>}
      {userChoice===''?<></>:<>{userChoice==='yes'?
        <p>Thanks for the feedback</p> : <div><input type='text' className="form-control w-100" onKeyDown={handleKeyEvent} ref={inpRef} onChange={updateInput} />
        <button
        type="button"
        className="btn btn-secondary col-md-1"
        onClick={updateFeedback}
      >
        <span className="material-icons">arrow_forward_ios</span>
      </button></div>}</>}
    </Modal>
  )
}
