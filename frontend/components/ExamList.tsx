"use client";

import { useEffect, useState, useCallback } from "react";
import api from "@/lib/api";
import { FileText, Calendar, ChevronRight, TrendingUp, Loader2, Trash2 } from "lucide-react";

// --- TYPES (Matching page.tsx to avoid errors) ---
interface AnalysisSummary {
  student_count: number;
  class_mean: number;
  pass_rate: number;
  top_student: string;
}

// Important: This interface matches page.tsx structure so we can pass it back
export interface ExamResult {
  id: string;
  title: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'; 
  message: string;
  uploaded_at: string;
  analysis_summary: AnalysisSummary;
  // These fields come from the backend but might be null
  processed_file: string | null;
  reports_zip: string | null;
  subject_chart: string | null;
  passrate_chart: string | null;
}

interface ExamListProps {
  onSelectExam: (exam: ExamResult) => void; 
  refreshTrigger: number;
}

export default function ExamList({ onSelectExam, refreshTrigger }: ExamListProps) {
  const [exams, setExams] = useState<ExamResult[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchExams = useCallback(async () => {
    try {
      // Don't show loading spinner if it's just a background refresh (trigger > 0)
      if (refreshTrigger === 0) setLoading(true); 
      
      const res = await api.get<ExamResult[]>("/api/analytics/exam-uploads/");
      setExams(res.data);
    } catch (error) {
      console.error("Failed to fetch exams", error);
    } finally {
      setLoading(false);
    }
  }, [refreshTrigger]);

  useEffect(() => {
    fetchExams();
  }, [fetchExams]); 

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Stop the click from opening the exam details
    if (!confirm("Are you sure you want to delete this exam record?")) return;
    
    try {
      await api.delete(`/api/analytics/exam-uploads/${id}/`);
      // Update UI immediately (Optimistic update)
      setExams(prev => prev.filter(ex => ex.id !== id));
    } catch (error) {
      console.error("Failed to delete exam", error);
      alert("Failed to delete. Please try again.");
    }
  };

  if (loading && exams.length === 0) {
    return <div className="flex justify-center p-8 text-slate-400"><Loader2 className="animate-spin" /></div>;
  }

  if (exams.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 text-center">
        <p className="text-slate-500 text-sm">No recent exams found.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden sticky top-6">
      <div className="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
        <h3 className="font-bold text-slate-700 flex items-center text-sm uppercase tracking-wide">
          <FileText className="w-4 h-4 mr-2" /> History
        </h3>
      </div>
      
      <div className="divide-y divide-slate-100 max-h-[calc(100vh-200px)] overflow-y-auto">
        {exams.map((exam) => (
          <div 
            key={exam.id}
            onClick={() => onSelectExam(exam)}
            className="p-4 hover:bg-blue-50 transition cursor-pointer flex justify-between items-center group relative"
          >
            <div className="flex-1 min-w-0 pr-4">
              <h4 className="font-semibold text-slate-800 text-sm truncate">{exam.title}</h4>
              <div className="flex flex-wrap gap-2 mt-2 text-xs text-slate-500">
                <span className="flex items-center">
                  <Calendar className="w-3 h-3 mr-1" />
                  {new Date(exam.uploaded_at).toLocaleDateString()}
                </span>
                
                {exam.analysis_summary?.class_mean > 0 && (
                  <span className="flex items-center text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full font-bold">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {exam.analysis_summary.class_mean}
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
               {/* Status Dot */}
               <div className={`w-2 h-2 rounded-full ${
                 exam.status === 'COMPLETED' ? 'bg-green-500' : 
                 exam.status === 'FAILED' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
               }`} />
               
               {/* Delete Button (Visible on Hover) */}
               <button 
                onClick={(e) => handleDelete(exam.id, e)}
                className="p-1.5 text-slate-300 hover:text-red-600 hover:bg-red-50 rounded-full transition opacity-0 group-hover:opacity-100"
                title="Delete"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              
              <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-blue-500" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}