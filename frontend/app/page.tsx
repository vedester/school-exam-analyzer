"use client";

import { useState } from "react";
// 1. IMPORT isAxiosError helper
import axios, { isAxiosError } from "axios";
import Image from "next/image"; 
import { UploadCloud, FileSpreadsheet, Download, CheckCircle, Loader2, BarChart3, PieChart, FileArchive } from "lucide-react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState("idle"); 
  const [resultUrl, setResultUrl] = useState("");
  const [summary, setSummary] = useState("");

  const [subjectChartUrl, setSubjectChartUrl] = useState("");
  const [passRateChartUrl, setPassRateChartUrl] = useState("");

  const [zipUrl, setZipUrl] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !title) {
      alert("Please select a file and give it a title.");
      return;
    }

    setLoading(true);
    setStatus("processing");

    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      
      const response = await axios.post(`${apiUrl}/api/uploads/`, formData);

      const data = response.data;
      
      setResultUrl(data.processed_file); 
      setZipUrl(data.reports_zip); // <--- Save the backend PDF link
      setSummary(data.message);
      setSubjectChartUrl(data.subject_chart);
      setPassRateChartUrl(data.passrate_chart);
      setStatus("completed");
      
    } catch (err) {
      console.error("Full Error:", err);
      
      // 2. USE TYPE GUARD instead of 'any'
      if (isAxiosError(err) && err.response && err.response.data) {
        // Now TypeScript knows 'err' is an AxiosError with a response
        alert(`Server Error: ${JSON.stringify(err.response.data)}`);
      } else {
        alert("Upload failed! Is the backend running?");
      }
      
      setStatus("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6">
      
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">School Exam Analyzer 🚀</h1>
        <p className="text-slate-600">Upload raw marks, get instant ranked reports & visualizations.</p>
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-2xl border border-slate-100">
        
        <div className="mb-8">
            <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-1">Exam Title</label>
            <input 
                type="text" 
                placeholder="e.g. Class 8 Term 1" 
                className="w-full p-3 border border-slate-300 rounded-lg text-black focus:ring-2 focus:ring-blue-500 outline-none"
                onChange={(e) => setTitle(e.target.value)}
            />
            </div>

            <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-1">Upload Excel File</label>
            <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 flex flex-col items-center justify-center hover:bg-slate-50 transition cursor-pointer relative">
                <input 
                type="file" 
                accept=".xlsx, .csv"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={handleFileChange}
                />
                
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
        </div>

        {status === "completed" && (
          <div className="mt-8 pt-8 border-t border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            <div className="flex items-center text-green-700 font-bold mb-4 text-xl">
              <CheckCircle className="mr-2 h-6 w-6" /> Analysis Complete!
            </div>
            
            <p className="text-sm text-slate-600 mb-6 bg-slate-50 p-3 rounded-lg border border-slate-200 whitespace-pre-line">
              {summary}
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {subjectChartUrl && (
                    <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
                        <div className="bg-slate-50 px-4 py-2 border-b flex items-center text-sm font-semibold text-slate-700">
                            <BarChart3 className="w-4 h-4 mr-2" /> Subject Performance
                        </div>
                        <div className="p-2">
                            <Image 
                              src={subjectChartUrl} 
                              alt="Subject Performance" 
                              width={500} 
                              height={300} 
                              className="w-full h-auto rounded" 

                              unoptimized
                            />
                        </div>
                    </div>
                )}

                {passRateChartUrl && (
                    <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
                        <div className="bg-slate-50 px-4 py-2 border-b flex items-center text-sm font-semibold text-slate-700">
                            <PieChart className="w-4 h-4 mr-2" /> Pass Rate
                        </div>
                        <div className="p-2">
                            <Image 
                              src={passRateChartUrl} 
                              alt="Pass Rate" 
                              width={500} 
                              height={300} 
                              className="w-full h-auto rounded" 
                              unoptimized
                            />
                        </div>
                    </div>
                )}
            </div>
                {/* Download Buttons Grid */}
            <div className="grid grid-cols-1 gap-4">
                <a 
                  href={resultUrl} 
                  className="block w-full py-4 bg-green-600 hover:bg-green-700 text-white text-lg text-center font-bold rounded-xl shadow-md transition flex items-center justify-center hover:scale-[1.02] transform duration-200"
                >
                  <Download className="mr-2 h-6 w-6" /> Download Excel Report
                </a>

                {zipUrl && (
                    <a 
                      href={zipUrl} 
                      className="block w-full py-4 bg-blue-600 hover:bg-blue-700 text-white text-lg text-center font-bold rounded-xl shadow-md transition flex items-center justify-center hover:scale-[1.02] transform duration-200"
                    >
                      <FileArchive className="mr-2 h-6 w-6" /> Download PDF Report Cards
                    </a>
                )}
            </div>
         
          </div>
        )}

        {status === "error" && (
          <div className="mt-8 pt-8 border-t border-slate-100 text-red-600 font-bold text-center">
            ❌ An error occurred during analysis. Please try again.
          </div>
        )}
      </div>
    </main>
  );
}