"use client"
import { useState } from 'react';
import Link from 'next/link';
import { motion } from "framer-motion";
import { Terminal, ArrowLeft } from 'lucide-react';
import { Button } from "@/components/ui/button";

export default function Waitlist() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setMessage('Please enter a valid email address.');
      return;
    }
    setIsSubmitted(true);
    setMessage('Thank you! You have been added to the waitlist.');
    setEmail('');
  };

  return (
    <main className="relative min-h-screen flex flex-col items-center justify-center">
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#00ff94]/10 via-transparent to-transparent" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md p-8 relative z-10"
      >
        <div className="bg-black/50 backdrop-blur-sm border-2 border-[#00ff94]/20 rounded-xl p-8">
          <h1 className="text-4xl font-bold mb-2 text-white">
            Join the <span className="text-[#00ff94] glitch-text">Resurrection</span>
          </h1>
          <p className="text-[#00ff94]/70 font-mono mb-8">&gt; Be the first to breathe new life into dead repos</p>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label htmlFor="email" className="block text-sm font-medium text-[#00ff94]/90 mb-2 font-mono">
                &gt; Enter your email:
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-black/50 text-[#00ff94] border-2 border-[#00ff94]/20 rounded-lg focus:outline-none focus:border-[#00ff94]/50 font-mono placeholder-[#00ff94]/30"
                placeholder="developer@example.com"
                required
              />
            </div>
            {message && (
              <p className={`text-sm font-mono mb-6 ${isSubmitted ? 'text-[#00ff94]' : 'text-red-500'}`}>
                &gt; {message}
              </p>
            )}
            <Button
              type="submit"
              size="lg"
              className="w-full bg-[#00ff94] text-black hover:bg-[#00ff94]/90 font-bold text-lg shadow-neon"
            >
              <Terminal className="mr-2 h-5 w-5" />
              ./join-waitlist
            </Button>
          </form>
        </div>

        <Link href="/" className="block mt-6 text-center">
          <Button variant="ghost" className="text-[#00ff94]/70 hover:text-[#00ff94] font-mono">
            <ArrowLeft className="mr-2 h-4 w-4" />
            cd ..
          </Button>
        </Link>
      </motion.div>
    </main>
  );
}
