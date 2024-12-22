"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Terminal, GitBranch, Sparkles, Zap, FileCode, Wrench } from 'lucide-react'
import Image from "next/image"
import Link from "next/link"

export default function Home() {
  return (
    <main className="relative min-h-screen">
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#00ff94]/10 via-transparent to-transparent" />
      
      {/* Hero Section */}
      <section className="relative overflow-hidden py-24 md:py-32">
        <div className="container mx-auto px-6 relative z-10">
          <div className="max-w-2xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-block mb-6 px-4 py-1.5 border-2 border-[#00ff94]/20 rounded-full bg-black/50 text-[#00ff94]/80 font-bold">
                pip install grim-repor
              </div>
              <h1 className="text-5xl md:text-7xl font-bold mb-8 text-white leading-tight">
                Your Code's
                <span className="block text-[#00ff94] glitch-text mt-2">Second Chance</span>
              </h1>
              <p className="text-lg md:text-xl text-[#00ff94]/70 mb-10 font-mono leading-relaxed max-w-xl mx-auto">
                &gt; We resurrect research repositories by fixing broken Python dependencies. 
                Our AI vigilante roams the internet, finding and fixing outdated dependencies 
                so your code runs smoothly again.
              </p>
              <div className="flex justify-center gap-4">
                <Link href="/waitlist">
                  <Button size="lg" variant="outline" className="border-2 border-[#00ff94] text-[#00ff94] hover:bg-[#00ff94]/10 font-bold text-lg">
                    <GitBranch className="mr-2 h-5 w-5" />
                    Submit Repository
                    </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Features Section */}
        <div className="container mx-auto px-6 py-32">
          <h2 className="text-4xl md:text-6xl font-bold text-center mb-20 text-white max-w-3xl mx-auto leading-tight">
            &gt; Bringing Your Code <span className="text-[#00ff94] glitch-text">Back to Life</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-10 max-w-6xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.2, duration: 0.5 }}
                className="group bg-black/50 backdrop-blur-sm p-8 rounded-xl border-2 border-[#00ff94]/20 hover:border-[#00ff94]/50 transition-all duration-300"
              >
                <div className="h-16 w-16 rounded-lg bg-[#00ff94]/10 flex items-center justify-center mb-6 group-hover:bg-[#00ff94]/20 transition-colors">
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold mb-4 text-[#00ff94]">{feature.title}</h3>
                <p className="text-[#00ff94]/70 font-mono text-base leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="container mx-auto px-6 pb-32">
          <motion.div 
            className="bg-[#00ff94]/10 border-2 border-[#00ff94]/30 rounded-xl p-12 text-center max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">Found a Dead Repository?</h2>
            <p className="text-xl text-[#00ff94]/70 mb-8 font-mono max-w-2xl mx-auto">Let our AI necromancer bring it back to life.</p>
            <Link href="/submit">
              <Button size="lg" className="bg-[#00ff94] text-black hover:bg-[#00ff94]/90 font-bold text-lg shadow-neon">
                <Zap className="mr-2 h-5 w-5" />
                Resurrect Now
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>
    </main>
  )
}

const features = [
  {
    title: "Smart Scanning",
    description: "&gt; Our AI vigilante automatically identifies broken or outdated Python dependencies in research repositories.",
    icon: <Terminal className="h-8 w-8 text-[#00ff94]" />,
  },
  {
    title: "Auto-Fix Magic",
    description: "&gt; Intelligent version resolution and compatibility fixes for requirements.txt, environment.yml, and setup.py.",
    icon: <Wrench className="h-8 w-8 text-[#00ff94]" />,
  },
  {
    title: "Research First",
    description: "&gt; Specialized in keeping research code alive, ensuring your valuable work remains accessible and reproducible.",
    icon: <Sparkles className="h-8 w-8 text-[#00ff94]" />,
  },
]

