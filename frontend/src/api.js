import axios from "axios";

const API_BASE_URL = "http://localhost:8000/train"; // Update base for training-related endpoints

// Fetch available datasets from the backend
export const fetchDatasets = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/datasets`);
        return response.data.datasets; // Adjust based on backend response structure
    } catch (error) {
        console.error("Error fetching datasets:", error);
        throw error;
    }
};

// Fetch column names of a selected dataset
export const fetchDatasetColumns = async (datasetName) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/dataset-columns/${encodeURIComponent(datasetName)}`);
        // Ensure response contains 'columns' array and is not undefined/null
        return response.data.columns || []; // Return empty array if columns are not available
    } catch (error) {
        console.error("Error fetching dataset columns:", error);
        throw error;
    }
};

// Trigger preprocessing before training
export const preprocessDataset = async (data) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/preprocess`, data);
        return response.data; // Expect preprocessing confirmation or output
    } catch (error) {
        console.error("Error preprocessing data:", error);
        throw error;
    }
};

// Train a model with all tuner types in parallel
export const trainModel = async (data) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/train`, data);
        return response.data;
    } catch (error) {
        console.error("Error training model:", error);
        throw error;
    }
};

// Make predictions using the trained model
export const makePrediction = async (data) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/predict`, data);
        return response.data;
    } catch (error) {
        console.error("Error making predictions:", error);
        throw error;
    }
};



// import axios from 'axios';

// // Create an instance of axios with the base URL
// const api = axios.create({
//   baseURL: "http://localhost:8000"
// });

// // Export the Axios instance
// export default api;