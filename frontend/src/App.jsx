import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css"; // Import the CSS file

const API_BASE_URL = "http://localhost:8000"; // Update if your backend is running elsewhere

const ModelManager = () => {
    const [models, setModels] = useState([]);
    const [selectedModel, setSelectedModel] = useState("");
    const [inputParams, setInputParams] = useState([]);
    const [outputParams, setOutputParams] = useState([]);
    const [inputValues, setInputValues] = useState({});
    const [predictions, setPredictions] = useState(null);
    const [file, setFile] = useState(null);

    // Fetch available models
    useEffect(() => {
        axios.get(`${API_BASE_URL}/models`)
            .then(res => setModels(res.data.models))
            .catch(err => console.error("Error fetching models:", err));
    }, []);

    // Upload a new model
    const handleUpload = async () => {
        if (!file) {
            alert("Please select a model file to upload.");
            return;
        }
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await axios.post(`${API_BASE_URL}/upload`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            alert(res.data.message);
            setModels([...models, res.data.model_name]); // Update model list
        } catch (error) {
            console.error("Error uploading model:", error);
        }
    };

    // Load a selected model
    const handleLoadModel = async () => {
        if (!selectedModel) {
            alert("Please select a model.");
            return;
        }

        try {
            const res = await axios.post(`${API_BASE_URL}/load_model`, { model_name: selectedModel });
            alert(res.data.message);
        } catch (error) {
            console.error("Error loading model:", error);
        }
    };

    // Handle input parameter changes
    const handleInputChange = (param, value) => {
        setInputValues({ ...inputValues, [param]: parseFloat(value) || 0 });
    };

    // Make a prediction
    const handlePredict = async () => {
        if (!selectedModel) {
            alert("Please select a model first.");
            return;
        }
        if (inputParams.length === 0 || outputParams.length === 0) {
            alert("Define both input and output parameters.");
            return;
        }

        try {
            const res = await axios.post(`${API_BASE_URL}/predict`, {
                model_name: selectedModel,
                input_data: inputValues,
                input_params: inputParams,
                output_params: outputParams,
            });
            setPredictions(res.data.prediction);
        } catch (error) {
            console.error("Error making prediction:", error);
        }
    };

    return (
        <div className="container">
            <h2>Model Manager</h2>

            {/* Upload Section */}
            <div className="section">
                <input type="file" onChange={(e) => setFile(e.target.files[0])} />
                <button onClick={handleUpload} className="button upload">
                    Upload Model
                </button>
            </div>

            {/* Model Selection */}
            <div className="section">
                <h3>Select Model</h3>
                <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)} className="select">
                    <option value="">-- Select a model --</option>
                    {models.map((model, idx) => (
                        <option key={idx} value={model}>{model}</option>
                    ))}
                </select>
                <button onClick={handleLoadModel} className="button load">
                    Load Model
                </button>
            </div>

            {/* Input Parameter Definition */}
            <div className="section">
                <h3>Define Input Parameters</h3>
                <input type="text" placeholder="Comma-separated inputs (e.g., AmountServer,Coolingdefect)"
                    className="input"
                    onBlur={(e) => setInputParams(e.target.value.split(",").map(p => p.trim()))}
                />
            </div>

            {/* Output Parameter Definition */}
            <div className="section">
                <h3>Define Output Parameters</h3>
                <input type="text" placeholder="Comma-separated outputs (e.g., Throughput,OEE)"
                    className="input"
                    onBlur={(e) => setOutputParams(e.target.value.split(",").map(p => p.trim()))}
                />
            </div>

            {/* Input Values */}
            <div className="section">
                <h3>Enter Input Values</h3>
                {inputParams.map((param, idx) => (
                    <div key={idx} className="input-group">
                        <label>{param}</label>
                        <input type="number" placeholder={`Enter ${param}`}
                            className="input"
                            onChange={(e) => handleInputChange(param, e.target.value)}
                        />
                    </div>
                ))}
            </div>

            {/* Prediction Button */}
            <button onClick={handlePredict} className="button predict">
                Predict
            </button>

            {/* Prediction Results */}
            {predictions && (
                <div className="prediction-box">
                    <h3>Prediction Results:</h3>
                    <pre>{JSON.stringify(predictions, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default ModelManager;



// second iteration
// import "./App.css";
// import { useState } from "react";
// import axios from "axios";

// export default function App() {
//     const [page, setPage] = useState("predict");
    
//     return (
//         <div className="dashboard">
//             {/* Sidebar Navigation */}
//             <nav className="sidebar">
//                 <h2>ML Dashboard</h2>
//                 <ul>
//                     <li><button onClick={() => setPage("predict")}>Prediction</button></li>
//                     <li><button onClick={() => setPage("model")}>Model Management</button></li>
//                 </ul>
//             </nav>
            
//             {/* Dynamic Content */}
//             <div className="main-content">
//                 {page === "predict" ? <PredictionDashboard /> : <ModelManagement />}
//             </div>
//         </div>
//     );
// }

// function PredictionDashboard() {
//     const [inputs, setInputs] = useState({
//         AmountServer: "",
//         Coolingdefect: "",
//         InterarrivalTime: "",
//         defekteModulanzahl: ""
//     });
//     const [prediction, setPrediction] = useState(null);
//     const [loading, setLoading] = useState(false);
//     const [error, setError] = useState(null);

//     const handleChange = (e) => {
//         setInputs({ ...inputs, [e.target.name]: e.target.value });
//     };

//     const handleSubmit = async (e) => {
//         e.preventDefault();
//         setError(null);
//         setLoading(true);

//         try {
//             const response = await axios.post("http://localhost:8000/predict", {
//                 AmountServer: Number(inputs.AmountServer),
//                 Coolingdefect: Number(inputs.Coolingdefect),
//                 InterarrivalTime: Number(inputs.InterarrivalTime),
//                 defekteModulanzahl: Number(inputs.defekteModulanzahl)
//             });
//             setPrediction(response.data);
//         } catch (error) {
//             setError("Failed to get prediction. Please try again later.");
//         } finally {
//             setLoading(false);
//         }
//     };

//     return (
//         <div>
//             <h2>Machine Learning Prediction</h2>
//             <form onSubmit={handleSubmit}>
//                 <input type="number" name="AmountServer" placeholder="Amount of Servers" onChange={handleChange} required />
//                 <input type="number" name="Coolingdefect" placeholder="Cooling Defect" onChange={handleChange} required />
//                 <input type="number" name="InterarrivalTime" placeholder="Interarrival Time" onChange={handleChange} required />
//                 <input type="number" name="defekteModulanzahl" placeholder="Defekte Modulanzahl" onChange={handleChange} required />
//                 <button type="submit" disabled={loading}>{loading ? "Loading..." : "Predict"}</button>
//             </form>
//             {error && <p className="error">{error}</p>}
//             {prediction && <pre>{JSON.stringify(prediction, null, 2)}</pre>}
//         </div>
//     );
// }

// function ModelManagement() {
//     const [modelFile, setModelFile] = useState(null);
//     const [scalerFile, setScalerFile] = useState(null);
//     const [uploading, setUploading] = useState(false);
//     const [message, setMessage] = useState(null);

//     const handleFileChange = (e, setFile) => {
//         setFile(e.target.files[0]);
//     };

//     const handleUpload = async () => {
//         if (!modelFile || !scalerFile) {
//             setMessage("Please select both model and scaler files.");
//             return;
//         }
//         setUploading(true);
//         setMessage(null);

//         const formData = new FormData();
//         formData.append("model", modelFile);
//         formData.append("scaler", scalerFile);

//         try {
//             await axios.post("http://localhost:8000/upload", formData, {
//                 headers: { "Content-Type": "multipart/form-data" }
//             });
//             setMessage("Model and scaler uploaded successfully!");
//         } catch (error) {
//             setMessage("Upload failed. Please try again.");
//         } finally {
//             setUploading(false);
//         }
//     };

//     return (
//         <div>
//             <h2>Model Management</h2>
//             <input type="file" onChange={(e) => handleFileChange(e, setModelFile)} />
//             <input type="file" onChange={(e) => handleFileChange(e, setScalerFile)} />
//             <button onClick={handleUpload} disabled={uploading}>{uploading ? "Uploading..." : "Upload Model & Scaler"}</button>
//             {message && <p>{message}</p>}
//         </div>
//     );
// }



// first iteration
// export default function PredictionDashboard() {
//     const [inputs, setInputs] = useState({
//         AmountServer: "",
//         Coolingdefect: "",
//         InterarrivalTime: "",
//         defekteModulanzahl: ""
//     });

//     const [prediction, setPrediction] = useState(null);
//     const [loading, setLoading] = useState(false);
//     const [error, setError] = useState(null);

//     const handleChange = (e) => {
//         setInputs({ ...inputs, [e.target.name]: e.target.value });
//     };

//     const handleSubmit = async (e) => {
//         e.preventDefault();
//         setError(null); // Reset previous error
//         setLoading(true);  // Start loading

//         // Input validation
//         if (inputs.AmountServer <= 0 || inputs.CoolingDefect < 0 || inputs.InterarrivalTime <= 0 || inputs.DefekteModulanzahl < 0) {
//             setError("Please enter valid positive values.");
//             setLoading(false);  // Stop loading
//             return;
//         }

//         try {
//             // Add a timestamp to avoid request caching
//             const response = await axios.post("http://localhost:8000/predict", {
//                 AmountServer: Number(inputs.AmountServer),
//                 Coolingdefect: Number(inputs.Coolingdefect),
//                 InterarrivalTime: Number(inputs.InterarrivalTime),
//                 defekteModulanzahl: Number(inputs.defekteModulanzahl),
//                 timestamp: new Date().getTime()  // Add timestamp to prevent caching
//             });

//             setPrediction(response.data);
//         } catch (error) {
//             console.error("Error making prediction:", error);
//             setError("Failed to get prediction. Please try again later.");
//         } finally {
//             setLoading(false);  // Stop loading
//         }
//     };

//     return (
//         <div className="dashboard">
//             {/* Sidebar */}
//             <nav className="sidebar">
//                 <h2>ML Dashboard</h2>
//                 <ul>
//                     <li><a href="#">Home</a></li>
//                     <li><a href="#">Predictions</a></li>
//                     <li><a href="#">Settings</a></li>
//                 </ul>
//             </nav>

//             {/* Main Content */}
//             <div className="main-content">
//                 <h2>Machine Learning Prediction</h2>
//                 <form className="prediction-form" onSubmit={handleSubmit}>
//                     <input
//                         type="number"
//                         name="AmountServer"
//                         placeholder="Amount of Servers [6-10]"
//                         onChange={handleChange}
//                         required
//                     />
//                     <input
//                         type="number"
//                         step="0.01"
//                         name="Coolingdefect"
//                         placeholder="Cooling Defect [0-18]"
//                         onChange={handleChange}
//                         required
//                     />
//                     <input
//                         type="number"
//                         step="0.01"
//                         name="InterarrivalTime"
//                         placeholder="Interarrival Time [4300-5500]"
//                         onChange={handleChange}
//                         required
//                     />
//                     <input
//                         type="number"
//                         name="defekteModulanzahl"
//                         placeholder="Defekte Modulanzahl [0-11]"
//                         onChange={handleChange}
//                         required
//                     />
//                     <button type="submit" disabled={loading}>
//                         {loading ? "Loading..." : "Predict"}
//                     </button>
//                 </form>

//                 {error && (
//                     <div className="error">
//                         <p>{error}</p>
//                     </div>
//                 )}

//                 {prediction && !loading && (
//                     <div className="prediction-results">
//                         <h3>Prediction Results:</h3>
//                         <pre>{JSON.stringify(prediction, null, 2)}</pre>
//                     </div>
//                 )}
//             </div>
//         </div>
//     );
// }
