// src/components/document/DocumentsPanel.tsx
import React, { useState } from 'react';
import useStore from '../../store/useStore';
import { Upload, File } from 'lucide-react';
import socketService from '../../services/socketService';

const DocumentsPanel: React.FC = () => {
  const documents = useStore((state) => state.room?.documents);
  const roomName = useStore((state) => state.room?.name);
  const [isUploading, setIsUploading] = useState(false);
  // const currentUser = useStore((state) => state.currentUser);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && roomName) {
      // Check file size before upload
      const maxSize = 100 * 1024 * 1024; // 100MB
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
      
      if (file.size > maxSize) {
        alert(`File too large. Maximum size is 100MB, got ${fileSizeMB}MB`);
        return;
      }
      
      setIsUploading(true);
      try {
        await socketService.uploadFile(file, roomName);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        alert(`Upload failed: ${errorMessage}`);
      } finally {
        setIsUploading(false);
      }
    }
    
    // Clear the input so the same file can be selected again
    event.target.value = '';
  };

  const handleUploadClick = () => {
    document.getElementById('file-upload')?.click();
  };
  
  const handleSetView = (docId: number) => {
    socketService.setView(docId, 0);
  };

  return (
    <div className="h-full p-4 flex flex-col">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Documents</h2>
        <input
          type="file"
          id="file-upload"
          className="hidden"
          onChange={handleFileChange}
          accept=".pdf"
          title="Select PDF file (max 100MB)"
        />
        <button
          onClick={handleUploadClick}
          disabled={isUploading}
          className={`w-full flex flex-col items-center justify-center p-2.5 rounded-lg transition-colors ${
            isUploading 
              ? 'bg-gray-400 text-gray-200 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isUploading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              <span className="font-medium">Uploading...</span>
            </div>
          ) : (
            <>
              <div className="flex items-center">
                <Upload className="w-5 h-5 mr-2" />
                <span className="font-medium">Upload PDF</span>
              </div>
              <span className="text-xs mt-1 opacity-90">(Max 100MB)</span>
            </>
          )}
        </button>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Room's Files</h2>
        {!documents ? (
          <p className="text-sm text-slate-500">Loading...</p>
        ) : documents.length === 0 ? (
          <p className="text-sm text-slate-500">No documents uploaded yet.</p>
        ) : (
          <ul className="space-y-1">
            {documents.map((file) => (
              <li
                key={file.id}
                onClick={() => handleSetView(file.id)}
                className="flex items-center p-2.5 rounded-lg space-x-3 hover:bg-slate-50 cursor-pointer group"
              >
                <div className="p-2 rounded-lg bg-slate-100 group-hover:bg-slate-200">
                  <File className="w-5 h-5 text-slate-500" />
                </div>
                <span className="text-sm font-medium text-slate-700">{file.name}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default DocumentsPanel;