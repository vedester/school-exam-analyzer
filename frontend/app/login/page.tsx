"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
// 1. Import isAxiosError for safe type checking (optional but good practice)
import { isAxiosError } from "axios"; 
import api from "@/lib/api"; 
import { Lock, User, LogIn, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await api.post("/api/auth/token/", { username, password });
      
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      
      router.push("/");
      
    } catch (err: unknown) { // <--- 2. CHANGED 'any' TO 'unknown'
      
      // 3. Optional: Use type guard if you want to log specific details
      if (isAxiosError(err)) {
        console.error("Login failed:", err.response?.data);
      } else {
        console.error("Unexpected error:", err);
      }

      setError("Invalid Username or Password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-slate-100">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-800">Welcome Back</h1>
          <p className="text-slate-500 mt-2">Sign in to access your analytics</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-6 flex items-center text-sm">
            <AlertCircle className="w-4 h-4 mr-2" /> {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
              <input 
                className="w-full pl-10 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                placeholder="Enter your username"
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
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
                className="w-full pl-10 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition"
                placeholder="••••••••"
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                required
              />
            </div>
          </div>

          <button 
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition flex items-center justify-center shadow-lg shadow-blue-500/30 disabled:opacity-70"
          >
            {loading ? "Signing in..." : <><LogIn className="w-5 h-5 mr-2"/> Sign In</>}
          </button>
        </form>

        <p className="mt-6 text-center text-slate-600 text-sm">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-blue-600 font-bold hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}