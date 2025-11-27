// frontend/app/login/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api"; 
import { Lock, User } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // The backend endpoint we set up earlier
      const res = await api.post("/api/auth/token/", { username, password });
      
      // Save tokens
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      
      // Redirect to Dashboard
      router.push("/");
    } catch (err) {
      alert("Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <form onSubmit={handleLogin} className="bg-white p-8 rounded-xl shadow-lg w-96 border">
        <h1 className="text-2xl font-bold mb-6 text-center">Admin Login</h1>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Username</label>
          <div className="relative">
            <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input 
              className="w-full pl-10 p-2 border rounded"
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
            />
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-1">Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input 
              type="password"
              className="w-full pl-10 p-2 border rounded"
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
            />
          </div>
        </div>

        <button 
          disabled={loading}
          className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:bg-blue-300"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
    </div>
  );
}