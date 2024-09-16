import React from 'react';

function UploadComponent({ onClose, onFileChange, onUpload }) {
  return (
    <div className="upload-component fixed top-0 left-0 right-0 bottom-0 flex justify-center items-center bg-gray-800 bg-opacity-50 z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg relative">
        <button
          className="absolute top-3 right-4 text-gray-600 hover:text-gray-900"
          onClick={onClose}
        >
          <i className="fas fa-times"></i> {/* Font Awesome close icon */}
        </button>
        <h2 className="text-2xl font-bold mb-4">Upload Files</h2> {/* Changed to plural */}
        <div className="mb-4">
          <input
            type="file"
            id="fileInput"
            accept=".jpg, .jpeg, .png, .pdf"
            className="border border-gray-300 p-2 w-full"
            multiple  // Allows selecting multiple files
            onChange={onFileChange}
          />
        </div>
        <div className="flex justify-center">
          <button 
            className="bg-[#FE2C2B] text-white py-2 px-4 rounded-md hover:bg-[#e02c2b]"
            onClick={onUpload}
          >
            Upload
          </button>
        </div>
      </div>
    </div>
  );
}

export default UploadComponent;
