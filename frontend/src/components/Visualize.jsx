import React, { useState, useEffect } from "react";
import axios from "axios";
import Plot from "react-plotly.js";

const Visualize = () => {
  const [models, setModels] = useState([]);
  const [selectedModels, setSelectedModels] = useState([]);
  const [trialMAE, setTrialMAE] = useState({});
  const [trainingTime, setTrainingTime] = useState({});
  const [error, setError] = useState("");


  // Fetch available models
  useEffect(() => {
    axios
      .get("http://localhost:8000/visualize/models")
      .then((res) => setModels(res.data.models || []))
      .catch(() => setError("Failed to load models."));
  }, []);

  // Fetch visualization data for selected models
  const handleVisualize = async () => {
    if (selectedModels.length === 0) {
      setError("Please select at least one model.");
      return;
    }
    setError("");

    const newTrialMAE = {};
    const newTrainingTime = {};

    await Promise.all(
      selectedModels.map(async (model) => {
        try {
          const res = await axios.get(`http://localhost:8000/visualize/data/${model}`);
          newTrialMAE[model] = res.data.trial_mae || [];
          newTrainingTime[model] = res.data.training_time || 0;
        } catch {
          setError(`Failed to load data for ${model}`);
        }
      })
    );

    setTrialMAE(newTrialMAE);
    setTrainingTime(newTrainingTime);
  };

  const handleModelChange = (e) => {
    const selectedOptions = Array.from(e.target.selectedOptions, (option) => option.value);
    setSelectedModels(selectedOptions);
  };

  return (
    <div className="container mx-auto p-6 bg-gray-50 rounded-lg shadow-md">
      <h2 className="text-3xl font-semibold text-center mb-6">Model Visualization</h2>

      {error && <p className="text-red-500">{error}</p>}

      {/* Model selection */}
      <div className="mb-6">
        <label className="block text-lg font-medium mb-2">Select Models</label>
        <select
          multiple
          value={selectedModels}
          onChange={handleModelChange}
          className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          {models.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>

      {/* Button to fetch and visualize data */}
      <button
        onClick={handleVisualize}
        className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 focus:outline-none"
      >
        Visualize
      </button>

      {/* Display graphs in a 2x2 grid */}
      {selectedModels.length > 0 && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          {selectedModels.map((model) => (
            <React.Fragment key={model}>
              {/* MAE vs Trial Graph */}
              {trialMAE[model] && trialMAE[model].length > 0 && (
                <div className="p-4 bg-white rounded-lg shadow-md">
                  <h4 className="text-lg font-semibold text-center">{`${model} - MAE vs. Trial`}</h4>
                  <Plot
                    data={[
                      {
                        x: Array.from({ length: trialMAE[model].length }, (_, i) => i + 1),
                        y: trialMAE[model],
                        type: "scatter",
                        mode: "lines+markers",
                        marker: { color: "blue" },
                      },
                    ]}
                    layout={{
                      title: "MAE vs. Trial",
                      xaxis: { title: "Trial Number" },
                      yaxis: { title: "MAE" },
                      height: 400,
                      width: 500,
                    }}
                  />
                </div>
              )}

              {/* MAE vs Training Time Graph */}
              {trainingTime[model] !== undefined && (
                <div className="p-4 bg-white rounded-lg shadow-md">
                  <h4 className="text-lg font-semibold text-center">{`${model} - MAE vs. Training Time`}</h4>
                  <Plot
                    data={[
                      {
                        x: [model],
                        y: [Math.min(...trialMAE[model] || [0])], // Best MAE value for this model
                        type: "bar",
                        name: "Best MAE",
                        marker: { color: "blue" },
                        yaxis: "y1",
                      },
                      {
                        x: [model],
                        y: [trainingTime[model]], // Training time for this model
                        type: "bar",
                        name: "Training Time (s)",
                        marker: { color: "orange" },
                        yaxis: "y2",
                      },
                    ]}
                    layout={{
                      title: "MAE vs. Training Time",
                      barmode: "group",
                      xaxis: { title: "Model" },
                      yaxis: {
                        title: "Best MAE",
                        showgrid: false,
                      },
                      yaxis2: {
                        title: "Training Time (s)",
                        overlaying: "y",
                        side: "right",
                        showgrid: false,
                        anchor: "x",
                      },
                      height: 400,
                      width: 500,
                    }}
                  />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      )}
    </div>
  );
};

export default Visualize;
