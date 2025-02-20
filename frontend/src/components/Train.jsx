import React, { useState, useEffect } from "react";
import { trainModel } from "../api.js"; // Assuming trainModel is an API function

const Train = () => {
    const [projectName, setProjectName] = useState("");
    const [datasets, setDatasets] = useState([]); // Store available datasets
    const [selectedDataset, setSelectedDataset] = useState("");
    const [inputParams, setInputParams] = useState([]);
    const [outputParams, setOutputParams] = useState([]);
    const [splitType, setSplitType] = useState("train_test");
    const [fetchError, setFetchError] = useState(null); // To store fetch error messages
    const [datasetColumns, setDatasetColumns] = useState([]); // Store dataset columns

    // Fetch datasets when the component mounts
    useEffect(() => {
        const fetchDatasets = async () => {
            try {
                const response = await fetch("http://127.0.0.1:8000/train/datasets");
                if (!response.ok) {
                    throw new Error("Failed to fetch datasets");
                }
                const result = await response.json();
                setDatasets(result.datasets); // Assuming the response contains the datasets under 'datasets'
            } catch (error) {
                setFetchError(error.message);
            }
        };

        fetchDatasets();
    }, []);

    // Fetch columns of the selected dataset dynamically (for both JSON and CSV)
    useEffect(() => {
        const fetchColumns = async () => {
            if (!selectedDataset) return;
        
            try {
                const response = await fetch(`http://127.0.0.1:8000/train/dataset-columns/${encodeURIComponent(selectedDataset)}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch dataset columns: ${response.statusText}`);
                }
                const result = await response.json();
                setDatasetColumns(result.columns); // Use 'columns' key
            } catch (error) {
                setFetchError(error.message);
            }
        };

        fetchColumns();
    }, []);

    const handleTrain = async () => {
        if (!selectedDataset) {
            alert("Please select a dataset.");
            return;
        }

        const data = {
            project_name: projectName,
            dataset_name: selectedDataset,
            input_params: inputParams,
            output_params: outputParams,
            split_type: splitType,
            tuner_types: ["random", "bayesian", "hyperband", "greedy"], // Send all tuner types in parallel
        };

        try {
            const res = await trainModel(data);
            alert(res.data.message);
            // Optionally, set params based on backend response after model is trained
            setInputParams(res.data.input_params);
            setOutputParams(res.data.output_params);
        } catch (error) {
            console.error("Error training model:", error);
        }
    };

    return (
        <div>
            <h2>Train Model</h2>
            <input
                type="text"
                placeholder="Project Name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
            />

            {fetchError ? (
                <p style={{ color: "red" }}>Error: {fetchError}</p>
            ) : (
                <select value={selectedDataset} onChange={(e) => setSelectedDataset(e.target.value)}>
                    <option value="">Select Dataset</option>
                    {datasets.map((dataset, index) => (
                        <option key={index} value={dataset}>
                            {dataset}
                        </option>
                    ))}
                </select>
            )}

            <input
                type="text"
                placeholder="Input Parameters (comma-separated)"
                value={inputParams.join(",")}
                onChange={(e) => setInputParams(e.target.value.split(","))}
            />
            <input
                type="text"
                placeholder="Output Parameters (comma-separated)"
                value={outputParams.join(",")}
                onChange={(e) => setOutputParams(e.target.value.split(","))}
            />
            <select value={splitType} onChange={(e) => setSplitType(e.target.value)}>
                <option value="train_test">Train/Test Split</option>
                <option value="train_only">Train Only</option>
            </select>
            <button onClick={handleTrain}>Train</button>
        </div>
    );
};

export default Train;
