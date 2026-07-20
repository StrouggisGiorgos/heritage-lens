"use client";
import React, { useEffect, useRef } from "react";
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: string;
  content: string;
}

interface ResponseProps {
  messages: Message[];
  isLoading: boolean;
}

const ResponseWindow = ({ messages, isLoading }: ResponseProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);
  
  return (
    <div className="w-full max-w-2xl bg-white/90 backdrop-blur-sm p-6 rounded-xl shadow-lg border border-amber-200 h-[530px] flex flex-col justify-between">
      <div className="text-black overflow-y-auto pr-2 flex flex-col gap-4 max-h-[510px]">
        {messages.length === 0 ? (
          <p className="text-gray-400 italic text-center pt-32">
            Step into the vast world of the Metropolitan Museum of Art! <br />
            The curator is waiting for your inquiry.
          </p>
        ) : (
          messages.map((msg, index) => {
            const isUser = msg.role === "user";
            return (
              <div 
                key={index} 
                className={`flex flex-col w-full ${isUser ? "items-end" : "items-start"}`}
              >
                <span className="text-[10px] uppercase tracking-wider text-gray-400 font-bold mb-1 px-1">
                  {isUser ? "You" : "Curator"}
                </span>

                <div 
                  className={`max-w-[85%] px-4 py-3 rounded-2xl text-[14px] shadow-sm leading-relaxed border ${
                    isUser 
                      ? "bg-amber-500 text-white border-amber-600 rounded-tr-none" 
                      : "bg-gray-50 text-gray-800 border-gray-200 rounded-tl-none"
                  }`}
                >
                  <div className="prose prose-sm max-w-none break-words whitespace-pre-wrap">
                    <ReactMarkdown>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            );
          })
        )}

        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500 italic text-xs pt-2 self-start bg-gray-50 px-4 py-2.5 border border-gray-200 rounded-2xl rounded-tl-none shadow-sm">
            <Image src="/loading.gif" alt="loading" width={18} height={18} className="animate-spin" />
            <span>Curating historical data panels...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

    </div>
  );
};

export default ResponseWindow;