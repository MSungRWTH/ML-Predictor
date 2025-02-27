import axios from 'axios';

// Set the base URL for the API
const api = axios.create({
  baseURL: 'http://localhost:8000', // Ensure this points to your FastAPI backend
});

// Fetch files from the backend
export const fetchFiles = async () => {
  try {
    const response = await api.get('/files/');
    return response.data;
  } catch (error) {
    console.error('Error fetching files:', error);
    throw error;  // Propagate the error to the calling function
  }
};

// Upload a file to the backend
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data', // Required for file uploads
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;  // Propagate the error to the calling function
  }
};
