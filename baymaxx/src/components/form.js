import React, { useState } from "react";
import Input from "./input";

function Form({
  userId,
  counter,
  handleCounter,
  handleHistory,
  handleIsChoice,
  isChoice,
}) {
  const [btnClicked, btnClickedState] = useState(false);

  function submitInput() {
    btnClickedState(true);
  }

  function handleBtnChange() {
    btnClickedState(false);
  }

  return (
    <>
      <div className="card text-center">
        <div className="card-header row">
          <Input
            btnClicked={btnClicked}
            onInputSubmit={handleBtnChange}
            counter={counter}
            handleCounter={handleCounter}
            userId={userId}
            handleHistory={handleHistory}
            handleIsChoice={handleIsChoice}
            isChoice={isChoice}
          />
          {isChoice ? (
            <></>
          ) : (
            <button
              type="button"
              className="btn btn-secondary col-md-1"
              onClick={submitInput}
            >
              <span className="material-icons">arrow_forward_ios</span>
            </button>
          )}
        </div>
      </div>
    </>
  );
}

export default Form;
