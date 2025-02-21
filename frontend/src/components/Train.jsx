import React, { useState, useEffect } from "react";
import { fetchDatasets, fetchDatasetColumns, preprocessDataset, trainModel } from "../api.js";

const Train = () => {
    const [projectName, setProjectName] = useState("");
    const [datasets, setDatasets] = useState([]);
    const [selectedDataset, setSelectedDataset] = useState("");
    const [datasetColumns, setDatasetColumns] = useState([]);
    const [inputParams, setInputParams] = useState([]);
    const [outputParams, setOutputParams] = useState([]);
    const [splitType, setSplitType] = useState("train_test");
    const [fetchError, setFetchError] = useState(null);

    useEffect(() => {
        const loadDatasets = async () => {
            try {
                const datasets = await fetchDatasets();
                setDatasets(datasets);
            } catch (error) {
                setFetchError(error.message);
            }
        };
        loadDatasets();
    }, []);

    useEffect(() => {
        if (!selectedDataset) return; // Only fetch when a dataset is selected
        const loadDatasetColumns = async () => {
            try {
                const columns = await fetchDatasetColumns(selectedDataset);
                setDatasetColumns(columns || []);
            } catch (error) {
                setFetchError(error.message);
            }
        };
        loadDatasetColumns();
    }, [selectedDataset]);

    const handlePreprocess = async () => {
        if (!selectedDataset) {
            alert("Please select a dataset.");
            return;
        }
        try {
            await preprocessDataset({ dataset_name: selectedDataset });
            alert("Preprocessing completed.");
        } catch (error) {
            console.error("Error preprocessing dataset:", error);
        }
    };

    const handleTrain = async () => {
        if (!selectedDataset || inputParams.length === 0 || outputParams.length === 0) {
            alert("Please complete all selections.");
            return;
        }
        try {
            const res = await trainModel({
                project_name: projectName,
                dataset_name: selectedDataset,
                input_params: inputParams,
                output_params: outputParams,
                split_type: splitType,
                tuner_types: ["random", "bayesian", "hyperband", "greedy"],
            });
            alert(res.data.message);
        } catch (error) {
            console.error("Error training model:", error);
        }
    };

    return (
        <div>
            <h2>Train Model</h2>
            <input type="text" placeholder="Project Name" value={projectName} onChange={(e) => setProjectName(e.target.value)} />
            {fetchError ? <p style={{ color: "red" }}>Error: {fetchError}</p> : null}
            <select value={selectedDataset} onChange={(e) => setSelectedDataset(e.target.value)}>
                {/* <option value="">Select Dataset</option>
                {datasets.map((dataset, index) => (
                    <option key={index} value={dataset}>{dataset}</option>
                ))} */}
            </select>
            <button onClick={handlePreprocess}>Preprocess</button>

            {Array.isArray(datasetColumns) && datasetColumns.length > 0 && (
                <select multiple value={inputParams} onChange={(e) => setInputParams([...e.target.selectedOptions].map(o => o.value))}>
                    {datasetColumns.map((col, index) => (
                        <option key={index} value={col}>
                            {col}
                        </option>
                    ))}
                </select>
            )}

            <select value={splitType} onChange={(e) => setSplitType(e.target.value)}>
                <option value="train_test">Train/Test Split</option>
                <option value="train_only">Train Only</option>
            </select>
            <button onClick={handleTrain}>Train</button>
        </div>
    );
};

export default Train;
