import React from "react";
import Display from "./display";
import { v4 as uuidv4 } from "uuid";

export default function Card({ history }) {
  const textHistory = history.map((element) => {
    return (
      <div className="row" key={uuidv4()}>
        <Display
          alignment={element.isUser ? "text-end" : "text-start"}
          kolor={element.isUser ? "bg-secondary" : "bg-primary"}
          msg={element.message}
        />
      </div>
    );
  });

  return (
    <>
      <div className="card" id="card">
        <div className="card-header text-center">Baymaxx</div>
        <div className="card-body">{textHistory}</div>
      </div>
    </>
  );
}
