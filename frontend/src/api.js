import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

// Upload a JSON file for a specific project
export const uploadJson = (file, projectName) => {
    const formData = new FormData();
    formData.append("file", file);
    return axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        params: { project_name: projectName },
    });
};

// Fetch available datasets from app/datas
export const fetchDatasets = async () => {
    try {
        const response = await axios.get('http://localhost:8000/datasets');
        return response.data;  // List of datasets from backend
    } catch (error) {
        console.error("Error fetching datasets:", error);
        throw error;
    }
};


// Train a model using a selected dataset
export const trainModel = (data) => {
    return axios.post(`${API_BASE_URL}/train`, data);
};

// Make predictions using the trained model
export const makePrediction = (data) => {
    return axios.post(`${API_BASE_URL}/predict`, data);
};



// import axios from 'axios';

// // Create an instance of axios with the base URL
// const api = axios.create({
//   baseURL: "http://localhost:8000"
// });

// // Export the Axios instance
// export default api;