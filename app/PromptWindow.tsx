"use client";
import React, { useState } from "react";
import Image from 'next/image';

interface Message {
  role: string;
  content: string;
}

interface PromptProps {
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setIsLoading: (loading: boolean) => void;
  isLoading: boolean;
}

const PromptWindow = ({ setMessages, setIsLoading, isLoading }: PromptProps) => {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;

    setIsLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: prompt }]);

    try {
      const res = await fetch("http://localhost:8000/api/process-query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: prompt }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        const errorMessage = errorData.detail || "Backend pipeline error";
        throw new Error(errorMessage);
      }

      const data = await res.json();
      setMessages((prev) => [...prev, { role: "curator", content: data.response }]);
    } catch (err: any) {
      setIsLoading(false);
      setMessages((prev) => [...prev, { role: "system", content: `Error: ${err.message}` }]);
      console.error(err);
    } finally {
      setIsLoading(false);
      setPrompt("");
    }
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className="w-full max-w-2xl bg-white/90 backdrop-blur-sm p-2 rounded-xl shadow-lg border border-amber-200 flex gap-3"
    >
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        disabled={isLoading}
        placeholder={isLoading ? "Curator is searching archives..." : "Ask the virtual curator anything..."}
        className="flex-1 px-4 py-3 bg-gray-50 text-black border border-gray-200 rounded-lg focus:outline-none focus:border-amber-500 disabled:bg-gray-100"
      />
      <button
        type="submit"
        disabled={isLoading}
        className="px-6 py-3 bg-amber-500 hover:bg-amber-600 disabled:bg-amber-300 text-white font-semibold rounded-lg shadow-sm transition-colors cursor-pointer"
      >
        {isLoading ? (
          <Image src="/loading.gif" alt="loading" width={24} height={24} className="animate-spin" />
        ) : (
          <Image src='/enterarrow.png' alt='enterarrow' width={24} height={12}/>
        )}
      </button>
    </form>
  );
};

export default PromptWindow;