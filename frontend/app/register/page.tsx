"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
// 1. Import isAxiosError for safe type checking (optional but good practice)
import { isAxiosError } from "axios"; 
import api from "@/lib/api"; 
import { Lock, User, Mail, CheckCircle, AlertCircle } from "lucide-react";

export default function RegisterPage() {
  const [formData, setFormData] = useState({ username: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // 1. Call the Registration Endpoint
      await api.post("/api/analytics/register/", formData);
      
      // 2. If successful, redirect to login
      alert("Account created successfully! Please login.");
      router.push("/login");
     
      // 3. Safe Type Guard 
    } catch (err: unknown) { // <--- 2. CHANGED 'any' TO 'unknown'
      if (isAxiosError(err) && err.response?.data) {
        const data = err.response.data as {username?: string[]};
        // 4. Handle specific error messages
        if (data.username){
            setError("Username already taken.");
                
        } else {
            setError("Registration failed. Please try again.");
        }
      }else {
            setError("Unexpected error occurred.Please check your connection.");
            console.error("Unexpected error:", err);
      }
        } finally {
        setLoading(false);
        }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-slate-100">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-800">Create Account</h1>
          <p className="text-slate-500 mt-2">Join to start analyzing exams</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-6 flex items-center text-sm">
            <AlertCircle className="w-4 h-4 mr-2" /> {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
              <input 
                className="w-full pl-10 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none transition"
                placeholder="Choose a username"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
              <input 
                type="email"
                className="w-full pl-10 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none transition"
                placeholder="teacher@school.com"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
              <input 
                type="password"
                className="w-full pl-10 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none transition"
                placeholder="Choose a strong password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
              />
            </div>
          </div>

          <button 
            disabled={loading}
            className="w-full bg-emerald-600 text-white py-3 rounded-lg font-bold hover:bg-emerald-700 transition flex items-center justify-center shadow-lg shadow-emerald-500/30 disabled:opacity-70"
          >
            {loading ? "Creating Account..." : <><CheckCircle className="w-5 h-5 mr-2"/> Register</>}
          </button>
        </form>

        <p className="mt-6 text-center text-slate-600 text-sm">
          Already have an account?{" "}
          <Link href="/login" className="text-emerald-600 font-bold hover:underline">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}