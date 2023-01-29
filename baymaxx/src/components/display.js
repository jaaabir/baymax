import React from "react";

export default function Display({ alignment, kolor, msg }) {
  return (
    <>
      <div className={"message " + alignment}>
        <span className={"badge " + kolor}>
          <p className="card-text">{msg}</p>
        </span>
      </div>
    </>
  );
}
