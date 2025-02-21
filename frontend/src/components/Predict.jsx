import React, { useState, useEffect } from "react";

// Static data for testing purposes
const models = ["Experiment_1", "Experiment_2", "Experiment_3"];
const inputParams = ["AmountServer", "CoolingDefect", "InterarrivalTime", "DefekteModulanzahl"];
const outputParams = [
    "AverageServerUtilisation",
    "AverageFlowTime",
    "OEE",
    "TotalAverageQueueLength",
    "ProcessingTimeAverage",
    "WaitingTimeAverage",
    "MovingTimeAverage",
    "FailedTimeAverage",
    "BlockedTimeAverage",
    "Throughput"
];

const staticPrediction = {
    prediction: [0.89, 45898.48, 0.89, 0.51, 21265.73, 21773.21, 183.75, 0, 2192.59, 10.88], // example prediction output
};

const Predict = () => {
    const [selectedModel, setSelectedModel] = useState("");
    const [inputData, setInputData] = useState({});
    const [prediction, setPrediction] = useState(null);

    // Simulate the prediction logic (hardcoded for appearance)
    const handlePredict = () => {
        // Here we would normally call an API to make the prediction
        // For testing, we are using static data
        setPrediction(staticPrediction.prediction);
    };

    const handleInputChange = (e, param) => {
        setInputData((prevData) => ({
            ...prevData,
            [param]: e.target.value,
        }));
    };

    return (
        <div>
            <h2>Make Prediction</h2>

            {/* Model Selection Dropdown */}
            <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
                <option value="">Select Model</option>
                {models.map((model, index) => (
                    <option key={index} value={model}>
                        {model}
                    </option>
                ))}
            </select>

            {/* Input Fields for Parameters */}
            {inputParams.length > 0 ? (
                inputParams.map((param, index) => (
                    <div key={index}>
                        <label>{param}</label>
                        <input
                            type="text"
                            placeholder={param}
                            value={inputData[param] || ""}
                            onChange={(e) => handleInputChange(e, param)}
                        />
                    </div>
                ))
            ) : (
                <div>No input parameters available</div>
            )}

            {/* Button to Trigger Prediction */}
            <button onClick={handlePredict}>Predict</button>

            {/* Display Output Params */}
            {outputParams.length > 0 && prediction && (
                <div>
                    <h3>Prediction Results</h3>
                    {outputParams.map((param, index) => (
                        <div key={index}>
                            <strong>{param}: </strong>
                            {prediction[index]}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Predict;


























// import React, { useState, useEffect } from "react";
// import { makePrediction } from "../api.js";

// const Predict = () => {
//     const [models, setModels] = useState([]);
//     const [selectedModel, setSelectedModel] = useState("");
//     const [inputData, setInputData] = useState({});
//     const [prediction, setPrediction] = useState(null);
//     const [inputParams, setInputParams] = useState([]);

//     useEffect(() => {
//         const fetchModels = async () => {
//             try {
//                 const response = await fetch("http://127.0.0.1:8000/predict/models");
//                 const result = await response.json();
//                 setModels(result.models);
//             } catch (error) {
//                 console.error("Error fetching models:", error);
//             }
//         };

//         fetchModels();
//     }, []);

//     useEffect(() => {
//         const fetchModelParams = async () => {
//             if (selectedModel) {
//                 try {
//                     const response = await fetch(`http://127.0.0.1:8000/predict/params/${selectedModel}`);
//                     const result = await response.json();
//                     setInputParams(result.input_params || []); // Ensure inputParams is always an array
//                 } catch (error) {
//                     console.error("Error fetching model parameters:", error);
//                     setInputParams([]); // Reset to empty array if error occurs
//                 }
//             }
//         };

//         fetchModelParams();
//     }, [selectedModel]);

//     const handlePredict = async () => {
//         const data = {
//             project_name: selectedModel,
//             input_data: inputData,
//         };
//         try {
//             const res = await makePrediction(data);
//             setPrediction(res.data.prediction);
//         } catch (error) {
//             console.error("Error making prediction:", error);
//         }
//     };

//     const handleInputChange = (e, param) => {
//         setInputData((prevData) => ({
//             ...prevData,
//             [param]: e.target.value,
//         }));
//     };

//     return (
//         <div>
//             <h2>Make Prediction</h2>

//             <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
//                 <option value="">Select Model</option>
//                 {models.length > 0 ? (
//                     models.map((model, index) => (
//                         <option key={index} value={model}>
//                             {model}
//                         </option>
//                     ))
//                 ) : (
//                     <option value="">No models available</option>
//                 )}
//             </select>

//             {Array.isArray(inputParams) && inputParams.length > 0 ? (
//                 inputParams.map((param, index) => (
//                     <div key={index}>
//                         <label>{param}</label>
//                         <input
//                             type="text"
//                             placeholder={param}
//                             value={inputData[param] || ""}
//                             onChange={(e) => handleInputChange(e, param)}
//                         />
//                     </div>
//                 ))
//             ) : (
//                 <div>No input parameters available</div>
//             )}

//             <button onClick={handlePredict}>Predict</button>

//             {prediction && <pre>{JSON.stringify(prediction, null, 2)}</pre>}
//         </div>
//     );
// };

// export default Predict;
