// frontend/app/page.tsx

"use client"; // This tells Next.js: "This page has interactivity (buttons/forms)"

import { useState } from "react";
import axios from "axios"; // The messenger library
import { UploadCloud, FileSpreadsheet, Download, CheckCircle, Loader2 } from "lucide-react"; // Icons

export default function Home() {
  // --- STATE VARIABLES (Think of these as your "Memory") ---
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState("idle"); // idle, processing, completed, error
  const [resultUrl, setResultUrl] = useState("");
  const [summary, setSummary] = useState("");

  // --- FUNCTIONS (The Logic) ---
  
  // 1. When user selects a file
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  // 2. When user clicks "Run Analysis"
  const handleUpload = async () => {
    if (!file || !title) {
      alert("Please select a file and give it a title.");
      return;
    }

    setLoading(true);
    setStatus("processing");

    // Prepare the data to send
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);

    try {
      // SEND TO DJANGO (Make sure your backend is running!)
      // here is the line that ensures the backed and front end are communicating. It acts as the waiter in a hotel or restaurant.

      
      // const response = await axios.post("http://127.0.0.1:8000/api/uploads/", formData, {
      //   headers: {
      //     "Content-Type": "multipart/form-data",
      //   },

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
        const response = await axios.post(`${apiUrl}/api/uploads/`, formData,{
         headers: {
           "Content-Type": "multipart/form-data",
        },
    });

      // SUCCESS!
      //here the waiter or the axios brings the result from the kitchen (backend),
      const data = response.data;
      setResultUrl(data.processed_file); // Save the download link
      setSummary(data.message);          // Save the summary text
      setStatus("completed");
      
    } catch (error) {
      console.error(error);
      setStatus("error");
      alert("Upload failed! Is the Django backend running?");
    } finally {
      setLoading(false);
    }
  };

  // --- THE UI (HTML with Tailwind CSS) ---
  return (
    <main className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6">
      
      {/* 1. Header Section */}
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">School Exam Analyzer 🚀</h1>
        <p className="text-slate-600">Upload raw marks, get instant ranked reports.</p>
      </div>

      {/* 2. Main White Card */}
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-slate-100">
        
        {/* Title Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1">Exam Title</label>
          <input 
            type="text" 
            placeholder="e.g. Class 8 Term 1" 
            className="w-full p-3 border border-slate-300 rounded-lg text-black focus:ring-2 focus:ring-blue-500 outline-none"
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        {/* File Upload Area */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-1">Upload Excel File</label>
          <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 flex flex-col items-center justify-center hover:bg-slate-50 transition cursor-pointer relative">
            
            {/* The hidden HTML file input */}
            <input 
              type="file" 
              accept=".xlsx, .csv"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              onChange={handleFileChange}
            />
            
            {/* What the user actually sees */}
            {file ? (
              <div className="flex items-center text-blue-600 font-medium">
                <FileSpreadsheet className="mr-2 h-6 w-6" />
                {file.name}
              </div>
            ) : (
              <div className="flex flex-col items-center text-slate-400">
                <UploadCloud className="h-10 w-10 mb-2" />
                <span className="text-sm">Click to upload (.xlsx)</span>
              </div>
            )}
          </div>
        </div>

        {/* The Action Button */}
        <button 
          onClick={handleUpload}
          disabled={loading}
          className={`w-full py-3 rounded-lg font-bold text-white transition flex items-center justify-center
            ${loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/30'}
          `}
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Analyzing...
            </>
          ) : (
            "Run Analysis"
          )}
        </button>

        {/* 3. Success & Download Section */}
        {status === "completed" && (
          <div className="mt-8 p-4 bg-green-50 border border-green-200 rounded-xl">
            <div className="flex items-center text-green-700 font-bold mb-2">
              <CheckCircle className="mr-2 h-5 w-5" /> Analysis Complete!
            </div>
            
            <p className="text-sm text-green-800 whitespace-pre-line mb-4 border-l-4 border-green-500 pl-2 bg-green-100/50 p-2 rounded">
              {summary}
            </p>

            <a 
              href={resultUrl} 
              className="block w-full py-3 bg-green-600 hover:bg-green-700 text-white text-center font-bold rounded-lg shadow-md transition flex items-center justify-center"
            >
              <Download className="mr-2 h-5 w-5" /> Download Report
            </a>
          </div>
        )}
      </div>
    </main>
  );
}