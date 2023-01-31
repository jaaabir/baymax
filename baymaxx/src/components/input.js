import React, { useState, useEffect, useCallback, useRef } from "react";
import Alert from "./alert";
import Choices from "./choices";

function Input({
  btnClicked,
  onInputSubmit,
  userId,
  counter,
  handleCounter,
  handleHistory,
  handleIsChoice,
  isChoice,
}) {
  const [userInp, userInpState] = useState("");
  const [failRes, setFailRes] = useState(false);

  function updateInput(event) {
    userInpState(event.target.value);
  }

  async function postdata() {
    const url = "http://localhost:6969/api/getsymps";
    const body = {
      userId: userId,
      message: userInp,
      isUser: true,
      type: {
        yesNo: false,
        selected: null,
      },
      msgTime: Date(),
      endConvo: false,
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
      setFailRes(true);
    } else {
      const botData = await response.json();
      handleHistory(botData.body);
    }
  }

  function sendToBackend() {
    handleHistory(userInp);
    if (counter <= 2) {
      handleCounter();
    } else {
      console.log("posting the data");
      postdata();
    }
    userInpState("");
    inpRef.current.focus();
  }

  useEffect(() => {
    if (btnClicked) {
      sendToBackend();
      onInputSubmit();
    }
  }, [userInp, btnClicked]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setFailRes(false);
    }, 1000);

    return () => clearTimeout(timeout);
  }, [failRes]);

  const handleKeyEvent = useCallback((e) => {
    if (e.key === "Enter") {
      sendToBackend();
    }
  });

  const inpRef = useRef(null);
  const [userChoice, setUserChoice] = useState("");

  function handleUserChoice(value) {
    setUserChoice(value);
    userInpState(value);
  }

  useEffect(() => {
    if (isChoice) {
      sendToBackend();
      handleIsChoice(false);
    }
  }, [userChoice, userInp]);

  // useEffect(() =>{
  //   console.log('from userInp effect : ' + userInp)
  // }, [userInp])

  const showInpStyle = {
    display: isChoice ? "none" : "inline",
  };

  return (
    <>
      {failRes ? <Alert type="danger" msg="didnt send the message" /> : <></>}
      <div className="col-md-10">
        {isChoice ? <Choices handleUserChoice={handleUserChoice} /> : <></>}
        <input
          type="text"
          className="form-control w-100"
          id="user_ip"
          placeholder="Hi, how can i help you today ?"
          onChange={updateInput}
          value={userInp}
          autoComplete="off"
          onKeyDown={handleKeyEvent}
          ref={inpRef}
          style={showInpStyle}
        />
      </div>
    </>
  );
}

export default Input;
