import React, { useState, useEffect } from "react";
import axios from "axios";

const Upload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState([]); // Available files in UPLOAD_DIRECTORY
  const [selectedFile, setSelectedFile] = useState(""); // File user selects
  const [columns, setColumns] = useState([]); // File columns for input/output selection
  const [inputParams, setInputParams] = useState([]); // Selected input parameters
  const [outputParams, setOutputParams] = useState([]); // Selected output parameters
  const [projectName, setProjectName] = useState(""); // Project name
  const [scalerType, setScalerType] = useState(""); // Selected scaler type (StandardScaler or MinMaxScaler)

  // Fetch available files from UPLOAD_DIRECTORY
  useEffect(() => {
    axios
      .get("http://localhost:8000/upload/files/")
      .then((res) => {
        console.log("Fetched files:", res.data);
        if (Array.isArray(res.data)) {
          setFiles(res.data); // Set the files array directly
        } else {
          console.error("Unexpected response structure", res.data);
          setFiles([]); // Fallback to empty array if data is incorrect
        }
      })
      .catch((err) => {
        console.error("Error fetching files:", err);
        setFiles([]); // Fallback to empty array on error
      });
  }, []);

  // Fetch columns from the selected file
  const fetchColumns = async (fileName) => {
    if (!fileName) return;
    setSelectedFile(fileName);
    try {
      const res = await axios.get(
        `http://localhost:8000/upload/get_columns/?file_name=${fileName}`
      );
      setColumns(res.data.columns || []); // Ensure columns is always an array
    } catch (error) {
      console.error("Error fetching columns:", error);
      setColumns([]); // Set empty array in case of error
    }
  };

  // Handle parameter selection (checkboxes)
  const handleParamSelection = (param, type) => {
    if (type === "input") {
      setInputParams((prev) =>
        prev.includes(param) ? prev.filter((p) => p !== param) : [...prev, param]
      );
    } else {
      setOutputParams((prev) =>
        prev.includes(param) ? prev.filter((p) => p !== param) : [...prev, param]
      );
    }
  };

  // Handle scaler type selection
  const handleScalerSelection = (e) => {
    setScalerType(e.target.value);
  };

  // Save selected parameters
  const handleSaveParams = async () => {
    if (!selectedFile || !projectName || inputParams.length === 0 || outputParams.length === 0 || !scalerType) {
      alert("Please fill all fields.");
      return;
    }

    const requestData = {
      project_name: projectName,
      input_params: inputParams,
      output_params: outputParams,
      file_name: selectedFile,
      scaler_type: scalerType, // Include selected scaler type
    };

    try {
      console.log("Sending request with data:", requestData); // Log the data being sent
      await axios.post("http://localhost:8000/upload/save_params/", requestData, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      alert("Parameters saved successfully!");
    } catch (error) {
      console.error("Error saving parameters:", error.response ? error.response.data : error);
      alert("Error saving parameters. Please try again.");
    }
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploading(true);
      const response = await axios.post("http://localhost:8000/upload/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setUploading(false);
      setMessage(response.data.message);
    } catch (error) {
      console.error("Error uploading file:", error);
      setUploading(false);
      setMessage("Upload failed. Please try again.");
    }
  };

  // Trigger preprocessing
  const handlePreprocess = async () => {
    if (!selectedFile || !projectName || inputParams.length === 0 || outputParams.length === 0 || !scalerType) {
      alert("Please fill all fields and select a scaler.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/upload/preprocess/", {
        file_name: selectedFile,
        input_params: inputParams,
        output_params: outputParams,
        scaler_type: scalerType,
        project_name: projectName,
      });

      setMessage(response.data.message);
      alert("Preprocessing completed!");
    } catch (error) {
      console.error("Error preprocessing data:", error);
      setMessage("Preprocessing failed. Please try again.");
    }
  };

  return (
    <div className="container mx-auto p-4 bg-gray-50 rounded-lg shadow-md">
      <h2 className="text-3xl font-semibold text-center mb-6">Upload JSON/CSV File</h2>

      {/* File upload section */}
      <div className="mb-4">
        <input
          type="file"
          accept=".json, .csv"
          onChange={(e) => setFile(e.target.files[0])}
          className="block w-full px-4 py-2 mb-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        {file && <p className="text-gray-600">Selected File: {file.name}</p>}
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 focus:outline-none disabled:bg-gray-400"
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
        {message && <p className="mt-2 text-gray-600">{message}</p>}
      </div>

      {/* Select existing file */}
      <div className="mb-6">
        <label className="block text-lg font-medium mb-2">Select Existing File</label>
        <select
          onChange={(e) => fetchColumns(e.target.value)}
          disabled={files.length === 0}
          value={selectedFile}
          className="block w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">-- Select a file --</option>
          {files.length > 0 ? (
            files.map((f, index) => <option key={index} value={f}>{f}</option>)
          ) : (
            <option disabled>No files available</option>
          )}
        </select>
      </div>

      {/* File column options */}
      {columns.length > 0 && (
        <div className="space-y-6">
          {/* Project name input */}
          <div>
            <label className="block text-lg font-medium mb-2">Define Project</label>
            <input
              type="text"
              placeholder="Enter project name"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="block w-full px-4 py-2 mb-4 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          {/* Input parameters */}
          <div>
            <label className="block text-lg font-medium mb-2">Select Input Parameters</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {columns.map((col) => (
                <label key={col} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={inputParams.includes(col)}
                    onChange={() => handleParamSelection(col, "input")}
                    className="mr-2"
                  />
                  {col}
                </label>
              ))}
            </div>
          </div>

          {/* Output parameters */}
          <div>
            <label className="block text-lg font-medium mb-2">Select Output Parameters</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {columns.map((col) => (
                <label key={col} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={outputParams.includes(col)}
                    onChange={() => handleParamSelection(col, "output")}
                    className="mr-2"
                  />
                  {col}
                </label>
              ))}
            </div>
          </div>

          {/* Scaler selection */}
          <div>
            <label className="block text-lg font-medium mb-2">Select Scaler Type</label>
            <select
              onChange={handleScalerSelection}
              value={scalerType}
              className="block w-full px-4 py-2 mb-4 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option value="">-- Select Scaler Type --</option>
              <option value="StandardScaler">StandardScaler</option>
              <option value="MinMaxScaler">MinMaxScaler</option>
            </select>
          </div>

          {/* Save Parameters and Preprocess buttons */}
          <div className="flex space-x-4">
            <button
              onClick={handleSaveParams}
              className="w-full bg-green-500 text-white py-2 rounded-md hover:bg-green-600 focus:outline-none"
            >
              Save Parameters
            </button>
            <button
              onClick={handlePreprocess}
              className="w-full bg-yellow-500 text-white py-2 rounded-md hover:bg-yellow-600 focus:outline-none"
            >
              Preprocess Data
            </button>
          </div>
        </div>
      )}
      {columns.length === 0 && files.length > 0 && <p className="mt-4 text-gray-600">Loading columns...</p>}
    </div>
  );
};

export default Upload;
