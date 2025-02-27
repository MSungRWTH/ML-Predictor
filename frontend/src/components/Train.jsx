import React, { useState, useEffect } from "react";
import axios from "axios";

function Train() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("");
  const [inputParams, setInputParams] = useState([]);
  const [outputParams, setOutputParams] = useState([]);
  const [selectedTuner, setSelectedTuner] = useState("");  // Store selected tuner type
  const [loading, setLoading] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState("");

  // Fetch available processed projects
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await axios.get("http://localhost:8000/train/train/processed-files/");
        setProjects(response.data.files);
      } catch (error) {
        console.error("Error fetching processed projects", error);
      }
    };
    fetchProjects();
  }, []);

  // Handle project selection and fetch params.json
  const handleProjectSelection = async (e) => {
    const project = e.target.value;
    setSelectedProject(project);
    setSelectedTuner("");  // Reset tuner selection
    setTrainingStatus("");

    if (!project) return;
    try {
      const response = await axios.get(`http://localhost:8000/train/train/get-params/${project}`);
      setInputParams(response.data.input_params);
      setOutputParams(response.data.output_params);
    } catch (error) {
      console.error("Error fetching parameters", error);
      setInputParams([]);
      setOutputParams([]);
    }
  };

  // Handle tuner type selection
  const handleTunerSelection = (e) => {
    setSelectedTuner(e.target.value);
  };

  // Start training models
  const handleTrainModel = async () => {
    if (!selectedProject) {
      alert("Please select a project.");
      return;
    }
    if (!selectedTuner) {
      alert("Please select a tuner type.");
      return;
    }
  
    setLoading(true);
    setTrainingStatus("Training in progress...");
  
    try {
      const response = await axios.post("http://localhost:8000/train/train", {
        project_name: selectedProject,
        tuner: selectedTuner,  // Ensure the `tuner` value is correctly set
      });
      setTrainingStatus(response.data.message);
    } catch (error) {
      console.error("Error training model", error.response || error);
      setTrainingStatus(`Error during training: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <div className="container mx-auto p-6 bg-gray-50 rounded-lg shadow-md">
      <h1 className="text-3xl font-semibold text-center mb-6">Model Training</h1>

      {/* Project Selection */}
      <div className="mb-4">
        <label className="block text-lg font-medium mb-2">Select Project</label>
        <select
          className="block w-full px-4 py-2 mb-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          onChange={handleProjectSelection}
          value={selectedProject}
        >
          <option value="">Select a project</option>
          {projects.map((project) => (
            <option key={project} value={project}>
              {project}
            </option>
          ))}
        </select>
      </div>

      {/* Display Input/Output Parameters */}
      {selectedProject && (
        <div className="mb-4">
          <h2 className="text-xl font-semibold">Parameters for {selectedProject}</h2>
          <p><strong>Input:</strong> {inputParams.join(", ") || "Not available"}</p>
          <p><strong>Output:</strong> {outputParams.join(", ") || "Not available"}</p>
        </div>
      )}

      {/* Tuner Type Selection */}
      <div className="mb-4">
        <label className="block text-lg font-medium mb-2">Select Tuner Type</label>
        <select
          className="block w-full px-4 py-2 mb-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          onChange={handleTunerSelection}
          value={selectedTuner}
        >
          <option value="">Select a tuner type</option>
          <option value="random">Random</option>
          <option value="bayesian">Bayesian</option>
          <option value="hyperband">Hyperband</option>
          <option value="greedy">Greedy</option>
          <option value="all">Run all tuners in parallel</option> {/* Add 'all' option */}
        </select>
      </div>

      {/* Start Training Button */}
      <div className="mt-4">
        <button
          className={`${
            loading ? "bg-gray-500 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"
          } w-full text-white py-2 rounded-md focus:outline-none`}
          onClick={handleTrainModel}
          disabled={loading}
        >
          {loading ? "Training..." : "Start Training"}
        </button>
      </div>

      {/* Training Status */}
      <div className="mt-4 text-lg">
        {trainingStatus && <p>{trainingStatus}</p>}
      </div>
    </div>
  );
}

export default Train;
