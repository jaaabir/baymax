import React, {useEffect} from "react";
import { v4 as uuidv4 } from "uuid";


export default function Display({ alignment, kolor, msg }) {

  return (
    <>
      <div className={"row " + alignment} key={uuidv4()}>
        <span className={"badge " + kolor}>
          <p className="card-text">{msg.replace(" (y/n)", "")}</p>
        </span>
      </div>
    </>
  );
}
