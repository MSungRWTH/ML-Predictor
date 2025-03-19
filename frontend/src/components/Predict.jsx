import React, { useState, useEffect } from "react";
import axios from "axios";

const Predict = () => {
  const [models, setModels] = useState([]);
  const [processedFiles, setProcessedFiles] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [metrics, setMetrics] = useState({});
  const [selectedProject, setSelectedProject] = useState("");
  const [inputParams, setInputParams] = useState([]);
  const [outputParams, setOutputParams] = useState([]);
  const [inputValues, setInputValues] = useState({});
  const [predictions, setPredictions] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // NEW: Loading state

  useEffect(() => {
    axios.get("http://localhost:8000/predict/models")
      .then((res) => setModels(res.data.models || []))
      .catch(() => setError("Failed to load models."));
  }, []);

  useEffect(() => {
    axios.get("http://localhost:8000/predict/predict/processed-files/")
      .then((res) => setProcessedFiles(res.data.files || []))
      .catch(() => setError("Failed to load processed data."));
  }, []);

  useEffect(() => {
    if (selectedProject) {
      axios.get(`http://localhost:8000/predict/params/${selectedProject}`)
        .then((res) => {
          setInputParams(res.data.input_params || []);
          setOutputParams(res.data.output_params || []);
        })
        .catch(() => setError("Failed to load model parameters."));
    }
  }, [selectedProject]);

  const handleFetchMetrics = async () => {
    if (!selectedModel || !selectedProject) {
      setError("Please select both a model and a project to view metrics.");
      return;
    }

    setLoading(true);  // NEW: Start loading
    setError(""); // Clear any previous error

    try {
      const res = await axios.get(
        `http://localhost:8000/predict/metrics/${selectedModel}?project_name=${selectedProject}`
      );
      setMetrics(res.data);
    } catch {
      setError(`Failed to load metrics for ${selectedModel}`);
    } finally {
      setLoading(false); // NEW: Stop loading
    }
  };

  const handleInputChange = (param, value) => {
    setInputValues({ ...inputValues, [param]: value === "" ? "" : parseFloat(value) || 0 });
  };

  const handlePredict = () => {
    if (!selectedModel || !selectedProject) {
      alert("Please select a model and a processed project.");
      return;
    }
    axios.post("http://localhost:8000/predict/predict/", {
      model_name: selectedModel,
      project_name: selectedProject,
      input_data: inputValues,
    })
      .then((res) => setPredictions(res.data.predictions || {}))
      .catch(() => setError("Failed to get predictions."));
  };

  return (
    <div className="container mx-auto p-6 bg-gray-50 rounded-lg shadow-md">
      <h2 className="text-3xl font-semibold text-center mb-6">Predict</h2>
      {error && <p className="text-red-500">{error}</p>} {/* Global error message */}

      {/* Selection Section */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-lg font-medium mb-2">Select Model</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">Select a model</option>
            {models.map((model) => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-lg font-medium mb-2">Select Processed Data</label>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="">Select processed data</option>
            {processedFiles.map((project) => (
              <option key={project} value={project}>{project}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Content Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Enter Input Values</h3>
          {inputParams.map((param) => (
            <div key={param} className="mb-4">
              <label className="block text-lg font-medium">{param}: </label>
              <input
                type="number"
                value={inputValues[param] !== undefined ? inputValues[param] : ""}
                onChange={(e) => handleInputChange(param, e.target.value)}
                className="w-full px-4 py-2 mt-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
          ))}
          <button
            onClick={handlePredict}
            className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 focus:outline-none"
          >
            Predict
          </button>

          {Object.keys(predictions).length > 0 && (
            <div className="mt-6">
              <h3 className="text-xl font-semibold mb-4">Predictions</h3>
              {outputParams.map((param) => (
                <p key={param} className="text-lg">{param}: {predictions[param]?.toFixed(4)}</p>
              ))}
            </div>
          )}
        </div>

        {/* Metrics Section */}
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4 text-center">Model Evaluation Metrics</h3>
          <button
            onClick={handleFetchMetrics}
            disabled={loading} // NEW: Disable button while loading
            className={`w-full text-white py-2 rounded-md focus:outline-none mb-4 ${loading ? "bg-gray-400" : "bg-green-500 hover:bg-green-600"}`}
          >
            {loading ? "Loading metrics..." : "Show Model Metrics"} 
          </button>

          {loading && <p className="text-center text-blue-500">Loading metrics, please wait...</p>} {/* NEW: Loading message */}

          {error ? ( // Display error message inside the metrics section
            <p className="text-red-500 text-center">{error}</p>
          ) : metrics && Object.keys(metrics).length > 0 ? (
            <div className="p-4 bg-gray-100 rounded-lg shadow-sm">
              {Object.entries(metrics).map(([feature, values]) => (
                <div key={feature} className="mb-4">
                  <h4 className="text-lg font-semibold">{feature}</h4>
                  <p><strong>MAE:</strong> {values.mae?.toFixed(4) || "N/A"}</p>
                  <p><strong>R²:</strong> {values.r2?.toFixed(4) || "N/A"}</p>
                  <p><strong>MAPE:</strong> {values.mape?.toFixed(2) || "N/A"}%</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center mt-2">No metrics available.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Predict;






























// import React, { useState, useEffect } from "react";
// import axios from "axios";

// const Predict = () => {
//   const [models, setModels] = useState([]);
//   const [processedFiles, setProcessedFiles] = useState([]);
//   const [selectedModel, setSelectedModel] = useState("");
//   const [metrics, setMetrics] = useState({});
//   const [selectedProject, setSelectedProject] = useState("");
//   const [inputParams, setInputParams] = useState([]);
//   const [outputParams, setOutputParams] = useState([]);
//   const [inputValues, setInputValues] = useState({});
//   const [predictions, setPredictions] = useState({});
//   const [error, setError] = useState("");
//   const [loading, setLoading] = useState(false); // NEW: Loading state

//   useEffect(() => {
//     axios.get("http://localhost:8000/predict/models")
//       .then((res) => setModels(res.data.models || []))
//       .catch(() => setError("Failed to load models."));
//   }, []);

//   useEffect(() => {
//     axios.get("http://localhost:8000/predict/predict/processed-files/")
//       .then((res) => setProcessedFiles(res.data.files || []))
//       .catch(() => setError("Failed to load processed data."));
//   }, []);

//   useEffect(() => {
//     if (selectedProject) {
//       axios.get(`http://localhost:8000/predict/params/${selectedProject}`)
//         .then((res) => {
//           setInputParams(res.data.input_params || []);
//           setOutputParams(res.data.output_params || []);
//         })
//         .catch(() => setError("Failed to load model parameters."));
//     }
//   }, [selectedProject]);

//   const handleFetchMetrics = async () => {
//     if (!selectedModel || !selectedProject) {
//       setError("Please select both a model and a project to view metrics.");
//       return;
//     }

//     setLoading(true);  // NEW: Start loading
//     setError("");

//     try {
//       const res = await axios.get(
//         `http://localhost:8000/predict/metrics/${selectedModel}?project_name=${selectedProject}`
//       );
//       setMetrics(res.data);
//     } catch {
//       setError(`Failed to load metrics for ${selectedModel}`);
//     } finally {
//       setLoading(false); // NEW: Stop loading
//     }
//   };

//   const handleInputChange = (param, value) => {
//     setInputValues({ ...inputValues, [param]: value === "" ? "" : parseFloat(value) || 0 });
//   };

//   const handlePredict = () => {
//     if (!selectedModel || !selectedProject) {
//       alert("Please select a model and a processed project.");
//       return;
//     }
//     axios.post("http://localhost:8000/predict/predict/", {
//       model_name: selectedModel,
//       project_name: selectedProject,
//       input_data: inputValues,
//     })
//       .then((res) => setPredictions(res.data.predictions || {}))
//       .catch(() => setError("Failed to get predictions."));
//   };

//   return (
//     <div className="container mx-auto p-6 bg-gray-50 rounded-lg shadow-md">
//       <h2 className="text-3xl font-semibold text-center mb-6">Predict</h2>
//       {error && <p className="text-red-500">{error}</p>}

//       {/* Selection Section */}
//       <div className="grid grid-cols-2 gap-4 mb-6">
//         <div>
//           <label className="block text-lg font-medium mb-2">Select Model</label>
//           <select
//             value={selectedModel}
//             onChange={(e) => setSelectedModel(e.target.value)}
//             className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
//           >
//             <option value="">Select a model</option>
//             {models.map((model) => (
//               <option key={model} value={model}>{model}</option>
//             ))}
//           </select>
//         </div>

//         <div>
//           <label className="block text-lg font-medium mb-2">Select Processed Data</label>
//           <select
//             value={selectedProject}
//             onChange={(e) => setSelectedProject(e.target.value)}
//             className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
//           >
//             <option value="">Select processed data</option>
//             {processedFiles.map((project) => (
//               <option key={project} value={project}>{project}</option>
//             ))}
//           </select>
//         </div>
//       </div>

//       {/* Content Section */}
//       <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//         <div className="p-6 bg-white rounded-lg shadow-md">
//           <h3 className="text-xl font-semibold mb-4">Enter Input Values</h3>
//           {inputParams.map((param) => (
//             <div key={param} className="mb-4">
//               <label className="block text-lg font-medium">{param}: </label>
//               <input
//                 type="number"
//                 value={inputValues[param] !== undefined ? inputValues[param] : ""}
//                 onChange={(e) => handleInputChange(param, e.target.value)}
//                 className="w-full px-4 py-2 mt-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
//               />
//             </div>
//           ))}
//           <button
//             onClick={handlePredict}
//             className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 focus:outline-none"
//           >
//             Predict
//           </button>

//           {Object.keys(predictions).length > 0 && (
//             <div className="mt-6">
//               <h3 className="text-xl font-semibold mb-4">Predictions</h3>
//               {outputParams.map((param) => (
//                 <p key={param} className="text-lg">{param}: {predictions[param]?.toFixed(4)}</p>
//               ))}
//             </div>
//           )}
//         </div>

//         {/* Metrics Section */}
//         <div className="p-6 bg-white rounded-lg shadow-md">
//           <h3 className="text-xl font-semibold mb-4 text-center">Model Evaluation Metrics</h3>
//           <button
//             onClick={handleFetchMetrics}
//             disabled={loading} // NEW: Disable button while loading
//             className={`w-full text-white py-2 rounded-md focus:outline-none mb-4 ${loading ? "bg-gray-400" : "bg-green-500 hover:bg-green-600"}`}
//           >
//             {loading ? "Loading metrics..." : "Show Model Metrics"} 
//           </button>

//           {loading && <p className="text-center text-blue-500">Loading metrics, please wait...</p>} {/* NEW: Loading message */}

//           {metrics && Object.keys(metrics).length > 0 ? (
//             <div className="p-4 bg-gray-100 rounded-lg shadow-sm">
//               {Object.entries(metrics).map(([feature, values]) => (
//                 <div key={feature} className="mb-4">
//                   <h4 className="text-lg font-semibold">{feature}</h4>
//                   <p><strong>MAE:</strong> {values.mae?.toFixed(4) || "N/A"}</p>
//                   <p><strong>R²:</strong> {values.r2?.toFixed(4) || "N/A"}</p>
//                   <p><strong>MAPE:</strong> {values.mape?.toFixed(2) || "N/A"}%</p>
//                 </div>
//               ))}
//             </div>
//           ) : (
//             <p className="text-gray-500 text-center mt-2">No metrics available.</p>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Predict;







