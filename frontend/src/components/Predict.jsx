import React, { useState, useEffect } from "react";
import axios from "axios";

const Predict = () => {
  const [models, setModels] = useState([]);
  const [processedFiles, setProcessedFiles] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [selectedProject, setSelectedProject] = useState("");
  const [inputParams, setInputParams] = useState([]);
  const [outputParams, setOutputParams] = useState([]);
  const [inputValues, setInputValues] = useState({});
  const [predictions, setPredictions] = useState({});
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      .get("http://localhost:8000/predict/models")
      .then((res) => setModels(res.data.models || []))
      .catch((err) => setError("Failed to load models."));
  }, []);

  useEffect(() => {
    axios
      .get("http://localhost:8000/predict/predict/processed-files/")
      .then((res) => setProcessedFiles(res.data.files || []))
      .catch((err) => setError("Failed to load processed data."));
  }, []);

  useEffect(() => {
    if (selectedProject) {
      axios
        .get(`http://localhost:8000/predict/params/${selectedProject}`)
        .then((res) => {
          setInputParams(res.data.input_params || []);
          setOutputParams(res.data.output_params || []);
        })
        .catch((err) => setError("Failed to load model parameters."));
    }
  }, [selectedProject]);

  const handleInputChange = (param, value) => {
    // Ensure the value is treated as a number (including zero)
    const numericValue = value === "" ? "" : parseFloat(value) || 0;
    setInputValues({ ...inputValues, [param]: numericValue });
  };

  const handlePredict = () => {
    if (!selectedModel || !selectedProject) {
      alert("Please select a model and a processed project.");
      return;
    }

    axios
      .post("http://localhost:8000/predict/predict/", {
        model_name: selectedModel,
        project_name: selectedProject,
        input_data: inputValues,
      })
      .then((res) => setPredictions(res.data.predictions || {}))
      .catch((err) => setError("Failed to get predictions."));
  };

  return (
    <div className="container mx-auto p-6 bg-gray-50 rounded-lg shadow-md">
      <h2 className="text-3xl font-semibold text-center mb-6">Predict</h2>

      {error && <p className="text-red-500">{error}</p>}

      {/* Model selection */}
      <div className="mb-6">
        <label className="block text-lg font-medium mb-2">Select Model</label>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">Select a model</option>
          {models.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>

      {/* Processed data selection */}
      <div className="mb-6">
        <label className="block text-lg font-medium mb-2">Select Processed Data</label>
        <select
          value={selectedProject}
          onChange={(e) => setSelectedProject(e.target.value)}
          className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">Select processed data</option>
          {processedFiles.map((project) => (
            <option key={project} value={project}>
              {project}
            </option>
          ))}
        </select>
      </div>

      {/* Input parameters section */}
      {inputParams.length > 0 && (
        <div className="mb-6">
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
        </div>
      )}

      {/* Predictions section */}
      {Object.keys(predictions).length > 0 && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-4">Predictions</h3>
          {outputParams.map((param) => (
            <p key={param} className="text-lg">
              {param}: {predictions[param]?.toFixed(4)}
            </p>
          ))}
        </div>
      )}
    </div>
  );
};

export default Predict;
