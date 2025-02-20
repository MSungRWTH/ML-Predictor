import React, { useState } from "react";
import axios from "axios";

const Upload = () => {
    const [file, setFile] = useState(null);

    const handleUpload = async () => {
        if (!file) {
            alert("Please select a file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);  // Make sure 'file' is being appended properly

        try {
            const res = await axios.post("http://localhost:8000/upload/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",  // Ensure the correct content type is set
                },
            });
            alert(res.data.message);  // Show success message
        } catch (error) {
            console.error("Error uploading file:", error);
            alert("File upload failed. Please try again.");
        }
    };

    return (
        <div>
            <h2>Upload JSON/CSV File</h2>
            <input
                type="file"
                accept=".json, .csv"  // Limit file types to JSON and CSV
                onChange={(e) => setFile(e.target.files[0])}
            />
            <button onClick={handleUpload}>Upload</button>
        </div>
    );
};

export default Upload;


