import React, { useState, useEffect } from "react";
import axios from "axios";


const ModelTraining = () => {
  const [randomNumber, setRandomNumber] = useState(null);

  const generateRandomNumber = (min, max) => {
    const random = Math.floor(Math.random() * (max - min + 1)) + min;
    setRandomNumber(random);
  };

  return (
    <div>
      <h1>Random Number Generator</h1>
      <button onClick={() => generateRandomNumber(1, 100)}>
        Generate Random Number (1-100)
      </button>
      {randomNumber !== null && <p>Your random number is: {randomNumber}</p>}
    </div>
  );
};

export default ModelTraining;