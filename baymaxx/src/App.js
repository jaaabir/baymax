import React, { useState, useEffect } from "react";
import Form from "./components/form";
import Card from "./components/card";
import { v4 as uuidv4 } from "uuid";

function App() {
  const [history, setHistory] = useState([
    {
      message: "Hi, my name is baymaxx",
      isUser: false,
      type: {
        yesNo: false,
        selected: null,
      },
      msgTime: Date(),
      endConvo: false,
    },
    {
      message: "What is your name ? ",
      isUser: false,
      type: {
        yesNo: false,
        selected: null,
      },
      msgTime: Date(),
      endConvo: false,
    },
  ]);
  const [userId, setUserId] = useState(uuidv4());
  const [basicQues, setBasicQues] = useState([
    {
      message: "What is your age ?",
      isUser: false,
      type: {
        yesNo: false,
        selected: null,
      },
      msgTime: Date(),
      endConvo: false,
    },
    {
      message: "Do you smoke or drink ?",
      isUser: false,
      type: {
        yesNo: true,
        selected: null,
      },
      msgTime: Date(),
      endConvo: false,
    },
    {
      message: "What are your currently experincing symptoms ?",
      isUser: false,
      type: {
        yesNo: false,
        selected: null,
      },
      msgTime: Date(),
      endConvo: false,
    },
  ]);
  const [counter, setCounter] = useState(0);

  function handleCounter() {
    setCounter(counter + 1);
  }

  function handleHistory(Data) {
    if (Data) {
      setHistory((prevHistory) => {
        if (typeof Data === "object") {
          return [...prevHistory, Data];
        } else {
          const usrData = {
            message: Data,
            isUser: true,
            type: {
              yesNo: false,
              selected: null,
            },
            msgTime: Date(),
            endConvo: false,
          };

          return [...prevHistory, usrData];
        }
      });
    }
  }

  useEffect(() => {
    // console.log(counter);
    if (counter - 1 <= 2) {
      handleHistory(basicQues[counter - 1]);
    }
  }, [counter]);

  const [isChoice, setIsChoice] = useState(false);

  function handleIsChoice(val) {
    setIsChoice(val);
  }

  async function saveHistory() {
    const url = "http://localhost:6969/api/savechat";
    const body = {
      userId: userId,
      history: history,
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
      const diseases = await response.json();
      console.log(diseases);
      handleHistory(diseases.body);
    }
  }

  useEffect(() => {
    // console.log(history);
    const lastMsg = history[history.length - 1];
    const yn = lastMsg.type.yesNo;
    if (yn) {
      handleIsChoice(yn);
    }

    const endConvo = lastMsg.endConvo;
    if (endConvo) {
      console.log("ok now the convo ended ...");
      saveHistory();
    }
  }, [history]);

  useEffect(() => {
    console.log("user ID : " + userId);
  }, []);

  return (
    <>
      <div className="container">
        <Card history={history} />
        <Form
          userId={userId}
          counter={counter}
          handleCounter={handleCounter}
          handleHistory={handleHistory}
          handleIsChoice={handleIsChoice}
          isChoice={isChoice}
        />
      </div>
    </>
  );
}

export default App;
