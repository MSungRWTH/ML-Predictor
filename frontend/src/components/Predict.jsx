import React, { useState, useEffect } from "react";
import { makePrediction } from "../api.js";

const Predict = () => {
    const [models, setModels] = useState([]); // Initialize models state
    const [selectedModel, setSelectedModel] = useState(""); // Selected model from dropdown
    const [inputData, setInputData] = useState({});
    const [prediction, setPrediction] = useState(null);
    const [inputParams, setInputParams] = useState([]); // Store input parameters from the selected model

    // Fetch models from the backend (models in MODEL_DIRECTORY)
    useEffect(() => {
        const fetchModels = async () => {
            try {
                const response = await fetch("http://127.0.0.1:8000/predict/models");
                const result = await response.json();
                setModels(result.models); // Set models once fetched
            } catch (error) {
                console.error("Error fetching models:", error);
            }
        };
    
        fetchModels();
    }, []); // Fetch models only once when the component mounts

    // Fetch model parameters when a model is selected
    useEffect(() => {
        const fetchModelParams = async () => {
            if (selectedModel) {
                try {
                    const response = await fetch(`http://127.0.0.1:8000/predict/params/${selectedModel}`);
                    const result = await response.json();
                    setInputParams(result.input_params); // Set input parameters
                } catch (error) {
                    console.error("Error fetching model parameters:", error);
                }
            }
        };

        fetchModelParams();
    }, [selectedModel]); // Fetch params whenever a new model is selected

    const handlePredict = async () => {
        const data = {
            project_name: selectedModel, // Model name now used instead of project name
            input_data: inputData,
        };
        try {
            const res = await makePrediction(data);
            setPrediction(res.data.prediction);
        } catch (error) {
            console.error("Error making prediction:", error);
        }
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
            
            {/* Dropdown to select the model */}
            <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
                <option value="">Select Model</option>
                {models.length > 0 ? (
                    models.map((model, index) => (
                        <option key={index} value={model}>
                            {model}
                        </option>
                    ))
                ) : (
                    <option value="">No models available</option>
                )}
            </select>

            {/* Dynamically render input fields based on the selected model's parameters */}
            {inputParams.length > 0 &&
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
                ))}

            <button onClick={handlePredict}>Predict</button>

            {prediction && <pre>{JSON.stringify(prediction, null, 2)}</pre>}
        </div>
    );
};

export default Predict;





// import { useState, useEffect } from "react";
// import axios from "axios";

// const API_BASE_URL = "http://localhost:8000"; // Update if needed

// const ModelManager = () => {
//   const [models, setModels] = useState([]);
//   const [selectedModel, setSelectedModel] = useState("");
//   const [inputParams, setInputParams] = useState([]);
//   const [outputParams, setOutputParams] = useState([]);
//   const [inputValues, setInputValues] = useState({});
//   const [predictions, setPredictions] = useState(null);
//   const [file, setFile] = useState(null);

//   // Fetch available models
//   useEffect(() => {
//     const fetchModels = async () => {
//       try {
//         const res = await axios.get(`${API_BASE_URL}/models`);
//         setModels(res.data.models);
//       } catch (err) {
//         console.error("Error fetching models:", err);
//       }
//     };
//     fetchModels();
//   }, []);

//   // Upload a new model
//   const handleUpload = async () => {
//     if (!file) {
//       alert("Please select a model file to upload.");
//       return;
//     }
//     const formData = new FormData();
//     formData.append("file", file);

//     try {
//       const res = await axios.post(`${API_BASE_URL}/upload`, formData, {
//         headers: { "Content-Type": "multipart/form-data" },
//       });
//       alert(res.data.message);
//       setModels([...models, res.data.model_name]); // Update model list
//     } catch (error) {
//       console.error("Error uploading model:", error);
//     }
//   };

//   // Load a selected model
//   const handleLoadModel = async () => {
//     if (!selectedModel) {
//       alert("Please select a model.");
//       return;
//     }
//     try {
//       const res = await axios.post(
//         `${API_BASE_URL}/load_model`,
//         { model_name: selectedModel },
//         { headers: { "Content-Type": "application/json" } }
//       );
//       alert(res.data.message);

//       // Fetch input/output parameters
//       const modelInfoRes = await axios.get(`${API_BASE_URL}/model_info/${selectedModel}`);
//       setInputParams(modelInfoRes.data.input_params || []);
//       setOutputParams(modelInfoRes.data.output_params || []);

//       // Initialize inputValues with empty/default values
//       const defaultInputs = modelInfoRes.data.input_params.reduce((acc, param) => {
//         acc[param] = ""; // Initialize with an empty string or default value
//         return acc;
//       }, {});
//       setInputValues(defaultInputs);
//     } catch (error) {
//       console.error("Error loading model:", error.response?.data || error.message);
//     }
//   };

//   // Handle input parameter changes
//   const handleInputChange = (param, value) => {
//     setInputValues({ ...inputValues, [param]: parseFloat(value) || 0 });
//   };

//   // Make a prediction
//   const handlePredict = async () => {
//     if (!selectedModel) {
//       alert("Please select a model first.");
//       return;
//     }
//     try {
//       const res = await axios.post(`${API_BASE_URL}/predict`, {
//         model_name: selectedModel,
//         input_data: inputValues,
//       });
//       setPredictions(res.data.prediction);
//     } catch (error) {
//       console.error("Error making prediction:", error);
//     }
//   };

//   return (
//     <div className="container mx-auto p-6">
//       <h2 className="text-2xl font-semibold mb-6">Model Manager</h2>

//       {/* Upload Section */}
//       <div className="bg-white p-4 rounded-lg shadow-md mb-6">
//         <h3 className="text-lg font-medium mb-4">Upload New Model</h3>
//         <input type="file" onChange={(e) => setFile(e.target.files[0])} className="block mb-4 p-2 border rounded-md" />
//         <button onClick={handleUpload} className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
//           Upload Model
//         </button>
//       </div>

//       {/* Model Selection */}
//       <div className="bg-white p-4 rounded-lg shadow-md mb-6">
//         <h3 className="text-lg font-medium mb-4">Select Model</h3>
//         <select
//           value={selectedModel}
//           onChange={(e) => setSelectedModel(e.target.value)}
//           className="block mb-4 p-2 border rounded-md w-full"
//         >
//           <option value="">-- Select a model --</option>
//           {models.map((model, idx) => (
//             <option key={idx} value={model}>{model}</option>
//           ))}
//         </select>
//         <button onClick={handleLoadModel} className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
//           Load Model
//         </button>
//       </div>

//       {/* Input Values (Dynamically Generated) */}
//       {inputParams.length > 0 && (
//         <div className="bg-white p-4 rounded-lg shadow-md mb-6">
//           <h3 className="text-lg font-medium mb-4">Enter Input Values</h3>
//           {inputParams.map((param, idx) => (
//             <div key={idx} className="mb-4">
//               <label className="block text-sm font-medium mb-2">{param}</label>
//               <input
//                 type="number"
//                 placeholder={`Enter ${param}`}
//                 className="block p-2 border rounded-md w-full"
//                 value={inputValues[param] || ""}
//                 onChange={(e) => handleInputChange(param, e.target.value)}
//               />
//             </div>
//           ))}
//         </div>
//       )}

//       {/* Prediction Button */}
//       {inputParams.length > 0 && (
//         <div className="text-center mb-6">
//           <button onClick={handlePredict} className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 transition-colors">
//             Make Prediction
//           </button>
//         </div>
//       )}

//       {/* Prediction Results (Dynamically Generated) */}
//       {predictions && (
//         <div className="bg-white p-4 rounded-lg shadow-md">
//           <h3 className="text-lg font-medium mb-4">Prediction Results:</h3>
//           <ul>
//             {outputParams.map((param, idx) => (
//               <li key={idx} className="mb-2">
//                 <strong>{param}:</strong> {predictions[param]}
//               </li>
//             ))}
//           </ul>
//         </div>
//       )}
//     </div>
//   );
// };

// export default ModelManager;

/////////////////////////////////////////////////////////////////////////////////////////////////////////

// import { useState, useEffect } from "react";
// import axios from "axios";

// const API_BASE_URL = "http://localhost:8000"; // Update if your backend is running elsewhere

// const ModelManager = () => {
//   const [models, setModels] = useState([]);
//   const [selectedModel, setSelectedModel] = useState("");
//   const [inputParams, setInputParams] = useState([]);
//   const [outputParams, setOutputParams] = useState([]);
//   const [inputValues, setInputValues] = useState({});
//   const [predictions, setPredictions] = useState(null);
//   const [file, setFile] = useState(null);

//   // Fetch available models
//   const fetchModels = async () => {
//     try {
//       const res = await axios.get(`${API_BASE_URL}/models`);
//       setModels(res.data.models);
//     } catch (err) {
//       console.error("Error fetching models:", err);
//     }
//   };

//   useEffect(() => {
//     fetchModels();
//   }, []);

//   // Upload a new model
//   const handleUpload = async () => {
//     if (!file) {
//       alert("Please select a model file to upload.");
//       return;
//     }
//     const formData = new FormData();
//     formData.append("file", file);

//     try {
//       const res = await axios.post(`${API_BASE_URL}/upload`, formData, {
//         headers: { "Content-Type": "multipart/form-data" },
//       });
//       alert(res.data.message);
//       fetchModels(); // Refresh models list after upload
//     } catch (error) {
//       console.error("Error uploading model:", error);
//     }
//   };

//   // Load a selected model
//   const handleLoadModel = async () => {
//     if (!selectedModel) {
//       alert("Please select a model.");
//       return;
//     }
//     try {
//       const res = await axios.post(`${API_BASE_URL}/load_model`, {
//         model_name: selectedModel,
//       }, {
//         headers: { "Content-Type": "application/json" },
//       });
//       alert(res.data.message);
  
//       // Fetch model input/output parameters safely
//       const modelInfoRes = await axios.get(`${API_BASE_URL}/model_info/${selectedModel}`);
//       setInputParams(modelInfoRes.data.input_params || []); // Default to empty array if undefined
//       setOutputParams(modelInfoRes.data.output_params || []); // Default to empty array if undefined
//     } catch (error) {
//       console.error("Error loading model:", error.response?.data || error.message);
//     }
//   };

//   // Handle input parameter changes
//   const handleInputChange = (param, value) => {
//     setInputValues({ ...inputValues, [param]: parseFloat(value) || 0 });
//   };

//   // Make a prediction
//   const handlePredict = async () => {
//     if (!selectedModel) {
//       alert("Please select a model first.");
//       return;
//     }
//     if (inputParams.length === 0 || outputParams.length === 0) {
//       alert("Define both input and output parameters.");
//       return;
//     }

//     try {
//       const res = await axios.post(`${API_BASE_URL}/predict`, {
//         model_name: selectedModel,
//         input_data: inputValues,
//         input_params: inputParams,
//         output_params: outputParams,
//       });
//       setPredictions(res.data.prediction);
//     } catch (error) {
//       console.error("Error making prediction:", error);
//     }
//   };

//   return (
//     <div className="container mx-auto p-6">
//       <h2 className="text-2xl font-semibold mb-6">Model Manager</h2>

//       {/* Upload Section */}
//       <div className="bg-white p-4 rounded-lg shadow-md mb-6">
//         <h3 className="text-lg font-medium mb-4">Upload New Model</h3>
//         <input type="file" onChange={(e) => setFile(e.target.files[0])} className="block mb-4 p-2 border rounded-md" />
//         <button onClick={handleUpload} className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
//           Upload Model
//         </button>
//       </div>

//       {/* Model Selection */}
//       <div className="bg-white p-4 rounded-lg shadow-md mb-6">
//         <h3 className="text-lg font-medium mb-4">Select Model</h3>
//         <select
//           value={selectedModel}
//           onChange={(e) => setSelectedModel(e.target.value)}
//           className="block mb-4 p-2 border rounded-md w-full"
//         >
//           <option value="">-- Select a model --</option>
//           {models.map((model, idx) => (
//             <option key={idx} value={model}>{model}</option>
//           ))}
//         </select>
//         <button onClick={handleLoadModel} className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
//           Load Model
//         </button>
//       </div>

//       {/* Input Parameter Definition */}
//       <div className="bg-white p-4 rounded-lg shadow-md mb-6">
//         <h3 className="text-lg font-medium mb-4">Define Input Parameters</h3>
//         <input
//           type="text"
//           placeholder="Comma-separated inputs (e.g., AmountServer,Coolingdefect)"
//           className="block mb-4 p-2 border rounded-md w-full"
//           value={inputParams ? inputParams.join(", ") : ""} // Ensure inputParams is valid
//           onChange={(e) => setInputParams(e.target.value.split(",").map((p) => p.trim()))}
//         />
//       </div>

//       {/* Output Parameter Definition */}
//       <div className="bg-white p-4 rounded-lg shadow-md mb-6">
//         <h3 className="text-lg font-medium mb-4">Define Output Parameters</h3>
//         <input
//           type="text"
//           placeholder="Comma-separated outputs (e.g., Throughput,OEE)"
//           className="block mb-4 p-2 border rounded-md w-full"
//           value={outputParams ? outputParams.join(", ") : ""} // Ensure outputParams is valid
//           onChange={(e) => setOutputParams(e.target.value.split(",").map((p) => p.trim()))}
//         />
//       </div>

//       {/* Input Values */}
//       <div className="bg-white p-4 rounded-lg shadow-md mb-6">
//         <h3 className="text-lg font-medium mb-4">Enter Input Values</h3>
//         {inputParams.map((param, idx) => (
//           <div key={idx} className="mb-4">
//             <label className="block text-sm font-medium mb-2">{param}</label>
//             <input
//               type="number"
//               placeholder={`Enter ${param}`}
//               className="block p-2 border rounded-md w-full"
//               onChange={(e) => handleInputChange(param, e.target.value)}
//             />
//           </div>
//         ))}
//       </div>

//       {/* Prediction Button */}
//       <div className="text-center mb-6">
//         <button onClick={handlePredict} className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 transition-colors">
//           Make Prediction
//         </button>
//       </div>

//       {/* Prediction Results */}
//       {predictions && (
//         <div className="bg-white p-4 rounded-lg shadow-md">
//           <h3 className="text-lg font-medium mb-4">Prediction Results:</h3>
//           <pre className="whitespace-pre-wrap break-words">{JSON.stringify(predictions, null, 2)}</pre>
//         </div>
//       )}
//     </div>
//   );
// };

// export default ModelManager;



