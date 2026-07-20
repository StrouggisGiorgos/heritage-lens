"use client";
import { useState } from "react";
import Image from "next/image";
import PromptWindow from "../PromptWindow";
import ResponseWindow from "../ResponseWindow";

export default function Home() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  return (
    <>
      <header className="px-8 py-1 bg-amber-500 shadow-md">
        <nav className="flex items-center justify-between">
          <Image src='/met_gold.png' alt='met_gold' width={256} height={72}/>
        </nav>
      </header>

      <div className="fixed inset-0 w-screen h-screen z-[-10] overflow-hidden">
        <Image
          src="/metbackground.png"
          alt="metbackground"
          fill 
          className="object-cover object-center" 
          priority 
        />
      </div>

      <main className="relative z-10 flex flex-col items-center pt-4 gap-2 px-2">
        <ResponseWindow messages={messages} isLoading={isLoading} />
        <PromptWindow setMessages={setMessages} setIsLoading={setIsLoading} isLoading={isLoading} />
      </main>
    </>
  );
}