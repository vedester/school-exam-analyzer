"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { isAxiosError } from "axios";
import api from "@/lib/api"; 
import Image from "next/image"; 
import { 
  UploadCloud, FileSpreadsheet, Download, CheckCircle, Loader2, 
  BarChart3, PieChart, FileArchive, LogOut, Settings, Trash2, Plus, 
  BookOpen, LayoutList
} from "lucide-react";

// --- TYPES ---
interface AnalysisSummary {
  student_count: number;
  class_mean: number;
  pass_rate: number;
  top_student: string;
}

interface ExamResult {
  id: string;
  title: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  message: string;
  processed_file: string | null;
  reports_zip: string | null;
  subject_chart: string | null;
  passrate_chart: string | null;
  analysis_summary: AnalysisSummary;
}

interface GradingRule {
  min: number;
  max: number;
  grade: string;
  remark: string;
  points: number;
}

// --- PRESETS (The "Magic" Buttons) ---

const SCHEME_CBC: GradingRule[] = [
  { min: 80, max: 100, grade: "EE", remark: "Exceeding Expectations", points: 4 },
  { min: 50, max: 79,  grade: "ME", "remark": "Meeting Expectations",   points: 3 },
  { min: 40, max: 49,  grade: "AE", "remark": "Approaching Expectations", points: 2 },
  { min: 0,  max: 39,  grade: "BE", "remark": "Below Expectations",     points: 1 },
];

const SCHEME_844: GradingRule[] = [
  { min: 80, max: 100, grade: "A",  remark: "Excellent", points: 12 },
  { min: 75, max: 79,  grade: "A-", remark: "Excellent", points: 11 },
  { min: 70, max: 74,  grade: "B+", remark: "Very Good", points: 10 },
  { min: 65, max: 69,  grade: "B",  remark: "Good",      points: 9 },
  { min: 60, max: 64,  grade: "B-", remark: "Good",      points: 8 },
  { min: 50, max: 59,  grade: "C+", remark: "Fair",      points: 7 },
  { min: 40, max: 49,  grade: "C",  remark: "Average",   points: 6 },
  { min: 0,  max: 39,  grade: "E",  remark: "Poor",      points: 1 },
];

export default function Home() {
  const router = useRouter();
  
  // --- STATE ---
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState("idle"); 
  const [progressMsg, setProgressMsg] = useState("");
  const [resultData, setResultData] = useState<ExamResult | null>(null);

  // Settings
  const [showSettings, setShowSettings] = useState(false);
  const [ignoreColumns, setIgnoreColumns] = useState(""); 
  const [gradingScheme, setGradingScheme] = useState<GradingRule[]>(SCHEME_CBC);
  const [activePreset, setActivePreset] = useState<"CBC" | "844" | "Custom">("CBC");

  // Auth Check
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) router.push("/login");
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    router.push("/login");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  // --- PRESET HANDLERS ---
  const applyPreset = (type: "CBC" | "844") => {
    setActivePreset(type);
    if (type === "CBC") setGradingScheme(SCHEME_CBC);
    if (type === "844") setGradingScheme(SCHEME_844);
  };

  const updateRule = (index: number, field: keyof GradingRule, value: string | number) => {
    setActivePreset("Custom"); // Switch to custom if they edit
    const newScheme = [...gradingScheme];
    // @ts-expect-error: dynamic assignment
    newScheme[index][field] = value;
    setGradingScheme(newScheme);
  };

  const addRule = () => {
    setActivePreset("Custom");
    setGradingScheme([...gradingScheme, { min: 0, max: 0, grade: "?", remark: "", points: 0 }]);
  };

  const removeRule = (index: number) => {
    setActivePreset("Custom");
    setGradingScheme(gradingScheme.filter((_, i) => i !== index));
  };

  // --- UPLOAD LOGIC ---
  const handleUpload = async () => {
    if (!file || !title) {
      alert("Please select a file and give it a title.");
      return;
    }

    setLoading(true);
    setStatus("processing");
    setProgressMsg("Uploading...");

    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);
    
    if (ignoreColumns) formData.append("custom_ignore_columns", ignoreColumns);
    formData.append("grading_scheme", JSON.stringify(gradingScheme));

    try {
      const response = await api.post<ExamResult>(`/api/analytics/exam-uploads/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      pollStatus(response.data.id);
    } catch (err: unknown) {
      console.error(err);
      setStatus("error");
      setLoading(false);
      if (isAxiosError(err) && err.response?.status === 401) router.push("/login");
      else alert("Upload failed.");
    }
  };

  const pollStatus = async (uuid: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await api.get<ExamResult>(`/api/analytics/exam-uploads/${uuid}/`);
        if (res.data.status === 'COMPLETED') {
          clearInterval(interval);
          setResultData(res.data);
          setStatus("completed");
          setLoading(false);
        } else if (res.data.status === 'FAILED') {
          clearInterval(interval);
          setStatus("error");
          setLoading(false);
          alert(`Error: ${res.data.message}`);
        } else {
          setProgressMsg("Analyzing results...");
        }
      } catch (error) {
        clearInterval(interval);
        setLoading(false);
        setStatus("error");
      }
    }, 2000);
  };

  return (
    <main className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 relative">
      <button onClick={handleLogout} className="absolute top-6 right-6 text-slate-500 hover:text-red-500 flex items-center gap-2">
        <LogOut className="w-4 h-4" /> Logout
      </button>

      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Kenya School Analytics 🇰🇪</h1>
        <p className="text-slate-600">Upload marks, get Broadsheets & Report Cards automatically.</p>
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-3xl border border-slate-100">
        
        {/* TOP FORM */}
        <div className="space-y-6">
          
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Exam Title</label>
            <input 
              type="text" 
              placeholder="e.g. Grade 7 Term 1 2024" 
              className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-black"
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          {/* ADVANCED SETTINGS TOGGLE */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <button 
              onClick={() => setShowSettings(!showSettings)}
              className="flex items-center w-full justify-between text-sm font-semibold text-slate-700"
            >
              <div className="flex items-center">
                <Settings className="w-4 h-4 mr-2 text-blue-600" />
                Configure Grading & Columns
              </div>
              <span className="text-blue-600">{showSettings ? "Hide" : "Show"}</span>
            </button>

            {showSettings && (
              <div className="mt-4 pt-4 border-t border-slate-200 space-y-6 animate-in fade-in">
                
                {/* 1. GRADING SYSTEM SELECTOR */}
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Grading System</label>
                  <div className="flex gap-3 mb-4">
                    <button 
                      onClick={() => applyPreset("CBC")}
                      className={`flex-1 py-2 px-3 rounded-lg border text-sm font-medium transition flex items-center justify-center gap-2
                        ${activePreset === "CBC" ? "bg-blue-600 text-white border-blue-600" : "bg-white text-slate-600 hover:bg-slate-50"}
                      `}
                    >
                      <BookOpen className="w-4 h-4" /> CBC (Junior School)
                    </button>
                    
                    <button 
                      onClick={() => applyPreset("844")}
                      className={`flex-1 py-2 px-3 rounded-lg border text-sm font-medium transition flex items-center justify-center gap-2
                        ${activePreset === "844" ? "bg-blue-600 text-white border-blue-600" : "bg-white text-slate-600 hover:bg-slate-50"}
                      `}
                    >
                      <LayoutList className="w-4 h-4" /> 8-4-4 (Primary)
                    </button>
                  </div>

                  {/* EDITABLE TABLE */}
                  <div className="overflow-hidden rounded-lg border border-slate-200">
                    <table className="w-full text-sm text-left">
                      <thead className="bg-slate-100 text-xs uppercase text-slate-500 font-semibold">
                        <tr>
                          <th className="px-3 py-2">Min %</th>
                          <th className="px-3 py-2">Max %</th>
                          <th className="px-3 py-2">Grade</th>
                          <th className="px-3 py-2">Remark</th>
                          <th className="px-3 py-2 text-center">Del</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 bg-white">
                        {gradingScheme.map((rule, idx) => (
                          <tr key={idx} className="hover:bg-slate-50">
                            <td className="p-2">
                              <input type="number" value={rule.min} onChange={(e) => updateRule(idx, 'min', Number(e.target.value))} className="w-14 p-1 border rounded text-center"/>
                            </td>
                            <td className="p-2">
                              <input type="number" value={rule.max} onChange={(e) => updateRule(idx, 'max', Number(e.target.value))} className="w-14 p-1 border rounded text-center"/>
                            </td>
                            <td className="p-2">
                              <input type="text" value={rule.grade} onChange={(e) => updateRule(idx, 'grade', e.target.value)} className="w-16 p-1 border rounded text-center font-bold text-blue-700"/>
                            </td>
                            <td className="p-2">
                              <input type="text" value={rule.remark} onChange={(e) => updateRule(idx, 'remark', e.target.value)} className="w-full p-1 border rounded"/>
                            </td>
                            <td className="p-2 text-center">
                              <button onClick={() => removeRule(idx)} className="text-red-400 hover:text-red-600"><Trash2 className="w-4 h-4" /></button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <button onClick={addRule} className="w-full py-2 bg-slate-50 text-slate-500 text-xs font-bold hover:bg-slate-100 flex items-center justify-center gap-1 border-t border-slate-200">
                      <Plus className="w-3 h-3"/> Add Grading Rule
                    </button>
                  </div>
                </div>

                {/* 2. IGNORE COLUMNS */}
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Exclude Non-Subject Columns</label>
                  <p className="text-xs text-slate-400 mb-2">Does your Excel file have Fees, UPI, or Phone numbers? List them here so they don&apos;t get graded.</p>
                  <input 
                    type="text" 
                    placeholder="e.g. UPI, Fees Balance, Phone Number"
                    value={ignoreColumns}
                    onChange={(e) => setIgnoreColumns(e.target.value)}
                    className="w-full p-3 border border-slate-300 rounded-lg text-sm text-black placeholder:text-slate-400"
                  />
                </div>

              </div>
            )}
          </div>

          {/* UPLOAD AREA */}
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-1">Select Excel File</label>
            <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 flex flex-col items-center justify-center hover:bg-blue-50 hover:border-blue-400 transition cursor-pointer relative group">
              <input 
                type="file" 
                accept=".xlsx, .csv"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={handleFileChange}
              />
              
              {file ? (
                <div className="flex flex-col items-center text-blue-600">
                  <FileSpreadsheet className="h-10 w-10 mb-2" />
                  <span className="font-semibold">{file.name}</span>
                  <span className="text-xs text-blue-400 mt-1">Click to change</span>
                </div>
              ) : (
                <div className="flex flex-col items-center text-slate-400 group-hover:text-blue-500">
                  <UploadCloud className="h-10 w-10 mb-2" />
                  <span className="font-medium">Click to upload marksheet (.xlsx)</span>
                </div>
              )}
            </div>
          </div>

          <button 
            onClick={handleUpload}
            disabled={loading}
            className={`w-full py-4 rounded-xl font-bold text-white text-lg shadow-lg transition flex items-center justify-center
              ${loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-blue-500/30'}
            `}
          >
            {loading ? <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> {progressMsg}</> : "Start Analysis 🚀"}
          </button>
        </div>

        {/* RESULTS SECTION */}
        {status === "completed" && resultData && (
          <div className="mt-10 pt-10 border-t-2 border-dashed border-slate-200 animate-in fade-in slide-in-from-bottom-4">
            
            <div className="flex items-center justify-center text-green-600 font-bold mb-6 text-2xl">
              <CheckCircle className="mr-2 h-8 w-8" /> Analysis Complete!
            </div>
            
            {/* KPI CARDS */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-blue-50 p-4 rounded-xl text-center border border-blue-100">
                <div className="text-xs text-blue-500 uppercase font-bold tracking-wider">Class Mean</div>
                <div className="text-3xl font-extrabold text-blue-700">{resultData.analysis_summary?.class_mean}</div>
              </div>
              <div className="bg-green-50 p-4 rounded-xl text-center border border-green-100">
                <div className="text-xs text-green-500 uppercase font-bold tracking-wider">Pass Rate</div>
                <div className="text-3xl font-extrabold text-green-700">{resultData.analysis_summary?.pass_rate}%</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-xl text-center border border-purple-100">
                <div className="text-xs text-purple-500 uppercase font-bold tracking-wider">Top Student</div>
                <div className="text-xl font-bold text-purple-700 truncate px-2">{resultData.analysis_summary?.top_student}</div>
              </div>
            </div>

            {/* CHARTS */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {resultData.subject_chart && (
                <div className="bg-white border rounded-xl shadow-sm overflow-hidden p-4">
                  <h3 className="text-sm font-bold text-slate-700 mb-2 flex items-center"><BarChart3 className="w-4 h-4 mr-2"/> Subject Performance</h3>
                  <div className="relative h-64 w-full">
                    <Image src={resultData.subject_chart} alt="Subject Chart" fill className="object-contain" unoptimized />
                  </div>
                </div>
              )}
              {resultData.passrate_chart && (
                <div className="bg-white border rounded-xl shadow-sm overflow-hidden p-4">
                  <h3 className="text-sm font-bold text-slate-700 mb-2 flex items-center"><PieChart className="w-4 h-4 mr-2"/> Pass Rate</h3>
                  <div className="relative h-64 w-full">
                    <Image src={resultData.passrate_chart} alt="Pass Rate" fill className="object-contain" unoptimized />
                  </div>
                </div>
              )}
            </div>
            
            {/* DOWNLOADS */}
            <div className="grid grid-cols-1 gap-4">
              {resultData.processed_file && (
                <a href={resultData.processed_file} className="flex items-center justify-center w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white text-lg font-bold rounded-xl shadow-md transition hover:scale-[1.01]">
                  <Download className="mr-2 h-6 w-6" /> Download Broadsheet (Excel)
                </a>
              )}
              {resultData.reports_zip && (
                <a href={resultData.reports_zip} className="flex items-center justify-center w-full py-4 bg-blue-600 hover:bg-blue-700 text-white text-lg font-bold rounded-xl shadow-md transition hover:scale-[1.01]">
                  <FileArchive className="mr-2 h-6 w-6" /> Download Report Cards (PDF)
                </a>
              )}
            </div>
          </div>
        )}

      </div>
    </main>
  );
}