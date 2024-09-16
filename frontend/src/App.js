import React, { useState } from 'react';
import './App.css';
import Navbar from './layouts/navbar';
import UploadComponent from './components/UploadComponent.jsx';

function App() {
  const [isUploadVisible, setUploadVisible] = useState(false);
  const [files, setFiles] = useState([]); // To store multiple files
  const [filePreview, setFilePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleUploadClick = () => {
    setUploadVisible(true);
  };

  const handleCloseUpload = () => {
    setUploadVisible(false);
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);  // Store multiple files
    console.log("Selected files:", selectedFiles); // Keep this log for debugging

    if (selectedFiles.length > 0) {
      setFiles(selectedFiles); // Update state with the selected files

      // Create a URL for preview of the first file
      const fileUrl = URL.createObjectURL(selectedFiles[0]);
      setFilePreview(fileUrl);
    } else {
      setFiles([]);
      setFilePreview(null);
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    const formData = new FormData();

    // Append each file to the FormData
    files.forEach((file, i) => {
      formData.append('file', file);
    });

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'invoice_data.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        setUploadVisible(false);
        setSuccessMessage('Files processed successfully. Download started.');
      } else {
        throw new Error('Upload failed.');
      }
    } catch (error) {
      setError('Error uploading files. Please try again.');
      console.error('Error uploading files:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Navbar />
      <div className="cta-section-1 w-auto h-full">
        <div className="flex justify-center items-center h-[40vh]">
          <div>
            <h1 className="text-[#FE2C2B] text-[48px] leading-[72px] font-[700]">
              Invoice Bill Data Extractor
            </h1>
            <p className="text-center text-[24px] leading-[36px] font-[400] mt-2">
              Upload image or PDF here
            </p>
          </div>
        </div>
      </div>

      <div
        className="cta-section-2 relative w-full h-[50vh]"
        style={{
          borderRadius: "32px 32px 0 0",
          boxShadow: "0 -4px 8px rgba(0, 0, 0, 0.5)",
        }}
      >
        <button
          className="absolute top-[-10%] lg:left-[44%] md:left-[40%] left-[35%] text-white text-[24px] leading-[36px] font-[400] w-[180px] h-[60px] bg-[#FE2C2B]"
          style={{ borderRadius: "24px" }}
          onClick={handleUploadClick}
        >
          Upload
        </button>
        <div className="flex justify-around items-center">
          {loading && <p>Loading...</p>}
          {error && <p className="text-red-500">{error}</p>}
        </div>
      </div>

      {isUploadVisible && (
        <UploadComponent
          onClose={handleCloseUpload}
          onFileChange={handleFileChange}
          onUpload={handleUpload}
        />
      )}

      <div className="flex justify-around items-center">
        {loading && <p>Loading...</p>}
        {error && <p className="text-red-500">{error}</p>}
        {successMessage && <p className="text-green-500">{successMessage}</p>}
      </div>
      
      {filePreview && (
        <div className="preview-section flex justify-center items-center my-4">
          {files[0] && files[0].type.startsWith("image/") ? (
            <img src={filePreview} alt="Preview" className="w-[300px] h-auto" />
          ) : files[0] && files[0].type === "application/pdf" ? (
            <iframe
              src={filePreview}
              title="PDF Preview"
              className="w-[300px] h-[400px]"
            />
          ) : (
            <p>No preview available</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
